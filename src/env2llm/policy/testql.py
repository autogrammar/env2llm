"""Merge TestQL GUI/DOM automation catalog into SystemMapIR."""

from __future__ import annotations

import os
from pathlib import Path

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
    status = (
        "available"
        if catalog.get("playwright") or desktop_tools
        else "unknown"
    )

    existing_rt = ir.runtime("probe:testql")
    if existing_rt is not None:
        existing_rt.status = status  # type: ignore[assignment]
    else:
        ir.runtimes.append(_TESTQL_RUNTIME.model_copy(update={"status": status}))

    if not any(resource.id == _TESTQL_RESOURCE.id for resource in ir.resources):
        ir.resources.append(_TESTQL_RESOURCE.model_copy(deep=True))

    existing_cmds = {cmd.name for cmd in ir.commands}
    added: list[str] = []
    for item in catalog.get("gui_commands") or []:
        name = str(item.get("name") or "")
        if not name or name in existing_cmds:
            continue
        fields = [
            FieldSpec(name=field, required=True)
            for field in item.get("required") or []
        ]
        fields.extend(
            FieldSpec(name=field, required=False)
            for field in item.get("optional") or []
        )
        ir.commands.append(
            CommandSchemaIR(
                name=name,
                description=str(item.get("description") or ""),
                runtime="probe:testql",
                protocol=ProtocolSpec(name="testql", transport="dsl", endpoint="testql://run"),
                fields=fields,
            )
        )
        existing_cmds.add(name)
        added.append(name)

    if added:
        if not any(
            grant.agent == "testql-agent" and grant.resource_area == _TESTQL_RESOURCE.id
            for grant in ir.access
        ):
            ir.access.append(
                AccessGrantIR(
                    agent="testql-agent",
                    resource_area=_TESTQL_RESOURCE.id,
                    actions=added,
                    effect="allow",
                )
            )
        ir.metadata["testql_catalog"] = {
            "runtime_id": "probe:testql",
            "tool_count": len(added),
            "scenario_count": catalog.get("scenario_count", 0),
            "playwright": catalog.get("playwright", False),
            "desktop_tools": desktop_tools,
            "display_server": (catalog.get("desktop") or {}).get("display_server"),
        }
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

    for cmd in ir.commands:
        if cmd.name.startswith("testql_") and not cmd.runtime:
            cmd.runtime = resolve_command_runtime(cmd.name)

    return ir
