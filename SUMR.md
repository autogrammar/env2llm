# env2llm

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `env2llm`
- **version**: `0.1.2`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(2), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: env2llm;
  version: 0.1.2;
}

dependencies {
  runtime: "pydantic>=2.0, pyyaml>=6.0";
  dev: "pytest>=8.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="env2llm"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -r requirements.txt;
}

workflow[name="install-dev"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install pytest pytest-asyncio httpx anyio;
}

workflow[name="install-ai"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install litellm;
}

workflow[name="setup"] {
  trigger: manual;
  step-1: run cmd=echo "$(GREEN)✓ Setup complete$(RESET)";
}

workflow[name="env"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f .env ]; then \;
  step-2: run cmd=cp .env.example .env; \;
  step-3: run cmd=echo "$(GREEN)✓ Created .env from .env.example$(RESET)"; \;
  step-4: run cmd=else \;
  step-5: run cmd=echo "$(YELLOW)⚠ .env already exists$(RESET)"; \;
  step-6: run cmd=fi;
}

workflow[name="run"] {
  trigger: manual;
  step-1: depend target=web;
}

workflow[name="web"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting web server on http://$(HOST):$(PORT)$(RESET)";
  step-2: run cmd=$(PYTHON) -m web.app;
}

workflow[name="shell"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting interactive shell$(RESET)";
  step-2: run cmd=$(PYTHON) -m cli.main;
}

workflow[name="plan"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m cli.main plan examples/01-user-api/generated/iterun.yaml -o examples/01-user-api/generated/;
}

workflow[name="execute"] {
  trigger: manual;
  step-1: run cmd=ITERUN_EXECUTE=1 ./examples/01-user-api/run.sh;
}

workflow[name="examples"] {
  trigger: manual;
  step-1: run cmd=./examples/run-all.sh;
}

workflow[name="run-intent"] {
  trigger: manual;
  step-1: run cmd=if [ -z "$(FILE)" ]; then \;
  step-2: run cmd=echo "$(RED)ERROR: FILE not specified$(RESET)"; \;
  step-3: run cmd=echo "Usage: make run-intent FILE=path/to/iterun.yaml"; \;
  step-4: run cmd=exit 1; \;
  step-5: run cmd=fi;
  step-6: run cmd=$(PYTHON) -m cli.main execute $(FILE);
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/ -v;
}

workflow[name="test-shell"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_shell.py -v;
}

workflow[name="test-web"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_web.py -v;
}

workflow[name="test-ai"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_ai_gateway.py -v;
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term;
}

workflow[name="ollama-start"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting Ollama server...$(RESET)";
  step-2: run cmd=ollama serve &;
  step-3: run cmd=sleep 2;
  step-4: run cmd=echo "$(GREEN)✓ Ollama server started$(RESET)";
}

workflow[name="ollama-pull"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Pulling model: $(DEFAULT_MODEL)$(RESET)";
  step-2: run cmd=ollama pull $(DEFAULT_MODEL);
  step-3: run cmd=echo "$(GREEN)✓ Model $(DEFAULT_MODEL) ready$(RESET)";
}

workflow[name="ollama-models"] {
  trigger: manual;
  step-1: run cmd=echo "";
  step-2: run cmd=echo "$(CYAN)Recommended Ollama models (≤12B):$(RESET)";
  step-3: run cmd=echo "  $(GREEN)llama3.2$(RESET)       - 3B  - Default, fast";
  step-4: run cmd=echo "  llama3.2:1b    - 1B  - Ultra lightweight";
  step-5: run cmd=echo "  llama3.1:8b    - 8B  - Balanced";
  step-6: run cmd=echo "  mistral        - 7B  - Fast inference";
  step-7: run cmd=echo "  mistral-nemo   - 12B - Best quality";
  step-8: run cmd=echo "  gemma2         - 9B  - Google Gemma 2";
  step-9: run cmd=echo "  phi3           - 3.8B - Microsoft Phi-3";
  step-10: run cmd=echo "  qwen2.5        - 7B  - Alibaba Qwen";
  step-11: run cmd=echo "  codellama      - 7B  - Code generation";
  step-12: run cmd=echo "";
  step-13: run cmd=echo "$(YELLOW)Install:$(RESET) ollama pull <model>";
  step-14: run cmd=echo "";
}

workflow[name="ollama-status"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Checking Ollama status...$(RESET)";
  step-2: run cmd=curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \;
  step-3: run cmd=echo "$(GREEN)✓ Ollama is running$(RESET)" || \;
  step-4: run cmd=echo "$(RED)✗ Ollama is not running$(RESET)";
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=which ruff > /dev/null 2>&1 && ruff check . || echo "$(YELLOW)ruff not installed$(RESET)";
}

workflow[name="format"] {
  trigger: manual;
  step-1: run cmd=which ruff > /dev/null 2>&1 && ruff format . || echo "$(YELLOW)ruff not installed$(RESET)";
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Cleaning...$(RESET)";
  step-2: run cmd=rm -rf __pycache__ */__pycache__ */*/__pycache__;
  step-3: run cmd=rm -rf .pytest_cache */.pytest_cache;
  step-4: run cmd=rm -rf *.egg-info .eggs;
  step-5: run cmd=rm -rf htmlcov .coverage;
  step-6: run cmd=rm -rf /tmp/intent-*;
  step-7: run cmd=echo "$(GREEN)✓ Cleaned$(RESET)";
}

