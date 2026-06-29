"""Merge live host probe (cron, ports, tooling) into SystemMapIR."""

from __future__ import annotations

import os
from pathlib import Path

from env2llm.ir import (
    RuntimeSpecIR,
    ScheduleSpecIR,
    SystemMapIR,
)
from env2llm.probes.host import collect_host_probe, cron_entries_to_schedules

_HOST_RUNTIME = RuntimeSpecIR(
    id="probe:host",
    kind="external",
    uri="host://localhost",
    roles=["cron", "ports", "processes", "docker", "agents", "monitoring", "examples_test"],
    status="unknown",
)


def host_probe_enabled(*, explicit: bool | None = None) -> bool:
    if explicit is not None:
        return explicit
    token = os.environ.get("ENV2LLM_HOST_PROBE", "").strip().lower()
    if token in ("0", "false", "no"):
        return False
    if token in ("1", "true", "yes"):
        return True
    # Default on for project dirs that look like hypervisor/taskinity repos.
    return True


def apply_host_probe(
    ir: SystemMapIR,
    *,
    enabled: bool | None = None,
    project_dir: Path | str | None = None,
) -> SystemMapIR:
    """Attach cron, HTTP endpoints, and examples-test capability snapshot."""
    if not host_probe_enabled(explicit=enabled):
        return ir

    probe = collect_host_probe(project_dir=project_dir)
    ir.host = probe

    existing_rt = ir.runtime("probe:host")
    if existing_rt is not None:
        existing_rt.status = probe.status  # type: ignore[assignment]
    else:
        ir.runtimes.append(_HOST_RUNTIME.model_copy(update={"status": probe.status}))

    # Mirror into data + schedules (DOQL registry consumers read these blocks).
    ir.data["host.hostname"] = probe.hostname
    ir.data["host.platform"] = probe.platform
    ir.data["host.cron_taskinity_installed"] = probe.cron_taskinity_installed
    ir.data["host.cron_entry_count"] = len(probe.cron_entries)
    if probe.monitor_log_path:
        ir.data["host.monitor_log_path"] = probe.monitor_log_path
    if probe.examples_report_path:
        ir.data["host.examples_report_path"] = probe.examples_report_path
    if probe.examples_test_summary:
        ir.data["host.examples_test"] = probe.examples_test_summary
    ir.data["host.port_count"] = len(probe.ports)
    ir.data["host.process_count"] = len(probe.processes)
    ir.data["host.container_count"] = len(probe.containers)
    ir.data["host.agent_count"] = len(probe.agents)
    ir.data["host.agent_healthy_count"] = sum(1 for agent in probe.agents if agent.ok)
    ir.data["host.agent_degraded_count"] = sum(1 for agent in probe.agents if not agent.ok)

    for agent in probe.agents:
        if agent.effective_health_uri:
            ir.data[f"host.agent.{agent.id}.effective_health_uri"] = agent.effective_health_uri
        ir.data[f"host.agent.{agent.id}.ok"] = agent.ok
        if agent.recommended_action:
            ir.data[f"host.agent.{agent.id}.recommended_action"] = agent.recommended_action

    for key, value in probe.capabilities.items():
        ir.data[f"host.cap.{key}"] = value
        if value and key not in ir.capabilities:
            ir.capabilities.append(f"host_{key}")

    for endpoint in probe.endpoints:
        if endpoint.ok:
            ir.data[f"host.endpoint.{endpoint.id}"] = endpoint.url

    existing_schedule_ids = {sched.id for sched in ir.schedules}
    for item in cron_entries_to_schedules(probe.cron_entries):
        sched_id = item["id"]
        if sched_id in existing_schedule_ids:
            continue
        ir.schedules.append(
            ScheduleSpecIR(
                id=sched_id,
                cron=item["cron"],
                task=item["task"],
                enabled=True,
                timezone="local",
            )
        )
        existing_schedule_ids.add(sched_id)

    if probe.cron_taskinity_installed and "www_monitor_cron" not in ir.capabilities:
        ir.capabilities.append("www_monitor_cron")

    ir.metadata["host_probe"] = {
        "runtime_id": "probe:host",
        "status": probe.status,
        "cron_entries": len(probe.cron_entries),
        "cron_taskinity": probe.cron_taskinity_installed,
        "endpoints_up": sum(1 for ep in probe.endpoints if ep.ok),
        "ports": len(probe.ports),
        "processes": len(probe.processes),
        "containers": len(probe.containers),
        "agents": len(probe.agents),
        "agents_healthy": sum(1 for agent in probe.agents if agent.ok),
        "capabilities_available": [k for k, v in probe.capabilities.items() if v],
        "probed_at": probe.probed_at,
    }

    return ir
