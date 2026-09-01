"""Render host-related DOQL blocks from SystemMapIR."""

from __future__ import annotations

from env2llm.ir import (
    CronEntryIR,
    HostAgentIR,
    HostContainerIR,
    HostEndpointIR,
    HostPortIR,
    HostProbeIR,
    HostProcessIR,
    SystemMapIR,
)
from .helpers import bool_lit, esc_str, esc_str_full, join_csv


def _render_host_capability_lines(probe: HostProbeIR) -> list[str]:
    if not probe.capabilities:
        return []
    available = [key for key, ok in probe.capabilities.items() if ok]
    missing = [key for key, ok in probe.capabilities.items() if not ok]
    lines: list[str] = []
    if available:
        lines.append(f'  capabilities_available: "{join_csv(available)}";')
    if missing:
        lines.append(f'  capabilities_missing: "{join_csv(missing)}";')
    return lines


def _render_host_header(probe: HostProbeIR) -> list[str]:
    lines = [
        "host {",
        f'  hostname: "{esc_str(probe.hostname)}";',
        f'  platform: "{esc_str(probe.platform)}";',
        f'  status: "{probe.status}";',
        f"  cron_available: {bool_lit(probe.cron_available)};",
        f"  cron_taskinity_installed: {bool_lit(probe.cron_taskinity_installed)};",
    ]
    if probe.probed_at:
        lines.append(f'  probed_at: "{esc_str(probe.probed_at)}";')
    if probe.monitor_log_path:
        lines.append(f'  monitor_log_path: "{esc_str(probe.monitor_log_path)}";')
    if probe.examples_report_path:
        lines.append(f'  examples_report_path: "{esc_str(probe.examples_report_path)}";')
    lines.extend(_render_host_capability_lines(probe))
    lines.extend(["}", ""])
    return lines


def _render_host_cron_entries(entries: list[CronEntryIR]) -> list[str]:
    lines: list[str] = []
    for idx, entry in enumerate(entries):
        lines.append(f"host_cron[{idx}] {{")
        if entry.schedule:
            lines.append(f'  schedule: "{esc_str(entry.schedule)}";')
        if entry.command:
            lines.append(f'  command: "{esc_str_full(entry.command)}";')
        if entry.marker:
            lines.append(f'  marker: "{esc_str(entry.marker)}";')
        lines.append(f"  enabled: {bool_lit(entry.enabled)};")
        lines.extend(["}", ""])
    return lines


def _render_host_endpoints(endpoints: list[HostEndpointIR]) -> list[str]:
    lines: list[str] = []
    for idx, endpoint in enumerate(endpoints):
        lines.append(f"host_endpoint[{idx}] {{")
        lines.append(f'  id: "{esc_str(endpoint.id)}";')
        lines.append(f'  url: "{esc_str(endpoint.url)}";')
        lines.append(f"  ok: {bool_lit(endpoint.ok)};")
        if endpoint.detail:
            lines.append(f'  detail: "{esc_str(endpoint.detail)}";')
        lines.extend(["}", ""])
    return lines


def _render_host_ports(ports: list[HostPortIR]) -> list[str]:
    lines: list[str] = []
    for idx, port in enumerate(ports):
        lines.append(f"host_port[{idx}] {{")
        lines.append(f"  port: {port.port};")
        if port.address:
            lines.append(f'  address: "{esc_str(port.address)}";')
        lines.append(f'  protocol: "{esc_str(port.protocol)}";')
        if port.pid is not None:
            lines.append(f"  pid: {port.pid};")
        if port.process:
            lines.append(f'  process: "{esc_str(port.process)}";')
        if port.detail:
            lines.append(f'  detail: "{esc_str_full(port.detail)}";')
        lines.extend(["}", ""])
    return lines


def _render_host_processes(processes: list[HostProcessIR]) -> list[str]:
    lines: list[str] = []
    for idx, process in enumerate(processes):
        lines.append(f"host_process[{idx}] {{")
        lines.append(f"  pid: {process.pid};")
        if process.ppid is not None:
            lines.append(f"  ppid: {process.ppid};")
        if process.status:
            lines.append(f'  status: "{esc_str(process.status)}";')
        if process.elapsed:
            lines.append(f'  elapsed: "{esc_str(process.elapsed)}";')
        if process.command:
            lines.append(f'  command: "{esc_str(process.command)}";')
        if process.args:
            lines.append(f'  args: "{esc_str_full(process.args)}";')
        lines.extend(["}", ""])
    return lines