workflow[name="docker-clean"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Cleaning Docker resources...$(RESET)";
  step-2: run cmd=-docker ps -a --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker rm -f;
  step-3: run cmd=-docker images --filter "reference=$(CONTAINER_PREFIX)-*" -q | xargs -r docker rmi -f;
  step-4: run cmd=echo "$(GREEN)✓ Docker cleaned$(RESET)";
}

workflow[name="docker-ps"] {
  trigger: manual;
  step-1: run cmd=docker ps --filter "name=$(CONTAINER_PREFIX)-";
}

workflow[name="docker-stop"] {
  trigger: manual;
  step-1: run cmd=docker ps --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker stop;
  step-2: run cmd=echo "$(GREEN)✓ Containers stopped$(RESET)";
}

workflow[name="dev"] {
  trigger: manual;
  step-1: run cmd=uvicorn web.app:app --reload --host $(HOST) --port $(PORT);
}

workflow[name="new-intent"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m cli.main new;
}

workflow[name="show-config"] {
  trigger: manual;
  step-1: run cmd=echo "";
  step-2: run cmd=echo "$(CYAN)Current Configuration:$(RESET)";
  step-3: run cmd=echo "  HOST=$(HOST)";
  step-4: run cmd=echo "  PORT=$(PORT)";
  step-5: run cmd=echo "  DEFAULT_MODEL=$(DEFAULT_MODEL)";
  step-6: run cmd=echo "  CONTAINER_PORT=$(CONTAINER_PORT)";
  step-7: run cmd=echo "  CONTAINER_PREFIX=$(CONTAINER_PREFIX)";
  step-8: run cmd=echo "  OLLAMA_BASE_URL=$(OLLAMA_BASE_URL)";
  step-9: run cmd=echo "  SKIP_ITERUN_CONFIRMATION=$(SKIP_ITERUN_CONFIRMATION)";
  step-10: run cmd=echo "";
}

deploy {
  target: makefile;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.10;
}
```

## Workflows

## Dependencies

### Runtime

```text markpact:deps python
pydantic>=2.0
pyyaml>=6.0
```

### Development

```text markpact:deps python scope=dev
pytest>=8.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Call Graph

*149 nodes · 156 edges · 23 modules · CC̄=4.8*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `render_system_map_doql` *(in src.env2llm.render.doql.render)* | 1 | 2 | 37 | **39** |
| `build_runtimes_for_example` *(in src.env2llm.runtimes)* | 18 ⚠ | 1 | 35 | **36** |
| `load_platform_map` *(in src.env2llm.doql.parse)* | 18 ⚠ | 1 | 32 | **33** |
| `collect_task_context` *(in src.env2llm.doql.parse)* | 19 ⚠ | 1 | 32 | **33** |
| `task_context_to_system_map` *(in src.env2llm.bridge)* | 25 ⚠ | 3 | 30 | **33** |
| `enrich_task_context_from_client` *(in src.env2llm.doql.parse)* | 19 ⚠ | 1 | 29 | **30** |
| `render_doql_context` *(in src.env2llm.doql.render)* | 1 | 1 | 29 | **30** |
| `ensure_environment_map` *(in src.env2llm.bootstrap)* | 9 | 2 | 24 | **26** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/env2llm
# generated in 0.08s
# nodes: 149 | edges: 156 | modules: 23
# CC̄=4.8

HUBS[20]:
  src.env2llm.render.doql.render.render_system_map_doql
    CC=1  in:2  out:37  total:39
  src.env2llm.runtimes.build_runtimes_for_example
    CC=18  in:1  out:35  total:36
  src.env2llm.doql.parse.load_platform_map
    CC=18  in:1  out:32  total:33
  src.env2llm.doql.parse.collect_task_context
    CC=19  in:1  out:32  total:33
  src.env2llm.bridge.task_context_to_system_map
    CC=25  in:3  out:30  total:33
  src.env2llm.doql.parse.enrich_task_context_from_client
    CC=19  in:1  out:29  total:30
  src.env2llm.doql.render.render_doql_context
    CC=1  in:1  out:29  total:30
  src.env2llm.bootstrap.ensure_environment_map
    CC=9  in:2  out:24  total:26
  src.env2llm.policy.process.process_policy_from_profile_block
    CC=5  in:1  out:23  total:24
  src.env2llm.render.doql.helpers.join_csv
    CC=1  in:23  out:1  total:24
  src.env2llm.doql.parse._parse_runtime_body
    CC=1  in:1  out:21  total:22
  src.env2llm.layout.write_turn_snapshot
    CC=4  in:0  out:21  total:21
  src.env2llm.generate.build_introspection_payload
    CC=11  in:1  out:20  total:21
  src.env2llm.doql.parse._parse_command_body
    CC=1  in:1  out:19  total:20
  src.env2llm.doql.parse.load_commands_from_services_yaml
    CC=14  in:1  out:19  total:20
  src.env2llm.doql.runtime.context_inline_payload
    CC=14  in:1  out:18  total:19
  src.env2llm.doql.parse._append_collection_blocks
    CC=12  in:1  out:18  total:19
  src.env2llm.registry.refresh_doql_registry
    CC=10  in:1  out:17  total:18
  src.env2llm.layout._force_remove_path
    CC=7  in:1  out:15  total:16
  src.env2llm.generate.generate_system_map
    CC=8  in:1  out:15  total:16

