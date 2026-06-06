"""Tests for REST and MCP integrators."""

from __future__ import annotations

import json
import threading
from http.client import HTTPConnection

from env2llm.adapters.mcp import McpAdapter
from env2llm.adapters.rest import RestAdapter
from env2llm.ir import CommandSchemaIR, RuntimeSpecIR, SystemMapIR
from env2llm.service.registry_service import RegistryService


def _fake_service(tmp_path) -> RegistryService:
    ir = SystemMapIR(
        example_id="demo",
        commands=[CommandSchemaIR(name="ping", runtime="executor:worker")],
        runtimes=[RuntimeSpecIR(id="executor:worker", kind="worker", status="available")],
    )
    service = RegistryService(tmp_path, project_id="demo")

    def _load() -> SystemMapIR:
        service._cached_ir = ir
        return ir

    service.load = _load  # type: ignore[method-assign]
    service.get_ir = lambda refresh=False: _load()  # type: ignore[method-assign]
    return service


def test_rest_adapter_routes(tmp_path) -> None:
    adapter = RestAdapter(_fake_service(tmp_path))
    status, payload = adapter.dispatch("health")
    assert status == 200
    assert payload["ok"] is True

    status, payload = adapter.dispatch("registry_get", query="format=json")
    assert status == 200
    assert payload["registry"]["example_id"] == "demo"

    status, payload = adapter.dispatch("registry_commands")
    assert status == 200
    assert payload["commands"][0]["name"] == "ping"


def test_mcp_adapter_tools(tmp_path) -> None:
    adapter = McpAdapter(_fake_service(tmp_path))
    result = adapter.call_tool("env2llm_get_registry", {})
    assert "content" in result
    text = result["content"][0]["text"]
    assert '"example_id": "demo"' in text

    result = adapter.call_tool("env2llm_list_commands", {})
    assert "ping" in result["content"][0]["text"]


def test_rest_server_health(tmp_path) -> None:
    service = _fake_service(tmp_path)
    adapter = RestAdapter(service)
    handler_ready = threading.Event()
    port_holder: list[int] = []

    def _serve() -> None:
        from env2llm.integrators.rest_server import Env2LLMRequestHandler, ThreadingHTTPServer

        handler_cls = type(
            "TestHandler",
            (Env2LLMRequestHandler,),
            {"adapter": adapter},
        )
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        port_holder.append(server.server_address[1])
        handler_ready.set()
        server.handle_request()
        server.server_close()

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    assert handler_ready.wait(timeout=2.0)

    conn = HTTPConnection("127.0.0.1", port_holder[0], timeout=2.0)
    conn.request("GET", "/health")
    response = conn.getresponse()
    body = json.loads(response.read().decode("utf-8"))
    conn.close()
    thread.join(timeout=2.0)

    assert response.status == 200
    assert body["service"] == "env2llm"
