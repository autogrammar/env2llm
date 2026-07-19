"""stdlib HTTP REST server for env2llm live registry."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from env2llm import __version__
from env2llm.adapters.rest import RestAdapter
from env2llm.service import attach_mqtt_refresh_listener, build_registry_service
from env2llm.transport.mqtt import mqtt_enabled


class Env2LLMRequestHandler(BaseHTTPRequestHandler):
    adapter: RestAdapter

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return b""
        return self.rfile.read(length)

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self, method: str) -> None:
        status, payload = self.adapter.handle_http(
            method,
            self.path,
            body=self._read_body() if method == "POST" else b"",
        )
        self._send(status, payload)

    def do_GET(self) -> None:  # noqa: N802
        self._handle("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._handle("POST")


def run_server(
    *,
    host: str = "127.0.0.1",
    port: int = 8770,
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
    adapter = RestAdapter(service)
    handler_cls = type(
        "BoundEnv2LLMRequestHandler",
        (Env2LLMRequestHandler,),
        {"adapter": adapter},
    )
    server = ThreadingHTTPServer((host, port), handler_cls)
    mqtt_on = service.mqtt is not None
    print(
        f"env2llm REST listening on http://{host}:{port} "
        f"(v{__version__}, project={service.project_id}, mqtt={mqtt_on})",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if service.mqtt is not None:
            service.mqtt.disconnect()
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="env2llm-serve")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--project", default=".", help="project directory")
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--probe-desktop", action="store_true")
    parser.add_argument(
        "--mqtt",
        action="store_true",
        help="enable MQTT publish on refresh (or ENV2LLM_MQTT_ENABLED=1)",
    )
    args = parser.parse_args(argv)
    return run_server(
        host=args.host,
        port=args.port,
        project_dir=args.project,
        project_id=args.project_id,
        probe_desktop=True if args.probe_desktop else None,
        mqtt=True if args.mqtt else mqtt_enabled(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
