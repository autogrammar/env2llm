"""Stdio MCP server for env2llm live registry."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from typing import Any

from env2llm import __version__
from env2llm.adapters.mcp import MCP_TOOLS, McpAdapter
from env2llm.service import attach_mqtt_refresh_listener, build_registry_service
from env2llm.transport.mqtt import mqtt_enabled

_PROTOCOL_VERSION = "2024-11-05"
_SERVER_NAME = "env2llm"
_NOTIFICATIONS = frozenset({"notifications/initialized", "notifications/cancelled"})


def _jsonrpc_response(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _jsonrpc_error(req_id: Any, code: int, message: str, data: Any = None) -> dict[str, Any]:
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": err}


def _write_json(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":"), default=str) + "\n")
    sys.stdout.flush()


def _log(message: str) -> None:
    print(message, file=sys.stderr)


def handle_message(msg: dict[str, Any], *, adapter: McpAdapter) -> dict[str, Any] | None:
    req_id = msg.get("id")
    method = msg.get("method", "")

    if method in _NOTIFICATIONS:
        return None

    if method == "initialize":
        return _jsonrpc_response(
            req_id,
            {
                "protocolVersion": _PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": _SERVER_NAME, "version": __version__},
            },
        )
    if method == "tools/list":
        return _jsonrpc_response(req_id, {"tools": MCP_TOOLS})
    if method == "tools/call":
        params = msg.get("params") or {}
        tool_name = str(params.get("name") or "")
        arguments = params.get("arguments") or {}
        try:
            result = adapter.call_tool(tool_name, arguments)
            return _jsonrpc_response(req_id, result)
        except Exception as exc:
            return _jsonrpc_response(
                req_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error in {tool_name}: {exc}\n{traceback.format_exc()}",
                        }
                    ],
                    "isError": True,
                },
            )

    return _jsonrpc_error(req_id, -32601, f"Method not found: {method}")


def run_stdio(
    *,
    project_dir: str = ".",
    project_id: str | None = None,
    probe_desktop: bool | None = None,
    mqtt: bool | None = None,
) -> int:
    service = build_registry_service(
        project_dir,
        project_id=project_id,
        probe_desktop=probe_desktop,
        mqtt=mqtt,
    )
    attach_mqtt_refresh_listener(service)
    adapter = McpAdapter(service)
    _log(
        f"env2llm mcp-server: started (stdio, project={service.project_id}, "
        f"mqtt={service.mqtt is not None})"
    )
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as exc:
            _write_json(_jsonrpc_error(None, -32700, f"Parse error: {exc}"))
            continue
        response = handle_message(msg, adapter=adapter)
        if response is not None:
            _write_json(response)
    if service.mqtt is not None:
        service.mqtt.disconnect()
    _log("env2llm mcp-server: stdin closed, exiting")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="env2llm-mcp")
    parser.add_argument("--project", default=".")
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--probe-desktop", action="store_true")
    parser.add_argument("--mqtt", action="store_true")
    args = parser.parse_args(argv)
    return run_stdio(
        project_dir=args.project,
        project_id=args.project_id,
        probe_desktop=True if args.probe_desktop else None,
        mqtt=True if args.mqtt else mqtt_enabled(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
