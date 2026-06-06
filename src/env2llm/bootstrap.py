"""Bootstrap environment map files for a project directory."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from env2llm.env import collect_environment, merge_environment
from env2llm.formats import default_output_name, render_format
from env2llm.generate import generate_system_map
from env2llm.layout import ensure_layout, write_registry
from env2llm.policy.invoice import apply_invoice_policies
from env2llm.policy.process import apply_process_policies
from env2llm.registry import merge_registry_observations


def project_artifact_root(project_dir: Path | str) -> Path:
    return Path(project_dir).resolve() / ".nlp2dsl"


def ensure_environment_map(
    project_dir: Path | str,
    *,
    project_id: str | None = None,
    output_format: str = "doql.less",
    environment: Mapping[str, str] | None = None,
    client: Any | None = None,
    merge_existing: bool = True,
    attachment: bool | None = None,
    auto_execute: bool | None = None,
) -> Path:
    """
    Generate and write the environment map for LLM/orchestrator context.

    Default output: ``.nlp2dsl/registry/environment.doql.less``.
    Other formats: yaml, json, markdown (see ``env2llm.formats``).
    """
    root = Path(project_dir).resolve()
    project = project_id or root.name
    artifact_root = project_artifact_root(root)
    ensure_layout(artifact_root)

    env = merge_environment(collect_environment(), environment)
    ir = generate_system_map(
        root,
        example_id=project,
        environment=env,
        client=client,
    )

    if auto_execute is None:
        auto_execute = os.environ.get("NLP2DSL_AUTO_EXECUTE", "1").strip().lower() in (
            "1",
            "true",
            "yes",
        )
    if auto_execute:
        ir.conversation.sync_auto_execute = True

    registry_path = artifact_root / "registry" / "environment.doql.less"
    if merge_existing and registry_path.is_file():
        merge_registry_observations(ir, registry_path)

    repo_root = root.parent.parent if root.parent.name == "examples" else root.parent
    apply_process_policies(ir, example_id=project, repo_root=repo_root)
    apply_invoice_policies(ir, example_id=project, attachment=attachment)

    content = render_format(ir, output_format)
    out_name = default_output_name(output_format)
    if out_name == "environment.doql.less":
        path = write_registry(artifact_root, content)
    else:
        out_dir = artifact_root / "registry"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / out_name
        path.write_text(content, encoding="utf-8")
        mirror = artifact_root / out_name
        if mirror != path:
            mirror.write_text(content, encoding="utf-8")

    os.environ.setdefault("ENV2LLM_CONTEXT", str(path))
    os.environ.setdefault("NLP2DSL_DOQL_CONTEXT", str(path))
    return path
