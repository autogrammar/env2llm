"""REST route handlers for env2llm registry adapter."""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs

from env2llm.service.registry_service import RegistryService


class _QueryParams:
    def __init__(self, query: str) -> None:
        self._params = parse_qs(query.lstrip("?"))

    def param(self, name: str, default: str = "") -> str:
        values = self._params.get(name)
        return values[0] if values else default

    def bool(self, name: str) -> bool:
        return self.param(name, "false").strip().lower() in ("1", "true", "yes")


def _route_health(service: RegistryService, params: _QueryParams, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    del params, body
    return 200, {
        "ok": True,
        "status": "ok",
        "service": "env2llm",
        "project_id": service.project_id,
    }


def _route_registry_get(service: RegistryService, params: _QueryParams, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    del body
    refresh = params.bool("refresh")
    fmt = params.param("format", "json").strip().lower()
    if fmt in ("json", ""):
        return 200, {"ok": True, "registry": service.to_dict(refresh=refresh)}
    text = service.render(fmt, refresh=refresh)
    return 200, {"ok": True, "format": fmt, "content": text}


def _route_registry_refresh(
    service: RegistryService,
    params: _QueryParams,
    body: dict[str, Any] | None,
) -> tuple[int, dict[str, Any]]:
    del params
    payload = body or {}
    ir = service.refresh(
        write=bool(payload.get("write", True)),
        publish_mqtt=bool(payload.get("publish_mqtt", True)),
        output_format=str(payload.get("format") or "doql.less"),
    )
    path = service.registry_path()
    return 200, {
        "ok": True,
        "example_id": ir.example_id,
        "path": str(path) if path else None,
        "command_count": len(ir.commands),
    }


def _route_registry_desktop(service: RegistryService, params: _QueryParams, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    del body
    desktop = service.desktop_payload(refresh=params.bool("refresh"))
    return 200, {"ok": True, "desktop": desktop}


def _route_registry_commands(service: RegistryService, params: _QueryParams, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    del body
    commands = service.commands_payload(refresh=params.bool("refresh"))
    return 200, {"ok": True, "commands": commands}


def _route_registry_uris(service: RegistryService, params: _QueryParams, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    del body
    return 200, service.uris_payload(refresh=params.bool("refresh"))


def _route_registry_mqtt(service: RegistryService, params: _QueryParams, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    del params, body
    return 200, {"ok": True, **service.mqtt_status()}


REST_ROUTE_HANDLERS: dict[str, Any] = {
    "health": _route_health,
    "registry_get": _route_registry_get,
    "registry_refresh": _route_registry_refresh,
    "registry_desktop": _route_registry_desktop,
    "registry_commands": _route_registry_commands,
    "registry_uris": _route_registry_uris,
    "registry_mqtt": _route_registry_mqtt,
}
