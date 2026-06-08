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
from env2llm.ir import DesktopProbeIR, SystemMapIR
from env2llm.probes.desktop import collect_desktop_probe
from env2llm.policy.desktop import apply_desktop_probe
from env2llm.policy.mcp import apply_mcp_probe
from env2llm.policy.testql import apply_testql_probe
from env2llm.probes.testql import collect_testql_catalog, testql_available
from env2llm.probes.mcp import collect_koru_mcp_tools, collect_mcp_tools
from env2llm.layout import resolve_registry_path, write_registry
from env2llm.registry import refresh_doql_registry
from env2llm.service.registry_service import RegistryService
from env2llm.transport.mqtt import MqttRegistryBridge, mqtt_available

__all__ = [
    "DesktopProbeIR",
    "SystemMapIR",
    "apply_desktop_probe",
    "apply_mcp_probe",
    "apply_testql_probe",
    "collect_desktop_probe",
    "collect_koru_mcp_tools",
    "collect_mcp_tools",
    "collect_testql_catalog",
    "testql_available",
    "SUPPORTED_FORMATS",
    "collect_environment",
    "ensure_environment_map",
    "generate_system_map",
    "mask_secret",
    "merge_environment",
    "mqtt_available",
    "MqttRegistryBridge",
    "project_artifact_root",
    "RegistryService",
    "refresh_doql_registry",
    "render_format",
    "resolve_registry_path",
    "write_registry",
]

__version__ = "0.1.12"
