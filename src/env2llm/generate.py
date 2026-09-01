"""
Generate SystemMapIR at runtime via LLM + introspection.

Bootstrap fallback: collect_task_context() → task_context_to_system_map().
Enable LLM path: NLP2DSL_SYSTEM_MAP_LLM=1 and a configured LiteLLM provider.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Mapping

from env2llm.bridge import task_context_to_system_map
from env2llm.doql import collect_task_context, enrich_task_context_from_client
from env2llm.ir import SystemMapIR
from env2llm.llm_backend import LLMComplete
from env2llm.policy.desktop import desktop_probe_enabled
from env2llm.runtimes import load_example_profile

log = logging.getLogger("nlp2dsl.system_map")

_SYSTEM_PROMPT = """You are a system map generator for nlp2dsl.
Given introspection data about an example environment, emit ONE JSON object
matching env2llm.system_map.v1 (SystemMapIR).

Rules:
- runtimes[]: available execution environments (worker, nlp-service, llm, postgres, …) with status
- commands[]: each action with runtime ref, protocol (workflow/run or propact:*), fields with MIME/schema_ref
- artifacts[]: files with mime.type and schema_ref (e.g. application/pdf → InvoiceDocument)
- resources[] and access[]: from nlp2dsl.yaml hints when present
- data: known field values from fixtures
- conversation: autofill / attachment policies when inferable
- Return ONLY valid JSON, no markdown fences."""


def _introspection_base_payload(
    *,
    example_id: str,
    root: Path,
    profile: dict[str, Any] | None,
    environment: Mapping[str, str] | None,
    queries: list[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "example_id": example_id,
        "example_dir": str(root),
        "example_profile": profile,
        "environment": dict(environment or {}),
        "queries": list(queries or []),
        "fixtures": [],
        "services_yaml": None,
        "nlp2dsl_yaml": None,
        "workflow_actions": None,
    }


def _collect_fixture_introspection(artifact_root: Path) -> list[dict[str, str]]:
    fixtures_dir = artifact_root / "fixtures"
    if not fixtures_dir.is_dir():
        return []
    fixtures: list[dict[str, str]] = []
    for path in sorted(fixtures_dir.iterdir()):
        if path.is_file():
            fixtures.append(
                {"path": str(path.relative_to(artifact_root)), "suffix": path.suffix.lower()}
            )
    return fixtures


def _attach_config_snapshots(
    payload: dict[str, Any],
    *,
    artifact_root: Path,
    repo_root: Path,
) -> None:
    services_path = artifact_root / "services.yaml"
    if services_path.is_file():
        payload["services_yaml"] = services_path.read_text(encoding="utf-8")[:8000]

    config_path = repo_root / "nlp2dsl.yaml"
    if config_path.is_file():
        payload["nlp2dsl_yaml"] = config_path.read_text(encoding="utf-8")[:8000]


def _attach_live_introspection(payload: dict[str, Any], client: Any | None) -> None:
    if client is None:
        return
    try:
        payload["workflow_actions"] = client.workflow_actions()
    except Exception as exc:
        log.debug("workflow_actions introspection failed: %s", exc)

    if not desktop_probe_enabled():
        return
    from env2llm.probes.desktop import collect_desktop_probe

    payload["desktop_probe"] = collect_desktop_probe().model_dump()


def build_introspection_payload(
    example_dir: Path | str,
    *,
    example_id: str,
    environment: Mapping[str, str] | None = None,
    queries: list[Mapping[str, Any]] | None = None,
    client: Any | None = None,
) -> dict[str, Any]:
    """Collect raw signals for LLM (filesystem, YAML, live API)."""
    root = Path(example_dir).resolve()
    artifact_root = root / ".nlp2dsl"
    repo_root = root.parent.parent if root.parent.name == "examples" else root.parent
    profile = load_example_profile(example_id, repo_root)
    payload = _introspection_base_payload(
        example_id=example_id,
        root=root,
        profile=profile,
        environment=environment,
        queries=queries,
    )
    payload["fixtures"] = _collect_fixture_introspection(artifact_root)
    _attach_config_snapshots(payload, artifact_root=artifact_root, repo_root=repo_root)
    _attach_live_introspection(payload, client)
    return payload


def _bootstrap_system_map(
    example_dir: Path | str,
    *,
    example_id: str,
    environment: Mapping[str, str] | None = None,
    queries: list[Mapping[str, Any]] | None = None,
    client: Any | None = None,
) -> SystemMapIR:
    ctx = collect_task_context(
        example_dir,
        example_name=example_id,
        environment=environment,
        queries=queries,
    )
    if client is not None:
        enrich_task_context_from_client(ctx, client)
    return task_context_to_system_map(ctx, example_dir=example_dir)


def _parse_llm_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response is not a JSON object")
    return parsed


def generate_system_map(
    example_dir: Path | str,
    *,
    example_id: str,
    environment: Mapping[str, str] | None = None,
    queries: list[Mapping[str, Any]] | None = None,
    client: Any | None = None,
    llm_complete: LLMComplete | None = None,
    hints: Mapping[str, Any] | None = None,
) -> SystemMapIR:
    """
    Build SystemMapIR: LLM when enabled, else bootstrap from introspection code.
    """
    use_llm = os.getenv("NLP2DSL_SYSTEM_MAP_LLM", "").strip().lower() in ("1", "true", "yes")
    complete = llm_complete
    if use_llm and complete is None:
        try:
            from env2llm.llm_backend import LitellmComplete
            import litellm  # noqa: F401
            complete = LitellmComplete()
        except ImportError:
            log.warning("NLP2DSL_SYSTEM_MAP_LLM set but litellm not installed; using bootstrap")
            use_llm = False

    if not use_llm or complete is None:
        return _bootstrap_system_map(
            example_dir,
            example_id=example_id,
            environment=environment,
            queries=queries,
            client=client,
        )

    introspection = build_introspection_payload(
        example_dir,
        example_id=example_id,
        environment=environment,
        queries=queries,
        client=client,
    )
    schema = SystemMapIR.model_json_schema()
    user = json.dumps(
        {"schema": schema, "introspection": introspection, "hints": dict(hints or {})},
        ensure_ascii=False,
        indent=2,
    )
    try:
        raw = complete(_SYSTEM_PROMPT, user)
        data = _parse_llm_json(raw)
        ir = SystemMapIR.model_validate(data)
        ir.metadata.setdefault("source", "llm")
        return ir
    except Exception:
        log.exception("SystemMapGenerator LLM failed; falling back to bootstrap")
        return _bootstrap_system_map(
            example_dir,
            example_id=example_id,
            environment=environment,
            queries=queries,
            client=client,
        )
