"""Host environment probe — cron, HTTP ports, tooling, examples test report."""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import yaml

from env2llm.ir import (
    CronEntryIR,
    HostAgentIR,
    HostContainerIR,
    HostEndpointIR,
    HostPortIR,
    HostProbeIR,
    HostProcessIR,
)

TASKINITY_CRON_MARKER = "taskinity-www-monitor"
DEFAULT_MONITOR_LOG = "/tmp/taskinity-monitor.log"
EXAMPLES_REPORT = "output/examples/comprehensive_report.json"
RELEVANT_PROCESS_RE = re.compile(
    r"(uvicorn|hypervisor|uri2ops|urish|weather|invoice|taskinity|monitor|docker)",
    re.IGNORECASE,
)


def _http_ok(url: str, timeout: float = 2.5) -> tuple[bool, str]:
    try:
        req = Request(url, headers={"User-Agent": "env2llm-host-probe/0.1"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.status == 200, f"status={resp.status}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _tcp_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _run(
    cmd: list[str],
    *,
    timeout: int = 15,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _cli_available(name: str) -> bool:
    return shutil.which(name) is not None


def _playwright_available() -> bool:
    try:
        import playwright  # noqa: F401

        return True
    except ImportError:
        return False


def _uia_available() -> bool:
    if platform.system().lower() != "windows":
        return False
    try:
        import pywinauto  # noqa: F401

        return True
    except ImportError:
        return False


def _adb_device() -> bool:
    adb = shutil.which("adb")
    if adb is None:
        return False
    probe = _run([adb, "devices"], timeout=10)
    if probe.returncode != 0:
        return False
    lines = [line for line in probe.stdout.splitlines()[1:] if line.strip()]
    return any("\tdevice" in line for line in lines)


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    probe = _run(["docker", "info"], timeout=20)
    return probe.returncode == 0


def _read_crontab() -> tuple[bool, list[str]]:
    if shutil.which("crontab") is None:
        return False, []
    probe = _run(["crontab", "-l"], timeout=10)
    if probe.returncode != 0:
        return True, []
    lines = [line.strip() for line in probe.stdout.splitlines() if line.strip()]
    return True, lines


def _parse_cron_line(line: str) -> CronEntryIR:
    marker = ""
    if TASKINITY_CRON_MARKER in line:
        marker = TASKINITY_CRON_MARKER
    if line.startswith("#"):
        return CronEntryIR(raw=line, enabled=False, marker=marker)
    parts = line.split(None, 5)
    if len(parts) >= 6:
        schedule = " ".join(parts[:5])
        command = parts[5]
        if "#" in command:
            cmd_part, comment = command.split("#", 1)
            command = cmd_part.strip()
            comment = comment.strip()
            if TASKINITY_CRON_MARKER in comment:
                marker = TASKINITY_CRON_MARKER
            elif comment and not marker:
                marker = comment
        return CronEntryIR(
            raw=line,
            schedule=schedule,
            command=command,
            marker=marker,
            enabled=True,
        )
    return CronEntryIR(raw=line, command=line, enabled=True, marker=marker)


def _load_examples_summary(project_dir: Path) -> tuple[str, dict[str, Any]]:
    report_path = project_dir / EXAMPLES_REPORT
    if not report_path.is_file():
        return "", {}
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return str(report_path), {}
    summary = payload.get("summary") or {}
    caps = payload.get("capabilities") or {}
    return str(report_path), {
        "pass": summary.get("pass"),
        "fail": summary.get("fail"),
        "skip": summary.get("skip"),
        "available_capabilities": caps.get("available") or [],
        "unavailable_capabilities": caps.get("unavailable") or [],
        "generated_at": payload.get("generated_at"),
    }


def _tail_log(path: Path, lines: int = 8) -> list[str]:
    if not path.is_file():
        return []
    try:
        content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    return content[-lines:]


def _parse_labels(labels: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in labels.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def _collect_containers(limit: int = 80) -> list[HostContainerIR]:
    if shutil.which("docker") is None:
        return []
    probe = _run(["docker", "ps", "--format", "{{json .}}"], timeout=20)
    if probe.returncode != 0:
        return []
    containers: list[HostContainerIR] = []
    for line in probe.stdout.splitlines():
        if len(containers) >= limit:
            break
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        labels = _parse_labels(str(row.get("Labels") or ""))
        containers.append(
            HostContainerIR(
                id=str(row.get("ID") or ""),
                name=str(row.get("Names") or ""),
                image=str(row.get("Image") or ""),
                state=str(row.get("State") or ""),
                status=str(row.get("Status") or ""),
                ports=str(row.get("Ports") or ""),
                project=labels.get("com.docker.compose.project", ""),
                service=labels.get("com.docker.compose.service", ""),
            )
        )
    return containers


def _parse_ss_port(local_address: str) -> tuple[str, int | None]:
    match = re.search(r":(?P<port>\d+)$", local_address)
    if not match:
        return local_address, None
    return local_address[: match.start()], int(match.group("port"))


def _is_relevant_port(port: int, detail: str) -> bool:
    if port in {80, 443, 2222, 3000, 4000, 5173, 5432, 6379, 8788, 8791}:
        return True
    if 8000 <= port <= 9000:
        return True
    if 18000 <= port <= 18100:
        return True
    return bool(RELEVANT_PROCESS_RE.search(detail))


def _collect_ports(limit: int = 100) -> list[HostPortIR]:
    if shutil.which("ss") is None:
        return []
    probe = _run(["ss", "-ltnp"], timeout=10)
    if probe.returncode != 0:
        return []
    ports: list[HostPortIR] = []
    seen: set[tuple[str, int]] = set()
    for line in probe.stdout.splitlines()[1:]:
        parts = line.split(None, 5)
        if len(parts) < 4:
            continue
        address, port = _parse_ss_port(parts[3])
        if port is None:
            continue
        detail = parts[5] if len(parts) > 5 else ""
        if not _is_relevant_port(port, detail):
            continue
        key = (address, port)
        if key in seen:
            continue
        seen.add(key)
        pid_match = re.search(r"pid=(\d+)", detail)
        name_match = re.search(r'users:\(\("([^"]+)"', detail)
        ports.append(
            HostPortIR(
                port=port,
                address=address,
                pid=int(pid_match.group(1)) if pid_match else None,
                process=name_match.group(1) if name_match else "",
                detail=detail,
            )
        )
        if len(ports) >= limit:
            break
    return ports


def _collect_processes(limit: int = 80) -> list[HostProcessIR]:
    probe = _run(
        ["ps", "-eo", "pid,ppid,stat,etime,comm,args", "--sort=pid"],
        timeout=10,
    )
    if probe.returncode != 0:
        return []
    processes: list[HostProcessIR] = []
    for line in probe.stdout.splitlines()[1:]:
        if not RELEVANT_PROCESS_RE.search(line):
            continue
        parts = line.split(None, 5)
        if len(parts) < 6:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
        except ValueError:
            continue
        processes.append(
            HostProcessIR(
                pid=pid,
                ppid=ppid,
                status=parts[2],
                elapsed=parts[3],
                command=parts[4],
                args=parts[5],
            )
        )
        if len(processes) >= limit:
            break
    return processes


def _deployment_ids(project_dir: Path) -> list[str]:
    path = project_dir / "deployments" / "agent_deployments.yaml"
    if not path.is_file():
        return []
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return []
    ids: list[str] = []
    for item in payload.get("deployments") or []:
        if isinstance(item, dict) and item.get("id"):
            ids.append(str(item["id"]))
    return ids


def _failed_agent(deployment_id: str, service_status: str) -> HostAgentIR:
    return HostAgentIR(
        id=deployment_id,
        ok=False,
        service_status=service_status,
        runtime_status="unknown",
    )


def _agent_from_payload(deployment_id: str, payload: dict[str, Any]) -> HostAgentIR:
    readiness = payload.get("readiness") or {}
    agent_readiness = payload.get("agent_readiness") or {}
    process = payload.get("process") or {}
    return HostAgentIR(
        id=str(payload.get("id") or deployment_id),
        agent_ref=str(payload.get("agent_ref") or ""),
        ok=bool(payload.get("ok")),
        service_status=str(payload.get("service_status") or ""),
        runtime_status=str(payload.get("runtime_status") or ""),
        pid=process.get("pid") if isinstance(process.get("pid"), int) else None,
        process_running=bool(process.get("running")),
        effective_port=readiness.get("effective_port")
        if isinstance(readiness.get("effective_port"), int)
        else None,
        effective_health_uri=str(
            readiness.get("effective_health_uri")
            or agent_readiness.get("effective_health_uri")
            or ""
        ),
        recommended_action=str(agent_readiness.get("recommended_action") or ""),
        incident_codes=[str(code) for code in agent_readiness.get("incident_codes") or []],
        log_uri=str(payload.get("log_uri") or ""),
        process_log_uri=str(payload.get("process_log_uri") or ""),
    )


def _inspect_agent(deployment_id: str, project_dir: Path) -> HostAgentIR:
    probe = _run(
        ["hypervisor", "inspect-agent", deployment_id],
        timeout=20,
        cwd=project_dir,
    )
    if probe.returncode != 0:
        return _failed_agent(deployment_id, "inspect_failed")
    try:
        payload = json.loads(probe.stdout)
    except json.JSONDecodeError:
        return _failed_agent(deployment_id, "inspect_non_json")
    if not isinstance(payload, dict):
        return _failed_agent(deployment_id, "inspect_non_json")
    return _agent_from_payload(deployment_id, payload)


def _collect_agents(project_dir: Path, limit: int = 20) -> list[HostAgentIR]:
    if shutil.which("hypervisor") is None:
        return []
    return [
        _inspect_agent(deployment_id, project_dir)
        for deployment_id in _deployment_ids(project_dir)[:limit]
    ]


def collect_host_probe(*, project_dir: Path | str | None = None) -> HostProbeIR:
    """Snapshot cron, local services, and example-test readiness on this host."""
    root = Path(project_dir).resolve() if project_dir is not None else Path.cwd()
    now = datetime.now(UTC).isoformat()

    cron_ok, cron_lines = _read_crontab()
    cron_entries = [_parse_cron_line(line) for line in cron_lines]
    taskinity_cron = any(
        entry.enabled and entry.marker == TASKINITY_CRON_MARKER for entry in cron_entries
    )

    endpoints: list[HostEndpointIR] = []
    for port in range(8101, 8131):
        url = f"http://localhost:{port}/health"
        ok, detail = _http_ok(url, timeout=1.5)
        if ok or port in (8101, 8103, 8110, 8118):
            endpoints.append(
                HostEndpointIR(
                    id=f"agent_http_{port}",
                    url=url,
                    ok=ok,
                    detail=detail if not ok else "healthy",
                )
            )
    www_ok, www_detail = _http_ok("http://localhost:8788/www/", timeout=3.0)
    endpoints.append(
        HostEndpointIR(
            id="www_8788",
            url="http://localhost:8788/www/",
            ok=www_ok,
            detail=www_detail if not www_ok else "ok",
        )
    )
    api_ok, api_detail = _http_ok(
        "http://localhost:8788/health",
        timeout=2.0,
    )
    endpoints.append(
        HostEndpointIR(
            id="www_health",
            url="http://localhost:8788/health",
            ok=api_ok,
            detail=api_detail if not api_ok else "ok",
        )
    )

    ports = _collect_ports()
    processes = _collect_processes()
    containers = _collect_containers()
    agents = _collect_agents(root)

    capabilities = {
        "docker": _docker_available(),
        "playwright": _playwright_available(),
        "cli_uri": _cli_available("uri") or _cli_available("urish"),
        "cli_uri3": _cli_available("uri3"),
        "cli_hypervisor": _cli_available("hypervisor"),
        "cli_touri": _cli_available("touri"),
        "cli_uri2flow": _cli_available("uri2flow"),
        "cli_nl2uri": _cli_available("nl2uri"),
        "curl": _cli_available("curl"),
        "crontab": cron_ok,
        "adb": _adb_device(),
        "uia": _uia_available(),
        "openrouter": bool(os.environ.get("OPENROUTER_API_KEY", "").strip()),
        "agent_http_any": any(ep.ok and ep.id.startswith("agent_http_") for ep in endpoints),
        "agent_http_8101": next(
            (ep.ok for ep in endpoints if ep.id == "agent_http_8101"),
            False,
        ),
        "www_8788": www_ok,
        "www_health": api_ok,
        "docker_containers": bool(containers),
        "processes": bool(processes),
        "ports": bool(ports),
        "agents": bool(agents),
    }

    report_path, examples_summary = _load_examples_summary(root)
    monitor_log = Path(DEFAULT_MONITOR_LOG)
    if not monitor_log.is_file():
        alt = root / "output" / "monitoring" / "www-monitor.log"
        monitor_log = alt if alt.is_file() else monitor_log

    available_count = sum(1 for value in capabilities.values() if value)
    status: str
    if available_count >= 4:
        status = "available"
    elif available_count > 0:
        status = "partial"
    else:
        status = "unknown"

    return HostProbeIR(
        hostname=platform.node(),
        platform=platform.platform(),
        probed_at=now,
        status=status,  # type: ignore[arg-type]
        cron_available=cron_ok,
        cron_taskinity_installed=taskinity_cron,
        cron_entries=cron_entries,
        endpoints=endpoints,
        capabilities=capabilities,
        monitor_log_path=str(monitor_log) if monitor_log.is_file() else "",
        monitor_log_tail=_tail_log(monitor_log),
        examples_report_path=report_path,
        examples_test_summary=examples_summary,
        ports=ports,
        processes=processes,
        containers=containers,
        agents=agents,
    )


def cron_entries_to_schedules(entries: list[CronEntryIR]) -> list[dict[str, str]]:
    """Convert enabled cron lines to schedule dicts for SystemMapIR.schedules."""
    out: list[dict[str, str]] = []
    for idx, entry in enumerate(entries):
        if not entry.enabled or not entry.schedule:
            continue
        task = entry.command or entry.raw
        out.append(
            {
                "id": entry.marker or f"host_cron_{idx}",
                "cron": entry.schedule,
                "task": task,
            }
        )
    return out
