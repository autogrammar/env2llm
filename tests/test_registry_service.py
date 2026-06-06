"""Tests for RegistryService."""

from __future__ import annotations

from env2llm.ir import CommandSchemaIR, DesktopProbeIR, DesktopWindowIR, RuntimeSpecIR, SystemMapIR
from env2llm.service.registry_service import RegistryService


def test_registry_service_render_and_desktop(monkeypatch, tmp_path) -> None:
    probe = DesktopProbeIR(
        platform="linux",
        session="GNOME",
        windows=[DesktopWindowIR(title="Terminal", id="0x1", active=True)],
        status="available",
    )
    ir = SystemMapIR(
        example_id="demo",
        commands=[CommandSchemaIR(name="send_email", runtime="executor:worker")],
        runtimes=[RuntimeSpecIR(id="executor:worker", kind="worker", status="available")],
        desktop=probe,
    )

    monkeypatch.setattr(
        "env2llm.service.registry_service.ensure_environment_map",
        lambda *_a, **_k: tmp_path / "environment.doql.less",
    )
    monkeypatch.setattr(
        "env2llm.service.registry_service.doql_file_to_system_map",
        lambda _p: ir,
    )
    monkeypatch.setattr(
        RegistryService,
        "registry_path",
        lambda self: None,
    )
    monkeypatch.setattr(
        RegistryService,
        "_generate_ir",
        lambda self, write=False: ir,
    )

    service = RegistryService(tmp_path, project_id="demo")
    loaded = service.load()
    assert loaded.example_id == "demo"

    text = service.render("json")
    assert '"example_id": "demo"' in text

    desktop = service.desktop_payload()
    assert desktop is not None
    assert desktop["windows"][0]["title"] == "Terminal"

    commands = service.commands_payload()
    assert commands[0]["name"] == "send_email"

    uris = service.uris_payload()
    assert uris.get("ok") is False or "entries" in uris


def test_registry_service_refresh_publishes_mqtt(monkeypatch, tmp_path) -> None:
    ir = SystemMapIR(example_id="demo")
    published: list[str] = []

    class FakeMqtt:
        prefix = "env2llm"
        host = "127.0.0.1"
        port = 1883
        connected = True

        def publish_registry(self, project_id: str, payload: dict) -> None:
            published.append(f"registry:{project_id}")

        def publish_desktop(self, project_id: str, payload: dict) -> None:
            published.append(f"desktop:{project_id}")

        def publish_event(self, project_id: str, event: str, meta: dict) -> None:
            published.append(f"event:{event}")

    monkeypatch.setattr(
        "env2llm.service.registry_service.ensure_environment_map",
        lambda *_a, **_k: tmp_path / "environment.doql.less",
    )
    monkeypatch.setattr(
        "env2llm.service.registry_service.doql_file_to_system_map",
        lambda _p: ir,
    )

    service = RegistryService(tmp_path, project_id="demo", mqtt=FakeMqtt())
    service.refresh()
    assert "registry:demo" in published
    assert any(item.startswith("event:") for item in published)