MODULES:
  src.env2llm._runtime_health  [1 funcs]
    runtime_id_for_intent  CC=5  out:2
  src.env2llm.bootstrap  [3 funcs]
    ensure_doql_registry  CC=1  out:1
    ensure_environment_map  CC=9  out:24
    project_artifact_root  CC=1  out:2
  src.env2llm.bridge  [3 funcs]
    _command_to_ir  CC=12  out:10
    doql_file_to_system_map  CC=1  out:3
    task_context_to_system_map  CC=25  out:30
  src.env2llm.cli  [2 funcs]
    build_parser  CC=1  out:7
    main  CC=1  out:6
  src.env2llm.doql.context_blocks  [9 funcs]
    render_context_access  CC=4  out:8
    render_context_capabilities  CC=2  out:1
    render_context_conversation  CC=3  out:3
    render_context_data  CC=2  out:4
    render_context_environment  CC=3  out:5
    render_context_paths  CC=5  out:5
    render_context_process_access  CC=7  out:6
    render_context_resources  CC=5  out:9
    render_context_workflow_history  CC=6  out:9
  src.env2llm.doql.models  [1 funcs]
    runtime_for  CC=6  out:3
  src.env2llm.doql.parse  [24 funcs]
    _append_collection_blocks  CC=12  out:18
    _apply_capabilities_block  CC=5  out:7
    _apply_context_block  CC=10  out:10
    _apply_context_metadata  CC=3  out:4
    _apply_conversation_block  CC=1  out:10
    _apply_paths_block  CC=3  out:4
    _apply_process_access_block  CC=4  out:5
    _apply_process_block  CC=9  out:12
    _command_transport  CC=3  out:2
    _parse_access_body  CC=1  out:12
  src.env2llm.doql.render  [2 funcs]
    render_doql_context  CC=1  out:29
    write_doql_context  CC=1  out:4
  src.env2llm.doql.runtime  [15 funcs]
    _add_short_inline_alias  CC=5  out:5
    _apply_conversation_flag  CC=6  out:5
    _autofill_value  CC=2  out:3
    _candidate_data_keys  CC=1  out:0
    _canonical_field  CC=1  out:2
    _inline_data_key  CC=1  out:1
    _needs_field  CC=1  out:1
    _split_missing_ref  CC=4  out:4
    _value_from_artifacts  CC=6  out:0
    _value_from_data  CC=4  out:0
  src.env2llm.env  [3 funcs]
    collect_environment  CC=13  out:13
    mask_secret  CC=3  out:1
    merge_environment  CC=3  out:3
  src.env2llm.formats  [3 funcs]
    default_output_name  CC=2  out:1
    normalize_format  CC=2  out:4
    render_format  CC=2  out:6
  src.env2llm.formats.doql_less  [1 funcs]
    render_doql_less  CC=1  out:1
  src.env2llm.generate  [4 funcs]
    _bootstrap_system_map  CC=2  out:3
    _parse_llm_json  CC=5  out:8
    build_introspection_payload  CC=11  out:20
    generate_system_map  CC=8  out:15
  src.env2llm.layout  [13 funcs]
    _chmod_writable  CC=2  out:1
    _force_remove_path  CC=7  out:15
    artifact_root  CC=1  out:2
    clean_all_example_artifacts  CC=5  out:6
    clean_artifact_root  CC=9  out:9
    current_run_id  CC=2  out:4
    ensure_layout  CC=1  out:6
    resolve_registry_path  CC=9  out:11
    run_dir  CC=2  out:4
    write_last_run_report  CC=1  out:6
  src.env2llm.policy.invoice  [3 funcs]
    apply_invoice_context  CC=3  out:8
    apply_invoice_policies  CC=5  out:6
    is_invoice_example  CC=2  out:1
  src.env2llm.policy.process  [15 funcs]
    _apply_autonomous_policy  CC=5  out:4
    _apply_llm_policy  CC=4  out:3
    _apply_nlp_policy  CC=5  out:4
    _as_list  CC=8  out:9
    _deep_merge_process  CC=5  out:7
    _intract_flags  CC=2  out:4
    _load_nlp2dsl_payload  CC=12  out:12
    _merge_access  CC=5  out:10
    _merge_conversation_from_profile  CC=5  out:4
    _merge_paths  CC=4  out:8
  src.env2llm.policy.validations  [6 funcs]
    _parse_profile_validation_by_code  CC=4  out:8
    _parse_profile_validation_by_type  CC=5  out:9
    _parse_profile_validation_shorthand  CC=10  out:10
    apply_profile_validations  CC=3  out:2
    parse_profile_validation  CC=5  out:4
    parse_profile_validations  CC=4  out:2
  src.env2llm.registry  [11 funcs]
    _execution_steps  CC=4  out:3
    _merge_execution_header  CC=1  out:5
    _merge_execution_step  CC=4  out:6
    _merge_generate_invoice_output  CC=3  out:2
    _merge_send_invoice_output  CC=3  out:3
    _merge_workflow_id  CC=3  out:3
    _step_output  CC=4  out:3
    merge_execution_observation  CC=2  out:6
    merge_registry_observations  CC=11  out:10
    refresh_doql_registry  CC=10  out:17
  src.env2llm.render.doql.blocks  [14 funcs]
    render_access_block  CC=4  out:8
    render_capabilities_block  CC=2  out:1
    render_conversation_block  CC=3  out:7
    render_data_block  CC=3  out:4
    render_deploy_block  CC=3  out:3
    render_environment_block  CC=2  out:5
    render_generated_services_block  CC=6  out:10
    render_paths_block  CC=5  out:5
    render_process_access_block  CC=7  out:6
    render_process_block  CC=3  out:4
  src.env2llm.render.doql.helpers  [7 funcs]
    bool_lit  CC=2  out:0
    data_value_line  CC=3  out:4
    esc_str  CC=1  out:1
    esc_str_full  CC=1  out:2
    history_value_line  CC=4  out:4
    join_csv  CC=1  out:1
    process_field_line  CC=3  out:3
  src.env2llm.render.doql.render  [1 funcs]
    render_system_map_doql  CC=1  out:37
  src.env2llm.runtimes  [4 funcs]
    _repo_root_from_example  CC=2  out:0
    build_runtimes_for_example  CC=18  out:35
    load_example_profile  CC=7  out:7
    resolve_command_runtime  CC=7  out:3
  src.env2llm.system_map_models  [4 funcs]
    _annotation_for_field  CC=11  out:3
    build_command_registry  CC=2  out:1
    command_input_model  CC=4  out:5
    validate_config_against_map  CC=2  out:5

