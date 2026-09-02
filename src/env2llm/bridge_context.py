"""Field-level DoqlTaskContext → SystemMapIR mappers."""

from __future__ import annotations

from pathlib import Path

from env2llm.doql import DoqlArtifact, DoqlTaskContext
from env2llm.ir import (
    AccessGrantIR,
    ArtifactSpecIR,
    ConversationPolicyIR,
    MimeTypeSpec,
    ResourceSpecIR,
    RuntimeSpecIR,
)
from env2llm.runtimes import build_runtimes_for_example

_VALID_RUNTIME_KINDS = frozenset({
    "orchestrator", "gateway", "worker", "llm", "database", "cache", "mock", "external",
})
_VALID_RUNTIME_STATUSES = frozenset({"available", "unavailable", "unknown"})
_VALID_ACCESS_EFFECTS = frozenset({"allow", "deny", "approval"})


def mime_for_artifact(art: DoqlArtifact) -> MimeTypeSpec | None:
    path = art.path.lower()
    if path.endswith(".pdf"):
        return MimeTypeSpec(type="application/pdf", schema_ref="InvoiceDocument")
    if path.endswith(".json"):
        return MimeTypeSpec(type="application/json")
    if path.endswith(".txt"):
        return MimeTypeSpec(type="text/plain", schema_ref="InvoiceMetadata")
    return None


def repo_root_from_example_dir(example_dir: Path | str) -> Path:
    root = Path(example_dir).resolve()
    if root.parent.name == "examples":
        return root.parent.parent
    return root.parent


def runtime_to_ir(runtime) -> RuntimeSpecIR:
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


def runtimes_from_context(
    ctx: DoqlTaskContext,
    *,
    example_dir: Path | str | None,
) -> list[RuntimeSpecIR]:
    if ctx.runtimes:
        return [runtime_to_ir(runtime) for runtime in ctx.runtimes]
    if example_dir is not None:
        return build_runtimes_for_example(
            ctx.example_name,
            example_dir=example_dir,
            environment=ctx.environment,
        )
    return []


def resources_from_context(ctx: DoqlTaskContext) -> list[ResourceSpecIR]:
    return [
        ResourceSpecIR(
            id=resource.id,
            title=resource.title,
            connector=resource.connector,
            uri_patterns=list(resource.uri_patterns),
        )
        for resource in ctx.resources
    ]


def access_from_context(ctx: DoqlTaskContext) -> list[AccessGrantIR]:
    return [
        AccessGrantIR(
            agent=grant.agent,
            resource_area=grant.resource_area,
            actions=list(grant.actions),
            effect=grant.effect if grant.effect in _VALID_ACCESS_EFFECTS else "allow",
        )
        for grant in ctx.access
    ]


def artifacts_from_context(ctx: DoqlTaskContext) -> list[ArtifactSpecIR]:
    return [
        ArtifactSpecIR(
            path=artifact.path,
            kind=artifact.kind,
            mime=mime_for_artifact(artifact),
            values=dict(artifact.values),
        )
        for artifact in ctx.artifacts
    ]


def conversation_from_ctx(ctx: DoqlTaskContext) -> ConversationPolicyIR:
    return ConversationPolicyIR(
        autofill=ctx.autofill,
        attachment_required=ctx.attachment_required,
        generate_invoice_if_missing=ctx.generate_invoice_if_missing,
        sync_auto_execute=ctx.sync_auto_execute,
        strict_pdf=ctx.strict_pdf,
    )
