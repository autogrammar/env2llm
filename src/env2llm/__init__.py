"""
env2llm — environment introspection and LLM context generation.

Builds machine-readable maps of available services, artifacts, commands,
and environment variables (default: ``environment.doql.less``).
"""

from __future__ import annotations

from env2llm.bootstrap import ensure_environment_map, project_artifact_root
from env2llm.env import collect_environment, mask_secret, merge_environment
from env2llm.formats import render_format, SUPPORTED_FORMATS
from env2llm.generate import generate_system_map
from env2llm.ir import SystemMapIR
from env2llm.layout import resolve_registry_path, write_registry
from env2llm.registry import refresh_doql_registry

__all__ = [
    "SystemMapIR",
    "SUPPORTED_FORMATS",
    "collect_environment",
    "ensure_environment_map",
    "generate_system_map",
    "mask_secret",
    "merge_environment",
    "project_artifact_root",
    "refresh_doql_registry",
    "render_format",
    "resolve_registry_path",
    "write_registry",
]

__version__ = "0.1.1"