EDGES:
  src.env2llm.env.collect_environment → src.env2llm.env.mask_secret
  src.env2llm.formats.render_format → src.env2llm.formats.normalize_format
  src.env2llm.formats.default_output_name → src.env2llm.formats.normalize_format
  src.env2llm.formats.doql_less.render_doql_less → src.env2llm.render.doql.render.render_system_map_doql
  src.env2llm.policy.process.load_platform_process_defaults → src.env2llm.policy.process._load_nlp2dsl_payload
  src.env2llm.policy.process._merge_access → src.env2llm.policy.process._as_list
  src.env2llm.policy.process._merge_paths → src.env2llm.policy.process._as_list
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._apply_nlp_policy
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._apply_autonomous_policy
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._apply_llm_policy
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._intract_flags
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._merge_access
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._merge_paths
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._process_policy_from_parts
  src.env2llm.policy.process.merge_process_config → src.env2llm.policy.process.load_platform_process_defaults
  src.env2llm.policy.process.merge_process_config → src.env2llm.policy.process._deep_merge_process
  src.env2llm.policy.process.apply_process_policies → src.env2llm.policy.process.merge_process_config
  src.env2llm.policy.process.apply_process_policies → src.env2llm.policy.validations.apply_profile_validations
  src.env2llm.policy.process.apply_process_policies → src.env2llm.runtimes.load_example_profile
  src.env2llm.policy.process.apply_process_policies → src.env2llm.policy.process.process_policy_from_profile_block
  src.env2llm.policy.process.apply_process_policies → src.env2llm.policy.process._merge_conversation_from_profile
  src.env2llm.policy.validations.parse_profile_validation → src.env2llm.policy.validations._parse_profile_validation_shorthand
  src.env2llm.policy.validations.parse_profile_validation → src.env2llm.policy.validations._parse_profile_validation_by_code
  src.env2llm.policy.validations.parse_profile_validation → src.env2llm.policy.validations._parse_profile_validation_by_type
  src.env2llm.policy.validations.parse_profile_validations → src.env2llm.policy.validations.parse_profile_validation
  src.env2llm.policy.validations.apply_profile_validations → src.env2llm.policy.validations.parse_profile_validations
  src.env2llm.policy.invoice.apply_invoice_policies → src.env2llm.policy.invoice.is_invoice_example
  src.env2llm.policy.invoice.apply_invoice_context → src.env2llm.policy.invoice.is_invoice_example
  src.env2llm.doql.runtime.resolve_doql_context_path → src.env2llm.layout.resolve_registry_path
  src.env2llm.doql.runtime.load_doql_inline_from_env → src.env2llm.doql.runtime.resolve_doql_context_path
  src.env2llm.doql.runtime.load_doql_inline_from_env → src.env2llm.doql.runtime.context_inline_payload
  src.env2llm.doql.runtime.load_doql_inline_from_env → src.env2llm.doql.parse.load_doql_context
  src.env2llm.doql.runtime.merge_inline_context → src.env2llm.doql.runtime._inline_data_key
  src.env2llm.doql.runtime.merge_inline_context → src.env2llm.doql.runtime._add_short_inline_alias
  src.env2llm.doql.runtime.merge_inline_context → src.env2llm.doql.runtime._apply_conversation_flag
  src.env2llm.doql.runtime.autofill_entities → src.env2llm.doql.runtime._split_missing_ref
  src.env2llm.doql.runtime.autofill_entities → src.env2llm.doql.runtime._autofill_value
  src.env2llm.doql.runtime.autofill_entities → src.env2llm.doql.runtime._needs_field
  src.env2llm.doql.runtime._split_missing_ref → src.env2llm.doql.runtime._canonical_field
  src.env2llm.doql.runtime._autofill_value → src.env2llm.doql.runtime._value_from_data
  src.env2llm.doql.runtime._autofill_value → src.env2llm.doql.runtime._value_from_artifacts
  src.env2llm.doql.runtime._autofill_value → src.env2llm.doql.runtime._candidate_data_keys
  src.env2llm.doql.render.write_doql_context → src.env2llm.doql.render.render_doql_context
  src.env2llm.doql.context_blocks.render_context_environment → src.env2llm.render.doql.helpers.esc_str
  src.env2llm.doql.context_blocks.render_context_data → src.env2llm.render.doql.helpers.data_value_line
  src.env2llm.doql.context_blocks.render_context_resources → src.env2llm.render.doql.helpers.esc_str
  src.env2llm.doql.context_blocks.render_context_resources → src.env2llm.render.doql.helpers.join_csv
  src.env2llm.doql.context_blocks.render_context_access → src.env2llm.render.doql.helpers.join_csv
  src.env2llm.doql.context_blocks.render_context_capabilities → src.env2llm.render.doql.helpers.join_csv
  src.env2llm.doql.context_blocks.render_context_workflow_history → src.env2llm.render.doql.helpers.join_csv
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/env2llm
# generated in 0.08s
# nodes: 149 | edges: 156 | modules: 23
# CC̄=4.8

HUBS[20]:
  src.env2llm.render.doql.render.render_system_map_doql
    CC=1  in:2  out:37  total:39
  src.env2llm.runtimes.build_runtimes_for_example
    CC=18  in:1  out:35  total:36
  src.env2llm.doql.parse.load_platform_map
    CC=18  in:1  out:32  total:33
  src.env2llm.doql.parse.collect_task_context
    CC=19  in:1  out:32  total:33
  src.env2llm.bridge.task_context_to_system_map
    CC=25  in:3  out:30  total:33
  src.env2llm.doql.parse.enrich_task_context_from_client
    CC=19  in:1  out:29  total:30
  src.env2llm.doql.render.render_doql_context
    CC=1  in:1  out:29  total:30
  src.env2llm.bootstrap.ensure_environment_map
    CC=9  in:2  out:24  total:26
  src.env2llm.policy.process.process_policy_from_profile_block
    CC=5  in:1  out:23  total:24
  src.env2llm.render.doql.helpers.join_csv
    CC=1  in:23  out:1  total:24
  src.env2llm.doql.parse._parse_runtime_body
    CC=1  in:1  out:21  total:22
  src.env2llm.layout.write_turn_snapshot
    CC=4  in:0  out:21  total:21
  src.env2llm.generate.build_introspection_payload
    CC=11  in:1  out:20  total:21
  src.env2llm.doql.parse._parse_command_body
    CC=1  in:1  out:19  total:20
  src.env2llm.doql.parse.load_commands_from_services_yaml
    CC=14  in:1  out:19  total:20
  src.env2llm.doql.runtime.context_inline_payload
    CC=14  in:1  out:18  total:19
  src.env2llm.doql.parse._append_collection_blocks
    CC=12  in:1  out:18  total:19
  src.env2llm.registry.refresh_doql_registry
    CC=10  in:1  out:17  total:18
  src.env2llm.layout._force_remove_path
    CC=7  in:1  out:15  total:16
  src.env2llm.generate.generate_system_map
    CC=8  in:1  out:15  total:16

