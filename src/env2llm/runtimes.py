"""Bootstrap runtime catalog from example-profiles.yaml + environment hints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from env2llm.ir import RuntimeSpecIR

# Default command → runtime when profile includes worker
_WORKER_ACTIONS = frozenset(
    {
        "send_invoice",
        "generate_invoice",
        "send_email",
        "generate_report",
        "crm_update",
        "notify_slack",
        "notify_telegram",
        "notify_teams",
        "generate_code",
    }
)

_SYSTEM_ACTION_PREFIX = "system_"
_MULLM_ACTION_PREFIX = "mullm_"
_DESKTOP_ACTION_PREFIX = "desktop_"
_KORU_ACTION_PREFIX = "koru_"
_TESTQL_ACTION_PREFIX = "testql_"


def _repo_root_from_example(example_dir: Path) -> Path:
    if example_dir.parent.name == "examples":
        return example_dir.parent.parent
    return example_dir.parent


def load_example_profile(example_id: str, repo_root: Path | None = None) -> dict[str, Any] | None:
    root = repo_root or Path.cwd()
    path = root / "examples" / "example-profiles.yaml"
    if not path.is_file():
        return None
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError:
        return None
    examples = payload.get("examples") or {}
    profile = examples.get(example_id)
    return profile if isinstance(profile, dict) else None


def resolve_command_runtime(action: str, *, profile: dict[str, Any] | None = None) -> str:
    if action.startswith(_TESTQL_ACTION_PREFIX):
        return "probe:testql"
    if action.startswith(_KORU_ACTION_PREFIX):
        return "mcp:koru"
    if action.startswith(_DESKTOP_ACTION_PREFIX):
        return "probe:desktop"
    if action.startswith(_MULLM_ACTION_PREFIX):
        return "delegate:mullm"
    if action.startswith(_SYSTEM_ACTION_PREFIX):
        return "orchestrator:nlp-service"
    services = (profile or {}).get("services") or []
    if action in _WORKER_ACTIONS and "worker" in services:
        return "executor:worker"
    return "executor:worker"


def _env_urls(env: Mapping[str, str]) -> dict[str, str]:
    return {
        "backend": env.get("NLP2DSL_BACKEND_URL", "http://localhost:8010"),
        "nlp": env.get("NLP2DSL_NLP_SERVICE_URL", "http://localhost:8012"),
        "worker": env.get("NLP2DSL_WORKER_URL", "http://localhost:8004"),
        "llm_model": env.get("LLM_MODEL", "openrouter/openai/gpt-5-mini"),
    }


def _llm_available(env: Mapping[str, str]) -> bool:
    return bool(env.get("OPENROUTER_API_KEY") or env.get("OPENAI_API_KEY"))


def _maybe_nlp_service_runtime(
    *,
    services: list[str],
    profile: dict[str, Any],
    nlp_url: str,
) -> RuntimeSpecIR | None:
    if "nlp-service" not in services and not profile.get("conversation"):
        return None
    return RuntimeSpecIR(
        id="orchestrator:nlp-service",
        kind="orchestrator",
        url=nlp_url,
        health="GET /health",
        roles=["nlp_parse", "dsl_map", "autofill", "preflight"],
        status="available",
    )


def _maybe_backend_runtime(*, services: list[str], backend_url: str) -> RuntimeSpecIR | None:
    if "backend" not in services:
        return None
    return RuntimeSpecIR(
        id="gateway:backend",
        kind="gateway",
        url=backend_url,
        health="GET /health",
        roles=["workflow_dispatch", "history"],
        status="available",
    )


def _maybe_worker_runtime(
    *,
    services: list[str],
    worker_url: str,
    docker_profiles: list[str],
) -> RuntimeSpecIR | None:
    if "worker" not in services:
        return None
    return RuntimeSpecIR(
        id="executor:worker",
        kind="worker",
        url=worker_url,
        health="GET /health",
        docker_profile=",".join(docker_profiles) if docker_profiles else None,
        roles=sorted(_WORKER_ACTIONS),
        status="available",
    )


def _llm_runtime(*, llm_model: str, llm_available: bool) -> RuntimeSpecIR:
    return RuntimeSpecIR(
        id="llm:provider",
        kind="llm",
        model=llm_model,
        roles=["intent", "entities", "system_map", "clarification"],
        status="available" if llm_available else "unknown",
    )


def _maybe_postgres_runtime(services: list[str]) -> RuntimeSpecIR | None:
    if "postgres" not in services:
        return None
    return RuntimeSpecIR(
        id="store:postgres",
        kind="database",
        uri="postgresql://app@postgres:5432/automation",
        roles=["workflow_history", "idempotency"],
        status="available",
    )


def _maybe_redis_runtime(services: list[str]) -> RuntimeSpecIR | None:
    if "redis" not in services:
        return None
    return RuntimeSpecIR(
        id="cache:redis",
        kind="cache",
        uri="redis://redis:6379/0",
        roles=["conversation_state"],
        status="available",
    )


def _maybe_smtp_mock_runtime(
    *,
    services: list[str],
    docker_profiles: list[str],
) -> RuntimeSpecIR | None:
    if "smtp-mock" not in services and "invoice" not in docker_profiles and "email" not in docker_profiles:
        return None
    return RuntimeSpecIR(
        id="mock:smtp",
        kind="mock",
        url="http://localhost:8025",
        docker_profile="invoice,email",
        roles=["email_delivery_test"],
        status="available" if "smtp-mock" in services else "unknown",
    )


def _mullm_runtime() -> RuntimeSpecIR:
    return RuntimeSpecIR(
        id="delegate:mullm",
        kind="external",
        roles=["filesystem", "rag", "shell_delegated"],
        status="unavailable",
    )


def _append_optional_runtime(
    runtimes: list[RuntimeSpecIR],
    runtime: RuntimeSpecIR | None,
) -> None:
    if runtime is not None:
        runtimes.append(runtime)


def build_runtimes_for_example(
    example_id: str,
    *,
    example_dir: Path | str,
    environment: Mapping[str, str] | None = None,
) -> list[RuntimeSpecIR]:
    """Materialize runtimes[] from example-profiles.yaml + env URLs."""
    root = Path(example_dir).resolve()
    repo_root = _repo_root_from_example(root)
    profile = load_example_profile(example_id, repo_root) or {}
    services = list(profile.get("services") or [])
    docker_profiles = list(profile.get("docker_profiles") or [])
    env = dict(environment or {})
    urls = _env_urls(env)
    llm_available = _llm_available(env)

    runtimes: list[RuntimeSpecIR] = []
    _append_optional_runtime(
        runtimes,
        _maybe_nlp_service_runtime(services=services, profile=profile, nlp_url=urls["nlp"]),
    )
    _append_optional_runtime(
        runtimes,
        _maybe_backend_runtime(services=services, backend_url=urls["backend"]),
    )
    _append_optional_runtime(
        runtimes,
        _maybe_worker_runtime(
            services=services,
            worker_url=urls["worker"],
            docker_profiles=docker_profiles,
        ),
    )
    runtimes.append(_llm_runtime(llm_model=urls["llm_model"], llm_available=llm_available))
    _append_optional_runtime(runtimes, _maybe_postgres_runtime(services))
    _append_optional_runtime(runtimes, _maybe_redis_runtime(services))
    _append_optional_runtime(
        runtimes,
        _maybe_smtp_mock_runtime(services=services, docker_profiles=docker_profiles),
    )
    runtimes.append(_mullm_runtime())

    return runtimes
