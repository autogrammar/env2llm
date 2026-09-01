"""Merge TestQL GUI/DOM automation catalog into SystemMapIR."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from env2llm.ir import (
    AccessGrantIR,
    CommandSchemaIR,
    FieldSpec,
    ProtocolSpec,
    ResourceSpecIR,
    RuntimeSpecIR,
    SystemMapIR,
)
from env2llm.probes.testql import collect_testql_catalog, testql_available
from env2llm.runtimes import resolve_command_runtime

_TESTQL_RUNTIME = RuntimeSpecIR(
    id="probe:testql",
    kind="external",
    uri="testql://session",
    roles=[
        "gui_dom",
        "playwright",
        "scenario_runner",
        "browser_inspect",
        "desktop_control",
        "native_os",
    ],
    status="unknown",
)

_TESTQL_RESOURCE = ResourceSpecIR(
    id="testql:scenarios",
    title="TestQL scenario files",
    connector="testql",
    uri_patterns=["testql://**", "file://**/*.testql.toon.yaml", "file://**/*.oql"],
)


def testql_probe_enabled(
    *,
    explicit: bool | None = None,
    project_dir: Path | str | None = None,
) -> bool:
    if explicit is not None:
        return explicit
    token = os.environ.get("ENV2LLM_TESTQL_PROBE", "").strip().lower()
    if token in ("0", "false", "no"):
        return False
    if token in ("1", "true", "yes"):
        return True
    if project_dir is not None and testql_available():
        catalog = collect_testql_catalog(project_dir)
        return catalog["scenario_count"] > 0
    return False


def _catalog_status(catalog: dict[str, Any], desktop_tools: list[Any]) -> str:
    if catalog.get("playwright") or desktop_tools:
        return "available"
    return "unknown"


def _ensure_testql_runtime(ir: SystemMapIR, status: str) -> None:
    existing_rt = ir.runtime("probe:testql")
    if existing_rt is not None:
        existing_rt.status = status  # type: ignore[assignment]
        return
    ir.runtimes.append(_TESTQL_RUNTIME.model_copy(update={"status": status}))


def _ensure_testql_resource(ir: SystemMapIR) -> None:
    if any(resource.id == _TESTQL_RESOURCE.id for resource in ir.resources):
        return
    ir.resources.append(_TESTQL_RESOURCE.model_copy(deep=True))


def _field_specs_from_item(item: dict[str, Any]) -> list[FieldSpec]:
    fields = [
        FieldSpec(name=field, required=True)
        for field in item.get("required") or []
    ]
    fields.extend(
        FieldSpec(name=field, required=False)
        for field in item.get("optional") or []
    )
    return fields


def _merge_gui_commands(ir: SystemMapIR, catalog: dict[str, Any]) -> list[str]:
    existing_cmds = {cmd.name for cmd in ir.commands}
    added: list[str] = []
    for item in catalog.get("gui_commands") or []:
        name = str(item.get("name") or "")
        if not name or name in existing_cmds:
            continue
        ir.commands.append(
            CommandSchemaIR(
                name=name,
                description=str(item.get("description") or ""),
                runtime="probe:testql",
                protocol=ProtocolSpec(name="testql", transport="dsl", endpoint="testql://run"),
                fields=_field_specs_from_item(item),
            )
        )
        existing_cmds.add(name)
        added.append(name)
    return added


def _ensure_testql_access_grant(ir: SystemMapIR, added: list[str]) -> None:
    if any(
        grant.agent == "testql-agent" and grant.resource_area == _TESTQL_RESOURCE.id
        for grant in ir.access
    ):
        return
    ir.access.append(
        AccessGrantIR(
            agent="testql-agent",
            resource_area=_TESTQL_RESOURCE.id,
            actions=added,
            effect="allow",
        )
    )


def _record_testql_catalog_data(
    ir: SystemMapIR,
    catalog: dict[str, Any],
    *,
    desktop_tools: list[Any],
) -> None:
    ir.data["testql.scenario_count"] = catalog.get("scenario_count", 0)
    ir.data["testql.playwright"] = catalog.get("playwright", False)
    if desktop_tools:
        ir.data["testql.desktop_tools"] = desktop_tools
        if "desktop_control" not in ir.capabilities:
            ir.capabilities.append("desktop_control")
    if catalog.get("scenarios"):
        ir.data["testql.scenario_paths"] = [
            item["path"] for item in catalog["scenarios"][:12]
        ]
    if "testql_automation" not in ir.capabilities:
        ir.capabilities.append("testql_automation")


def _testql_catalog_metadata(
    catalog: dict[str, Any],
    *,
    desktop_tools: list[Any],
    tool_count: int,
) -> dict[str, Any]:
    return {
        "runtime_id": "probe:testql",
        "tool_count": tool_count,
        "scenario_count": catalog.get("scenario_count", 0),
        "playwright": catalog.get("playwright", False),
        "desktop_tools": desktop_tools,
        "display_server": (catalog.get("desktop") or {}).get("display_server"),
    }


def _record_testql_probe(ir: SystemMapIR, catalog: dict[str, Any], added: list[str]) -> None:
    desktop_tools = (catalog.get("desktop") or {}).get("host_tools") or []
    _ensure_testql_access_grant(ir, added)
    ir.metadata["testql_catalog"] = _testql_catalog_metadata(
        catalog,
        desktop_tools=desktop_tools,
        tool_count=len(added),
    )
    _record_testql_catalog_data(ir, catalog, desktop_tools=desktop_tools)


def _resolve_testql_command_runtimes(ir: SystemMapIR) -> None:
    for cmd in ir.commands:
        if cmd.name.startswith("testql_") and not cmd.runtime:
            cmd.runtime = resolve_command_runtime(cmd.name)


def apply_testql_probe(
    ir: SystemMapIR,
    *,
    enabled: bool | None = None,
    project_dir: Path | str | None = None,
) -> SystemMapIR:
    """Attach TestQL DOM/GUI scenario catalog when testql is available."""
    root = Path(project_dir) if project_dir is not None else None
    if not testql_probe_enabled(explicit=enabled, project_dir=root):
        return ir
    if not testql_available():
        return ir

    catalog = collect_testql_catalog(root)
    desktop_tools = (catalog.get("desktop") or {}).get("host_tools") or []
    status = _catalog_status(catalog, desktop_tools)

    _ensure_testql_runtime(ir, status)
    _ensure_testql_resource(ir)

    added = _merge_gui_commands(ir, catalog)
    if added:
        _record_testql_probe(ir, catalog, added)

    _resolve_testql_command_runtimes(ir)
    return ir
