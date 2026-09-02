"""Process-related DOQL context block renderers."""

from __future__ import annotations

from env2llm.render.doql.helpers import join_csv
from .models import DoqlProcessPolicy, DoqlTaskContext


def process_has_non_default_overrides(proc: DoqlProcessPolicy) -> bool:
    return bool(
        proc.nlp_enrich_missing
        or proc.llm_temperature is not None
        or not proc.autonomous_enabled
        or proc.ask_user != "when_exhausted"
        or proc.intract_gate
        or proc.intract_enforce_clarification
        or proc.llm_reasoning != "shallow"
    )


def process_is_default_profile(proc: DoqlProcessPolicy) -> bool:
    return (
        proc.mode == "balanced"
        and proc.nlp_parser == "auto"
        and proc.autonomous_max_rounds == 8
    )


def should_omit_process_block(proc: DoqlProcessPolicy) -> bool:
    return process_is_default_profile(proc) and not process_has_non_default_overrides(proc)


def process_core_lines(proc: DoqlProcessPolicy) -> list[str]:
    lines = [
        f'  mode: "{proc.mode}";',
        f'  nlp_parser: "{proc.nlp_parser}";',
        f"  nlp_confidence_min: {proc.nlp_confidence_min};",
        f'  llm_reasoning: "{proc.llm_reasoning}";',
    ]
    if proc.nlp_enrich_missing:
        lines.append("  nlp_enrich_missing: true;")
    return lines


def process_override_lines(proc: DoqlProcessPolicy) -> list[str]:
    lines: list[str] = []
    if proc.llm_temperature is not None:
        lines.append(f"  llm_temperature: {proc.llm_temperature};")
    if not proc.autonomous_enabled:
        lines.append("  autonomous: false;")
    if proc.autonomous_max_rounds != 8:
        lines.append(f"  autonomous_max_rounds: {proc.autonomous_max_rounds};")
    if proc.ask_user != "when_exhausted":
        lines.append(f'  ask_user: "{proc.ask_user}";')
    if proc.intract_gate:
        lines.append("  intract_gate: true;")
    if proc.intract_enforce_clarification:
        lines.append("  intract_enforce_clarification: true;")
    return lines


def render_context_process(ctx: DoqlTaskContext) -> list[str]:
    proc = ctx.process
    if should_omit_process_block(proc):
        return []

    lines = ["", "process {"]
    lines.extend(process_core_lines(proc))
    lines.extend(process_override_lines(proc))
    lines.append("}")
    return lines


def render_context_process_access(ctx: DoqlTaskContext) -> list[str]:
    proc = ctx.process
    if not (proc.agent or proc.allow_resource_areas or proc.deny_resource_areas):
        return []
    lines = ["", "process_access {"]
    if proc.agent:
        lines.append(f'  agent: "{proc.agent}";')
    if proc.allow_resource_areas:
        lines.append(f'  allow_areas: "{join_csv(proc.allow_resource_areas)}";')
    if proc.deny_resource_areas:
        lines.append(f'  deny_areas: "{join_csv(proc.deny_resource_areas)}";')
    lines.append("}")
    return lines


def render_context_paths(ctx: DoqlTaskContext) -> list[str]:
    proc = ctx.process
    if not (proc.paths_read or proc.paths_write):
        return []
    lines = ["", "paths {"]
    if proc.paths_read:
        lines.append(f'  read: "{join_csv(proc.paths_read)}";')
    if proc.paths_write:
        lines.append(f'  write: "{join_csv(proc.paths_write)}";')
    lines.append("}")
    return lines
