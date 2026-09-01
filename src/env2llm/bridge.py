"""Bridge: static DoqlTaskContext (today) ↔ SystemMapIR (target)."""

from __future__ import annotations

from pathlib import Path

from env2llm.doql import DoqlArtifact, DoqlCommand, DoqlTaskContext, load_doql_context
from env2llm.ir import (
    AccessGrantIR,
    ArtifactSpecIR,
    CommandSchemaIR,
    ConversationPolicyIR,
    FieldSpec,
    MimeTypeSpec,
    ProcessAccessScopeIR,
    ProcessPathsIR,
    ProcessPolicyIR,
    ProtocolSpec,
    ResourceSpecIR,
    RuntimeSpecIR,
    SystemMapIR,
)
from env2llm.runtimes import build_runtimes_for_example, load_example_profile, resolve_command_runtime
from env2llm.policy.process import apply_process_policies

# Bootstrap field schemas when services.yaml omits required/optional
_COMMAND_FIELDS: dict[str, tuple[list[str], list[str]]] = {
    "send_invoice": (["amount", "to"], ["currency", "attachment_path"]),
    "generate_invoice": (["amount", "to"], ["currency", "output_path"]),
    "send_email": (["to"], ["subject", "body"]),
    "generate_report": (["report_type"], ["format"]),
    "crm_update": (["record_id"], ["fields"]),
}

_VALID_RUNTIME_KINDS = frozenset({
    "orchestrator", "gateway", "worker", "llm", "database", "cache", "mock", "external",
})
_VALID_RUNTIME_STATUSES = frozenset({"available", "unavailable", "unknown"})
_VALID_ACCESS_EFFECTS = frozenset({"allow", "deny", "approval"})


def _mime_for_artifact(art: DoqlArtifact) -> MimeTypeSpec | None:
    path = art.path.lower()
    if path.endswith(".pdf"):
        return MimeTypeSpec(type="application/pdf", schema_ref="InvoiceDocument")
    if path.endswith(".json"):
        return MimeTypeSpec(type="application/json")
    if path.endswith(".txt"):
        return MimeTypeSpec(type="text/plain", schema_ref="InvoiceMetadata")
    return None


def _access_from_process_obj(proc) -> ProcessAccessScopeIR:
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


def _paths_from_process_obj(proc) -> ProcessPathsIR:
    paths = getattr(proc, "paths", None)
    return ProcessPathsIR(
        read=list(getattr(proc, "paths_read", None) or getattr(paths, "read", []) or []),
        write=list(getattr(proc, "paths_write", None) or getattr(paths, "write", []) or []),
    )


def _process_from_ctx(ctx) -> ProcessPolicyIR:
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
        access=_access_from_process_obj(proc),
        paths=_paths_from_process_obj(proc),
    )


def _repo_root_from_example_dir(example_dir: Path | str) -> Path:
    root = Path(example_dir).resolve()
    if root.parent.name == "examples":
        return root.parent.parent
    return root.parent


def _commands_from_context(
    ctx: DoqlTaskContext,
    *,
    profile: dict | None,
) -> list[CommandSchemaIR]:
    commands = [_command_to_ir(cmd, profile=profile) for cmd in ctx.commands or []]
    if commands or not ctx.capabilities:
        return commands
    return [
        CommandSchemaIR(
            name=name,
            runtime=resolve_command_runtime(name, profile=profile),
            protocol=ProtocolSpec(name="workflow/run", transport="backend→worker"),
        )
        for name in ctx.capabilities
    ]


def _runtime_to_ir(runtime) -> RuntimeSpecIR:
    return RuntimeSpecIR(
        id=runtime.id,
        kind=runtime.kind if runtime.kind in _VALID_RUNTIME_KINDS else "worker",
        url=runtime.url or None,
        uri=runtime.uri or None,
        health=runtime.health or None,
        docker_profile=runtime.docker_profile or None,
        model=runtime.model or None,
        roles=list(runtime.roles),
        status=runtime.status if runtime.status in _VALID_RUNTIME_STATUSES else "unknown",
    )


def _runtimes_from_context(
    ctx: DoqlTaskContext,
    *,
    example_dir: Path | str | None,
) -> list[RuntimeSpecIR]:
    if ctx.runtimes:
        return [_runtime_to_ir(runtime) for runtime in ctx.runtimes]
    if example_dir is not None:
        return build_runtimes_for_example(
            ctx.example_name,
            example_dir=example_dir,
            environment=ctx.environment,
        )
    return []


def _resources_from_context(ctx: DoqlTaskContext) -> list[ResourceSpecIR]:
    return [
        ResourceSpecIR(
            id=resource.id,
            title=resource.title,
            connector=resource.connector,
            uri_patterns=list(resource.uri_patterns),
        )
        for resource in ctx.resources
    ]


