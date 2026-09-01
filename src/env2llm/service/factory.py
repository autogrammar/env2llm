"""Public, deterministic factory contract for env2llm services."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from env2llm.service.registry_service import RegistryService
from env2llm.transport.mqtt import MqttRegistryBridge, mqtt_available, mqtt_enabled

SERVICE_FACTORY_REQUEST_V1 = "env2llm.service-factory-request.v1"
SERVICE_DESCRIPTOR_V1 = "env2llm.service-descriptor.v1"
SERVICE_FACTORY_ERROR_V1 = "env2llm.service-factory-error.v1"

_SCHEMA_FILES = {
    SERVICE_FACTORY_REQUEST_V1: "service-factory-request-v1.schema.json",
    SERVICE_DESCRIPTOR_V1: "service-descriptor-v1.schema.json",
    SERVICE_FACTORY_ERROR_V1: "service-factory-error-v1.schema.json",
}
_REGISTRY_CAPABILITIES = (
    "commands",
    "desktop",
    "host",
    "mqtt",
    "registry",
    "render",
    "uris",
)
_REQUEST_FIELDS = {
    "schema",
    "kind",
    "project_dir",
    "project_id",
    "probe_desktop",
    "merge_existing",
    "mqtt",
    "request_hash",
}


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _payload_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _optional_bool(payload: Mapping[str, Any], key: str) -> bool | None:
    value = payload.get(key)
    if value is not None and not isinstance(value, bool):
        raise ServiceFactoryError(f"{key} must be a boolean or null")
    return value


def service_contract_schema(schema_id: str) -> dict[str, Any]:
    """Load a packaged JSON Schema by its public contract identifier."""
    try:
        filename = _SCHEMA_FILES[schema_id]
    except KeyError as exc:
        raise KeyError(f"unknown env2llm service contract {schema_id!r}") from exc
    path = resources.files("env2llm.data").joinpath(filename)
    return json.loads(path.read_text(encoding="utf-8"))


class ServiceFactoryError(ValueError):
    """Typed, serializable service-factory failure."""

    code = "service_factory_error"

    def __init__(self, message: str, *, kind: str | None = None) -> None:
        super().__init__(message)
        self.kind = kind

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SERVICE_FACTORY_ERROR_V1,
            "ok": False,
            "code": self.code,
            "kind": self.kind,
            "message": str(self),
        }


class UnknownServiceKindError(ServiceFactoryError):
    """Raised when a request names a service kind the factory cannot build."""

    code = "unknown_service_kind"

    def __init__(self, kind: str) -> None:
        super().__init__(
            f"unknown env2llm service kind {kind!r} (known: registry)",
            kind=kind,
        )


def _validate_factory_schema(schema: Any) -> None:
    if schema not in {None, SERVICE_FACTORY_REQUEST_V1}:
        raise ServiceFactoryError(
            f"unsupported service factory request schema {schema!r}",
            kind="registry",
        )


def _validated_project_dir(project_dir: Any) -> str | Path:
    if not isinstance(project_dir, (str, Path)) or not str(project_dir).strip():
        raise ServiceFactoryError("project_dir must be a non-empty path")
    return project_dir


def _validated_merge_existing(value: Any) -> bool:
    if not isinstance(value, bool):
        raise ServiceFactoryError("merge_existing must be a boolean")
    return value


def _request_from_payload(payload: Mapping[str, Any]) -> ServiceFactoryRequest:
    merge_existing = _validated_merge_existing(payload.get("merge_existing", True))
    request = ServiceFactoryRequest(
        project_dir=_validated_project_dir(payload.get("project_dir")),
        kind=str(payload.get("kind") or "registry"),
        project_id=(str(payload["project_id"]) if payload.get("project_id") else None),
        probe_desktop=_optional_bool(payload, "probe_desktop"),
        merge_existing=merge_existing,
        mqtt=_optional_bool(payload, "mqtt"),
    )
    supplied_hash = payload.get("request_hash")
    if supplied_hash is not None and supplied_hash != request.request_hash:
        raise ServiceFactoryError("service factory request_hash does not match payload")
    return request


@dataclass(frozen=True)
class ServiceFactoryRequest:
    """Versioned input for deterministic service construction."""

    project_dir: str | Path
    kind: str = "registry"
    project_id: str | None = None
    probe_desktop: bool | None = None
    merge_existing: bool = True
    mqtt: bool | None = None

    @property
    def schema(self) -> str:
        return SERVICE_FACTORY_REQUEST_V1

    @property
    def normalized_project_dir(self) -> str:
        return str(Path(self.project_dir).resolve())

    @property
    def resolved_project_id(self) -> str:
        return self.project_id or Path(self.normalized_project_dir).name

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "kind": self.kind,
            "project_dir": self.normalized_project_dir,
            "project_id": self.resolved_project_id,
            "probe_desktop": self.probe_desktop,
            "merge_existing": self.merge_existing,
            "mqtt": self.mqtt,
        }

    @property
    def request_hash(self) -> str:
        return _payload_hash(self.canonical_dict())

    def to_dict(self) -> dict[str, Any]:
        return {**self.canonical_dict(), "request_hash": self.request_hash}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ServiceFactoryRequest:
        unknown = sorted(set(payload) - _REQUEST_FIELDS)
        if unknown:
            raise ServiceFactoryError(f"unknown service factory request fields: {unknown}")
        _validate_factory_schema(payload.get("schema"))
        return _request_from_payload(payload)


@dataclass(frozen=True)
class ServiceDescriptor:
    """Serializable description of the service instance returned by the factory."""

    kind: str
    project_dir: str
    project_id: str
    capabilities: tuple[str, ...]
    mqtt_requested: bool | None
    mqtt_connected: bool
    request_hash: str

    @property
    def schema(self) -> str:
        return SERVICE_DESCRIPTOR_V1

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "kind": self.kind,
            "project_dir": self.project_dir,
            "project_id": self.project_id,
            "capabilities": list(self.capabilities),
            "mqtt_requested": self.mqtt_requested,
            "mqtt_connected": self.mqtt_connected,
            "request_hash": self.request_hash,
        }

    @property
    def descriptor_hash(self) -> str:
        return _payload_hash(self.canonical_dict())

    def to_dict(self) -> dict[str, Any]:
        return {**self.canonical_dict(), "descriptor_hash": self.descriptor_hash}


@dataclass(frozen=True)
class ServiceFactoryResult:
    """Runtime service paired with its serializable provenance descriptor."""

    service: RegistryService
    descriptor: ServiceDescriptor


class RegistryServiceFactory:
    """Build and cache RegistryService instances from typed requests."""

    def __init__(self) -> None:
        self._cache: dict[tuple[str, str, bool, bool | None], RegistryService] = {}

    def create(
        self,
        request: ServiceFactoryRequest | Mapping[str, Any],
    ) -> ServiceFactoryResult:
        if not isinstance(request, ServiceFactoryRequest):
            request = ServiceFactoryRequest.from_dict(request)
        if request.kind != "registry":
            raise UnknownServiceKindError(request.kind)

        key = (
            request.normalized_project_dir,
            request.resolved_project_id,
            request.merge_existing,
            request.mqtt,
        )
        service = self._cache.get(key)
        if service is None:
            service = _build_registry_service(request)
            self._cache[key] = service
        if request.probe_desktop is not None:
            service.probe_desktop = request.probe_desktop

        descriptor = ServiceDescriptor(
            kind="registry",
            project_dir=request.normalized_project_dir,
            project_id=service.project_id,
            capabilities=_REGISTRY_CAPABILITIES,
            mqtt_requested=request.mqtt,
            mqtt_connected=bool(service.mqtt and getattr(service.mqtt, "connected", False)),
            request_hash=request.request_hash,
        )
        return ServiceFactoryResult(service=service, descriptor=descriptor)

    def clear(self) -> None:
        seen: set[int] = set()
        for service in self._cache.values():
            if id(service) in seen:
                continue
            seen.add(id(service))
            disconnect = getattr(service.mqtt, "disconnect", None)
            if callable(disconnect):
                disconnect()
        self._cache.clear()


def _build_registry_service(request: ServiceFactoryRequest) -> RegistryService:
    bridge: MqttRegistryBridge | None = None
    if mqtt_enabled(explicit=request.mqtt) and mqtt_available():
        bridge = MqttRegistryBridge()
        bridge.connect()
    return RegistryService(
        project_dir=Path(request.normalized_project_dir),
        project_id=request.resolved_project_id,
        merge_existing=request.merge_existing,
        probe_desktop=request.probe_desktop,
        mqtt=bridge,
    )


def build_registry_service(
    project_dir: str | Path,
    *,
    project_id: str | None = None,
    probe_desktop: bool | None = None,
    merge_existing: bool = True,
    mqtt: bool | None = None,
) -> RegistryService:
    """Compatibility-friendly public constructor for one registry service."""
    request = ServiceFactoryRequest(
        project_dir=project_dir,
        project_id=project_id,
        probe_desktop=probe_desktop,
        merge_existing=merge_existing,
        mqtt=mqtt,
    )
    return RegistryServiceFactory().create(request).service


def attach_mqtt_refresh_listener(service: RegistryService) -> Any | None:
    """Subscribe to MQTT refresh commands for *service*'s project."""
    if service.mqtt is None:
        return None

    def _on_refresh(project_id: str, body: dict[str, Any]) -> None:
        if project_id != service.project_id:
            return
        if "probe_desktop" in body:
            service.probe_desktop = bool(body.get("probe_desktop"))
        service.refresh(
            publish_mqtt=True,
            output_format=str(body.get("format") or "doql.less"),
        )

    service.mqtt.subscribe_refresh(_on_refresh)
    return service.mqtt
