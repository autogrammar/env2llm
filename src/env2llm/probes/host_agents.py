"""Hypervisor agent inspection for host probes."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Mapping

import yaml

from env2llm.ir import HostAgentIR

from .host_runtime import run_cmd


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


def _agent_process_pid(process: Mapping[str, Any]) -> int | None:
    pid = process.get("pid")
    return pid if isinstance(pid, int) else None


def _agent_effective_port(readiness: Mapping[str, Any]) -> int | None:
    port = readiness.get("effective_port")
    return port if isinstance(port, int) else None


def _agent_health_uri(
    readiness: Mapping[str, Any],
    agent_readiness: Mapping[str, Any],
) -> str:
    return str(
        readiness.get("effective_health_uri")
        or agent_readiness.get("effective_health_uri")
        or ""
    )


def _coerce_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _agent_incident_codes(agent_readiness: Mapping[str, Any]) -> list[str]:
    return [str(code) for code in agent_readiness.get("incident_codes") or []]


def _agent_from_payload(deployment_id: str, payload: dict[str, Any]) -> HostAgentIR:
    readiness = _coerce_mapping(payload.get("readiness"))
    agent_readiness = _coerce_mapping(payload.get("agent_readiness"))
    process = _coerce_mapping(payload.get("process"))
    return HostAgentIR(
        id=str(payload.get("id") or deployment_id),
        agent_ref=str(payload.get("agent_ref") or ""),
        ok=bool(payload.get("ok")),
        service_status=str(payload.get("service_status") or ""),
        runtime_status=str(payload.get("runtime_status") or ""),
        pid=_agent_process_pid(process),
        process_running=bool(process.get("running")),
        effective_port=_agent_effective_port(readiness),
        effective_health_uri=_agent_health_uri(readiness, agent_readiness),
        recommended_action=str(agent_readiness.get("recommended_action") or ""),
        incident_codes=_agent_incident_codes(agent_readiness),
        log_uri=str(payload.get("log_uri") or ""),
        process_log_uri=str(payload.get("process_log_uri") or ""),
    )


def _inspect_agent(deployment_id: str, project_dir: Path) -> HostAgentIR:
    probe = run_cmd(
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


def collect_agents(project_dir: Path, limit: int = 20) -> list[HostAgentIR]:
    if shutil.which("hypervisor") is None:
        return []
    return [
        _inspect_agent(deployment_id, project_dir)
        for deployment_id in _deployment_ids(project_dir)[:limit]
    ]
