"""Deprecated compatibility shim for the public service factory."""

from __future__ import annotations

import warnings

warnings.warn(
    "env2llm.integrators._service_factory is private and deprecated; "
    "import from env2llm.service instead",
    DeprecationWarning,
    stacklevel=2,
)

from env2llm.service.factory import (  # noqa: E402,F401
    attach_mqtt_refresh_listener,
    build_registry_service,
)

__all__ = ["attach_mqtt_refresh_listener", "build_registry_service"]
