"""Tests for MQTT registry bridge."""

from __future__ import annotations

import json
import sys
import types

from env2llm.transport import mqtt as mqtt_module


class _FakeClient:
    def __init__(self, *args, **kwargs) -> None:
        self.published: list[tuple[str, str, int, bool]] = []
        self.subscriptions: list[tuple[str, int]] = []

    def username_pw_set(self, username: str, password: str | None) -> None:
        pass

    def connect(self, host: str, port: int, keepalive: int) -> None:
        pass

    def loop_start(self) -> None:
        pass

    def loop_stop(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> None:
        self.published.append((topic, payload, qos, retain))

    def subscribe(self, topic: str, qos: int = 0) -> None:
        self.subscriptions.append((topic, qos))


def _install_fake_paho(monkeypatch) -> None:
    fake = types.ModuleType("paho.mqtt.client")
    fake.Client = _FakeClient
    fake.CallbackAPIVersion = types.SimpleNamespace(VERSION2=2)
    fake_mqtt = types.ModuleType("paho.mqtt")
    fake_mqtt.client = fake
    fake_paho = types.ModuleType("paho")
    fake_paho.mqtt = fake_mqtt
    monkeypatch.setitem(sys.modules, "paho", fake_paho)
    monkeypatch.setitem(sys.modules, "paho.mqtt", fake_mqtt)
    monkeypatch.setitem(sys.modules, "paho.mqtt.client", fake)
    monkeypatch.setattr(mqtt_module, "_MQTT_AVAILABLE", True)
    monkeypatch.setattr(mqtt_module, "mqtt", fake)


def test_mqtt_publish_topics(monkeypatch) -> None:
    _install_fake_paho(monkeypatch)
    from env2llm.transport.mqtt import MqttRegistryBridge

    bridge = MqttRegistryBridge(prefix="env2llm")
    bridge._client = _FakeClient()
    bridge.connected = True

    bridge.publish_registry("demo", {"example_id": "demo"})
    bridge.publish_desktop("demo", {"windows": []})
    bridge.publish_event("demo", "registry.refreshed", {"command_count": 1})

    topics = [item[0] for item in bridge._client.published]
    assert "env2llm/demo/registry" in topics
    assert "env2llm/demo/registry/desktop" in topics
    assert "env2llm/demo/events" in topics

    registry_payload = json.loads(next(body for topic, body, *_ in bridge._client.published if topic.endswith("/registry")))
    assert registry_payload["example_id"] == "demo"
