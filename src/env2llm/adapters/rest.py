"""REST adapter for live env2llm registry."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs, urlparse

from env2llm.service.registry_service import RegistryService


class RestAdapter:
    ROUTES: dict[str, str] = {
        "GET /health": "health",
        "GET /v1/registry": "registry_get",
        "POST /v1/registry/refresh": "registry_refresh",
        "GET /v1/registry/desktop": "registry_desktop",
        "GET /v1/registry/commands": "registry_commands",
        "GET /v1/registry/uris": "registry_uris",
        "GET /v1/registry/mqtt": "registry_mqtt",
    }

    def __init__(self, service: RegistryService) -> None:
        self.service = service

    @classmethod
    def match_route(cls, method: str, path: str) -> str | None:
        key = f"{method.upper()} {path.rstrip('/') or '/'}"
        if key in cls.ROUTES:
            return cls.ROUTES[key]
        if method.upper() == "GET" and path.rstrip("/") == "/v1/registry":
            return cls.ROUTES["GET /v1/registry"]
        return None

    def dispatch(self, route: str, *, query: str = "", body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        params = parse_qs(query.lstrip("?"))

        def _param(name: str, default: str = "") -> str:
            values = params.get(name)
            return values[0] if values else default

        def _bool(name: str) -> bool:
            return _param(name, "false").strip().lower() in ("1", "true", "yes")

        try:
            if route == "health":
                return 200, {
                    "ok": True,
                    "status": "ok",
                    "service": "env2llm",
                    "project_id": self.service.project_id,
                }

            if route == "registry_get":
                refresh = _bool("refresh")
                fmt = _param("format", "json").strip().lower()
                if fmt in ("json", ""):
                    return 200, {"ok": True, "registry": self.service.to_dict(refresh=refresh)}
                text = self.service.render(fmt, refresh=refresh)
                return 200, {"ok": True, "format": fmt, "content": text}

            if route == "registry_refresh":
                payload = body or {}
                ir = self.service.refresh(
                    write=bool(payload.get("write", True)),
                    publish_mqtt=bool(payload.get("publish_mqtt", True)),
                    output_format=str(payload.get("format") or "doql.less"),
                )
                path = self.service.registry_path()
                return 200, {
                    "ok": True,
                    "example_id": ir.example_id,
                    "path": str(path) if path else None,
                    "command_count": len(ir.commands),
                }

            if route == "registry_desktop":
                desktop = self.service.desktop_payload(refresh=_bool("refresh"))
                return 200, {"ok": True, "desktop": desktop}

            if route == "registry_commands":
                commands = self.service.commands_payload(refresh=_bool("refresh"))
                return 200, {"ok": True, "commands": commands}

            if route == "registry_uris":
                return 200, self.service.uris_payload(refresh=_bool("refresh"))

            if route == "registry_mqtt":
                return 200, {"ok": True, **self.service.mqtt_status()}

            return 404, {"ok": False, "error": f"unknown route: {route}"}
        except Exception as exc:  # pragma: no cover
            return 500, {"ok": False, "error": str(exc)}

    def handle_http(self, method: str, path: str, *, body: bytes = b"") -> tuple[int, dict[str, Any]]:
        route = self.match_route(method, urlparse(path).path)
        if route is None:
            return 404, {"ok": False, "error": "not found"}
        parsed = urlparse(path)
        payload: dict[str, Any] | None = None
        if body:
            try:
                payload = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                return 400, {"ok": False, "error": "invalid json"}
        return self.dispatch(route, query=parsed.query, body=payload)
