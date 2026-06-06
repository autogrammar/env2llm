"""Minimal runtime routing helpers (no HTTP health probes)."""

from __future__ import annotations

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


def runtime_id_for_intent(intent: str | None) -> str | None:
    if not intent:
        return None
    if intent.startswith("mullm_"):
        return "delegate:mullm"
    if intent.startswith("system_"):
        return "orchestrator:nlp-service"
    if intent in _WORKER_ACTIONS:
        return "executor:worker"
    return None
