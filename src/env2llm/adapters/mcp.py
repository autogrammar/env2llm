"""MCP adapter — env2llm live registry tools."""

from __future__ import annotations

import json
import traceback
from typing import Any

from env2llm.service.registry_service import RegistryService

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


class McpAdapter:
    def __init__(self, service: RegistryService) -> None:
        self.service = service

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            if tool_name == "env2llm_get_registry":
                payload = {
                    "ok": True,
                    "registry": self.service.to_dict(refresh=bool(arguments.get("refresh"))),
                }
            elif tool_name == "env2llm_render_registry":
                fmt = str(arguments.get("format") or "json")
                text = self.service.render(fmt, refresh=bool(arguments.get("refresh")))
                payload = {"ok": True, "format": fmt, "content": text}
            elif tool_name == "env2llm_refresh_registry":
                if "probe_desktop" in arguments:
                    self.service.probe_desktop = bool(arguments.get("probe_desktop"))
                ir = self.service.refresh(
                    publish_mqtt=bool(arguments.get("publish_mqtt", True)),
                    output_format=str(arguments.get("format") or "doql.less"),
                )
                path = self.service.registry_path()
                payload = {
                    "ok": True,
                    "example_id": ir.example_id,
                    "path": str(path) if path else None,
                    "command_count": len(ir.commands),
                }
            elif tool_name == "env2llm_get_desktop":
                payload = {
                    "ok": True,
                    "desktop": self.service.desktop_payload(refresh=bool(arguments.get("refresh"))),
                }
            elif tool_name == "env2llm_list_commands":
                payload = {
                    "ok": True,
                    "commands": self.service.commands_payload(refresh=bool(arguments.get("refresh"))),
                }
            elif tool_name == "env2llm_list_uris":
                payload = self.service.uris_payload(refresh=bool(arguments.get("refresh")))
            elif tool_name == "env2llm_mqtt_status":
                payload = {"ok": True, **self.service.mqtt_status()}
            else:
                return _mcp_error(f"unknown tool: {tool_name}")

            return {
                "content": [{"type": "text", "text": json.dumps(payload, indent=2, default=str)}],
            }
        except Exception as exc:
            return _mcp_error(f"Error in {tool_name}: {exc}\n{traceback.format_exc()}")


def _mcp_error(message: str) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }
