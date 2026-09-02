"""Bridge: static DoqlTaskContext (today) ↔ SystemMapIR (target)."""

from __future__ import annotations

from pathlib import Path

from env2llm.bridge_commands import commands_from_context
from env2llm.bridge_context import (
    access_from_context,
    artifacts_from_context,
    conversation_from_ctx,
    repo_root_from_example_dir,
    resources_from_context,
    runtimes_from_context,
)
from env2llm.bridge_process import process_from_ctx
from env2llm.doql import DoqlTaskContext, load_doql_context
from env2llm.ir import CommandSchemaIR, RuntimeSpecIR, SystemMapIR
from env2llm.policy.process import apply_process_policies
from env2llm.runtimes import load_example_profile


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
        resources=resources_from_context(ctx),
        access=access_from_context(ctx),
        artifacts=artifacts_from_context(ctx),
        capabilities=list(ctx.capabilities),
        workflow_history=dict(ctx.workflow_history),
        conversation=conversation_from_ctx(ctx),
        process=process_from_ctx(ctx),
        metadata={"source": "doql_context.bootstrap"},
    )


def task_context_to_system_map(ctx: DoqlTaskContext, *, example_dir: Path | str | None = None) -> SystemMapIR:
    """Convert hardcoded/bootstrap context into SystemMapIR (migration helper)."""
    profile = None
    if example_dir is not None:
        profile = load_example_profile(ctx.example_name, repo_root_from_example_dir(example_dir))

    ir = _base_system_map(
        ctx,
        runtimes=runtimes_from_context(ctx, example_dir=example_dir),
        commands=commands_from_context(ctx, profile=profile),
    )

    if example_dir is not None:
        apply_process_policies(
            ir,
            example_id=ctx.example_name,
            repo_root=repo_root_from_example_dir(example_dir),
        )
    if ctx.validations:
        ir.validations = list(ctx.validations)
    return ir


def doql_file_to_system_map(path: Path | str) -> SystemMapIR:
    """Parse environment.doql.less → SystemMapIR (round-trip via DoqlTaskContext)."""
    path = Path(path)
    ctx = load_doql_context(path)
    return task_context_to_system_map(ctx, example_dir=path.parent.parent)