MODULES:
  src.env2llm._runtime_health  [1 funcs]
    runtime_id_for_intent  CC=5  out:2
  src.env2llm.bootstrap  [3 funcs]
    ensure_doql_registry  CC=1  out:1
    ensure_environment_map  CC=9  out:24
    project_artifact_root  CC=1  out:2
  src.env2llm.bridge  [3 funcs]
    _command_to_ir  CC=12  out:10
    doql_file_to_system_map  CC=1  out:3
    task_context_to_system_map  CC=25  out:30
  src.env2llm.cli  [2 funcs]
    build_parser  CC=1  out:7
    main  CC=1  out:6
  src.env2llm.doql.context_blocks  [9 funcs]
    render_context_access  CC=4  out:8
    render_context_capabilities  CC=2  out:1
    render_context_conversation  CC=3  out:3
    render_context_data  CC=2  out:4
    render_context_environment  CC=3  out:5
    render_context_paths  CC=5  out:5
    render_context_process_access  CC=7  out:6
    render_context_resources  CC=5  out:9
    render_context_workflow_history  CC=6  out:9
  src.env2llm.doql.models  [1 funcs]
    runtime_for  CC=6  out:3
  src.env2llm.doql.parse  [24 funcs]
    _append_collection_blocks  CC=12  out:18
    _apply_capabilities_block  CC=5  out:7
    _apply_context_block  CC=10  out:10
    _apply_context_metadata  CC=3  out:4
    _apply_conversation_block  CC=1  out:10
    _apply_paths_block  CC=3  out:4
    _apply_process_access_block  CC=4  out:5
    _apply_process_block  CC=9  out:12
    _command_transport  CC=3  out:2
    _parse_access_body  CC=1  out:12
  src.env2llm.doql.render  [2 funcs]
    render_doql_context  CC=1  out:29
    write_doql_context  CC=1  out:4
  src.env2llm.doql.runtime  [15 funcs]
    _add_short_inline_alias  CC=5  out:5
    _apply_conversation_flag  CC=6  out:5
    _autofill_value  CC=2  out:3
    _candidate_data_keys  CC=1  out:0
    _canonical_field  CC=1  out:2
    _inline_data_key  CC=1  out:1
    _needs_field  CC=1  out:1
    _split_missing_ref  CC=4  out:4
    _value_from_artifacts  CC=6  out:0
    _value_from_data  CC=4  out:0
  src.env2llm.env  [3 funcs]
    collect_environment  CC=13  out:13
    mask_secret  CC=3  out:1
    merge_environment  CC=3  out:3
  src.env2llm.formats  [3 funcs]
    default_output_name  CC=2  out:1
    normalize_format  CC=2  out:4
    render_format  CC=2  out:6
  src.env2llm.formats.doql_less  [1 funcs]
    render_doql_less  CC=1  out:1
  src.env2llm.generate  [4 funcs]
    _bootstrap_system_map  CC=2  out:3
    _parse_llm_json  CC=5  out:8
    build_introspection_payload  CC=11  out:20
    generate_system_map  CC=8  out:15
  src.env2llm.layout  [13 funcs]
    _chmod_writable  CC=2  out:1
    _force_remove_path  CC=7  out:15
    artifact_root  CC=1  out:2
    clean_all_example_artifacts  CC=5  out:6
    clean_artifact_root  CC=9  out:9
    current_run_id  CC=2  out:4
    ensure_layout  CC=1  out:6
    resolve_registry_path  CC=9  out:11
    run_dir  CC=2  out:4
    write_last_run_report  CC=1  out:6
  src.env2llm.policy.invoice  [3 funcs]
    apply_invoice_context  CC=3  out:8
    apply_invoice_policies  CC=5  out:6
    is_invoice_example  CC=2  out:1
  src.env2llm.policy.process  [15 funcs]
    _apply_autonomous_policy  CC=5  out:4
    _apply_llm_policy  CC=4  out:3
    _apply_nlp_policy  CC=5  out:4
    _as_list  CC=8  out:9
    _deep_merge_process  CC=5  out:7
    _intract_flags  CC=2  out:4
    _load_nlp2dsl_payload  CC=12  out:12
    _merge_access  CC=5  out:10
    _merge_conversation_from_profile  CC=5  out:4
    _merge_paths  CC=4  out:8
  src.env2llm.policy.validations  [6 funcs]
    _parse_profile_validation_by_code  CC=4  out:8
    _parse_profile_validation_by_type  CC=5  out:9
    _parse_profile_validation_shorthand  CC=10  out:10
    apply_profile_validations  CC=3  out:2
    parse_profile_validation  CC=5  out:4
    parse_profile_validations  CC=4  out:2
  src.env2llm.registry  [11 funcs]
    _execution_steps  CC=4  out:3
    _merge_execution_header  CC=1  out:5
    _merge_execution_step  CC=4  out:6
    _merge_generate_invoice_output  CC=3  out:2
    _merge_send_invoice_output  CC=3  out:3
    _merge_workflow_id  CC=3  out:3
    _step_output  CC=4  out:3
    merge_execution_observation  CC=2  out:6
    merge_registry_observations  CC=11  out:10
    refresh_doql_registry  CC=10  out:17
  src.env2llm.render.doql.blocks  [14 funcs]
    render_access_block  CC=4  out:8
    render_capabilities_block  CC=2  out:1
    render_conversation_block  CC=3  out:7
    render_data_block  CC=3  out:4
    render_deploy_block  CC=3  out:3
    render_environment_block  CC=2  out:5
    render_generated_services_block  CC=6  out:10
    render_paths_block  CC=5  out:5
    render_process_access_block  CC=7  out:6
    render_process_block  CC=3  out:4
  src.env2llm.render.doql.helpers  [7 funcs]
    bool_lit  CC=2  out:0
    data_value_line  CC=3  out:4
    esc_str  CC=1  out:1
    esc_str_full  CC=1  out:2
    history_value_line  CC=4  out:4
    join_csv  CC=1  out:1
    process_field_line  CC=3  out:3
  src.env2llm.render.doql.render  [1 funcs]
    render_system_map_doql  CC=1  out:37
  src.env2llm.runtimes  [4 funcs]
    _repo_root_from_example  CC=2  out:0
    build_runtimes_for_example  CC=18  out:35
    load_example_profile  CC=7  out:7
    resolve_command_runtime  CC=7  out:3
  src.env2llm.system_map_models  [4 funcs]
    _annotation_for_field  CC=11  out:3
    build_command_registry  CC=2  out:1
    command_input_model  CC=4  out:5
    validate_config_against_map  CC=2  out:5

