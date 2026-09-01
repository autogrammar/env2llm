"""MCP adapter — env2llm live registry tools."""

from __future__ import annotations

import json
import os
import traceback
from typing import Any

from env2llm.service.registry_service import RegistryService

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def _enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _require_permission(name: str, action: str) -> None:
    if not _enabled(name):
        raise PermissionError(f"{action} through MCP is disabled; set {name}=1 to enable it")


def _guard_tool(tool_name: str, arguments: dict[str, Any]) -> None:
    refresh_requested = tool_name == "env2llm_refresh_registry" or bool(
        arguments.get("refresh", False)
    )
    if refresh_requested:
        _require_permission("ENV2LLM_MCP_ALLOW_MUTATION", "registry refresh")

    desktop_requested = tool_name == "env2llm_get_desktop" or (
        tool_name == "env2llm_refresh_registry" and bool(arguments.get("probe_desktop"))
    )
    if desktop_requested:
        _require_permission("ENV2LLM_MCP_ALLOW_DESKTOP", "desktop metadata access")

MCP_TOOLS: list[dict[str, Any]] = [
    {
        "name": "env2llm_get_registry",
        "description": "Get live SystemMapIR registry (JSON) for the configured project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "default": False,
                    "description": "Regenerate registry before read",
                },
            },
        },
    },
    {
        "name": "env2llm_render_registry",
        "description": "Render registry as doql.less, yaml, json, or markdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "default": "json",
                    "description": "doql.less | yaml | json | markdown",
                },
                "refresh": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "env2llm_refresh_registry",
        "description": "Regenerate and persist environment.*; optional MQTT publish.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {"type": "string", "default": "doql.less"},
                "publish_mqtt": {"type": "boolean", "default": True},
                "probe_desktop": {"type": "boolean"},
            },
        },
    },
    {
        "name": "env2llm_get_desktop",
        "description": "Live desktop probe slice (windows, displays, session).",
        "inputSchema": {
            "type": "object",
            "properties": {"refresh": {"type": "boolean", "default": False}},
        },
    },
    {
        "name": "env2llm_list_commands",
        "description": "List command schemas from the registry.",
        "inputSchema": {
            "type": "object",
            "properties": {"refresh": {"type": "boolean", "default": False}},
        },
    },
    {
        "name": "env2llm_list_uris",
        "description": "nlp2uri URI index over registry (command://, desktop-window://, …).",
        "inputSchema": {
            "type": "object",
            "properties": {"refresh": {"type": "boolean", "default": False}},
        },
    },
    {
        "name": "env2llm_mqtt_status",
        "description": "MQTT bridge connection status for this registry service.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _mcp_error(message: str) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }


def _mcp_success(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(payload, indent=2, default=str)}],
    }


def _tool_get_registry(service: RegistryService, arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "registry": service.to_dict(refresh=bool(arguments.get("refresh"))),
    }


def _tool_render_registry(service: RegistryService, arguments: dict[str, Any]) -> dict[str, Any]:
    fmt = str(arguments.get("format") or "json")
    text = service.render(fmt, refresh=bool(arguments.get("refresh")))
    return {"ok": True, "format": fmt, "content": text}


def _tool_refresh_registry(service: RegistryService, arguments: dict[str, Any]) -> dict[str, Any]:
    if "probe_desktop" in arguments:
        service.probe_desktop = bool(arguments.get("probe_desktop"))
    ir = service.refresh(
        publish_mqtt=bool(arguments.get("publish_mqtt", True)),
        output_format=str(arguments.get("format") or "doql.less"),
    )
    path = service.registry_path()
    return {
        "ok": True,
        "example_id": ir.example_id,
        "path": str(path) if path else None,
        "command_count": len(ir.commands),
    }


def _tool_get_desktop(service: RegistryService, arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "desktop": service.desktop_payload(refresh=bool(arguments.get("refresh"))),
    }


def _tool_list_commands(service: RegistryService, arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "commands": service.commands_payload(refresh=bool(arguments.get("refresh"))),
    }


def _tool_list_uris(service: RegistryService, arguments: dict[str, Any]) -> dict[str, Any]:
    return service.uris_payload(refresh=bool(arguments.get("refresh")))


def _tool_mqtt_status(service: RegistryService, arguments: dict[str, Any]) -> dict[str, Any]:
    del arguments
    return {"ok": True, **service.mqtt_status()}


_MCP_TOOL_HANDLERS: dict[str, Any] = {
    "env2llm_get_registry": _tool_get_registry,
    "env2llm_render_registry": _tool_render_registry,
    "env2llm_refresh_registry": _tool_refresh_registry,
    "env2llm_get_desktop": _tool_get_desktop,
    "env2llm_list_commands": _tool_list_commands,
    "env2llm_list_uris": _tool_list_uris,
    "env2llm_mqtt_status": _tool_mqtt_status,
}


class McpAdapter:
    def __init__(self, service: RegistryService) -> None:
        self.service = service

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            _guard_tool(tool_name, arguments)
            handler = _MCP_TOOL_HANDLERS.get(tool_name)
            if handler is None:
                return _mcp_error(f"unknown tool: {tool_name}")
            return _mcp_success(handler(self.service, arguments))
        except Exception as exc:
            return _mcp_error(f"Error in {tool_name}: {exc}\n{traceback.format_exc()}")