def _render_host_containers(containers: list[HostContainerIR]) -> list[str]:
    lines: list[str] = []
    for idx, container in enumerate(containers):
        lines.append(f"host_container[{idx}] {{")
        if container.id:
            lines.append(f'  id: "{esc_str(container.id)}";')
        if container.name:
            lines.append(f'  name: "{esc_str(container.name)}";')
        if container.image:
            lines.append(f'  image: "{esc_str(container.image)}";')
        if container.state:
            lines.append(f'  state: "{esc_str(container.state)}";')
        if container.status:
            lines.append(f'  status: "{esc_str(container.status)}";')
        if container.ports:
            lines.append(f'  ports: "{esc_str_full(container.ports)}";')
        if container.project:
            lines.append(f'  project: "{esc_str(container.project)}";')
        if container.service:
            lines.append(f'  service: "{esc_str(container.service)}";')
        lines.extend(["}", ""])
    return lines


def _render_host_agent_identity(agent: HostAgentIR) -> list[str]:
    lines: list[str] = []
    if agent.id:
        lines.append(f'  id: "{esc_str(agent.id)}";')
    if agent.agent_ref:
        lines.append(f'  agent_ref: "{esc_str(agent.agent_ref)}";')
    lines.append(f"  ok: {bool_lit(agent.ok)};")
    if agent.service_status:
        lines.append(f'  service_status: "{esc_str(agent.service_status)}";')
    if agent.runtime_status:
        lines.append(f'  runtime_status: "{esc_str(agent.runtime_status)}";')
    return lines


def _render_host_agent_runtime(agent: HostAgentIR) -> list[str]:
    lines: list[str] = []
    if agent.pid is not None:
        lines.append(f"  pid: {agent.pid};")
    lines.append(f"  process_running: {bool_lit(agent.process_running)};")
    if agent.effective_port is not None:
        lines.append(f"  effective_port: {agent.effective_port};")
    if agent.effective_health_uri:
        lines.append(f'  effective_health_uri: "{esc_str(agent.effective_health_uri)}";')
    if agent.recommended_action:
        lines.append(f'  recommended_action: "{esc_str(agent.recommended_action)}";')
    if agent.incident_codes:
        lines.append(f'  incident_codes: "{join_csv(agent.incident_codes)}";')
    if agent.log_uri:
        lines.append(f'  log_uri: "{esc_str(agent.log_uri)}";')
    if agent.process_log_uri:
        lines.append(f'  process_log_uri: "{esc_str(agent.process_log_uri)}";')
    return lines


def _render_host_agent_block(idx: int, agent: HostAgentIR) -> list[str]:
    lines = [f"host_agent[{idx}] {{"]
    lines.extend(_render_host_agent_identity(agent))
    lines.extend(_render_host_agent_runtime(agent))
    lines.extend(["}", ""])
    return lines


def _render_host_agents(agents: list[HostAgentIR]) -> list[str]:
    lines: list[str] = []
    for idx, agent in enumerate(agents):
        lines.extend(_render_host_agent_block(idx, agent))
    return lines


def _render_host_monitor_tail(tail: list[str]) -> list[str]:
    if not tail:
        return []
    lines = ["host_monitor_log_tail {"]
    for idx, row in enumerate(tail):
        lines.append(f'  line_{idx}: "{esc_str_full(row)}";')
    lines.extend(["}", ""])
    return lines


def _render_host_examples_test(summary: dict) -> list[str]:
    if not summary:
        return []
    lines = ["host_examples_test {"]
    for key, value in summary.items():
        if isinstance(value, list):
            lines.append(f'  {key}: "{join_csv(str(v) for v in value)}";')
        else:
            lines.append(f'  {key}: "{esc_str(str(value))}";')
    lines.extend(["}", ""])
    return lines


def render_host_block(ir: SystemMapIR) -> list[str]:
    probe = ir.host
    if probe is None:
        return []
    lines: list[str] = []
    lines.extend(_render_host_header(probe))
    lines.extend(_render_host_cron_entries(probe.cron_entries))
    lines.extend(_render_host_endpoints(probe.endpoints))
    lines.extend(_render_host_ports(probe.ports))
    lines.extend(_render_host_processes(probe.processes))
    lines.extend(_render_host_containers(probe.containers))
    lines.extend(_render_host_agents(probe.agents))
    lines.extend(_render_host_monitor_tail(probe.monitor_log_tail))
    lines.extend(_render_host_examples_test(probe.examples_test_summary))
    return lines
