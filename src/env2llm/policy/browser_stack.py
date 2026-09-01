"""Merge nlp2oql / nlp2cmd / curllm automation catalog into SystemMapIR."""

from __future__ import annotations

from typing import Any

from env2llm.ir import CommandSchemaIR, FieldSpec, ProtocolSpec, RuntimeSpecIR, SystemMapIR
from env2llm.runtimes import resolve_command_runtime

_NLP2OQL_RUNTIME = RuntimeSpecIR(
    id="probe:nlp2oql",
    kind="external",
    uri="nlp2oql://router",
    roles=["nl_planning", "browser_router", "testql_codegen"],
    status="unknown",
)

_NLP2CMD_RUNTIME = RuntimeSpecIR(
    id="probe:nlp2cmd",
    kind="external",
    uri="nlp2cmd://run",
    roles=["browser_automation", "playwright", "credentials", "multi_step"],
    status="unknown",
)

_CURLLM_RUNTIME = RuntimeSpecIR(
    id="probe:curllm",
    kind="external",
    uri="curllm://execute",
    roles=["llm_browser", "form_fill", "captcha_solver", "extraction"],
    status="unknown",
)

_BROWSER_RUNTIME_NAMES = ("nlp2oql", "nlp2cmd", "curllm")


def _command_rows() -> list[dict]:
    try:
        from nlp2oql.backends.catalog import collect_backend_catalog

        return collect_backend_catalog().get("commands") or []
    except ImportError:
        return [
            {
                "name": "nlp2oql_run",
                "description": "Route NL to testql/nlp2cmd/curllm",
                "required": ["prompt"],
                "optional": ["backend", "execute"],
                "runtime": "nlp2oql",
            },
            {
                "name": "curllm_fill_form",
                "description": "LLM form fill + optional captcha",
                "required": ["url", "instruction"],
                "optional": ["captcha_solver"],
                "runtime": "curllm",
            },
        ]


def _runtime_for_name(runtime_name: str, available: list[str]) -> RuntimeSpecIR | None:
    mapping = {
        "nlp2oql": _NLP2OQL_RUNTIME,
        "nlp2cmd": _NLP2CMD_RUNTIME,
        "curllm": _CURLLM_RUNTIME,
    }
    spec = mapping.get(runtime_name)
    if spec is None:
        return None
    status = "available" if runtime_name in available else "unknown"
    return spec.model_copy(update={"status": status})


def _load_backend_catalog(*, enabled: bool | None) -> dict[str, Any] | None:
    try:
        from nlp2oql.backends.catalog import collect_backend_catalog

        return collect_backend_catalog()
    except ImportError:
        if enabled is not True:
            return None
        return {}


def _sync_browser_runtime(ir: SystemMapIR, spec: RuntimeSpecIR) -> None:
    existing = ir.runtime(spec.id)
    if existing is None:
        ir.runtimes.append(spec)
        return
    existing.status = spec.status  # type: ignore[assignment]


def _sync_browser_runtimes(ir: SystemMapIR, available: list[str]) -> None:
    for runtime_name in _BROWSER_RUNTIME_NAMES:
        spec = _runtime_for_name(runtime_name, available)
        if spec is not None:
            _sync_browser_runtime(ir, spec)


def _command_fields(item: dict[str, Any]) -> list[FieldSpec]:
    fields = [FieldSpec(name=field, required=True) for field in item.get("required") or []]
    fields.extend(FieldSpec(name=field, required=False) for field in item.get("optional") or [])
    return fields


def _catalog_command(item: dict[str, Any]) -> CommandSchemaIR | None:
    name = str(item.get("name") or "")
    if not name:
        return None
    runtime_name = str(item.get("runtime") or "nlp2oql")
    return CommandSchemaIR(
        name=name,
        description=str(item.get("description") or ""),
        runtime=f"probe:{runtime_name}",
        protocol=ProtocolSpec(name=runtime_name, transport="dsl", endpoint=f"{runtime_name}://run"),
        fields=_command_fields(item),
    )


def _merge_catalog_commands(ir: SystemMapIR) -> list[str]:
    existing_cmds = {cmd.name for cmd in ir.commands}
    added: list[str] = []
    for item in _command_rows():
        command = _catalog_command(item)
        if command is None or command.name in existing_cmds:
            continue
        ir.commands.append(command)
        existing_cmds.add(command.name)
        added.append(command.name)
    return added


def _record_browser_stack_metadata(ir: SystemMapIR, *, available: list[str], added: list[str]) -> None:
    if not added:
        return
    ir.metadata["browser_stack"] = {
        "runtimes": available,
        "command_count": len(added),
    }
    if "browser_automation" not in ir.capabilities:
        ir.capabilities.append("browser_automation")


def _resolve_browser_command_runtimes(ir: SystemMapIR) -> None:
    for cmd in ir.commands:
        if cmd.name.startswith(("nlp2oql_", "nlp2cmd_", "curllm_")) and not cmd.runtime:
            cmd.runtime = resolve_command_runtime(cmd.name)


def apply_browser_stack_probe(
    ir: SystemMapIR,
    *,
    enabled: bool | None = None,
) -> SystemMapIR:
    if enabled is False:
        return ir

    catalog = _load_backend_catalog(enabled=enabled)
    if catalog is None:
        return ir

    available = catalog.get("runtimes") or []
    _sync_browser_runtimes(ir, available)
    added = _merge_catalog_commands(ir)
    _record_browser_stack_metadata(ir, available=available, added=added)
    _resolve_browser_command_runtimes(ir)

    return ir
