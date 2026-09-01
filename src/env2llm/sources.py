"""Configurable sources for profiles, platform config, and services."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Protocol

import yaml


class EnvironmentSources(Protocol):
    def example_profile(self, project_id: str, repo_root: Path) -> dict[str, Any] | None: ...

    def platform_config(self, repo_root: Path) -> dict[str, Any]: ...

    def services_snapshot(self, artifact_root: Path) -> list[dict[str, Any]]: ...


def _dict_rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _actions_from_services_doc(doc: Any) -> list[dict[str, Any]]:
    if isinstance(doc, list):
        return _dict_rows(doc)
    if isinstance(doc, dict):
        return _dict_rows(doc.get("actions") or doc.get("commands") or [])
    return []


@dataclass
class DefaultEnvironmentSources:
    """Read nlp2dsl-style YAML layouts (example-profiles.yaml, nlp2dsl.yaml)."""

    profiles_filename: str = "example-profiles.yaml"
    platform_filenames: tuple[str, ...] = ("nlp2dsl.yaml", "nlp2dsl.local.yaml", "env2llm.yaml")
    extra_profile_dirs: tuple[Path, ...] = field(default_factory=tuple)

    def example_profile(self, project_id: str, repo_root: Path) -> dict[str, Any] | None:
        candidates = [
            repo_root / "examples" / self.profiles_filename,
            repo_root / self.profiles_filename,
            *[path / self.profiles_filename for path in self.extra_profile_dirs],
        ]
        for path in candidates:
            if not path.is_file():
                continue
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if not isinstance(doc, dict):
                continue
            profile = doc.get(project_id)
            if isinstance(profile, dict):
                return profile
        return None

    def platform_config(self, repo_root: Path) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for name in self.platform_filenames:
            path = repo_root / name
            if not path.is_file():
                continue
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if isinstance(doc, dict):
                merged.update(doc)
        return merged

    def services_snapshot(self, artifact_root: Path) -> list[dict[str, Any]]:
        path = artifact_root / "services.yaml"
        if not path.is_file():
            return []
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return _actions_from_services_doc(doc)
