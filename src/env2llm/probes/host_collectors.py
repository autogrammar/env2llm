"""Collect host inventory: containers, ports, processes, examples report."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from env2llm.ir import HostContainerIR, HostPortIR, HostProcessIR

from .host_runtime import EXAMPLES_REPORT, RELEVANT_PROCESS_RE, run_cmd


def load_examples_summary(project_dir: Path) -> tuple[str, dict[str, Any]]:
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


def tail_log(path: Path, lines: int = 8) -> list[str]:
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


def _container_from_docker_row(row: dict[str, Any]) -> HostContainerIR:
    labels = _parse_labels(str(row.get("Labels") or ""))
    return HostContainerIR(
        id=str(row.get("ID") or ""),
        name=str(row.get("Names") or ""),
        image=str(row.get("Image") or ""),
        state=str(row.get("State") or ""),
        status=str(row.get("Status") or ""),
        ports=str(row.get("Ports") or ""),
        project=labels.get("com.docker.compose.project", ""),
        service=labels.get("com.docker.compose.service", ""),
    )


def collect_containers(limit: int = 80) -> list[HostContainerIR]:
    if shutil.which("docker") is None:
        return []
    probe = run_cmd(["docker", "ps", "--format", "{{json .}}"], timeout=20)
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
        if not isinstance(row, dict):
            continue
        containers.append(_container_from_docker_row(row))
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


def _port_from_ss_detail(detail: str) -> tuple[int | None, str]:
    pid_match = re.search(r"pid=(\d+)", detail)
    name_match = re.search(r'users:\(\("([^"]+)"', detail)
    pid = int(pid_match.group(1)) if pid_match else None
    process = name_match.group(1) if name_match else ""
    return pid, process


def _port_from_ss_line(
    line: str,
    *,
    seen: set[tuple[str, int]],
) -> HostPortIR | None:
    parts = line.split(None, 5)
    if len(parts) < 4:
        return None
    address, port = _parse_ss_port(parts[3])
    if port is None:
        return None
    detail = parts[5] if len(parts) > 5 else ""
    if not _is_relevant_port(port, detail):
        return None
    key = (address, port)
    if key in seen:
        return None
    seen.add(key)
    pid, process = _port_from_ss_detail(detail)
    return HostPortIR(
        port=port,
        address=address,
        pid=pid,
        process=process,
        detail=detail,
    )


def collect_ports(limit: int = 100) -> list[HostPortIR]:
    if shutil.which("ss") is None:
        return []
    probe = run_cmd(["ss", "-ltnp"], timeout=10)
    if probe.returncode != 0:
        return []
    ports: list[HostPortIR] = []
    seen: set[tuple[str, int]] = set()
    for line in probe.stdout.splitlines()[1:]:
        port = _port_from_ss_line(line, seen=seen)
        if port is None:
            continue
        ports.append(port)
        if len(ports) >= limit:
            break
    return ports


def collect_processes(limit: int = 80) -> list[HostProcessIR]:
    probe = run_cmd(
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