EDGES:
  src.env2llm.env.collect_environment → src.env2llm.env.mask_secret
  src.env2llm.formats.render_format → src.env2llm.formats.normalize_format
  src.env2llm.formats.default_output_name → src.env2llm.formats.normalize_format
  src.env2llm.formats.doql_less.render_doql_less → src.env2llm.render.doql.render.render_system_map_doql
  src.env2llm.policy.process.load_platform_process_defaults → src.env2llm.policy.process._load_nlp2dsl_payload
  src.env2llm.policy.process._merge_access → src.env2llm.policy.process._as_list
  src.env2llm.policy.process._merge_paths → src.env2llm.policy.process._as_list
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._apply_nlp_policy
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._apply_autonomous_policy
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._apply_llm_policy
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._intract_flags
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._merge_access
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._merge_paths
  src.env2llm.policy.process.process_policy_from_profile_block → src.env2llm.policy.process._process_policy_from_parts
  src.env2llm.policy.process.merge_process_config → src.env2llm.policy.process.load_platform_process_defaults
  src.env2llm.policy.process.merge_process_config → src.env2llm.policy.process._deep_merge_process
  src.env2llm.policy.process.apply_process_policies → src.env2llm.policy.process.merge_process_config
  src.env2llm.policy.process.apply_process_policies → src.env2llm.policy.validations.apply_profile_validations
  src.env2llm.policy.process.apply_process_policies → src.env2llm.runtimes.load_example_profile
  src.env2llm.policy.process.apply_process_policies → src.env2llm.policy.process.process_policy_from_profile_block
  src.env2llm.policy.process.apply_process_policies → src.env2llm.policy.process._merge_conversation_from_profile
  src.env2llm.policy.validations.parse_profile_validation → src.env2llm.policy.validations._parse_profile_validation_shorthand
  src.env2llm.policy.validations.parse_profile_validation → src.env2llm.policy.validations._parse_profile_validation_by_code
  src.env2llm.policy.validations.parse_profile_validation → src.env2llm.policy.validations._parse_profile_validation_by_type
  src.env2llm.policy.validations.parse_profile_validations → src.env2llm.policy.validations.parse_profile_validation
  src.env2llm.policy.validations.apply_profile_validations → src.env2llm.policy.validations.parse_profile_validations
  src.env2llm.policy.invoice.apply_invoice_policies → src.env2llm.policy.invoice.is_invoice_example
  src.env2llm.policy.invoice.apply_invoice_context → src.env2llm.policy.invoice.is_invoice_example
  src.env2llm.doql.runtime.resolve_doql_context_path → src.env2llm.layout.resolve_registry_path
  src.env2llm.doql.runtime.load_doql_inline_from_env → src.env2llm.doql.runtime.resolve_doql_context_path
  src.env2llm.doql.runtime.load_doql_inline_from_env → src.env2llm.doql.runtime.context_inline_payload
  src.env2llm.doql.runtime.load_doql_inline_from_env → src.env2llm.doql.parse.load_doql_context
  src.env2llm.doql.runtime.merge_inline_context → src.env2llm.doql.runtime._inline_data_key
  src.env2llm.doql.runtime.merge_inline_context → src.env2llm.doql.runtime._add_short_inline_alias
  src.env2llm.doql.runtime.merge_inline_context → src.env2llm.doql.runtime._apply_conversation_flag
  src.env2llm.doql.runtime.autofill_entities → src.env2llm.doql.runtime._split_missing_ref
  src.env2llm.doql.runtime.autofill_entities → src.env2llm.doql.runtime._autofill_value
  src.env2llm.doql.runtime.autofill_entities → src.env2llm.doql.runtime._needs_field
  src.env2llm.doql.runtime._split_missing_ref → src.env2llm.doql.runtime._canonical_field
  src.env2llm.doql.runtime._autofill_value → src.env2llm.doql.runtime._value_from_data
  src.env2llm.doql.runtime._autofill_value → src.env2llm.doql.runtime._value_from_artifacts
  src.env2llm.doql.runtime._autofill_value → src.env2llm.doql.runtime._candidate_data_keys
  src.env2llm.doql.render.write_doql_context → src.env2llm.doql.render.render_doql_context
  src.env2llm.doql.context_blocks.render_context_environment → src.env2llm.render.doql.helpers.esc_str
  src.env2llm.doql.context_blocks.render_context_data → src.env2llm.render.doql.helpers.data_value_line
  src.env2llm.doql.context_blocks.render_context_resources → src.env2llm.render.doql.helpers.esc_str
  src.env2llm.doql.context_blocks.render_context_resources → src.env2llm.render.doql.helpers.join_csv
  src.env2llm.doql.context_blocks.render_context_access → src.env2llm.render.doql.helpers.join_csv
  src.env2llm.doql.context_blocks.render_context_capabilities → src.env2llm.render.doql.helpers.join_csv
  src.env2llm.doql.context_blocks.render_context_workflow_history → src.env2llm.render.doql.helpers.join_csv
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 46f 4838L | python:41,shell:2,yaml:1,toml:1 | 2026-06-06
# generated in 0.01s
# CC̅=4.8 | critical:7/185 | dups:0 | cycles:0

HEALTH[7]:
  🟡 CC    render_markdown CC=22 (limit:15)
  🟡 CC    render_context_process CC=18 (limit:15)
  🟡 CC    build_runtimes_for_example CC=18 (limit:15)
  🟡 CC    load_platform_map CC=18 (limit:15)
  🟡 CC    enrich_task_context_from_client CC=19 (limit:15)
  🟡 CC    collect_task_context CC=19 (limit:15)
  🟡 CC    task_context_to_system_map CC=25 (limit:15)

REFACTOR[1]:
  1. split 7 high-CC methods  (CC>15)