def _access_from_context(ctx: DoqlTaskContext) -> list[AccessGrantIR]:
    return [
        AccessGrantIR(
            agent=grant.agent,
            resource_area=grant.resource_area,
            actions=list(grant.actions),
            effect=grant.effect if grant.effect in _VALID_ACCESS_EFFECTS else "allow",
        )
        for grant in ctx.access
    ]


def _artifacts_from_context(ctx: DoqlTaskContext) -> list[ArtifactSpecIR]:
    return [
        ArtifactSpecIR(
            path=artifact.path,
            kind=artifact.kind,
            mime=_mime_for_artifact(artifact),
            values=dict(artifact.values),
        )
        for artifact in ctx.artifacts
    ]


def _conversation_from_ctx(ctx: DoqlTaskContext) -> ConversationPolicyIR:
    return ConversationPolicyIR(
        autofill=ctx.autofill,
        attachment_required=ctx.attachment_required,
        generate_invoice_if_missing=ctx.generate_invoice_if_missing,
        sync_auto_execute=ctx.sync_auto_execute,
        strict_pdf=ctx.strict_pdf,
    )


def _base_system_map(
    ctx: DoqlTaskContext,
    *,
    runtimes: list[RuntimeSpecIR],
    commands: list[CommandSchemaIR],
) -> SystemMapIR:
    return SystemMapIR(
        example_id=ctx.example_name,
        environment=dict(ctx.environment),
        data=dict(ctx.data),
        runtimes=runtimes,
        commands=commands,
        resources=_resources_from_context(ctx),
        access=_access_from_context(ctx),
        artifacts=_artifacts_from_context(ctx),
        capabilities=list(ctx.capabilities),
        workflow_history=dict(ctx.workflow_history),
        conversation=_conversation_from_ctx(ctx),
        process=_process_from_ctx(ctx),
        metadata={"source": "doql_context.bootstrap"},
    )


def task_context_to_system_map(ctx: DoqlTaskContext, *, example_dir: Path | str | None = None) -> SystemMapIR:
    """Convert hardcoded/bootstrap context into SystemMapIR (migration helper)."""
    profile = None
    if example_dir is not None:
        profile = load_example_profile(ctx.example_name, _repo_root_from_example_dir(example_dir))

    ir = _base_system_map(
        ctx,
        runtimes=_runtimes_from_context(ctx, example_dir=example_dir),
        commands=_commands_from_context(ctx, profile=profile),
    )

    if example_dir is not None:
        apply_process_policies(
            ir,
            example_id=ctx.example_name,
            repo_root=_repo_root_from_example_dir(example_dir),
        )
    if ctx.validations:
        ir.validations = list(ctx.validations)
    return ir


def _command_field_names(cmd: DoqlCommand) -> tuple[list[str], list[str]]:
    required = list(cmd.required)
    optional = list(cmd.optional)
    if not required and cmd.name in _COMMAND_FIELDS:
        required, optional = _COMMAND_FIELDS[cmd.name]
    return required, optional


def _transport_for_runtime(cmd: DoqlCommand, runtime_id: str) -> str:
    if runtime_id == "orchestrator:nlp-service":
        return "nlp-service/system"
    if runtime_id == "delegate:mullm":
        return "nlp-service→mullm"
    if runtime_id == "executor:worker":
        return "gateway:backend→executor:worker"
    return cmd.transport


def _protocol_for_command(cmd: DoqlCommand, transport: str) -> ProtocolSpec:
    protocol_name = "workflow/run"
    if cmd.transport == "nlp-service/system":
        protocol_name = "propact:shell"
    elif "notify" in cmd.name:
        protocol_name = "workflow/run"
    return ProtocolSpec(
        name=protocol_name,
        transport=transport,
        endpoint=cmd.endpoint,
    )


def _command_to_ir(cmd: DoqlCommand, *, profile: dict | None = None) -> CommandSchemaIR:
    required, optional = _command_field_names(cmd)
    fields = [
        *[FieldSpec(name=n, required=True) for n in required],
        *[FieldSpec(name=n, required=False) for n in optional],
    ]
    runtime_id = cmd.runtime or resolve_command_runtime(cmd.name, profile=profile)
    transport = _transport_for_runtime(cmd, runtime_id)
    return CommandSchemaIR(
        name=cmd.name,
        description=cmd.description,
        runtime=runtime_id,
        protocol=_protocol_for_command(cmd, transport),
        fields=fields,
        input_model=f"{''.join(p.title() for p in cmd.name.split('_'))}Config",
    )


def doql_file_to_system_map(path: Path | str) -> SystemMapIR:
    """Parse environment.doql.less → SystemMapIR (round-trip via DoqlTaskContext)."""
    path = Path(path)
    ctx = load_doql_context(path)
    return task_context_to_system_map(ctx, example_dir=path.parent.parent)
