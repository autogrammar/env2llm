"""Low-level DOQL entity parsing helpers."""

from __future__ import annotations

import re
from typing import Any

from .models import (
    DoqlAccess,
    DoqlArtifact,
    DoqlCommand,
    DoqlResource,
    DoqlRuntime,
)
from env2llm.ir import ProfileValidationIR

BLOCK_RE = re.compile(
    r"(environment|data|conversation|capabilities|workflow_history|process|process_access|paths)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}",
    re.DOTALL,
)
ARTIFACT_RE = re.compile(r"artifacts\s*\[[^\]]*\]\s*\{([^}]*)\}", re.DOTALL)
COMMAND_RE = re.compile(r"commands\s*\[[^\]]*\]\s*\{([^}]*)\}", re.DOTALL)
RESOURCE_RE = re.compile(r"resources\s*\[[^\]]*\]\s*\{([^}]*)\}", re.DOTALL)
ACCESS_RE = re.compile(r"access\s*\[[^\]]*\]\s*\{([^}]*)\}", re.DOTALL)
RUNTIME_RE = re.compile(r"runtimes\s*\[[^\]]*\]\s*\{([^}]*)\}", re.DOTALL)
VALIDATION_RE = re.compile(r"validations\s*\[[^\]]*\]\s*\{([^}]*)\}", re.DOTALL)
KV_RE = re.compile(
    r"(\w+(?:\.\w+)*)\s*:\s*(\"(?:\\.|[^\"])*\"|'(?:\\.|[^'])*'|[^;]+)\s*;",
)

PROCESS_STRING_FIELDS: dict[str, str] = {
    "mode": "mode",
    "nlp_parser": "nlp_parser",
    "llm_reasoning": "llm_reasoning",
    "ask_user": "ask_user",
}
PROCESS_FLOAT_FIELDS: dict[str, str] = {
    "nlp_confidence_min": "nlp_confidence_min",
    "llm_temperature": "llm_temperature",
}
PROCESS_INT_FIELDS: dict[str, str] = {"autonomous_max_rounds": "autonomous_max_rounds"}
PROCESS_BOOL_FIELDS: dict[str, str] = {
    "nlp_enrich_missing": "nlp_enrich_missing",
    "autonomous": "autonomous_enabled",
    "intract_gate": "intract_gate",
    "intract_enforce_clarification": "intract_enforce_clarification",
}


def parse_value(raw: str) -> Any:
    text = raw.strip().rstrip(",")
    if not text:
        return ""
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1].replace('\\"', '"')
    if text.startswith("'") and text.endswith("'"):
        return text[1:-1].replace("\\'", "'")
    lower = text.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def parse_block_body(body: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for match in KV_RE.finditer(body):
        out[match.group(1)] = parse_value(match.group(2))
    return out


def split_csv(raw: str) -> list[str]:
    return [part.strip() for part in str(raw).split(",") if part.strip()]


def parse_command_body(body: str) -> DoqlCommand:
    kv = parse_block_body(body)
    name = str(kv.get("name", kv.get("action", "")))
    return DoqlCommand(
        name=name,
        description=str(kv.get("description", "")),
        required=split_csv(str(kv.get("required", ""))),
        optional=split_csv(str(kv.get("optional", ""))),
        runtime=str(kv.get("runtime", "")),
        transport=str(kv.get("transport", "backend→worker")),
        endpoint=str(kv.get("endpoint", "POST /workflow/run")),
    )


def parse_resource_body(body: str) -> DoqlResource:
    kv = parse_block_body(body)
    return DoqlResource(
        id=str(kv.get("id", "")),
        title=str(kv.get("title", "")),
        connector=str(kv.get("connector", "")),
        uri_patterns=split_csv(str(kv.get("uri_patterns", kv.get("uri", "")))),
    )


def parse_access_body(body: str) -> DoqlAccess:
    kv = parse_block_body(body)
    return DoqlAccess(
        agent=str(kv.get("agent", "")),
        resource_area=str(kv.get("resource_area", kv.get("resource", ""))),
        actions=split_csv(str(kv.get("actions", ""))),
        effect=str(kv.get("effect", "allow")),
    )


def parse_runtime_body(body: str) -> DoqlRuntime:
    kv = parse_block_body(body)
    return DoqlRuntime(
        id=str(kv.get("id", "")),
        kind=str(kv.get("kind", "worker")),
        url=str(kv.get("url", "")),
        uri=str(kv.get("uri", "")),
        health=str(kv.get("health", "")),
        docker_profile=str(kv.get("docker_profile", "")),
        model=str(kv.get("model", "")),
        roles=split_csv(str(kv.get("roles", ""))),
        status=str(kv.get("status", "unknown")),
    )


def parse_validation_body(body: str) -> ProfileValidationIR:
    kv = parse_block_body(body)
    return ProfileValidationIR(
        code=str(kv.get("code", "")),
        action=str(kv.get("action", "")),
        status=str(kv.get("status", "")),
        path=str(kv.get("path", "")),
    )


def parse_artifact_body(body: str) -> DoqlArtifact:
    kv = parse_block_body(body)
    values: dict[str, Any] = {}
    path = str(kv.get("path", ""))
    kind = str(kv.get("kind", "file"))
    for key in ("to", "amount", "currency", "attachment_path", "recipient"):
        if key in kv:
            values[key] = kv[key]
    return DoqlArtifact(path=path, kind=kind, values=values)
