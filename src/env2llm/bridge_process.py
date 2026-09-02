"""Process policy conversion for DoqlTaskContext → SystemMapIR."""

from __future__ import annotations

from env2llm.ir import ProcessAccessScopeIR, ProcessPathsIR, ProcessPolicyIR


def access_from_process_obj(proc) -> ProcessAccessScopeIR:
    access = getattr(proc, "access", None)
    return ProcessAccessScopeIR(
        agent=str(getattr(proc, "agent", "") or getattr(access, "agent", "")),
        allow_resource_areas=list(
            getattr(proc, "allow_resource_areas", None)
            or getattr(access, "allow_resource_areas", [])
            or []
        ),
        deny_resource_areas=list(
            getattr(proc, "deny_resource_areas", None)
            or getattr(access, "deny_resource_areas", [])
            or []
        ),
    )


def paths_from_process_obj(proc) -> ProcessPathsIR:
    paths = getattr(proc, "paths", None)
    return ProcessPathsIR(
        read=list(getattr(proc, "paths_read", None) or getattr(paths, "read", []) or []),
        write=list(getattr(proc, "paths_write", None) or getattr(paths, "write", []) or []),
    )


def process_from_ctx(ctx) -> ProcessPolicyIR:
    proc = getattr(ctx, "process", None)
    if proc is None:
        return ProcessPolicyIR()
    if isinstance(proc, ProcessPolicyIR):
        return proc
    return ProcessPolicyIR(
        mode=getattr(proc, "mode", "balanced"),
        nlp_parser=getattr(proc, "nlp_parser", "auto"),
        nlp_confidence_min=float(getattr(proc, "nlp_confidence_min", 0.5)),
        nlp_enrich_missing=bool(getattr(proc, "nlp_enrich_missing", False)),
        llm_reasoning=getattr(proc, "llm_reasoning", "shallow"),
        llm_temperature=getattr(proc, "llm_temperature", None),
        autonomous_enabled=bool(getattr(proc, "autonomous_enabled", True)),
        autonomous_max_rounds=int(getattr(proc, "autonomous_max_rounds", 8)),
        ask_user=getattr(proc, "ask_user", "when_exhausted"),
        intract_gate=bool(getattr(proc, "intract_gate", False)),
        intract_enforce_clarification=bool(getattr(proc, "intract_enforce_clarification", False)),
        access=access_from_process_obj(proc),
        paths=paths_from_process_obj(proc),
    )
