"""Dynamic Pydantic models from SystemMapIR FieldSpec + MIME types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, create_model

from env2llm.ir import CommandSchemaIR, FieldSpec, SystemMapIR


_NUMERIC_FIELD_NAMES = frozenset({"amount", "total", "price", "quantity"})


def _base_type_for_field(field: FieldSpec) -> type:
    if field.mime:
        mime_type = field.mime.type
        if mime_type == "application/pdf":
            return str
        if mime_type == "application/json":
            return dict[str, Any]
        if mime_type.startswith("text/"):
            return str
    if field.name in _NUMERIC_FIELD_NAMES:
        return float
    return Any


def _annotation_for_field(field: FieldSpec) -> tuple[type, Any]:
    base = _base_type_for_field(field)
    if field.required:
        return base, Field(description=field.description or None)
    return base | None, Field(default=None, description=field.description or None)


def command_input_model(cmd: CommandSchemaIR) -> type[BaseModel]:
    """Build a runtime Pydantic model for one command's step config."""
    model_name = cmd.input_model or "".join(part.title() for part in cmd.name.split("_")) + "Config"
    field_defs: dict[str, tuple[type, Any]] = {}
    for spec in cmd.fields:
        field_defs[spec.name] = _annotation_for_field(spec)
    return create_model(model_name, **field_defs)  # type: ignore[call-overload]


def build_command_registry(ir: SystemMapIR) -> dict[str, type[BaseModel]]:
    return {cmd.name: command_input_model(cmd) for cmd in ir.commands}


def validate_config_against_map(ir: SystemMapIR, action: str, config: dict[str, Any]) -> dict[str, Any]:
    """Validate config with dynamic model; raises ValidationError on failure."""
    cmd = ir.command(action)
    if cmd is None:
        raise ValueError(f"unknown action: {action}")
    model = command_input_model(cmd)
    return model.model_validate(config).model_dump(exclude_none=True)
