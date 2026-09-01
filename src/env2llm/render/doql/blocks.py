"""Render individual DOQL blocks from SystemMapIR."""

from __future__ import annotations

from datetime import datetime, timezone

from env2llm.ir import (
    CronEntryIR,
    DesktopDisplayIR,
    DesktopIdeCalibrationIR,
    DesktopPointerIR,
    DesktopProbeIR,
    DesktopWindowIR,
    HostAgentIR,
    HostContainerIR,
    HostEndpointIR,
    HostPortIR,
    HostProbeIR,
    HostProcessIR,
    SystemMapIR,
)
from .helpers import (
    bool_lit,
    data_value_line,
    esc_str,
    esc_str_full,
    history_value_line,
    join_csv,
    process_field_line,
)


def render_header(ir: SystemMapIR) -> list[str]:
    return [
        f"// DOQL system map — {ir.example_id}",
        "// role: LLM-generated schema (SystemMapIR → DOQL)",
        f"// format: {ir.format}",
        f"// generated: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]


def render_environment_block(ir: SystemMapIR) -> list[str]:
    lines = [f'environment[name="{ir.example_id}"] {{']
    for key in sorted(ir.environment):
        lines.append(f'  {key}: "{esc_str(str(ir.environment[key]))}";')
    lines.extend(["}", ""])
    return lines


def render_data_block(ir: SystemMapIR) -> list[str]:
    if not ir.data:
        return []
    lines = ["data {"]
    for key in sorted(ir.data):
        lines.append(data_value_line(key, ir.data[key]))
    lines.extend(["}", ""])
    return lines


def render_artifacts_block(ir: SystemMapIR) -> list[str]:
    lines: list[str] = []
    for idx, art in enumerate(ir.artifacts):
        lines.append(f"artifacts[{idx}] {{")
        lines.append(f'  path: "{art.path}";')
        lines.append(f'  kind: "{art.kind}";')
        if art.mime:
            lines.append(f'  mime: "{art.mime.type}";')
            if art.mime.schema_ref:
                lines.append(f'  schema_ref: "{art.mime.schema_ref}";')
        for k, v in sorted(art.values.items()):
            if isinstance(v, str):
                lines.append(f'  {k}: "{v}";')
            else:
                lines.append(f"  {k}: {v};")
        lines.extend(["}", ""])
    return lines


def _render_desktop_summary(probe: DesktopProbeIR) -> list[str]:
    lines = ["desktop {"]
    lines.append(f'  platform: "{esc_str(probe.platform)}";')
    lines.append(f'  session: "{esc_str(probe.session)}";')
    lines.append(f'  status: "{probe.status}";')
    if probe.compositor:
        lines.append(f'  compositor: "{esc_str(probe.compositor)}";')
    if probe.display_server:
        lines.append(f'  display_server: "{esc_str(probe.display_server)}";')
    if probe.probed_at:
        lines.append(f'  probed_at: "{esc_str(probe.probed_at)}";')
    if probe.tools_used:
        lines.append(f"  tools_used: {join_csv(probe.tools_used)};")
    if probe.canvas_width is not None:
        lines.append(f"  canvas_width: {probe.canvas_width};")
    if probe.canvas_height is not None:
        lines.append(f"  canvas_height: {probe.canvas_height};")
    lines.extend(["}", ""])
    return lines


def _render_desktop_pointer_block(pointer: DesktopPointerIR) -> list[str]:
    lines = ["desktop_pointer {"]
    lines.append(f"  x: {pointer.x};")
    lines.append(f"  y: {pointer.y};")
    if pointer.screen is not None:
        lines.append(f"  screen: {pointer.screen};")
    if pointer.window_id:
        lines.append(f'  window_id: "{esc_str(pointer.window_id)}";')
    if pointer.display_id:
        lines.append(f'  display_id: "{esc_str(pointer.display_id)}";')
    if pointer.display_output:
        lines.append(f'  display_output: "{esc_str(pointer.display_output)}";')
    if pointer.display_x is not None:
        lines.append(f"  display_x: {pointer.display_x};")
    if pointer.display_y is not None:
        lines.append(f"  display_y: {pointer.display_y};")
    lines.extend(["}", ""])
    return lines


def _render_desktop_display_block(idx: int, display: DesktopDisplayIR) -> list[str]:
    lines = [f"desktop_displays[{idx}] {{"]
    lines.append(f'  id: "{esc_str(display.id)}";')
    lines.append(f"  width: {display.width};")
    lines.append(f"  height: {display.height};")
    lines.append(f"  left: {display.left};")
    lines.append(f"  top: {display.top};")
    lines.append(f"  is_primary: {bool_lit(display.is_primary)};")
    if display.output:
        lines.append(f'  output: "{esc_str(display.output)}";')
    if display.index is not None:
        lines.append(f"  index: {display.index};")
    lines.extend(["}", ""])
    return lines


def _render_desktop_ide_calibration_block(
    idx: int,
    calibration: DesktopIdeCalibrationIR,
) -> list[str]:
    lines = [f"desktop_ide_calibrations[{idx}] {{"]
    lines.append(f'  ide: "{esc_str(calibration.ide)}";')
    lines.append(f"  chat_x: {calibration.chat_x};")
    lines.append(f"  chat_y: {calibration.chat_y};")
    if calibration.config_path:
        lines.append(f'  config_path: "{esc_str_full(calibration.config_path)}";')
    if calibration.source:
        lines.append(f'  source: "{esc_str(calibration.source)}";')
    if calibration.display_id:
        lines.append(f'  display_id: "{esc_str(calibration.display_id)}";')
    if calibration.display_output:
        lines.append(f'  display_output: "{esc_str(calibration.display_output)}";')
    if calibration.display_x is not None:
        lines.append(f"  display_x: {calibration.display_x};")
    if calibration.display_y is not None:
        lines.append(f"  display_y: {calibration.display_y};")
    if calibration.window_id is not None:
        lines.append(f"  window_id: {calibration.window_id};")
    if calibration.calibrated_at:
        lines.append(f'  calibrated_at: "{esc_str(calibration.calibrated_at)}";')
    lines.extend(["}", ""])
    return lines


def _render_desktop_window_block(idx: int, window: DesktopWindowIR) -> list[str]:
    lines = [f"desktop_windows[{idx}] {{"]
    lines.append(f'  id: "{esc_str(window.id)}";')
    lines.append(f'  title: "{esc_str_full(window.title)}";')
    lines.append(f"  x: {window.x};")
    lines.append(f"  y: {window.y};")
    lines.append(f"  width: {window.width};")
    lines.append(f"  height: {window.height};")
    lines.append(f"  workspace: {window.workspace};")
    lines.append(f"  is_browser: {bool_lit(window.is_browser)};")
    lines.append(f"  active: {bool_lit(window.active)};")
    lines.extend(["}", ""])
    return lines


def render_desktop_block(ir: SystemMapIR) -> list[str]:
    if ir.desktop is None:
        return []
    probe = ir.desktop
    lines: list[str] = []
    lines.extend(_render_desktop_summary(probe))
    if probe.pointer is not None:
        lines.extend(_render_desktop_pointer_block(probe.pointer))
    for idx, display in enumerate(probe.displays):
        lines.extend(_render_desktop_display_block(idx, display))
    for idx, calibration in enumerate(probe.ide_calibrations):
        lines.extend(_render_desktop_ide_calibration_block(idx, calibration))
    for idx, window in enumerate(probe.windows):
        lines.extend(_render_desktop_window_block(idx, window))
    return lines


def render_runtimes_block(ir: SystemMapIR) -> list[str]:
    lines: list[str] = []
    for idx, rt in enumerate(ir.runtimes):
        lines.append(f"runtimes[{idx}] {{")
        lines.append(f'  id: "{rt.id}";')
        lines.append(f'  kind: "{rt.kind}";')
        if rt.url:
            lines.append(f'  url: "{rt.url}";')
        if rt.uri:
            lines.append(f'  uri: "{rt.uri}";')
        if rt.health:
            lines.append(f'  health: "{rt.health}";')
        if rt.docker_profile:
            lines.append(f'  docker_profile: "{rt.docker_profile}";')
        if rt.model:
            lines.append(f'  model: "{rt.model}";')
        if rt.roles:
            lines.append(f'  roles: "{join_csv(rt.roles)}";')
        lines.append(f'  status: "{rt.status}";')
        lines.extend(["}", ""])
    return lines


def render_commands_block(ir: SystemMapIR) -> list[str]:
    lines: list[str] = []
    for idx, cmd in enumerate(ir.commands):
        lines.append(f"commands[{idx}] {{")
        lines.append(f'  name: "{cmd.name}";')
        if cmd.description:
            lines.append(f'  description: "{esc_str(cmd.description)}";')
        if cmd.required_names:
            lines.append(f'  required: "{join_csv(cmd.required_names)}";')
        if cmd.optional_names:
            lines.append(f'  optional: "{join_csv(cmd.optional_names)}";')
        if cmd.input_model:
            lines.append(f'  input_model: "{cmd.input_model}";')
        if cmd.runtime:
            lines.append(f'  runtime: "{cmd.runtime}";')
        proto = cmd.protocol
        if proto.transport:
            lines.append(f'  transport: "{proto.transport}";')
        if proto.endpoint:
            lines.append(f'  endpoint: "{proto.endpoint}";')
        lines.append(f'  protocol: "{proto.name}";')
        lines.extend(["}", ""])
    return lines


def render_resources_block(ir: SystemMapIR) -> list[str]:
    lines: list[str] = []
    for idx, res in enumerate(ir.resources):
        lines.append(f"resources[{idx}] {{")
        lines.append(f'  id: "{res.id}";')
        if res.title:
            lines.append(f'  title: "{esc_str(res.title)}";')
        if res.connector:
            lines.append(f'  connector: "{res.connector}";')
        if res.uri_patterns:
            lines.append(f'  uri_patterns: "{join_csv(res.uri_patterns)}";')
        lines.extend(["}", ""])
    return lines


def render_access_block(ir: SystemMapIR) -> list[str]:
    lines: list[str] = []
    for idx, grant in enumerate(ir.access):
        lines.append(f"access[{idx}] {{")
        lines.append(f'  agent: "{grant.agent}";')
        if grant.resource_area:
            lines.append(f'  resource_area: "{grant.resource_area}";')
        if grant.actions:
            lines.append(f'  actions: "{join_csv(grant.actions)}";')
        lines.append(f'  effect: "{grant.effect}";')
        lines.extend(["}", ""])
    return lines


def render_capabilities_block(ir: SystemMapIR) -> list[str]:
    if not ir.capabilities:
        return []
    return [
        "capabilities {",
        f'  actions: "{join_csv(ir.capabilities)}";',
        "}",
        "",
    ]


def render_workflow_history_block(ir: SystemMapIR) -> list[str]:
    if not ir.workflow_history:
        return []
    lines = ["workflow_history {"]
    for key in sorted(ir.workflow_history):
        lines.append(history_value_line(key, ir.workflow_history[key]))
    lines.extend(["}", ""])
    return lines


def render_conversation_block(ir: SystemMapIR) -> list[str]:
    conv = ir.conversation
    lines = [
        "conversation {",
        f"  autofill: {bool_lit(conv.autofill)};",
        f"  sync_auto_execute: {bool_lit(conv.sync_auto_execute)};",
    ]
    if conv.attachment_required:
        lines.append("  attachment_required: true;")
    lines.append(
        f"  generate_invoice_if_missing: {bool_lit(conv.generate_invoice_if_missing)};"
    )
    if conv.strict_pdf:
        lines.append("  strict_pdf: true;")
    lines.extend(["}", ""])
    return lines


def render_process_block(ir: SystemMapIR) -> list[str]:
    proc = ir.process
    lines = ["process {"]
    for key, val in (
        ("mode", proc.mode),
        ("nlp_parser", proc.nlp_parser),
        ("nlp_confidence_min", proc.nlp_confidence_min),
        ("nlp_enrich_missing", proc.nlp_enrich_missing),
        ("llm_reasoning", proc.llm_reasoning),
        ("autonomous", proc.autonomous_enabled),
        ("autonomous_max_rounds", proc.autonomous_max_rounds),
        ("ask_user", proc.ask_user),
        ("intract_gate", proc.intract_gate),
        ("intract_enforce_clarification", proc.intract_enforce_clarification),
    ):
        lines.append(process_field_line(key, val))
    if proc.llm_temperature is not None:
        lines.append(f"  llm_temperature: {proc.llm_temperature};")
    lines.extend(["}", ""])
    return lines


def render_process_access_block(ir: SystemMapIR) -> list[str]:
    acc = ir.process.access
    if not (acc.agent or acc.allow_resource_areas or acc.deny_resource_areas):
        return []
    lines = ["process_access {"]
    if acc.agent:
        lines.append(f'  agent: "{acc.agent}";')
    if acc.allow_resource_areas:
        lines.append(f'  allow_areas: "{join_csv(acc.allow_resource_areas)}";')
    if acc.deny_resource_areas:
        lines.append(f'  deny_areas: "{join_csv(acc.deny_resource_areas)}";')
    lines.extend(["}", ""])
    return lines


def render_paths_block(ir: SystemMapIR) -> list[str]:
    paths = ir.process.paths
    if not (paths.read or paths.write):
        return []
    lines = ["paths {"]
    if paths.read:
        lines.append(f'  read: "{join_csv(paths.read)}";')
    if paths.write:
        lines.append(f'  write: "{join_csv(paths.write)}";')
    lines.extend(["}", ""])
    return lines


def render_schedules_block(ir: SystemMapIR) -> list[str]:
    lines: list[str] = []
    for idx, sched in enumerate(ir.schedules):
        lines.append(f"schedules[{idx}] {{")
        lines.append(f'  id: "{sched.id}";')
        lines.append(f'  cron: "{sched.cron}";')
        lines.append(f'  task: "{esc_str_full(sched.task)}";')
        if sched.workflow_action:
            lines.append(f'  workflow_action: "{sched.workflow_action}";')
        lines.append(f"  enabled: {bool_lit(sched.enabled)};")
        lines.append(f'  timezone: "{sched.timezone}";')
        lines.extend(["}", ""])
    return lines


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


def _render_host_agent_block(idx: int, agent: HostAgentIR) -> list[str]:
    lines = [f"host_agent[{idx}] {{"]
    if agent.id:
        lines.append(f'  id: "{esc_str(agent.id)}";')
    if agent.agent_ref:
        lines.append(f'  agent_ref: "{esc_str(agent.agent_ref)}";')
    lines.append(f"  ok: {bool_lit(agent.ok)};")
    if agent.service_status:
        lines.append(f'  service_status: "{esc_str(agent.service_status)}";')
    if agent.runtime_status:
        lines.append(f'  runtime_status: "{esc_str(agent.runtime_status)}";')
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


def render_deploy_block(ir: SystemMapIR) -> list[str]:
    if not ir.deploy:
        return []
    dep = ir.deploy
    lines = [
        "deploy {",
        f'  target: "{dep.target}";',
        f'  platform_compose: "{dep.platform_compose}";',
        f'  mocks_compose: "{dep.mocks_compose}";',
        f'  stack_compose: "{dep.stack_compose}";',
    ]
    if dep.docker_profiles:
        lines.append(f'  docker_profiles: "{join_csv(dep.docker_profiles)}";')
    lines.extend(
        [
            f'  cron_service: "{dep.cron_service}";',
            f'  cron_image: "{dep.cron_image}";',
            "}",
            "",
        ]
    )
    return lines


def render_generated_services_block(ir: SystemMapIR) -> list[str]:
    lines: list[str] = []
    for idx, svc in enumerate(ir.generated_services):
        lines.append(f"generated_services[{idx}] {{")
        lines.append(f'  name: "{svc.name}";')
        if svc.description:
            lines.append(f'  description: "{esc_str(svc.description)}";')
        if svc.image:
            lines.append(f'  image: "{svc.image}";')
        if svc.build_context:
            lines.append(f'  build_context: "{svc.build_context}";')
        if svc.roles:
            lines.append(f'  roles: "{join_csv(svc.roles)}";')
        lines.extend(["}", ""])
    return lines


def render_validations_block(ir: SystemMapIR) -> list[str]:
    lines: list[str] = []
    for idx, spec in enumerate(ir.validations):
        lines.append(f"validations[{idx}] {{")
        lines.append(f'  code: "{spec.code}";')
        if spec.action:
            lines.append(f'  action: "{spec.action}";')
        if spec.status:
            lines.append(f'  status: "{spec.status}";')
        if spec.path:
            lines.append(f'  path: "{esc_str(spec.path)}";')
        lines.extend(["}", ""])
    return lines
