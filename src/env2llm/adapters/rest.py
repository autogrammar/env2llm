"""REST adapter for live env2llm registry."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

from env2llm.adapters.rest_routes import REST_ROUTE_HANDLERS, _QueryParams
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
        handler = REST_ROUTE_HANDLERS.get(route)
        if handler is None:
            return 404, {"ok": False, "error": f"unknown route: {route}"}
        try:
            return handler(self.service, _QueryParams(query), body)
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
