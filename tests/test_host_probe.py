"""Tests for host environment probe (cron, ports, examples report)."""

from __future__ import annotations

import json
from pathlib import Path

from env2llm.ir import (
    HostAgentIR,
    HostContainerIR,
    HostPortIR,
    HostProcessIR,
    SystemMapIR,
)
from env2llm.policy.host import apply_host_probe
from env2llm.probes.host import collect_host_probe, _parse_cron_line


def test_parse_cron_line_taskinity_marker() -> None:
    line = "*/5 * * * * bash scripts/www/run_monitors.sh # taskinity-www-monitor"
    entry = _parse_cron_line(line)
    assert entry.enabled is True
    assert entry.schedule == "*/5 * * * *"
    assert "run_monitors.sh" in entry.command
    assert entry.marker == "taskinity-www-monitor"


def test_apply_host_probe_adds_schedules_and_doql_block(monkeypatch, tmp_path: Path) -> None:
    report_dir = tmp_path / "output" / "examples"
    report_dir.mkdir(parents=True)
    (report_dir / "comprehensive_report.json").write_text(
        json.dumps(
            {
                "summary": {"pass": 10, "fail": 0, "skip": 2},
                "capabilities": {"available": ["docker", "www_8788"], "unavailable": ["adb"]},
            }
        ),
        encoding="utf-8",
    )

    probe = collect_host_probe(project_dir=tmp_path)

    monkeypatch.setattr(
        "env2llm.policy.host.collect_host_probe",
        lambda **_: probe.model_copy(
            update={
                "cron_entries": [_parse_cron_line("0 * * * * echo hi # taskinity-www-monitor")],
                "cron_taskinity_installed": True,
                "examples_test_summary": {"pass": 10, "fail": 0, "skip": 2},
                "examples_report_path": str(report_dir / "comprehensive_report.json"),
                "ports": [
                    HostPortIR(
                        port=8788,
                        address="0.0.0.0",
                        pid=123,
                        process="uvicorn",
                    )
                ],
                "processes": [
                    HostProcessIR(
                        pid=123,
                        ppid=1,
                        status="Ssl",
                        command="uvicorn",
                        args="uvicorn app:app --port 8788",
                    )
                ],
                "containers": [
                    HostContainerIR(
                        id="abc123",
                        name="hypervisor-www-chat",
                        image="hypervisor-www-chat:latest",
                        state="running",
                        status="Up",
                        project="www",
                        service="www-chat",
                    )
                ],
                "agents": [
                    HostAgentIR(
                        id="weather-map-agent.local",
                        agent_ref="agent://weather-map-agent",
                        ok=False,
                        service_status="stopped",
                        runtime_status="stopped",
                        effective_port=8101,
                        effective_health_uri="http://localhost:8101/health",
                        recommended_action="rebind_port",
                        incident_codes=["HEALTH_FAILED"],
                    )
                ],
            }
        ),
    )

    ir = SystemMapIR(example_id="hypervisor")
    apply_host_probe(ir, enabled=True, project_dir=tmp_path)

    assert ir.host is not None
    assert ir.host.cron_taskinity_installed is True
    assert any(sched.id == "taskinity-www-monitor" for sched in ir.schedules)
    assert ir.data.get("host.examples_test", {}).get("pass") == 10
    assert ir.data["host.port_count"] == 1
    assert ir.data["host.process_count"] == 1
    assert ir.data["host.container_count"] == 1
    assert ir.data["host.agent_count"] == 1
    assert ir.data["host.agent_degraded_count"] == 1

    from env2llm.render.doql.blocks import render_host_block

    doql = "".join(render_host_block(ir))
    assert "host {" in doql
    assert "host_cron[" in doql or "cron_taskinity_installed: true" in doql
    assert "host_examples_test" in doql
    assert "host_port[" in doql
    assert "host_process[" in doql
    assert "host_container[" in doql
    assert "host_agent[" in doql
    assert "recommended_action" in doql