PIPELINES[30]:
  [1] Src [render_markdown]: render_markdown
      PURITY: 100% pure
  [2] Src [render_yaml]: render_yaml
      PURITY: 100% pure
  [3] Src [render_json]: render_json
      PURITY: 100% pure
  [4] Src [render_doql_less]: render_doql_less → render_system_map_doql → render_header
      PURITY: 100% pure
  [5] Src [effective_nlp_parser_mode]: effective_nlp_parser_mode
      PURITY: 100% pure
  [6] Src [process_scope_denied]: process_scope_denied
      PURITY: 100% pure
  [7] Src [load_doql_inline_from_env]: load_doql_inline_from_env → resolve_doql_context_path → resolve_registry_path → artifact_root
      PURITY: 100% pure
  [8] Src [merge_inline_context]: merge_inline_context → _inline_data_key
      PURITY: 100% pure
  [9] Src [autofill_entities]: autofill_entities → _split_missing_ref → _canonical_field
      PURITY: 100% pure
  [10] Src [write_doql_context]: write_doql_context → render_doql_context → render_context_header
      PURITY: 100% pure
  [11] Src [clean_all_example_artifacts]: clean_all_example_artifacts → clean_artifact_root → artifact_root
      PURITY: 100% pure
  [12] Src [example_fixtures_dir]: example_fixtures_dir
      PURITY: 100% pure
  [13] Src [write_turn_snapshot]: write_turn_snapshot → run_dir → current_run_id
      PURITY: 100% pure
  [14] Src [write_reflection_snapshot]: write_reflection_snapshot → run_dir → current_run_id
      PURITY: 100% pure
  [15] Src [write_last_run_report]: write_last_run_report → ensure_layout
      PURITY: 100% pure
  [16] Src [main]: main → normalize_format
      PURITY: 100% pure
  [17] Src [build_command_registry]: build_command_registry → command_input_model → _annotation_for_field
      PURITY: 100% pure
  [18] Src [validate_config_against_map]: validate_config_against_map → command_input_model → _annotation_for_field
      PURITY: 100% pure
  [19] Src [_litellm_complete]: _litellm_complete
      PURITY: 100% pure
  [20] Src [example_profile]: example_profile
      PURITY: 100% pure
  [21] Src [platform_config]: platform_config
      PURITY: 100% pure
  [22] Src [services_snapshot]: services_snapshot
      PURITY: 100% pure
  [23] Src [runtime_for_command]: runtime_for_command
      PURITY: 100% pure
  [24] Src [validate_step_config]: validate_step_config
      PURITY: 100% pure
  [25] Src [refresh_doql_registry_from_state]: refresh_doql_registry_from_state → refresh_doql_registry → load_doql_context → _apply_context_metadata
      PURITY: 100% pure
  [26] Src [doql_file_to_system_map]: doql_file_to_system_map → load_doql_context → _apply_context_metadata
      PURITY: 100% pure
  [27] Src [ensure_doql_registry]: ensure_doql_registry → ensure_environment_map → project_artifact_root
      PURITY: 100% pure
  [28] Src [entity_values]: entity_values
      PURITY: 100% pure
  [29] Src [required_fields_for]: required_fields_for
      PURITY: 100% pure
  [30] Src [runtime_for]: runtime_for → runtime_id_for_intent
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.8    ←in:0  →out:0
  │ !! parse                      482L  0C   25m  CC=19     ←5
  │ process                    337L  0C   20m  CC=12     ←2
  │ blocks                     300L  0C   18m  CC=9      ←1
  │ ir                         274L  17C    4m  CC=7      ←0
  │ layout                     266L  0C   14m  CC=9      ←3
  │ !! context_blocks             234L  0C   14m  CC=18     ←1
  │ registry                   230L  0C   12m  CC=11     ←1
  │ !! bridge                     225L  0C    5m  CC=25     ←2
  │ runtime                    206L  0C   15m  CC=14     ←0
  │ generate                   202L  0C    5m  CC=11     ←1
  │ !! runtimes                   174L  0C    4m  CC=18     ←3
  │ models                     134L  7C    4m  CC=6      ←0
  │ bootstrap                  102L  0C    3m  CC=9      ←1
  │ validations                 73L  0C    6m  CC=10     ←1
  │ env                         72L  0C    3m  CC=13     ←1
  │ sources                     67L  2C    6m  CC=12     ←0
  │ __init__                    59L  0C    3m  CC=2      ←2
  │ cli                         57L  0C    2m  CC=1      ←0
  │ !! markdown                    52L  0C    1m  CC=22     ←0
  │ invoice                     52L  0C    3m  CC=5      ←3
  │ render                      49L  0C    2m  CC=1      ←0
  │ render                      48L  0C    1m  CC=1      ←2
  │ system_map_models           48L  0C    4m  CC=11     ←0
  │ __init__                    48L  0C    0m  CC=0.0    ←0
  │ helpers                     45L  0C    7m  CC=4      ←2
  │ __init__                    33L  0C    0m  CC=0.0    ←0
  │ _runtime_health             29L  0C    1m  CC=5      ←1
  │ doql_context                26L  0C    0m  CC=0.0    ←0
  │ yaml_fmt                    13L  0C    1m  CC=1      ←0
  │ json_fmt                    13L  0C    1m  CC=1      ←0
  │ doql_less                   11L  0C    1m  CC=1      ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __main__                     3L  0C    0m  CC=0.0    ←0
  │ system_map_generator         1L  0C    0m  CC=0.0    ←0
  │ system_map_render            1L  0C    0m  CC=0.0    ←0
  │ artifact_layout              1L  0C    0m  CC=0.0    ←0
  │ system_map_runtimes          1L  0C    0m  CC=0.0    ←0
  │ system_map_bridge            1L  0C    0m  CC=0.0    ←0
  │ system_map_ir                1L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ Makefile                   222L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              63L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 0f 0L | 2026-06-06

SUMMARY:
  files_scanned: 0
  total_lines:   0
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       2346
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 185 func | 28f | 2026-06-06
# generated in 0.00s

NEXT[7] (ranked by impact):
  [1] !! SPLIT-FUNC      task_context_to_system_map  CC=25  fan=20
      WHY: CC=25 exceeds 15
      EFFORT: ~1h  IMPACT: 500

  [2] !  SPLIT-FUNC      collect_task_context  CC=19  fan=26
      WHY: CC=19 exceeds 15
      EFFORT: ~1h  IMPACT: 494

  [3] !  SPLIT-FUNC      load_platform_map  CC=18  fan=14
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 252

  [4] !  SPLIT-FUNC      build_runtimes_for_example  CC=18  fan=13
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 234

  [5] !  SPLIT-FUNC      enrich_task_context_from_client  CC=19  fan=12
      WHY: CC=19 exceeds 15
      EFFORT: ~1h  IMPACT: 228

  [6] !  SPLIT-FUNC      render_markdown  CC=22  fan=8
      WHY: CC=22 exceeds 15
      EFFORT: ~1h  IMPACT: 176

  [7] !! SPLIT           goal.yaml
      WHY: 511L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[1]:
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.8 → ≤3.4
  max-CC:      25 → ≤12
  god-modules: 1 → 0
  high-CC(≥15): 7 → ≤3
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  (first run — no previous data)
```

## Intent

Generate environment maps (services, artifacts, env vars) for LLM decision-making
