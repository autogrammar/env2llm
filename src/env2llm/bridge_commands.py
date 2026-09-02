"""Command schema conversion for DoqlTaskContext → SystemMapIR."""

from __future__ import annotations

from env2llm.doql import DoqlCommand, DoqlTaskContext
from env2llm.ir import CommandSchemaIR, FieldSpec, ProtocolSpec
from env2llm.runtimes import resolve_command_runtime

# Bootstrap field schemas when services.yaml omits required/optional
_COMMAND_FIELDS: dict[str, tuple[list[str], list[str]]] = {
    "send_invoice": (["amount", "to"], ["currency", "attachment_path"]),
    "generate_invoice": (["amount", "to"], ["currency", "output_path"]),
    "send_email": (["to"], ["subject", "body"]),
    "generate_report": (["report_type"], ["format"]),
    "crm_update": (["record_id"], ["fields"]),
}


def command_field_names(cmd: DoqlCommand) -> tuple[list[str], list[str]]:
    required = list(cmd.required)
    optional = list(cmd.optional)
    if not required and cmd.name in _COMMAND_FIELDS:
        required, optional = _COMMAND_FIELDS[cmd.name]
    return required, optional


def transport_for_runtime(cmd: DoqlCommand, runtime_id: str) -> str:
    if runtime_id == "orchestrator:nlp-service":
        return "nlp-service/system"
    if runtime_id == "delegate:mullm":
        return "nlp-service→mullm"
    if runtime_id == "executor:worker":
        return "gateway:backend→executor:worker"
    return cmd.transport


def protocol_for_command(cmd: DoqlCommand, transport: str) -> ProtocolSpec:
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


def command_to_ir(cmd: DoqlCommand, *, profile: dict | None = None) -> CommandSchemaIR:
    required, optional = command_field_names(cmd)
    fields = [
        *[FieldSpec(name=n, required=True) for n in required],
        *[FieldSpec(name=n, required=False) for n in optional],
    ]
    runtime_id = cmd.runtime or resolve_command_runtime(cmd.name, profile=profile)
    transport = transport_for_runtime(cmd, runtime_id)
    return CommandSchemaIR(
        name=cmd.name,
        description=cmd.description,
        runtime=runtime_id,
        protocol=protocol_for_command(cmd, transport),
        fields=fields,
        input_model=f"{''.join(p.title() for p in cmd.name.split('_'))}Config",
    )


def commands_from_context(
    ctx: DoqlTaskContext,
    *,
    profile: dict | None,
) -> list[CommandSchemaIR]:
    commands = [command_to_ir(cmd, profile=profile) for cmd in ctx.commands or []]
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
