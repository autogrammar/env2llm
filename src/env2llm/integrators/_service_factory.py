"""Shared wiring for REST, MCP, and MQTT integrators."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from env2llm.service.registry_service import RegistryService
from env2llm.transport.mqtt import MqttRegistryBridge, mqtt_available, mqtt_enabled


def build_registry_service(
    project_dir: str | Path,
    *,
    project_id: str | None = None,
    probe_desktop: bool | None = None,
    merge_existing: bool = True,
    mqtt: bool | None = None,
) -> RegistryService:
    bridge: MqttRegistryBridge | None = None
    if mqtt_enabled(explicit=mqtt) and mqtt_available():
        bridge = MqttRegistryBridge()
        bridge.connect()
    return RegistryService(
        project_dir=Path(project_dir),
        project_id=project_id or "",
        merge_existing=merge_existing,
        probe_desktop=probe_desktop,
        mqtt=bridge,
    )


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
