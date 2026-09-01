"""MQTT publish/subscribe for live env2llm registry snapshots."""

from __future__ import annotations

import json
import os
import threading
from typing import Any, Callable

_MQTT_IMPORT_ERROR: str | None = None

try:
    import paho.mqtt.client as mqtt
    from paho.mqtt.client import MQTTMessage

    _MQTT_AVAILABLE = True
except ImportError as exc:
    _MQTT_AVAILABLE = False
    _MQTT_IMPORT_ERROR = str(exc)
    mqtt = None  # type: ignore[assignment,misc]
    MQTTMessage = Any  # type: ignore[misc,assignment]


def mqtt_available() -> bool:
    return _MQTT_AVAILABLE


def mqtt_missing_message() -> str:
    if _MQTT_IMPORT_ERROR:
        return (
            f"paho-mqtt is not installed ({_MQTT_IMPORT_ERROR}). "
            "Install with: pip install 'env2llm[mqtt]'"
        )
    return "paho-mqtt is not installed. Install with: pip install 'env2llm[mqtt]'"


def mqtt_enabled(*, explicit: bool | None = None) -> bool:
    if explicit is not None:
        return explicit
    return os.environ.get("ENV2LLM_MQTT_ENABLED", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _mqtt_env_str(key: str, fallback: str) -> str:
    return os.environ.get(key, fallback)


def _mqtt_env_int(key: str, fallback: int) -> int:
    return int(os.environ.get(key, str(fallback)))


def _create_mqtt_client(
    *,
    client_id: str,
    username: str | None,
    password: str | None,
) -> Any:
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
    )
    if username:
        client.username_pw_set(username, password)
    return client


class MqttRegistryBridge:
    """
    Publish registry snapshots and listen for remote refresh commands.

    Topics (default prefix ``env2llm``):

    - ``{prefix}/{project_id}/registry`` — full SystemMapIR JSON (retained)
    - ``{prefix}/{project_id}/registry/desktop`` — desktop probe slice (retained)
    - ``{prefix}/{project_id}/events`` — refresh/metadata events
    - ``{prefix}/{project_id}/registry/refresh`` — POST refresh command (subscribe)
    """

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        prefix: str | None = None,
        client_id: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        if not _MQTT_AVAILABLE:
            raise RuntimeError(mqtt_missing_message())

        self.host = host or _mqtt_env_str("ENV2LLM_MQTT_HOST", "127.0.0.1")
        self.port = port if port is not None else _mqtt_env_int("ENV2LLM_MQTT_PORT", 1883)
        self.prefix = (prefix or _mqtt_env_str("ENV2LLM_MQTT_TOPIC_PREFIX", "env2llm")).strip("/")
        self.username = username or os.environ.get("ENV2LLM_MQTT_USERNAME") or None
        self.password = password or os.environ.get("ENV2LLM_MQTT_PASSWORD") or None
        self._client_id = client_id or _mqtt_env_str("ENV2LLM_MQTT_CLIENT_ID", "env2llm-registry")
        self._client = _create_mqtt_client(
            client_id=self._client_id,
            username=self.username,
            password=self.password,
        )
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self.connected = False
        self._refresh_handler: Callable[[str, dict[str, Any]], None] | None = None
        self._lock = threading.Lock()

    def topic(self, project_id: str, *parts: str) -> str:
        segments = [self.prefix, project_id, *parts]
        return "/".join(segment.strip("/") for segment in segments if segment)

    def connect(self) -> None:
        self._client.connect(self.host, self.port, keepalive=60)
        self._client.loop_start()

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
        self.connected = False

    def publish_registry(self, project_id: str, payload: dict[str, Any], *, retain: bool = True) -> None:
        topic = self.topic(project_id, "registry")
        self._publish(topic, json.dumps(payload, default=str), retain=retain)

    def publish_desktop(self, project_id: str, payload: dict[str, Any], *, retain: bool = True) -> None:
        topic = self.topic(project_id, "registry", "desktop")
        self._publish(topic, json.dumps(payload, default=str), retain=retain)

    def publish_event(self, project_id: str, event: str, meta: dict[str, Any]) -> None:
        topic = self.topic(project_id, "events")
        body = json.dumps({"event": event, **meta}, default=str)
        self._publish(topic, body, retain=False)

    def subscribe_refresh(self, handler: Callable[[str, dict[str, Any]], None]) -> None:
        """Handle messages on ``{prefix}/+/registry/refresh``."""
        self._refresh_handler = handler
        topic = f"{self.prefix}/+/registry/refresh"
        self._client.subscribe(topic, qos=1)

    def _publish(self, topic: str, payload: str, *, retain: bool) -> None:
        with self._lock:
            if not self.connected:
                self.connect()
            self._client.publish(topic, payload, qos=1, retain=retain)

    def _on_connect(self, client: Any, userdata: Any, flags: Any, reason_code: Any, properties: Any) -> None:
        self.connected = reason_code == 0
        topic = f"{self.prefix}/+/registry/refresh"
        if self._refresh_handler is not None:
            client.subscribe(topic, qos=1)

    def _on_message(self, client: Any, userdata: Any, msg: MQTTMessage) -> None:
        if self._refresh_handler is None:
            return
        parts = msg.topic.split("/")
        if len(parts) < 4 or parts[-2:] != ["registry", "refresh"]:
            return
        project_id = parts[-3] if len(parts) >= 4 else ""
        if not project_id:
            return
        body: dict[str, Any] = {}
        try:
            raw = msg.payload.decode("utf-8")
            if raw.strip():
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    body = parsed
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
        self._refresh_handler(project_id, body)
