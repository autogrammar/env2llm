"""Profile validation specs from example-profiles.yaml."""

from __future__ import annotations

from typing import Any

from env2llm.ir import ProfileValidationIR, SystemMapIR


def _parse_profile_validation_by_code(raw: dict[str, Any]) -> ProfileValidationIR:
    return ProfileValidationIR(
        code=str(raw["code"]),
        action=str(raw.get("action") or ""),
        status=str(raw.get("status") or ""),
        path=str(raw.get("path") or ""),
    )


def _parse_profile_validation_by_type(raw: dict[str, Any]) -> ProfileValidationIR | None:
    vtype = str(raw.get("type", "")).strip()
    if vtype == "dsl_action":
        action = str(raw.get("action", "")).strip()
        if action:
            return ProfileValidationIR(code="profile.dsl_action", action=action)
    if vtype == "execution_completed":
        return ProfileValidationIR(code="profile.execution_completed")
    if vtype == "conversation_executed":
        return ProfileValidationIR(code="profile.conversation_executed")
    return None


def _parse_profile_validation_shorthand(raw: dict[str, Any]) -> ProfileValidationIR | None:
    if len(raw) != 1:
        return None
    key, value = next(iter(raw.items()))
    key = str(key)
    value_str = str(value)
    if key == "execution_status" and value_str == "completed":
        return ProfileValidationIR(code="profile.execution_completed", status=value_str)
    if key == "dsl_action" and value_str:
        return ProfileValidationIR(code="profile.dsl_action", action=value_str)
    if key == "conversation_status" and value_str == "executed":
        return ProfileValidationIR(code="profile.conversation_executed", status=value_str)
    if key == "artifact_exists" and value_str:
        return ProfileValidationIR(code="profile.artifact_exists", path=value_str)
    return None


def parse_profile_validation(raw: Any) -> ProfileValidationIR | None:
    if not isinstance(raw, dict) or not raw:
        return None
    if "code" in raw:
        return _parse_profile_validation_by_code(raw)
    if typed := _parse_profile_validation_by_type(raw):
        return typed
    return _parse_profile_validation_shorthand(raw)


def parse_profile_validations(raw_list: list[Any] | None) -> list[ProfileValidationIR]:
    out: list[ProfileValidationIR] = []
    for raw in raw_list or []:
        spec = parse_profile_validation(raw)
        if spec is not None:
            out.append(spec)
    return out


def apply_profile_validations(ir: SystemMapIR, profile: dict[str, Any] | None) -> None:
    if not profile:
        return
    specs = parse_profile_validations(profile.get("validations"))
    if specs:
        ir.validations = specs
