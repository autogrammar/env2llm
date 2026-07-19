"""Standalone MQTT bridge — subscribe refresh, publish live registry."""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from typing import Any

from env2llm.service import attach_mqtt_refresh_listener, build_registry_service
from env2llm.transport.mqtt import mqtt_available, mqtt_enabled, mqtt_missing_message


def run_bridge(
    *,
    project_dir: str = ".",
    project_id: str | None = None,
    probe_desktop: bool | None = None,
    publish_initial: bool = True,
) -> int:
    if not mqtt_available():
        print(mqtt_missing_message(), file=sys.stderr)
        return 1

    service = build_registry_service(
        project_dir,
        project_id=project_id,
        probe_desktop=probe_desktop,
        mqtt=True,
    )
    if service.mqtt is None:
        print("MQTT bridge failed to start", file=sys.stderr)
        return 1

    attach_mqtt_refresh_listener(service)

    if publish_initial:
        service.refresh(publish_mqtt=True)

    stop = False

    def _shutdown(_signum: int, _frame: Any) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    print(
        f"env2llm MQTT bridge: project={service.project_id} "
        f"prefix={service.mqtt.prefix} host={service.mqtt.host}:{service.mqtt.port}",
        flush=True,
    )
    print(
        f"  publish: {service.mqtt.topic(service.project_id, 'registry')}",
        flush=True,
    )
    print(
        f"  refresh: {service.mqtt.topic(service.project_id, 'registry', 'refresh')}",
        flush=True,
    )

    while not stop:
        time.sleep(0.5)

    service.mqtt.disconnect()
    return 0


def publish_once(
    *,
    project_dir: str,
    project_id: str | None = None,
    probe_desktop: bool | None = None,
    topic_project_id: str | None = None,
) -> int:
    """Refresh registry and publish a single MQTT snapshot (CLI helper)."""
    if not mqtt_available():
        print(mqtt_missing_message(), file=sys.stderr)
        return 1

    service = build_registry_service(
        project_dir,
        project_id=project_id,
        probe_desktop=probe_desktop,
        mqtt=True,
    )
    if service.mqtt is None:
        return 1

    ir = service.refresh(publish_mqtt=True)
    payload = {
        "ok": True,
        "project_id": topic_project_id or service.project_id,
        "example_id": ir.example_id,
        "topic": service.mqtt.topic(service.project_id, "registry"),
    }
    print(json.dumps(payload, indent=2))
    service.mqtt.disconnect()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="env2llm-mqtt",
        description="MQTT bridge for live env2llm registry snapshots",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_bridge = sub.add_parser("bridge", help="listen for refresh commands and republish")
    p_bridge.add_argument("--project", default=".")
    p_bridge.add_argument("--project-id", default=None)
    p_bridge.add_argument("--probe-desktop", action="store_true")
    p_bridge.add_argument("--no-initial-publish", action="store_true")

    p_pub = sub.add_parser("publish", help="refresh once and publish retained snapshot")
    p_pub.add_argument("--project", default=".")
    p_pub.add_argument("--project-id", default=None)
    p_pub.add_argument("--probe-desktop", action="store_true")

    args = parser.parse_args(argv)
    probe = True if getattr(args, "probe_desktop", False) else None

    if args.command == "bridge":
        if not mqtt_enabled(explicit=True):
            print("Set ENV2LLM_MQTT_ENABLED=1 or use env2llm-serve --mqtt", file=sys.stderr)
        return run_bridge(
            project_dir=args.project,
            project_id=args.project_id,
            probe_desktop=probe,
            publish_initial=not args.no_initial_publish,
        )

    return publish_once(
        project_dir=args.project,
        project_id=args.project_id,
        probe_desktop=probe,
    )


if __name__ == "__main__":
    raise SystemExit(main())
