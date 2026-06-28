"""Live environment registry — load, refresh, render, URI index."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from env2llm.bootstrap import ensure_environment_map, project_artifact_root
from env2llm.bridge import doql_file_to_system_map
from env2llm.formats import render_format
from env2llm.ir import SystemMapIR
from env2llm.layout import resolve_registry_path


@dataclass
class RegistryService:
    """In-memory view over env2llm ``SystemMapIR`` with optional MQTT fan-out."""

    project_dir: Path
    project_id: str = ""
    merge_existing: bool = True
    probe_desktop: bool | None = None
    probe_mcp: bool | None = None
    probe_testql: bool | None = None
    probe_host: bool | None = None
    mqtt: Any | None = field(default=None, repr=False)
    _cached_ir: SystemMapIR | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.project_dir = Path(self.project_dir).resolve()
        if not self.project_id:
            self.project_id = self.project_dir.name

    def registry_path(self) -> Path | None:
        path = resolve_registry_path(example_dir=self.project_dir)
        return path if path and path.is_file() else None

    def load(self) -> SystemMapIR:
        """Load registry from disk without regenerating."""
        path = self.registry_path()
        if path is not None:
            self._cached_ir = doql_file_to_system_map(path)
            return self._cached_ir
        self._cached_ir = self._generate_ir(write=False)
        return self._cached_ir

    def refresh(
        self,
        *,
        write: bool = True,
        publish_mqtt: bool = True,
        output_format: str = "doql.less",
    ) -> SystemMapIR:
        """Regenerate registry (probes, policies) and optionally persist + MQTT publish."""
        if write:
            ensure_environment_map(
                self.project_dir,
                project_id=self.project_id,
                output_format=output_format,
                merge_existing=self.merge_existing,
                probe_desktop=self.probe_desktop,
                probe_mcp=self.probe_mcp,
                probe_testql=self.probe_testql,
                probe_host=self.probe_host,
            )
            # DOQL round-trip does not yet restore desktop probe blocks; keep
            # the freshly generated in-memory IR so API/MQTT slices stay live.
            self._cached_ir = self._generate_ir(write=False)
        else:
            self._cached_ir = self._generate_ir(write=False)

        if publish_mqtt and self.mqtt is not None:
            self._publish_mqtt()
        return self._cached_ir

    def get_ir(self, *, refresh: bool = False) -> SystemMapIR:
        if refresh:
            return self.refresh()
        if self._cached_ir is not None:
            return self._cached_ir
        return self.load()

    def render(self, fmt: str = "json", *, refresh: bool = False) -> str:
        return render_format(self.get_ir(refresh=refresh), fmt)

    def to_dict(self, *, refresh: bool = False) -> dict[str, Any]:
        return self.get_ir(refresh=refresh).model_dump()

    def host_payload(self, *, refresh: bool = False) -> dict[str, Any] | None:
        host = self.get_ir(refresh=refresh).host
        return host.model_dump() if host is not None else None

    def desktop_payload(self, *, refresh: bool = False) -> dict[str, Any] | None:
        desktop = self.get_ir(refresh=refresh).desktop
        return desktop.model_dump() if desktop is not None else None

    def commands_payload(self, *, refresh: bool = False) -> list[dict[str, Any]]:
        return [cmd.model_dump() for cmd in self.get_ir(refresh=refresh).commands]

    def uris_payload(self, *, refresh: bool = False) -> dict[str, Any]:
        try:
            from nlp2uri.systemmap.index import build_uri_index
        except ImportError:
            return {
                "ok": False,
                "error": "nlp2uri not installed; pip install 'nlp2uri[envmap]'",
            }
        index = build_uri_index(self.get_ir(refresh=refresh))
        return {"ok": True, **index.to_dict()}

    def mqtt_status(self) -> dict[str, Any]:
        if self.mqtt is None:
            return {"enabled": False, "connected": False}
        return {
            "enabled": True,
            "connected": bool(getattr(self.mqtt, "connected", False)),
            "host": getattr(self.mqtt, "host", None),
            "port": getattr(self.mqtt, "port", None),
            "topic_prefix": getattr(self.mqtt, "prefix", None),
            "project_id": self.project_id,
        }

    def _generate_ir(self, *, write: bool) -> SystemMapIR:
        if write:
            path = ensure_environment_map(
                self.project_dir,
                project_id=self.project_id,
                merge_existing=self.merge_existing,
                probe_desktop=self.probe_desktop,
                probe_mcp=self.probe_mcp,
                probe_testql=self.probe_testql,
                probe_host=self.probe_host,
            )
            return doql_file_to_system_map(path)

        from env2llm.env import collect_environment, merge_environment
        from env2llm.generate import generate_system_map
        from env2llm.policy.desktop import apply_desktop_probe
        from env2llm.policy.invoice import apply_invoice_policies
        from env2llm.policy.mcp import apply_mcp_probe
        from env2llm.policy.browser_stack import apply_browser_stack_probe
        from env2llm.policy.host import apply_host_probe
        from env2llm.policy.testql import apply_testql_probe
        from env2llm.policy.process import apply_process_policies
        from env2llm.registry import merge_registry_observations

        env = merge_environment(collect_environment(), None)
        ir = generate_system_map(
            self.project_dir,
            example_id=self.project_id,
            environment=env,
        )
        registry_path = project_artifact_root(self.project_dir) / "registry" / "environment.doql.less"
        if self.merge_existing and registry_path.is_file():
            merge_registry_observations(ir, registry_path)
        repo_root = (
            self.project_dir.parent.parent
            if self.project_dir.parent.name == "examples"
            else self.project_dir.parent
        )
        apply_process_policies(ir, example_id=self.project_id, repo_root=repo_root)
        apply_invoice_policies(ir, example_id=self.project_id)
        apply_desktop_probe(ir, enabled=self.probe_desktop, project_dir=self.project_dir)
        apply_mcp_probe(ir, enabled=self.probe_mcp, project_dir=self.project_dir)
        apply_testql_probe(ir, enabled=self.probe_testql, project_dir=self.project_dir)
        apply_browser_stack_probe(ir)
        apply_host_probe(ir, enabled=self.probe_host, project_dir=self.project_dir)
        return ir

    def _publish_mqtt(self) -> None:
        if self.mqtt is None or self._cached_ir is None:
            return
        payload = self._cached_ir.model_dump()
        self.mqtt.publish_registry(self.project_id, payload)
        desktop = self.desktop_payload()
        if desktop is not None:
            self.mqtt.publish_desktop(self.project_id, desktop)
        self.mqtt.publish_event(
            self.project_id,
            "registry.refreshed",
            {
                "project_id": self.project_id,
                "example_id": self._cached_ir.example_id,
                "command_count": len(self._cached_ir.commands),
                "window_count": len(desktop.get("windows", [])) if desktop else 0,
            },
        )
