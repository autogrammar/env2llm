# env2llm

Generate environment maps (services, artifacts, env vars) for LLM decision-making

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `env2llm`
- **version**: `0.1.5`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(2), app.doql.less, goal.yaml, .env.example, project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: env2llm;
  version: 0.1.5;
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

## Interfaces

### CLI Entry Points

- `env2llm`
- `env2llm-serve`
- `env2llm-mcp`
- `env2llm-mqtt`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m env2llm
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m env2llm --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m env2llm --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m env2llm --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 68 assertions from pytest
ASSERT[68]{field, operator, expected}:
  worker.status, ==, "available"
  ctx.example_name, ==, "01-invoice"
  ctx.generated_at, ==, "2026-06-06T08:00:00+00:00"
  ctx.environment.NLP2DSL_BACKEND_URL, ==, "http://localhost:8010"
  ctx.data.send_invoice.amount, ==, 1500
  ctx.capabilities, ==, ["send_invoice"
  ctx.workflow_history, ==, {"count": 2
  ctx.process.mode, ==, "deterministic"
  ctx.process.nlp_parser, ==, "rules_first"
  ctx.process.nlp_confidence_min, ==, 0.75
  ctx.process.llm_reasoning, ==, "deep"
  ctx.process.llm_temperature, ==, 0.1
  ctx.process.autonomous_max_rounds, ==, 3
  ctx.process.ask_user, ==, "never"
  ctx.process.agent, ==, "user"
  ctx.process.allow_resource_areas, ==, ["files:project"]
  ctx.process.deny_resource_areas, ==, ["mullm:rag"
  ctx.process.paths_read, ==, ["fixtures/**"]
  ctx.process.paths_write, ==, ["generated/**"]
  ctx.artifacts[0].values.amount, ==, 1500
  ctx.commands[0].required, ==, ["amount"
  ctx.commands[0].runtime, ==, "executor:worker"
  ctx.resources[0].id, ==, "mullm:rag"
  ctx.access[0].effect, ==, "deny"
  ctx.runtimes[0].status, ==, "available"
  loaded.example_name, ==, "roundtrip"
  loaded.data.send_invoice.amount, ==, 99
  loaded.commands[0].name, ==, "send_invoice"
  loaded.runtimes[0].health, ==, "http://localhost:8004/health"
  len(ctx.validations), ==, 2
  ctx.validations[0].code, ==, "profile.dsl_action"
  ctx.validations[0].action, ==, "send_invoice"
  ctx.validations[1].code, ==, "profile.execution_completed"
  ctx.validations[1].status, ==, "completed"
  worker.status, ==, "available"
  ctx.example_name, ==, "01-invoice"
  ctx.generated_at, ==, "2026-06-06T08:00:00+00:00"
  ctx.environment.NLP2DSL_BACKEND_URL, ==, "http://localhost:8010"
  ctx.data.send_invoice.amount, ==, 1500
  ctx.capabilities, ==, ["send_invoice"
  ctx.workflow_history, ==, {"count": 2
  ctx.process.mode, ==, "deterministic"
  ctx.process.nlp_parser, ==, "rules_first"
  ctx.process.nlp_confidence_min, ==, 0.75
  ctx.process.llm_reasoning, ==, "deep"
  ctx.process.llm_temperature, ==, 0.1
  ctx.process.autonomous_max_rounds, ==, 3
  ctx.process.ask_user, ==, "never"
  ctx.process.agent, ==, "user"
  ctx.process.allow_resource_areas, ==, ["files:project"]
  ctx.process.deny_resource_areas, ==, ["mullm:rag"
  ctx.process.paths_read, ==, ["fixtures/**"]
  ctx.process.paths_write, ==, ["generated/**"]
  ctx.artifacts[0].values.amount, ==, 1500
  ctx.commands[0].required, ==, ["amount"
  ctx.commands[0].runtime, ==, "executor:worker"
  ctx.resources[0].id, ==, "mullm:rag"
  ctx.access[0].effect, ==, "deny"
  ctx.runtimes[0].status, ==, "available"
  loaded.example_name, ==, "roundtrip"
  loaded.data.send_invoice.amount, ==, 99
  loaded.commands[0].name, ==, "send_invoice"
  loaded.runtimes[0].health, ==, "http://localhost:8004/health"
  len(ctx.validations), ==, 2
  ctx.validations[0].code, ==, "profile.dsl_action"
  ctx.validations[0].action, ==, "send_invoice"
  ctx.validations[1].code, ==, "profile.execution_completed"
  ctx.validations[1].status, ==, "completed"
```

## Workflows

## Configuration

```yaml
project:
  name: env2llm
  version: 0.1.5
  env: local
```

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

## Deployment

```bash markpact:run
pip install env2llm

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`env2llm`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/cryptography/__init__.py:__version__`

## Makefile Targets

- `CYAN` — Colors
- `GREEN`
- `YELLOW`
- `RED`
- `RESET`
- `help`
- `install`
- `install-dev`
- `install-ai`
- `setup`
- `env`
- `run`
- `web`
- `shell`
- `plan`
- `execute`
- `examples`
- `run-intent` — Run with custom package file: make run-intent FILE=path/to/iterun.yaml
- `test`
- `test-shell`
- `test-web`
- `test-ai`
- `test-cov`
- `ollama-start`
- `ollama-pull`
- `ollama-models`
- `ollama-status`
- `lint`
- `format`
- `clean`
- `docker-clean`
- `docker-ps`
- `docker-stop`
- `dev`
- `new-intent`
- `show-config`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# env2llm | 67f 6616L | python:64,shell:2,less:1 | 2026-06-06
# stats: 232 func | 35 cls | 67 mod | CC̄=4.9 | critical:29 | cycles:0
# alerts[5]: CC test_load_doql_context_all_supported_blocks=34; CC task_context_to_system_map=25; CC render_markdown=22; CC enrich_task_context_from_client=19; CC collect_task_context=19
# hotspots[5]: collect_task_context fan=26; ensure_environment_map fan=22; render_system_map_doql fan=21; task_context_to_system_map fan=20; test_rest_server_health fan=20
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[67]:
  app.doql.less,231
  project.sh,59
  src/env2llm/__init__.py,44
  src/env2llm/__main__.py,4
  src/env2llm/_runtime_health.py,32
  src/env2llm/adapters/__init__.py,7
  src/env2llm/adapters/mcp.py,143
  src/env2llm/adapters/rest.py,107
  src/env2llm/artifact_layout.py,2
  src/env2llm/bootstrap.py,106
  src/env2llm/bridge.py,226
  src/env2llm/cli.py,64
  src/env2llm/doql/__init__.py,49
  src/env2llm/doql/context_blocks.py,235
  src/env2llm/doql/models.py,135
  src/env2llm/doql/parse.py,483
  src/env2llm/doql/render.py,50
  src/env2llm/doql/runtime.py,207
  src/env2llm/doql_context.py,27
  src/env2llm/env.py,73
  src/env2llm/formats/__init__.py,60
  src/env2llm/formats/doql_less.py,12
  src/env2llm/formats/json_fmt.py,14
  src/env2llm/formats/markdown.py,53
  src/env2llm/formats/yaml_fmt.py,14
  src/env2llm/generate.py,209
  src/env2llm/integrators/__init__.py,2
  src/env2llm/integrators/_service_factory.py,50
  src/env2llm/integrators/mcp_server.py,137
  src/env2llm/integrators/mqtt_bridge.py,146
  src/env2llm/integrators/rest_server.py,115
  src/env2llm/ir.py,316
  src/env2llm/layout.py,267
  src/env2llm/policy/__init__.py,5
  src/env2llm/policy/desktop.py,176
  src/env2llm/policy/invoice.py,53
  src/env2llm/policy/process.py,338
  src/env2llm/policy/validations.py,74
  src/env2llm/probes/__init__.py,6
  src/env2llm/probes/desktop.py,143
  src/env2llm/registry.py,231
  src/env2llm/render/__init__.py,4
  src/env2llm/render/doql/__init__.py,6
  src/env2llm/render/doql/blocks.py,341
  src/env2llm/render/doql/helpers.py,46
  src/env2llm/render/doql/render.py,51
  src/env2llm/runtimes.py,178
  src/env2llm/service/__init__.py,6
  src/env2llm/service/registry_service.py,166
  src/env2llm/sources.py,68
  src/env2llm/system_map_bridge.py,2
  src/env2llm/system_map_generator.py,2
  src/env2llm/system_map_ir.py,2
  src/env2llm/system_map_models.py,49
  src/env2llm/system_map_render.py,2
  src/env2llm/system_map_runtimes.py,2
  src/env2llm/transport/__init__.py,6
  src/env2llm/transport/mqtt.py,153
  tests/conftest.py,24
  tests/test_desktop_probe.py,69
  tests/test_doql_context.py,312
  tests/test_formats.py,24
  tests/test_integrators.py,91
  tests/test_mqtt.py,73
  tests/test_registry_service.py,92
  tests/test_system_map_ir.py,140
  tree.sh,2
D:
  src/env2llm/__init__.py:
  src/env2llm/__main__.py:
  src/env2llm/_runtime_health.py:
    e: runtime_id_for_intent
    runtime_id_for_intent(intent)
  src/env2llm/adapters/__init__.py:
  src/env2llm/adapters/mcp.py:
    e: _mcp_error,McpAdapter
    McpAdapter: __init__(1),call_tool(2)
    _mcp_error(message)
  src/env2llm/adapters/rest.py:
    e: RestAdapter
    RestAdapter: __init__(1),match_route(3),dispatch(1),handle_http(2)
  src/env2llm/artifact_layout.py:
  src/env2llm/bootstrap.py:
    e: project_artifact_root,ensure_environment_map,ensure_doql_registry
    project_artifact_root(project_dir)
    ensure_environment_map(project_dir)
    ensure_doql_registry(example_dir)
  src/env2llm/bridge.py:
    e: _mime_for_artifact,_process_from_ctx,task_context_to_system_map,_command_to_ir,doql_file_to_system_map
    _mime_for_artifact(art)
    _process_from_ctx(ctx)
    task_context_to_system_map(ctx)
    _command_to_ir(cmd)
    doql_file_to_system_map(path)
  src/env2llm/cli.py:
    e: build_parser,main
    build_parser()
    main(argv)
  src/env2llm/doql/__init__.py:
  src/env2llm/doql/context_blocks.py:
    e: render_context_header,render_context_environment,render_context_data,render_context_artifacts,render_context_commands,render_context_resources,render_context_access,render_context_runtimes,render_context_capabilities,render_context_workflow_history,render_context_process,render_context_process_access,render_context_paths,render_context_conversation
    render_context_header(ctx)
    render_context_environment(ctx)
    render_context_data(ctx)
    render_context_artifacts(ctx)
    render_context_commands(ctx)
    render_context_resources(ctx)
    render_context_access(ctx)
    render_context_runtimes(ctx)
    render_context_capabilities(ctx)
    render_context_workflow_history(ctx)
    render_context_process(ctx)
    render_context_process_access(ctx)
    render_context_paths(ctx)
    render_context_conversation(ctx)
  src/env2llm/doql/models.py:
    e: DoqlArtifact,DoqlRuntime,DoqlCommand,DoqlResource,DoqlAccess,DoqlProcessPolicy,DoqlTaskContext
    DoqlArtifact:
    DoqlRuntime:  # Execution environment (where command effects run).
    DoqlCommand:  # Schema kroku CMD — akcja workflow + wymagane pola + runtime 
    DoqlResource:
    DoqlAccess:
    DoqlProcessPolicy:
    DoqlTaskContext: entity_values(1),command(1),required_fields_for(1),runtime_for(1)
  src/env2llm/doql/parse.py:
    e: _parse_value,_parse_block_body,_split_csv,_parse_command_body,_parse_resource_body,_parse_access_body,_parse_runtime_body,_parse_validation_body,_parse_artifact_body,_apply_context_metadata,_apply_conversation_block,_apply_capabilities_block,_apply_process_block,_apply_process_access_block,_apply_paths_block,_apply_context_block,_append_collection_blocks,load_doql_context,_repo_root_from_example,_command_transport,load_platform_map,load_commands_from_services_yaml,enrich_task_context_from_client,parse_fixture_metadata,collect_task_context
    _parse_value(raw)
    _parse_block_body(body)
    _split_csv(raw)
    _parse_command_body(body)
    _parse_resource_body(body)
    _parse_access_body(body)
    _parse_runtime_body(body)
    _parse_validation_body(body)
    _parse_artifact_body(body)
    _apply_context_metadata(ctx;text)
    _apply_conversation_block(ctx;kv)
    _apply_capabilities_block(ctx;kv)
    _apply_process_block(ctx;kv)
    _apply_process_access_block(ctx;kv)
    _apply_paths_block(ctx;kv)
    _apply_context_block(ctx;block_type;kv)
    _append_collection_blocks(ctx;text)
    load_doql_context(path)
    _repo_root_from_example(example_dir)
    _command_transport(action)
    load_platform_map(repo_root)
    load_commands_from_services_yaml(path)
    enrich_task_context_from_client(ctx;client)
    parse_fixture_metadata(path)
    collect_task_context(example_dir)
  src/env2llm/doql/render.py:
    e: render_doql_context,write_doql_context
    render_doql_context(ctx)
    write_doql_context(path;ctx)
  src/env2llm/doql/runtime.py:
    e: resolve_doql_context_path,context_inline_payload,load_doql_inline_from_env,merge_inline_context,autofill_entities,_inline_data_key,_apply_conversation_flag,_add_short_inline_alias,_split_missing_ref,_canonical_field,_autofill_value,_candidate_data_keys,_value_from_data,_value_from_artifacts,_needs_field
    resolve_doql_context_path()
    context_inline_payload(ctx)
    load_doql_inline_from_env()
    merge_inline_context(ctx;inline)
    autofill_entities(entities;missing_refs;ctx)
    _inline_data_key(key)
    _apply_conversation_flag(ctx;flag;value)
    _add_short_inline_alias(merged_data;key;mapped;value)
    _split_missing_ref(ref;entities)
    _canonical_field(field)
    _autofill_value(action;field;ctx)
    _candidate_data_keys(action;field)
    _value_from_data(candidates;ctx)
    _value_from_artifacts(field;ctx)
    _needs_field(entities;field)
  src/env2llm/doql_context.py:
  src/env2llm/env.py:
    e: mask_secret,collect_environment,merge_environment
    mask_secret(value)
    collect_environment()
    merge_environment(base;override)
  src/env2llm/formats/__init__.py:
    e: normalize_format,render_format,default_output_name
    normalize_format(name)
    render_format(ir;fmt)
    default_output_name(fmt)
  src/env2llm/formats/doql_less.py:
    e: render_doql_less
    render_doql_less(ir;_ctx)
  src/env2llm/formats/json_fmt.py:
    e: render_json
    render_json(ir;_ctx)
  src/env2llm/formats/markdown.py:
    e: render_markdown
    render_markdown(ir;_ctx)
  src/env2llm/formats/yaml_fmt.py:
    e: render_yaml
    render_yaml(ir;_ctx)
  src/env2llm/generate.py:
    e: build_introspection_payload,_bootstrap_system_map,_litellm_complete,_parse_llm_json,generate_system_map
    build_introspection_payload(example_dir)
    _bootstrap_system_map(example_dir)
    _litellm_complete(system;user)
    _parse_llm_json(raw)
    generate_system_map(example_dir)
  src/env2llm/integrators/__init__.py:
  src/env2llm/integrators/_service_factory.py:
    e: build_registry_service,attach_mqtt_refresh_listener
    build_registry_service(project_dir)
    attach_mqtt_refresh_listener(service)
  src/env2llm/integrators/mcp_server.py:
    e: _jsonrpc_response,_jsonrpc_error,_write_json,_log,handle_message,run_stdio,main
    _jsonrpc_response(req_id;result)
    _jsonrpc_error(req_id;code;message;data)
    _write_json(payload)
    _log(message)
    handle_message(msg)
    run_stdio()
    main(argv)
  src/env2llm/integrators/mqtt_bridge.py:
    e: run_bridge,publish_once,main
    run_bridge()
    publish_once()
    main(argv)
  src/env2llm/integrators/rest_server.py:
    e: run_server,main,Env2LLMRequestHandler
    Env2LLMRequestHandler: log_message(1),_read_body(0),_send(2),_handle(1),do_GET(0),do_POST(0)
    run_server()
    main(argv)
  src/env2llm/ir.py:
    e: MimeTypeSpec,RuntimeSpecIR,ProtocolSpec,FieldSpec,CommandSchemaIR,ResourceSpecIR,AccessGrantIR,ArtifactSpecIR,ConversationPolicyIR,ProcessAccessScopeIR,ProcessPathsIR,ProcessPolicyIR,ScheduleSpecIR,GeneratedServiceIR,DeploySpecIR,ProfileValidationIR,DesktopWindowIR,DesktopDisplayIR,DesktopProbeIR,SystemMapIR
    MimeTypeSpec:  # Artifact or payload MIME + optional Pydantic schema referenc
    RuntimeSpecIR:  # Execution environment available to the example (where effect
    ProtocolSpec:  # Transport / execution protocol for a command step.
    FieldSpec:  # Single command parameter with optional MIME/schema.
    CommandSchemaIR: required_names(0),optional_names(0)  # CMD layer schema — one workflow action / service call.
    ResourceSpecIR:
    AccessGrantIR:
    ArtifactSpecIR:
    ConversationPolicyIR:
    ProcessAccessScopeIR:  # Process-level ACL scope (subset of platform grants).
    ProcessPathsIR:  # Filesystem paths available to the process agent.
    ProcessPolicyIR:  # Per-example process behaviour — workflow style, NLP/LLM, Int
    ScheduleSpecIR:  # Cron / trigger schedule bound to a workflow or NL task.
    GeneratedServiceIR:  # Optional service stub emitted under .nlp2dsl/generated/servi
    DeploySpecIR:  # Docker Compose deployment descriptor for transparent process
    ProfileValidationIR:  # Example-profile acceptance check — maps example-profiles.yam
    DesktopWindowIR:  # Single top-level window from a desktop probe (wmctrl/xdotool
    DesktopDisplayIR:  # Display geometry when available from the probe tools.
    DesktopProbeIR:  # Live GUI session snapshot for agents (GNOME/X11/Wayland).
    SystemMapIR: command(1),runtime(1),runtime_for_command(1),validate_step_config(2)  # env2llm.system_map.v1 — canonical map of available system ca
  src/env2llm/layout.py:
    e: artifact_root,_chmod_writable,_force_remove_path,clean_artifact_root,clean_all_example_artifacts,example_fixtures_dir,ensure_layout,resolve_registry_path,write_registry,current_run_id,run_dir,write_turn_snapshot,write_reflection_snapshot,write_last_run_report
    artifact_root(example_dir)
    _chmod_writable(path)
    _force_remove_path(path)
    clean_artifact_root(example_dir)
    clean_all_example_artifacts(examples_dir)
    example_fixtures_dir(example_dir)
    ensure_layout(root)
    resolve_registry_path()
    write_registry(root;content)
    current_run_id(root)
    run_dir(root;run_id)
    write_turn_snapshot(artifact_root_path)
    write_reflection_snapshot(artifact_root_path)
    write_last_run_report(root;payload)
  src/env2llm/policy/__init__.py:
  src/env2llm/policy/desktop.py:
    e: desktop_probe_enabled,_ensure_desktop_runtime,_ensure_desktop_resource,_ensure_desktop_commands,_ensure_desktop_access,_mirror_desktop_summary,apply_desktop_probe
    desktop_probe_enabled()
    _ensure_desktop_runtime(ir)
    _ensure_desktop_resource(ir)
    _ensure_desktop_commands(ir)
    _ensure_desktop_access(ir)
    _mirror_desktop_summary(ir)
    apply_desktop_probe(ir)
  src/env2llm/policy/invoice.py:
    e: is_invoice_example,apply_invoice_policies,apply_invoice_context
    is_invoice_example(example_id)
    apply_invoice_policies(ir)
    apply_invoice_context(ctx)
  src/env2llm/policy/process.py:
    e: _as_list,_deep_merge_process,_load_nlp2dsl_payload,load_platform_process_defaults,_merge_access,_merge_paths,process_policy_from_profile_block,_mapping_block,_apply_nlp_policy,_apply_autonomous_policy,_apply_llm_policy,_intract_flags,_normalized_mode,_process_policy_from_parts,_merge_conversation_from_profile,merge_process_config,apply_process_policies,effective_nlp_parser_mode,process_policy_to_doql_dict,process_scope_denied
    _as_list(raw)
    _deep_merge_process(base;override)
    _load_nlp2dsl_payload(repo_root)
    load_platform_process_defaults(repo_root)
    _merge_access(raw)
    _merge_paths(raw)
    process_policy_from_profile_block(raw)
    _mapping_block(raw;key)
    _apply_nlp_policy(preset;nlp)
    _apply_autonomous_policy(preset;autonomous)
    _apply_llm_policy(preset;llm)
    _intract_flags(intract)
    _normalized_mode(mode)
    _process_policy_from_parts()
    _merge_conversation_from_profile(ir;raw)
    merge_process_config()
    apply_process_policies(ir)
    effective_nlp_parser_mode(process)
    process_policy_to_doql_dict(process)
    process_scope_denied(process)
  src/env2llm/policy/validations.py:
    e: _parse_profile_validation_by_code,_parse_profile_validation_by_type,_parse_profile_validation_shorthand,parse_profile_validation,parse_profile_validations,apply_profile_validations
    _parse_profile_validation_by_code(raw)
    _parse_profile_validation_by_type(raw)
    _parse_profile_validation_shorthand(raw)
    parse_profile_validation(raw)
    parse_profile_validations(raw_list)
    apply_profile_validations(ir;profile)
  src/env2llm/probes/__init__.py:
  src/env2llm/probes/desktop.py:
    e: _run_text,_is_browser_title,parse_wmctrl_listing,_probe_display_geometry,_probe_active_window_id,collect_desktop_probe
    _run_text(argv)
    _is_browser_title(title)
    parse_wmctrl_listing(text)
    _probe_display_geometry()
    _probe_active_window_id()
    collect_desktop_probe()
  src/env2llm/registry.py:
    e: entities_to_data,merge_execution_observation,_merge_execution_header,_execution_steps,_merge_execution_step,_step_output,_merge_send_invoice_output,_merge_generate_invoice_output,_merge_workflow_id,merge_registry_observations,refresh_doql_registry,refresh_doql_registry_from_state
    entities_to_data(intent;entities)
    merge_execution_observation(ir_data;workflow_history;execution)
    _merge_execution_header(history;execution)
    _execution_steps(execution)
    _merge_execution_step(data;history;step)
    _step_output(step)
    _merge_send_invoice_output(data;history;output)
    _merge_generate_invoice_output(data;output)
    _merge_workflow_id(history;execution)
    merge_registry_observations(ir;path)
    refresh_doql_registry(path)
    refresh_doql_registry_from_state(path)
  src/env2llm/render/__init__.py:
  src/env2llm/render/doql/__init__.py:
  src/env2llm/render/doql/blocks.py:
    e: render_header,render_environment_block,render_data_block,render_artifacts_block,render_desktop_block,render_runtimes_block,render_commands_block,render_resources_block,render_access_block,render_capabilities_block,render_workflow_history_block,render_conversation_block,render_process_block,render_process_access_block,render_paths_block,render_schedules_block,render_deploy_block,render_generated_services_block,render_validations_block
    render_header(ir)
    render_environment_block(ir)
    render_data_block(ir)
    render_artifacts_block(ir)
    render_desktop_block(ir)
    render_runtimes_block(ir)
    render_commands_block(ir)
    render_resources_block(ir)
    render_access_block(ir)
    render_capabilities_block(ir)
    render_workflow_history_block(ir)
    render_conversation_block(ir)
    render_process_block(ir)
    render_process_access_block(ir)
    render_paths_block(ir)
    render_schedules_block(ir)
    render_deploy_block(ir)
    render_generated_services_block(ir)
    render_validations_block(ir)
  src/env2llm/render/doql/helpers.py:
    e: esc_str,esc_str_full,bool_lit,join_csv,data_value_line,history_value_line,process_field_line
    esc_str(value)
    esc_str_full(value)
    bool_lit(value)
    join_csv(items)
    data_value_line(key;val)
    history_value_line(key;val)
    process_field_line(key;val)
  src/env2llm/render/doql/render.py:
    e: render_system_map_doql
    render_system_map_doql(ir)
  src/env2llm/runtimes.py:
    e: _repo_root_from_example,load_example_profile,resolve_command_runtime,build_runtimes_for_example
    _repo_root_from_example(example_dir)
    load_example_profile(example_id;repo_root)
    resolve_command_runtime(action)
    build_runtimes_for_example(example_id)
  src/env2llm/service/__init__.py:
  src/env2llm/service/registry_service.py:
    e: RegistryService
    RegistryService: __post_init__(0),registry_path(0),load(0),refresh(0),get_ir(0),render(1),to_dict(0),desktop_payload(0),commands_payload(0),uris_payload(0),mqtt_status(0),_generate_ir(0),_publish_mqtt(0)  # In-memory view over env2llm ``SystemMapIR`` with optional MQ
  src/env2llm/sources.py:
    e: EnvironmentSources,DefaultEnvironmentSources
    EnvironmentSources: example_profile(2),platform_config(1),services_snapshot(1)
    DefaultEnvironmentSources: example_profile(2),platform_config(1),services_snapshot(1)  # Read nlp2dsl-style YAML layouts (example-profiles.yaml, nlp2
  src/env2llm/system_map_bridge.py:
  src/env2llm/system_map_generator.py:
  src/env2llm/system_map_ir.py:
  src/env2llm/system_map_models.py:
    e: _annotation_for_field,command_input_model,build_command_registry,validate_config_against_map
    _annotation_for_field(field)
    command_input_model(cmd)
    build_command_registry(ir)
    validate_config_against_map(ir;action;config)
  src/env2llm/system_map_render.py:
  src/env2llm/system_map_runtimes.py:
  src/env2llm/transport/__init__.py:
  src/env2llm/transport/mqtt.py:
    e: mqtt_available,mqtt_missing_message,mqtt_enabled,MqttRegistryBridge
    MqttRegistryBridge: __init__(0),topic(1),connect(0),disconnect(0),publish_registry(2),publish_desktop(2),publish_event(3),subscribe_refresh(1),_publish(2),_on_connect(5),_on_message(3)  # Publish registry snapshots and listen for remote refresh com
    mqtt_available()
    mqtt_missing_message()
    mqtt_enabled()
  tests/conftest.py:
    e: nlp2dsl_root,invoice_example_dir
    nlp2dsl_root()
    invoice_example_dir()
  tests/test_desktop_probe.py:
    e: test_parse_wmctrl_listing_detects_geometry_and_browser,test_apply_desktop_probe_adds_runtime_commands_and_doql_block
    test_parse_wmctrl_listing_detects_geometry_and_browser()
    test_apply_desktop_probe_adds_runtime_commands_and_doql_block(monkeypatch)
  tests/test_doql_context.py:
    e: test_load_doql_context_all_supported_blocks,test_doql_roundtrip_preserves_core_fields,test_autofill_entities_from_data_and_aliases,test_autofill_entities_from_artifact_values,test_autofill_entities_skips_optional_attachment_path,test_merge_inline_context_promotes_short_aliases,test_autofill_entities_disabled_returns_original_object,test_load_doql_context_parses_validations,test_validations_doql_roundtrip_via_system_map
    test_load_doql_context_all_supported_blocks(tmp_path)
    test_doql_roundtrip_preserves_core_fields(tmp_path)
    test_autofill_entities_from_data_and_aliases()
    test_autofill_entities_from_artifact_values()
    test_autofill_entities_skips_optional_attachment_path()
    test_merge_inline_context_promotes_short_aliases()
    test_autofill_entities_disabled_returns_original_object()
    test_load_doql_context_parses_validations(tmp_path)
    test_validations_doql_roundtrip_via_system_map(tmp_path)
  tests/test_formats.py:
    e: test_render_json_yaml_markdown
    test_render_json_yaml_markdown()
  tests/test_integrators.py:
    e: _fake_service,test_rest_adapter_routes,test_mcp_adapter_tools,test_rest_server_health
    _fake_service(tmp_path)
    test_rest_adapter_routes(tmp_path)
    test_mcp_adapter_tools(tmp_path)
    test_rest_server_health(tmp_path)
  tests/test_mqtt.py:
    e: _install_fake_paho,test_mqtt_publish_topics,_FakeClient
    _FakeClient: __init__(0),username_pw_set(2),connect(3),loop_start(0),loop_stop(0),disconnect(0),publish(4),subscribe(2)
    _install_fake_paho(monkeypatch)
    test_mqtt_publish_topics(monkeypatch)
  tests/test_registry_service.py:
    e: test_registry_service_render_and_desktop,test_registry_service_refresh_publishes_mqtt
    test_registry_service_render_and_desktop(monkeypatch;tmp_path)
    test_registry_service_refresh_publishes_mqtt(monkeypatch;tmp_path)
  tests/test_system_map_ir.py:
    e: test_system_map_validate_step_config,test_dynamic_command_input_model,test_task_context_to_system_map_and_render,test_build_runtimes_for_01_invoice,test_resolve_command_runtime,test_doql_roundtrip_runtimes,test_generate_system_map_01_invoice
    test_system_map_validate_step_config()
    test_dynamic_command_input_model()
    test_task_context_to_system_map_and_render(invoice_example_dir)
    test_build_runtimes_for_01_invoice(invoice_example_dir)
    test_resolve_command_runtime()
    test_doql_roundtrip_runtimes(tmp_path)
    test_generate_system_map_01_invoice(invoice_example_dir)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('env2llm', '0.1.5', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 231, 'less').
project_file('project.sh', 59, 'shell').
project_file('src/env2llm/__init__.py', 44, 'python').
project_file('src/env2llm/__main__.py', 4, 'python').
project_file('src/env2llm/_runtime_health.py', 32, 'python').
project_file('src/env2llm/adapters/__init__.py', 7, 'python').
project_file('src/env2llm/adapters/mcp.py', 143, 'python').
project_file('src/env2llm/adapters/rest.py', 107, 'python').
project_file('src/env2llm/artifact_layout.py', 2, 'python').
project_file('src/env2llm/bootstrap.py', 106, 'python').
project_file('src/env2llm/bridge.py', 226, 'python').
project_file('src/env2llm/cli.py', 64, 'python').
project_file('src/env2llm/doql/__init__.py', 49, 'python').
project_file('src/env2llm/doql/context_blocks.py', 235, 'python').
project_file('src/env2llm/doql/models.py', 135, 'python').
project_file('src/env2llm/doql/parse.py', 483, 'python').
project_file('src/env2llm/doql/render.py', 50, 'python').
project_file('src/env2llm/doql/runtime.py', 207, 'python').
project_file('src/env2llm/doql_context.py', 27, 'python').
project_file('src/env2llm/env.py', 73, 'python').
project_file('src/env2llm/formats/__init__.py', 60, 'python').
project_file('src/env2llm/formats/doql_less.py', 12, 'python').
project_file('src/env2llm/formats/json_fmt.py', 14, 'python').
project_file('src/env2llm/formats/markdown.py', 53, 'python').
project_file('src/env2llm/formats/yaml_fmt.py', 14, 'python').
project_file('src/env2llm/generate.py', 209, 'python').
project_file('src/env2llm/integrators/__init__.py', 2, 'python').
project_file('src/env2llm/integrators/_service_factory.py', 50, 'python').
project_file('src/env2llm/integrators/mcp_server.py', 137, 'python').
project_file('src/env2llm/integrators/mqtt_bridge.py', 146, 'python').
project_file('src/env2llm/integrators/rest_server.py', 115, 'python').
project_file('src/env2llm/ir.py', 316, 'python').
project_file('src/env2llm/layout.py', 267, 'python').
project_file('src/env2llm/policy/__init__.py', 5, 'python').
project_file('src/env2llm/policy/desktop.py', 176, 'python').
project_file('src/env2llm/policy/invoice.py', 53, 'python').
project_file('src/env2llm/policy/process.py', 338, 'python').
project_file('src/env2llm/policy/validations.py', 74, 'python').
project_file('src/env2llm/probes/__init__.py', 6, 'python').
project_file('src/env2llm/probes/desktop.py', 143, 'python').
project_file('src/env2llm/registry.py', 231, 'python').
project_file('src/env2llm/render/__init__.py', 4, 'python').
project_file('src/env2llm/render/doql/__init__.py', 6, 'python').
project_file('src/env2llm/render/doql/blocks.py', 341, 'python').
project_file('src/env2llm/render/doql/helpers.py', 46, 'python').
project_file('src/env2llm/render/doql/render.py', 51, 'python').
project_file('src/env2llm/runtimes.py', 178, 'python').
project_file('src/env2llm/service/__init__.py', 6, 'python').
project_file('src/env2llm/service/registry_service.py', 166, 'python').
project_file('src/env2llm/sources.py', 68, 'python').
project_file('src/env2llm/system_map_bridge.py', 2, 'python').
project_file('src/env2llm/system_map_generator.py', 2, 'python').
project_file('src/env2llm/system_map_ir.py', 2, 'python').
project_file('src/env2llm/system_map_models.py', 49, 'python').
project_file('src/env2llm/system_map_render.py', 2, 'python').
project_file('src/env2llm/system_map_runtimes.py', 2, 'python').
project_file('src/env2llm/transport/__init__.py', 6, 'python').
project_file('src/env2llm/transport/mqtt.py', 153, 'python').
project_file('tests/conftest.py', 24, 'python').
project_file('tests/test_desktop_probe.py', 69, 'python').
project_file('tests/test_doql_context.py', 312, 'python').
project_file('tests/test_formats.py', 24, 'python').
project_file('tests/test_integrators.py', 91, 'python').
project_file('tests/test_mqtt.py', 73, 'python').
project_file('tests/test_registry_service.py', 92, 'python').
project_file('tests/test_system_map_ir.py', 140, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('src/env2llm/_runtime_health.py', 'runtime_id_for_intent', 1, 6, 1).
python_function('src/env2llm/adapters/mcp.py', '_mcp_error', 1, 1, 0).
python_function('src/env2llm/bootstrap.py', 'project_artifact_root', 1, 1, 2).
python_function('src/env2llm/bootstrap.py', 'ensure_environment_map', 1, 9, 22).
python_function('src/env2llm/bootstrap.py', 'ensure_doql_registry', 1, 1, 1).
python_function('src/env2llm/bridge.py', '_mime_for_artifact', 1, 4, 3).
python_function('src/env2llm/bridge.py', '_process_from_ctx', 1, 12, 10).
python_function('src/env2llm/bridge.py', 'task_context_to_system_map', 1, 25, 20).
python_function('src/env2llm/bridge.py', '_command_to_ir', 1, 12, 8).
python_function('src/env2llm/bridge.py', 'doql_file_to_system_map', 1, 1, 3).
python_function('src/env2llm/cli.py', 'build_parser', 0, 1, 4).
python_function('src/env2llm/cli.py', 'main', 1, 1, 6).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_header', 1, 1, 0).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_environment', 1, 3, 5).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_data', 1, 2, 4).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_artifacts', 1, 4, 6).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_commands', 1, 6, 5).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_resources', 1, 5, 5).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_access', 1, 4, 4).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_runtimes', 1, 10, 4).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_capabilities', 1, 2, 1).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_workflow_history', 1, 6, 5).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_process', 1, 18, 1).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_process_access', 1, 7, 2).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_paths', 1, 5, 2).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_conversation', 1, 3, 1).
python_function('src/env2llm/doql/parse.py', '_parse_value', 1, 10, 8).
python_function('src/env2llm/doql/parse.py', '_parse_block_body', 1, 2, 3).
python_function('src/env2llm/doql/parse.py', '_split_csv', 1, 3, 3).
python_function('src/env2llm/doql/parse.py', '_parse_command_body', 1, 1, 5).
python_function('src/env2llm/doql/parse.py', '_parse_resource_body', 1, 1, 5).
python_function('src/env2llm/doql/parse.py', '_parse_access_body', 1, 1, 5).
python_function('src/env2llm/doql/parse.py', '_parse_runtime_body', 1, 1, 5).
python_function('src/env2llm/doql/parse.py', '_parse_validation_body', 1, 1, 4).
python_function('src/env2llm/doql/parse.py', '_parse_artifact_body', 1, 3, 4).
python_function('src/env2llm/doql/parse.py', '_apply_context_metadata', 2, 3, 2).
python_function('src/env2llm/doql/parse.py', '_apply_conversation_block', 2, 1, 2).
python_function('src/env2llm/doql/parse.py', '_apply_capabilities_block', 2, 5, 4).
python_function('src/env2llm/doql/parse.py', '_apply_process_block', 2, 9, 6).
python_function('src/env2llm/doql/parse.py', '_apply_process_access_block', 2, 4, 2).
python_function('src/env2llm/doql/parse.py', '_apply_paths_block', 2, 3, 2).
python_function('src/env2llm/doql/parse.py', '_apply_context_block', 3, 10, 9).
python_function('src/env2llm/doql/parse.py', '_append_collection_blocks', 2, 12, 8).
python_function('src/env2llm/doql/parse.py', 'load_doql_context', 1, 2, 8).
python_function('src/env2llm/doql/parse.py', '_repo_root_from_example', 1, 2, 0).
python_function('src/env2llm/doql/parse.py', '_command_transport', 1, 3, 1).
python_function('src/env2llm/doql/parse.py', 'load_platform_map', 1, 18, 10).
python_function('src/env2llm/doql/parse.py', 'load_commands_from_services_yaml', 1, 14, 10).
python_function('src/env2llm/doql/parse.py', 'enrich_task_context_from_client', 2, 19, 10).
python_function('src/env2llm/doql/parse.py', 'parse_fixture_metadata', 1, 10, 11).
python_function('src/env2llm/doql/parse.py', 'collect_task_context', 1, 19, 26).
python_function('src/env2llm/doql/render.py', 'render_doql_context', 1, 1, 16).
python_function('src/env2llm/doql/render.py', 'write_doql_context', 2, 1, 4).
python_function('src/env2llm/doql/runtime.py', 'resolve_doql_context_path', 0, 1, 1).
python_function('src/env2llm/doql/runtime.py', 'context_inline_payload', 1, 14, 10).
python_function('src/env2llm/doql/runtime.py', 'load_doql_inline_from_env', 0, 2, 3).
python_function('src/env2llm/doql/runtime.py', 'merge_inline_context', 2, 8, 8).
python_function('src/env2llm/doql/runtime.py', 'autofill_entities', 3, 8, 6).
python_function('src/env2llm/doql/runtime.py', '_inline_data_key', 1, 1, 1).
python_function('src/env2llm/doql/runtime.py', '_apply_conversation_flag', 3, 6, 1).
python_function('src/env2llm/doql/runtime.py', '_add_short_inline_alias', 4, 5, 3).
python_function('src/env2llm/doql/runtime.py', '_split_missing_ref', 2, 4, 4).
python_function('src/env2llm/doql/runtime.py', '_canonical_field', 1, 1, 2).
python_function('src/env2llm/doql/runtime.py', '_autofill_value', 3, 2, 3).
python_function('src/env2llm/doql/runtime.py', '_candidate_data_keys', 2, 1, 0).
python_function('src/env2llm/doql/runtime.py', '_value_from_data', 2, 4, 0).
python_function('src/env2llm/doql/runtime.py', '_value_from_artifacts', 2, 6, 0).
python_function('src/env2llm/doql/runtime.py', '_needs_field', 2, 1, 1).
python_function('src/env2llm/env.py', 'mask_secret', 1, 3, 1).
python_function('src/env2llm/env.py', 'collect_environment', 0, 13, 10).
python_function('src/env2llm/env.py', 'merge_environment', 2, 3, 2).
python_function('src/env2llm/formats/__init__.py', 'normalize_format', 1, 2, 4).
python_function('src/env2llm/formats/__init__.py', 'render_format', 2, 2, 6).
python_function('src/env2llm/formats/__init__.py', 'default_output_name', 1, 2, 1).
python_function('src/env2llm/formats/doql_less.py', 'render_doql_less', 2, 1, 1).
python_function('src/env2llm/formats/json_fmt.py', 'render_json', 2, 1, 2).
python_function('src/env2llm/formats/markdown.py', 'render_markdown', 2, 22, 7).
python_function('src/env2llm/formats/yaml_fmt.py', 'render_yaml', 2, 1, 2).
python_function('src/env2llm/generate.py', 'build_introspection_payload', 1, 12, 19).
python_function('src/env2llm/generate.py', '_bootstrap_system_map', 1, 2, 3).
python_function('src/env2llm/generate.py', '_litellm_complete', 2, 3, 5).
python_function('src/env2llm/generate.py', '_parse_llm_json', 1, 5, 7).
python_function('src/env2llm/generate.py', 'generate_system_map', 1, 8, 14).
python_function('src/env2llm/integrators/_service_factory.py', 'build_registry_service', 1, 4, 6).
python_function('src/env2llm/integrators/_service_factory.py', 'attach_mqtt_refresh_listener', 1, 2, 5).
python_function('src/env2llm/integrators/mcp_server.py', '_jsonrpc_response', 2, 1, 0).
python_function('src/env2llm/integrators/mcp_server.py', '_jsonrpc_error', 4, 2, 0).
python_function('src/env2llm/integrators/mcp_server.py', '_write_json', 1, 1, 3).
python_function('src/env2llm/integrators/mcp_server.py', '_log', 1, 1, 1).
python_function('src/env2llm/integrators/mcp_server.py', 'handle_message', 1, 9, 6).
python_function('src/env2llm/integrators/mcp_server.py', 'run_stdio', 0, 6, 10).
python_function('src/env2llm/integrators/mcp_server.py', 'main', 1, 3, 5).
python_function('src/env2llm/integrators/mqtt_bridge.py', 'run_bridge', 0, 5, 10).
python_function('src/env2llm/integrators/mqtt_bridge.py', 'publish_once', 0, 4, 8).
python_function('src/env2llm/integrators/mqtt_bridge.py', 'main', 1, 4, 10).
python_function('src/env2llm/integrators/rest_server.py', 'run_server', 0, 3, 9).
python_function('src/env2llm/integrators/rest_server.py', 'main', 1, 3, 5).
python_function('src/env2llm/layout.py', 'artifact_root', 1, 1, 2).
python_function('src/env2llm/layout.py', '_chmod_writable', 1, 2, 1).
python_function('src/env2llm/layout.py', '_force_remove_path', 1, 7, 10).
python_function('src/env2llm/layout.py', 'clean_artifact_root', 1, 9, 7).
python_function('src/env2llm/layout.py', 'clean_all_example_artifacts', 1, 5, 6).
python_function('src/env2llm/layout.py', 'example_fixtures_dir', 1, 1, 2).
python_function('src/env2llm/layout.py', 'ensure_layout', 1, 1, 3).
python_function('src/env2llm/layout.py', 'resolve_registry_path', 0, 9, 5).
python_function('src/env2llm/layout.py', 'write_registry', 2, 2, 4).
python_function('src/env2llm/layout.py', 'current_run_id', 1, 2, 4).
python_function('src/env2llm/layout.py', 'run_dir', 2, 2, 4).
python_function('src/env2llm/layout.py', 'write_turn_snapshot', 1, 4, 13).
python_function('src/env2llm/layout.py', 'write_reflection_snapshot', 1, 1, 7).
python_function('src/env2llm/layout.py', 'write_last_run_report', 2, 1, 6).
python_function('src/env2llm/policy/desktop.py', 'desktop_probe_enabled', 0, 2, 3).
python_function('src/env2llm/policy/desktop.py', '_ensure_desktop_runtime', 1, 2, 3).
python_function('src/env2llm/policy/desktop.py', '_ensure_desktop_resource', 1, 3, 3).
python_function('src/env2llm/policy/desktop.py', '_ensure_desktop_commands', 1, 6, 6).
python_function('src/env2llm/policy/desktop.py', '_ensure_desktop_access', 1, 5, 3).
python_function('src/env2llm/policy/desktop.py', '_mirror_desktop_summary', 1, 12, 3).
python_function('src/env2llm/policy/desktop.py', 'apply_desktop_probe', 1, 6, 11).
python_function('src/env2llm/policy/invoice.py', 'is_invoice_example', 1, 2, 1).
python_function('src/env2llm/policy/invoice.py', 'apply_invoice_policies', 1, 5, 5).
python_function('src/env2llm/policy/invoice.py', 'apply_invoice_context', 1, 3, 6).
python_function('src/env2llm/policy/process.py', '_as_list', 1, 8, 4).
python_function('src/env2llm/policy/process.py', '_deep_merge_process', 2, 5, 5).
python_function('src/env2llm/policy/process.py', '_load_nlp2dsl_payload', 1, 12, 7).
python_function('src/env2llm/policy/process.py', 'load_platform_process_defaults', 1, 4, 6).
python_function('src/env2llm/policy/process.py', '_merge_access', 1, 5, 4).
python_function('src/env2llm/policy/process.py', '_merge_paths', 1, 4, 3).
python_function('src/env2llm/policy/process.py', 'process_policy_from_profile_block', 1, 5, 14).
python_function('src/env2llm/policy/process.py', '_mapping_block', 2, 2, 2).
python_function('src/env2llm/policy/process.py', '_apply_nlp_policy', 2, 5, 4).
python_function('src/env2llm/policy/process.py', '_apply_autonomous_policy', 2, 5, 4).
python_function('src/env2llm/policy/process.py', '_apply_llm_policy', 2, 4, 3).
python_function('src/env2llm/policy/process.py', '_intract_flags', 1, 2, 2).
python_function('src/env2llm/policy/process.py', '_normalized_mode', 1, 2, 0).
python_function('src/env2llm/policy/process.py', '_process_policy_from_parts', 0, 1, 5).
python_function('src/env2llm/policy/process.py', '_merge_conversation_from_profile', 2, 5, 4).
python_function('src/env2llm/policy/process.py', 'merge_process_config', 0, 4, 5).
python_function('src/env2llm/policy/process.py', 'apply_process_policies', 1, 8, 10).
python_function('src/env2llm/policy/process.py', 'effective_nlp_parser_mode', 1, 5, 1).
python_function('src/env2llm/policy/process.py', 'process_policy_to_doql_dict', 1, 2, 0).
python_function('src/env2llm/policy/process.py', 'process_scope_denied', 1, 12, 6).
python_function('src/env2llm/policy/validations.py', '_parse_profile_validation_by_code', 1, 4, 3).
python_function('src/env2llm/policy/validations.py', '_parse_profile_validation_by_type', 1, 5, 4).
python_function('src/env2llm/policy/validations.py', '_parse_profile_validation_shorthand', 1, 10, 6).
python_function('src/env2llm/policy/validations.py', 'parse_profile_validation', 1, 5, 4).
python_function('src/env2llm/policy/validations.py', 'parse_profile_validations', 1, 4, 2).
python_function('src/env2llm/policy/validations.py', 'apply_profile_validations', 2, 3, 2).
python_function('src/env2llm/probes/desktop.py', '_run_text', 1, 4, 2).
python_function('src/env2llm/probes/desktop.py', '_is_browser_title', 1, 1, 2).
python_function('src/env2llm/probes/desktop.py', 'parse_wmctrl_listing', 1, 3, 8).
python_function('src/env2llm/probes/desktop.py', '_probe_display_geometry', 0, 5, 6).
python_function('src/env2llm/probes/desktop.py', '_probe_active_window_id', 0, 4, 5).
python_function('src/env2llm/probes/desktop.py', 'collect_desktop_probe', 0, 15, 13).
python_function('src/env2llm/registry.py', 'entities_to_data', 2, 5, 4).
python_function('src/env2llm/registry.py', 'merge_execution_observation', 3, 2, 5).
python_function('src/env2llm/registry.py', '_merge_execution_header', 2, 1, 4).
python_function('src/env2llm/registry.py', '_execution_steps', 1, 4, 2).
python_function('src/env2llm/registry.py', '_merge_execution_step', 3, 4, 6).
python_function('src/env2llm/registry.py', '_step_output', 1, 4, 2).
python_function('src/env2llm/registry.py', '_merge_send_invoice_output', 3, 3, 2).
python_function('src/env2llm/registry.py', '_merge_generate_invoice_output', 2, 3, 1).
python_function('src/env2llm/registry.py', '_merge_workflow_id', 2, 3, 2).
python_function('src/env2llm/registry.py', 'merge_registry_observations', 2, 11, 9).
python_function('src/env2llm/registry.py', 'refresh_doql_registry', 1, 10, 16).
python_function('src/env2llm/registry.py', 'refresh_doql_registry_from_state', 1, 1, 1).
python_function('src/env2llm/render/doql/blocks.py', 'render_header', 1, 1, 2).
python_function('src/env2llm/render/doql/blocks.py', 'render_environment_block', 1, 2, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_data_block', 1, 3, 4).
python_function('src/env2llm/render/doql/blocks.py', 'render_artifacts_block', 1, 6, 6).
python_function('src/env2llm/render/doql/blocks.py', 'render_desktop_block', 1, 8, 7).
python_function('src/env2llm/render/doql/blocks.py', 'render_runtimes_block', 1, 8, 4).
python_function('src/env2llm/render/doql/blocks.py', 'render_commands_block', 1, 9, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_resources_block', 1, 5, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_access_block', 1, 4, 4).
python_function('src/env2llm/render/doql/blocks.py', 'render_capabilities_block', 1, 2, 1).
python_function('src/env2llm/render/doql/blocks.py', 'render_workflow_history_block', 1, 3, 4).
python_function('src/env2llm/render/doql/blocks.py', 'render_conversation_block', 1, 3, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_process_block', 1, 3, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_process_access_block', 1, 7, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_paths_block', 1, 5, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_schedules_block', 1, 3, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_deploy_block', 1, 3, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_generated_services_block', 1, 6, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_validations_block', 1, 5, 4).
python_function('src/env2llm/render/doql/helpers.py', 'esc_str', 1, 1, 1).
python_function('src/env2llm/render/doql/helpers.py', 'esc_str_full', 1, 1, 1).
python_function('src/env2llm/render/doql/helpers.py', 'bool_lit', 1, 2, 0).
python_function('src/env2llm/render/doql/helpers.py', 'join_csv', 1, 1, 1).
python_function('src/env2llm/render/doql/helpers.py', 'data_value_line', 2, 3, 3).
python_function('src/env2llm/render/doql/helpers.py', 'history_value_line', 2, 4, 3).
python_function('src/env2llm/render/doql/helpers.py', 'process_field_line', 2, 3, 2).
python_function('src/env2llm/render/doql/render.py', 'render_system_map_doql', 1, 1, 21).
python_function('src/env2llm/runtimes.py', '_repo_root_from_example', 1, 2, 0).
python_function('src/env2llm/runtimes.py', 'load_example_profile', 2, 7, 6).
python_function('src/env2llm/runtimes.py', 'resolve_command_runtime', 1, 8, 2).
python_function('src/env2llm/runtimes.py', 'build_runtimes_for_example', 1, 18, 12).
python_function('src/env2llm/system_map_models.py', '_annotation_for_field', 1, 11, 2).
python_function('src/env2llm/system_map_models.py', 'command_input_model', 1, 4, 5).
python_function('src/env2llm/system_map_models.py', 'build_command_registry', 1, 2, 1).
python_function('src/env2llm/system_map_models.py', 'validate_config_against_map', 3, 2, 5).
python_function('src/env2llm/transport/mqtt.py', 'mqtt_available', 0, 1, 0).
python_function('src/env2llm/transport/mqtt.py', 'mqtt_missing_message', 0, 2, 0).
python_function('src/env2llm/transport/mqtt.py', 'mqtt_enabled', 0, 2, 3).
python_function('tests/conftest.py', 'nlp2dsl_root', 0, 1, 1).
python_function('tests/conftest.py', 'invoice_example_dir', 0, 2, 3).
python_function('tests/test_desktop_probe.py', 'test_parse_wmctrl_listing_detects_geometry_and_browser', 0, 8, 2).
python_function('tests/test_desktop_probe.py', 'test_apply_desktop_probe_adds_runtime_commands_and_doql_block', 1, 11, 8).
python_function('tests/test_doql_context.py', 'test_load_doql_context_all_supported_blocks', 1, 34, 3).
python_function('tests/test_doql_context.py', 'test_doql_roundtrip_preserves_core_fields', 1, 7, 5).
python_function('tests/test_doql_context.py', 'test_autofill_entities_from_data_and_aliases', 0, 4, 2).
python_function('tests/test_doql_context.py', 'test_autofill_entities_from_artifact_values', 0, 3, 3).
python_function('tests/test_doql_context.py', 'test_autofill_entities_skips_optional_attachment_path', 0, 3, 3).
python_function('tests/test_doql_context.py', 'test_merge_inline_context_promotes_short_aliases', 0, 5, 2).
python_function('tests/test_doql_context.py', 'test_autofill_entities_disabled_returns_original_object', 0, 3, 2).
python_function('tests/test_doql_context.py', 'test_load_doql_context_parses_validations', 1, 6, 4).
python_function('tests/test_doql_context.py', 'test_validations_doql_roundtrip_via_system_map', 1, 4, 6).
python_function('tests/test_formats.py', 'test_render_json_yaml_markdown', 0, 5, 4).
python_function('tests/test_integrators.py', '_fake_service', 1, 1, 5).
python_function('tests/test_integrators.py', 'test_rest_adapter_routes', 1, 7, 3).
python_function('tests/test_integrators.py', 'test_mcp_adapter_tools', 1, 4, 3).
python_function('tests/test_integrators.py', 'test_rest_server_health', 1, 4, 20).
python_function('tests/test_mqtt.py', '_install_fake_paho', 1, 1, 4).
python_function('tests/test_mqtt.py', 'test_mqtt_publish_topics', 1, 8, 9).
python_function('tests/test_registry_service.py', 'test_registry_service_render_and_desktop', 2, 7, 13).
python_function('tests/test_registry_service.py', 'test_registry_service_refresh_publishes_mqtt', 2, 3, 8).
python_function('tests/test_system_map_ir.py', 'test_system_map_validate_step_config', 0, 3, 5).
python_function('tests/test_system_map_ir.py', 'test_dynamic_command_input_model', 0, 3, 7).
python_function('tests/test_system_map_ir.py', 'test_task_context_to_system_map_and_render', 1, 12, 7).
python_function('tests/test_system_map_ir.py', 'test_build_runtimes_for_01_invoice', 1, 9, 2).
python_function('tests/test_system_map_ir.py', 'test_resolve_command_runtime', 0, 4, 1).
python_function('tests/test_system_map_ir.py', 'test_doql_roundtrip_runtimes', 1, 3, 7).
python_function('tests/test_system_map_ir.py', 'test_generate_system_map_01_invoice', 1, 3, 2).

% ── Python Classes ───────────────────────────────────────
python_class('src/env2llm/adapters/mcp.py', 'McpAdapter').
python_method('McpAdapter', '__init__', 1, 1, 0).
python_method('McpAdapter', 'call_tool', 2, 13, 15).
python_class('src/env2llm/adapters/rest.py', 'RestAdapter').
python_method('RestAdapter', '__init__', 1, 1, 0).
python_method('RestAdapter', 'match_route', 3, 5, 2).
python_method('RestAdapter', 'dispatch', 1, 13, 18).
python_method('RestAdapter', 'handle_http', 2, 4, 5).
python_class('src/env2llm/doql/models.py', 'DoqlArtifact').
python_class('src/env2llm/doql/models.py', 'DoqlRuntime').
python_class('src/env2llm/doql/models.py', 'DoqlCommand').
python_class('src/env2llm/doql/models.py', 'DoqlResource').
python_class('src/env2llm/doql/models.py', 'DoqlAccess').
python_class('src/env2llm/doql/models.py', 'DoqlProcessPolicy').
python_class('src/env2llm/doql/models.py', 'DoqlTaskContext').
python_method('DoqlTaskContext', 'entity_values', 1, 5, 3).
python_method('DoqlTaskContext', 'command', 1, 3, 0).
python_method('DoqlTaskContext', 'required_fields_for', 1, 3, 2).
python_method('DoqlTaskContext', 'runtime_for', 1, 6, 3).
python_class('src/env2llm/integrators/rest_server.py', 'Env2LLMRequestHandler').
python_method('Env2LLMRequestHandler', 'log_message', 1, 1, 0).
python_method('Env2LLMRequestHandler', '_read_body', 0, 3, 3).
python_method('Env2LLMRequestHandler', '_send', 2, 1, 8).
python_method('Env2LLMRequestHandler', '_handle', 1, 2, 3).
python_method('Env2LLMRequestHandler', 'do_GET', 0, 1, 1).
python_method('Env2LLMRequestHandler', 'do_POST', 0, 1, 1).
python_class('src/env2llm/ir.py', 'MimeTypeSpec').
python_class('src/env2llm/ir.py', 'RuntimeSpecIR').
python_class('src/env2llm/ir.py', 'ProtocolSpec').
python_class('src/env2llm/ir.py', 'FieldSpec').
python_class('src/env2llm/ir.py', 'CommandSchemaIR').
python_method('CommandSchemaIR', 'required_names', 0, 3, 0).
python_method('CommandSchemaIR', 'optional_names', 0, 3, 0).
python_class('src/env2llm/ir.py', 'ResourceSpecIR').
python_class('src/env2llm/ir.py', 'AccessGrantIR').
python_class('src/env2llm/ir.py', 'ArtifactSpecIR').
python_class('src/env2llm/ir.py', 'ConversationPolicyIR').
python_class('src/env2llm/ir.py', 'ProcessAccessScopeIR').
python_class('src/env2llm/ir.py', 'ProcessPathsIR').
python_class('src/env2llm/ir.py', 'ProcessPolicyIR').
python_class('src/env2llm/ir.py', 'ScheduleSpecIR').
python_class('src/env2llm/ir.py', 'GeneratedServiceIR').
python_class('src/env2llm/ir.py', 'DeploySpecIR').
python_class('src/env2llm/ir.py', 'ProfileValidationIR').
python_class('src/env2llm/ir.py', 'DesktopWindowIR').
python_class('src/env2llm/ir.py', 'DesktopDisplayIR').
python_class('src/env2llm/ir.py', 'DesktopProbeIR').
python_class('src/env2llm/ir.py', 'SystemMapIR').
python_method('SystemMapIR', 'command', 1, 3, 0).
python_method('SystemMapIR', 'runtime', 1, 3, 0).
python_method('SystemMapIR', 'runtime_for_command', 1, 3, 2).
python_method('SystemMapIR', 'validate_step_config', 2, 7, 5).
python_class('src/env2llm/service/registry_service.py', 'RegistryService').
python_method('RegistryService', '__post_init__', 0, 2, 2).
python_method('RegistryService', 'registry_path', 0, 3, 2).
python_method('RegistryService', 'load', 0, 2, 3).
python_method('RegistryService', 'refresh', 0, 4, 4).
python_method('RegistryService', 'get_ir', 0, 3, 2).
python_method('RegistryService', 'render', 1, 1, 2).
python_method('RegistryService', 'to_dict', 0, 1, 2).
python_method('RegistryService', 'desktop_payload', 0, 2, 2).
python_method('RegistryService', 'commands_payload', 0, 2, 2).
python_method('RegistryService', 'uris_payload', 0, 2, 3).
python_method('RegistryService', 'mqtt_status', 0, 2, 2).
python_method('RegistryService', '_generate_ir', 0, 5, 11).
python_method('RegistryService', '_publish_mqtt', 0, 5, 7).
python_class('src/env2llm/sources.py', 'EnvironmentSources').
python_method('EnvironmentSources', 'example_profile', 2, 7, 0).
python_method('EnvironmentSources', 'platform_config', 1, 5, 0).
python_method('EnvironmentSources', 'services_snapshot', 1, 12, 0).
python_class('src/env2llm/sources.py', 'DefaultEnvironmentSources').
python_method('DefaultEnvironmentSources', 'example_profile', 2, 7, 5).
python_method('DefaultEnvironmentSources', 'platform_config', 1, 5, 5).
python_method('DefaultEnvironmentSources', 'services_snapshot', 1, 12, 5).
python_class('src/env2llm/transport/mqtt.py', 'MqttRegistryBridge').
python_method('MqttRegistryBridge', '__init__', 0, 11, 8).
python_method('MqttRegistryBridge', 'topic', 1, 3, 2).
python_method('MqttRegistryBridge', 'connect', 0, 1, 2).
python_method('MqttRegistryBridge', 'disconnect', 0, 1, 2).
python_method('MqttRegistryBridge', 'publish_registry', 2, 1, 3).
python_method('MqttRegistryBridge', 'publish_desktop', 2, 1, 3).
python_method('MqttRegistryBridge', 'publish_event', 3, 1, 3).
python_method('MqttRegistryBridge', 'subscribe_refresh', 1, 1, 1).
python_method('MqttRegistryBridge', '_publish', 2, 2, 2).
python_method('MqttRegistryBridge', '_on_connect', 5, 2, 1).
python_method('MqttRegistryBridge', '_on_message', 3, 9, 7).
python_class('tests/test_mqtt.py', '_FakeClient').
python_method('_FakeClient', '__init__', 0, 1, 0).
python_method('_FakeClient', 'username_pw_set', 2, 1, 0).
python_method('_FakeClient', 'connect', 3, 1, 0).
python_method('_FakeClient', 'loop_start', 0, 1, 0).
python_method('_FakeClient', 'loop_stop', 0, 1, 0).
python_method('_FakeClient', 'disconnect', 0, 1, 0).
python_method('_FakeClient', 'publish', 4, 1, 1).
python_method('_FakeClient', 'subscribe', 2, 1, 1).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────
makefile_target('CYAN', 'Colors').
makefile_target('GREEN', '').
makefile_target('YELLOW', '').
makefile_target('RED', '').
makefile_target('RESET', '').
makefile_target('help', '').
makefile_target('install', '').
makefile_target('install-dev', '').
makefile_target('install-ai', '').
makefile_target('setup', '').
makefile_target('env', '').
makefile_target('run', '').
makefile_target('web', '').
makefile_target('shell', '').
makefile_target('plan', '').
makefile_target('execute', '').
makefile_target('examples', '').
makefile_target('run-intent', 'Run with custom package file: make run-intent FILE=path/to/iterun.yaml').
makefile_target('test', '').
makefile_target('test-shell', '').
makefile_target('test-web', '').
makefile_target('test-ai', '').
makefile_target('test-cov', '').
makefile_target('ollama-start', '').
makefile_target('ollama-pull', '').
makefile_target('ollama-models', '').
makefile_target('ollama-status', '').
makefile_target('lint', '').
makefile_target('format', '').
makefile_target('clean', '').
makefile_target('docker-clean', '').
makefile_target('docker-ps', '').
makefile_target('docker-stop', '').
makefile_target('dev', '').
makefile_target('new-intent', '').
makefile_target('show-config', '').

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
sumd_workflow('install', 'manual').
sumd_workflow_step('install', 1, '$(PIP) install -r requirements.txt').
sumd_workflow('install-dev', 'manual').
sumd_workflow_step('install-dev', 1, '$(PIP) install pytest pytest-asyncio httpx anyio').
sumd_workflow('install-ai', 'manual').
sumd_workflow_step('install-ai', 1, '$(PIP) install litellm').
sumd_workflow('setup', 'manual').
sumd_workflow_step('setup', 1, 'echo "$(GREEN)✓ Setup complete$(RESET)"').
sumd_workflow('env', 'manual').
sumd_workflow_step('env', 1, 'if [ ! -f .env ]').
sumd_workflow_step('env', 2, 'cp .env.example .env').
sumd_workflow_step('env', 3, 'echo "$(GREEN)✓ Created .env from .env.example$(RESET)"').
sumd_workflow_step('env', 4, 'else \').
sumd_workflow_step('env', 5, 'echo "$(YELLOW)⚠ .env already exists$(RESET)"').
sumd_workflow_step('env', 6, 'fi').
sumd_workflow('run', 'manual').
sumd_workflow('web', 'manual').
sumd_workflow_step('web', 1, 'echo "$(CYAN)Starting web server on http://$(HOST):$(PORT)$(RESET)"').
sumd_workflow_step('web', 2, '$(PYTHON) -m web.app').
sumd_workflow('shell', 'manual').
sumd_workflow_step('shell', 1, 'echo "$(CYAN)Starting interactive shell$(RESET)"').
sumd_workflow_step('shell', 2, '$(PYTHON) -m cli.main').
sumd_workflow('plan', 'manual').
sumd_workflow_step('plan', 1, '$(PYTHON) -m cli.main plan examples/01-user-api/generated/iterun.yaml -o examples/01-user-api/generated/').
sumd_workflow('execute', 'manual').
sumd_workflow_step('execute', 1, 'ITERUN_EXECUTE=1 ./examples/01-user-api/run.sh').
sumd_workflow('examples', 'manual').
sumd_workflow_step('examples', 1, './examples/run-all.sh').
sumd_workflow('run-intent', 'manual').
sumd_workflow_step('run-intent', 1, 'if [ -z "$(FILE)" ]').
sumd_workflow_step('run-intent', 2, 'echo "$(RED)ERROR: FILE not specified$(RESET)"').
sumd_workflow_step('run-intent', 3, 'echo "Usage: make run-intent FILE=path/to/iterun.yaml"').
sumd_workflow_step('run-intent', 4, 'exit 1').
sumd_workflow_step('run-intent', 5, 'fi').
sumd_workflow_step('run-intent', 6, '$(PYTHON) -m cli.main execute $(FILE)').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, '$(PYTHON) -m pytest tests/ -v').
sumd_workflow('test-shell', 'manual').
sumd_workflow_step('test-shell', 1, '$(PYTHON) -m pytest tests/e2e/test_shell.py -v').
sumd_workflow('test-web', 'manual').
sumd_workflow_step('test-web', 1, '$(PYTHON) -m pytest tests/e2e/test_web.py -v').
sumd_workflow('test-ai', 'manual').
sumd_workflow_step('test-ai', 1, '$(PYTHON) -m pytest tests/e2e/test_ai_gateway.py -v').
sumd_workflow('test-cov', 'manual').
sumd_workflow_step('test-cov', 1, '$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term').
sumd_workflow('ollama-start', 'manual').
sumd_workflow_step('ollama-start', 1, 'echo "$(CYAN)Starting Ollama server...$(RESET)"').
sumd_workflow_step('ollama-start', 2, 'ollama serve &').
sumd_workflow_step('ollama-start', 3, 'sleep 2').
sumd_workflow_step('ollama-start', 4, 'echo "$(GREEN)✓ Ollama server started$(RESET)"').
sumd_workflow('ollama-pull', 'manual').
sumd_workflow_step('ollama-pull', 1, 'echo "$(CYAN)Pulling model: $(DEFAULT_MODEL)$(RESET)"').
sumd_workflow_step('ollama-pull', 2, 'ollama pull $(DEFAULT_MODEL)').
sumd_workflow_step('ollama-pull', 3, 'echo "$(GREEN)✓ Model $(DEFAULT_MODEL) ready$(RESET)"').
sumd_workflow('ollama-models', 'manual').
sumd_workflow_step('ollama-models', 1, 'echo ""').
sumd_workflow_step('ollama-models', 2, 'echo "$(CYAN)Recommended Ollama models (≤12B):$(RESET)"').
sumd_workflow_step('ollama-models', 3, 'echo "  $(GREEN)llama3.2$(RESET)       - 3B  - Default, fast"').
sumd_workflow_step('ollama-models', 4, 'echo "  llama3.2:1b    - 1B  - Ultra lightweight"').
sumd_workflow_step('ollama-models', 5, 'echo "  llama3.1:8b    - 8B  - Balanced"').
sumd_workflow_step('ollama-models', 6, 'echo "  mistral        - 7B  - Fast inference"').
sumd_workflow_step('ollama-models', 7, 'echo "  mistral-nemo   - 12B - Best quality"').
sumd_workflow_step('ollama-models', 8, 'echo "  gemma2         - 9B  - Google Gemma 2"').
sumd_workflow_step('ollama-models', 9, 'echo "  phi3           - 3.8B - Microsoft Phi-3"').
sumd_workflow_step('ollama-models', 10, 'echo "  qwen2.5        - 7B  - Alibaba Qwen"').
sumd_workflow_step('ollama-models', 11, 'echo "  codellama      - 7B  - Code generation"').
sumd_workflow_step('ollama-models', 12, 'echo ""').
sumd_workflow_step('ollama-models', 13, 'echo "$(YELLOW)Install:$(RESET) ollama pull <model>"').
sumd_workflow_step('ollama-models', 14, 'echo ""').
sumd_workflow('ollama-status', 'manual').
sumd_workflow_step('ollama-status', 1, 'echo "$(CYAN)Checking Ollama status...$(RESET)"').
sumd_workflow_step('ollama-status', 2, 'curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \').
sumd_workflow_step('ollama-status', 3, 'echo "$(GREEN)✓ Ollama is running$(RESET)" || \').
sumd_workflow_step('ollama-status', 4, 'echo "$(RED)✗ Ollama is not running$(RESET)"').
sumd_workflow('lint', 'manual').
sumd_workflow_step('lint', 1, 'which ruff > /dev/null 2>&1 && ruff check . || echo "$(YELLOW)ruff not installed$(RESET)"').
sumd_workflow('format', 'manual').
sumd_workflow_step('format', 1, 'which ruff > /dev/null 2>&1 && ruff format . || echo "$(YELLOW)ruff not installed$(RESET)"').
sumd_workflow('clean', 'manual').
sumd_workflow_step('clean', 1, 'echo "$(CYAN)Cleaning...$(RESET)"').
sumd_workflow_step('clean', 2, 'rm -rf __pycache__ */__pycache__ */*/__pycache__').
sumd_workflow_step('clean', 3, 'rm -rf .pytest_cache */.pytest_cache').
sumd_workflow_step('clean', 4, 'rm -rf *.egg-info .eggs').
sumd_workflow_step('clean', 5, 'rm -rf htmlcov .coverage').
sumd_workflow_step('clean', 6, 'rm -rf /tmp/intent-*').
sumd_workflow_step('clean', 7, 'echo "$(GREEN)✓ Cleaned$(RESET)"').
sumd_workflow('docker-clean', 'manual').
sumd_workflow_step('docker-clean', 1, 'echo "$(CYAN)Cleaning Docker resources...$(RESET)"').
sumd_workflow_step('docker-clean', 2, '-docker ps -a --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker rm -f').
sumd_workflow_step('docker-clean', 3, '-docker images --filter "reference=$(CONTAINER_PREFIX)-*" -q | xargs -r docker rmi -f').
sumd_workflow_step('docker-clean', 4, 'echo "$(GREEN)✓ Docker cleaned$(RESET)"').
sumd_workflow('docker-ps', 'manual').
sumd_workflow_step('docker-ps', 1, 'docker ps --filter "name=$(CONTAINER_PREFIX)-"').
sumd_workflow('docker-stop', 'manual').
sumd_workflow_step('docker-stop', 1, 'docker ps --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker stop').
sumd_workflow_step('docker-stop', 2, 'echo "$(GREEN)✓ Containers stopped$(RESET)"').
sumd_workflow('dev', 'manual').
sumd_workflow_step('dev', 1, 'uvicorn web.app:app --reload --host $(HOST) --port $(PORT)').
sumd_workflow('new-intent', 'manual').
sumd_workflow_step('new-intent', 1, '$(PYTHON) -m cli.main new').
sumd_workflow('show-config', 'manual').
sumd_workflow_step('show-config', 1, 'echo ""').
sumd_workflow_step('show-config', 2, 'echo "$(CYAN)Current Configuration:$(RESET)"').
sumd_workflow_step('show-config', 3, 'echo "  HOST=$(HOST)"').
sumd_workflow_step('show-config', 4, 'echo "  PORT=$(PORT)"').
sumd_workflow_step('show-config', 5, 'echo "  DEFAULT_MODEL=$(DEFAULT_MODEL)"').
sumd_workflow_step('show-config', 6, 'echo "  CONTAINER_PORT=$(CONTAINER_PORT)"').
sumd_workflow_step('show-config', 7, 'echo "  CONTAINER_PREFIX=$(CONTAINER_PREFIX)"').
sumd_workflow_step('show-config', 8, 'echo "  OLLAMA_BASE_URL=$(OLLAMA_BASE_URL)"').
sumd_workflow_step('show-config', 9, 'echo "  SKIP_ITERUN_CONFIRMATION=$(SKIP_ITERUN_CONFIRMATION)"').
sumd_workflow_step('show-config', 10, 'echo ""').
```

## Call Graph

*183 nodes · 206 edges · 32 modules · CC̄=4.5*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `render_system_map_doql` *(in src.env2llm.render.doql.render)* | 1 | 2 | 39 | **41** |
| `build_runtimes_for_example` *(in src.env2llm.runtimes)* | 18 ⚠ | 1 | 35 | **36** |
| `task_context_to_system_map` *(in src.env2llm.bridge)* | 25 ⚠ | 3 | 30 | **33** |
| `load_platform_map` *(in src.env2llm.doql.parse)* | 18 ⚠ | 1 | 32 | **33** |
| `collect_task_context` *(in src.env2llm.doql.parse)* | 19 ⚠ | 1 | 32 | **33** |
| `call_tool` *(in src.env2llm.adapters.mcp.McpAdapter)* | 13 ⚠ | 0 | 32 | **32** |
| `enrich_task_context_from_client` *(in src.env2llm.doql.parse)* | 19 ⚠ | 1 | 29 | **30** |
| `render_doql_context` *(in src.env2llm.doql.render)* | 1 | 1 | 29 | **30** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/env2llm
# generated in 0.20s
# nodes: 183 | edges: 206 | modules: 32
# CC̄=4.5

HUBS[20]:
  src.env2llm.render.doql.render.render_system_map_doql
    CC=1  in:2  out:39  total:41
  src.env2llm.runtimes.build_runtimes_for_example
    CC=18  in:1  out:35  total:36
  src.env2llm.bridge.task_context_to_system_map
    CC=25  in:3  out:30  total:33
  src.env2llm.doql.parse.load_platform_map
    CC=18  in:1  out:32  total:33
  src.env2llm.doql.parse.collect_task_context
    CC=19  in:1  out:32  total:33
  src.env2llm.adapters.mcp.McpAdapter.call_tool
    CC=13  in:0  out:32  total:32
  src.env2llm.doql.parse.enrich_task_context_from_client
    CC=19  in:1  out:29  total:30
  src.env2llm.doql.render.render_doql_context
    CC=1  in:1  out:29  total:30
  src.env2llm.bootstrap.ensure_environment_map
    CC=9  in:4  out:25  total:29
  src.env2llm.render.doql.helpers.join_csv
    CC=1  in:24  out:1  total:25
  src.env2llm.generate.build_introspection_payload
    CC=12  in:1  out:23  total:24
  src.env2llm.policy.process.process_policy_from_profile_block
    CC=5  in:1  out:23  total:24
  src.env2llm.doql.parse._parse_runtime_body
    CC=1  in:1  out:21  total:22
  src.env2llm.probes.desktop.collect_desktop_probe
    CC=15  in:2  out:19  total:21
  src.env2llm.layout.write_turn_snapshot
    CC=4  in:0  out:21  total:21
  src.env2llm.doql.parse.load_commands_from_services_yaml
    CC=14  in:1  out:19  total:20
  src.env2llm.doql.parse._parse_command_body
    CC=1  in:1  out:19  total:20
  src.env2llm.doql.parse._append_collection_blocks
    CC=12  in:1  out:18  total:19
  src.env2llm.doql.runtime.context_inline_payload
    CC=14  in:1  out:18  total:19
  src.env2llm.registry.refresh_doql_registry
    CC=10  in:1  out:17  total:18

MODULES:
  src.env2llm._runtime_health  [1 funcs]
    runtime_id_for_intent  CC=6  out:3
  src.env2llm.adapters.mcp  [2 funcs]
    call_tool  CC=13  out:32
    _mcp_error  CC=1  out:0
  src.env2llm.bootstrap  [3 funcs]
    ensure_doql_registry  CC=1  out:1
    ensure_environment_map  CC=9  out:25
    project_artifact_root  CC=1  out:2
  src.env2llm.bridge  [3 funcs]
    _command_to_ir  CC=12  out:10
    doql_file_to_system_map  CC=1  out:3
    task_context_to_system_map  CC=25  out:30
  src.env2llm.cli  [2 funcs]
    build_parser  CC=1  out:8
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
    build_introspection_payload  CC=12  out:23
    generate_system_map  CC=8  out:15
  src.env2llm.integrators._service_factory  [2 funcs]
    attach_mqtt_refresh_listener  CC=2  out:6
    build_registry_service  CC=4  out:6
  src.env2llm.integrators.mcp_server  [7 funcs]
    _jsonrpc_error  CC=2  out:0
    _jsonrpc_response  CC=1  out:0
    _log  CC=1  out:1
    _write_json  CC=1  out:3
    handle_message  CC=9  out:13
    main  CC=3  out:8
    run_stdio  CC=6  out:12
  src.env2llm.integrators.mqtt_bridge  [2 funcs]
    publish_once  CC=4  out:9
    run_bridge  CC=5  out:16
  src.env2llm.integrators.rest_server  [2 funcs]
    main  CC=3  out:10
    run_server  CC=3  out:9
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
  src.env2llm.policy.desktop  [7 funcs]
    _ensure_desktop_access  CC=5  out:3
    _ensure_desktop_commands  CC=6  out:7
    _ensure_desktop_resource  CC=3  out:3
    _ensure_desktop_runtime  CC=2  out:3
    _mirror_desktop_summary  CC=12  out:3
    apply_desktop_probe  CC=6  out:11
    desktop_probe_enabled  CC=2  out:3
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
  src.env2llm.probes.desktop  [4 funcs]
    _probe_active_window_id  CC=4  out:5
    _probe_display_geometry  CC=5  out:7
    _run_text  CC=4  out:2
    collect_desktop_probe  CC=15  out:19
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
    render_system_map_doql  CC=1  out:39
  src.env2llm.runtimes  [4 funcs]
    _repo_root_from_example  CC=2  out:0
    build_runtimes_for_example  CC=18  out:35
    load_example_profile  CC=7  out:7
    resolve_command_runtime  CC=8  out:4
  src.env2llm.service.registry_service  [5 funcs]
    _generate_ir  CC=5  out:11
    load  CC=2  out:3
    refresh  CC=4  out:4
    registry_path  CC=3  out:2
    render  CC=1  out:2
  src.env2llm.system_map_models  [4 funcs]
    _annotation_for_field  CC=11  out:3
    build_command_registry  CC=2  out:1
    command_input_model  CC=4  out:5
    validate_config_against_map  CC=2  out:5
  src.env2llm.transport.mqtt  [3 funcs]
    mqtt_available  CC=1  out:0
    mqtt_enabled  CC=2  out:3
    mqtt_missing_message  CC=2  out:0

EDGES:
  src.env2llm.system_map_models.command_input_model → src.env2llm.system_map_models._annotation_for_field
  src.env2llm.system_map_models.build_command_registry → src.env2llm.system_map_models.command_input_model
  src.env2llm.system_map_models.validate_config_against_map → src.env2llm.system_map_models.command_input_model
  src.env2llm.registry.merge_execution_observation → src.env2llm.registry._merge_execution_header
  src.env2llm.registry.merge_execution_observation → src.env2llm.registry._execution_steps
  src.env2llm.registry.merge_execution_observation → src.env2llm.registry._merge_workflow_id
  src.env2llm.registry.merge_execution_observation → src.env2llm.registry._merge_execution_step
  src.env2llm.registry._merge_execution_step → src.env2llm.registry._step_output
  src.env2llm.registry._merge_execution_step → src.env2llm.registry._merge_send_invoice_output
  src.env2llm.registry._merge_execution_step → src.env2llm.registry._merge_generate_invoice_output
  src.env2llm.registry.merge_registry_observations → src.env2llm.doql.parse.load_doql_context
  src.env2llm.registry.merge_registry_observations → src.env2llm.policy.invoice.is_invoice_example
  src.env2llm.registry.refresh_doql_registry → src.env2llm.doql.parse.load_doql_context
  src.env2llm.registry.refresh_doql_registry → src.env2llm.bridge.task_context_to_system_map
  src.env2llm.registry.refresh_doql_registry → src.env2llm.render.doql.render.render_system_map_doql
  src.env2llm.registry.refresh_doql_registry_from_state → src.env2llm.registry.refresh_doql_registry
  src.env2llm.layout._force_remove_path → src.env2llm.layout._chmod_writable
  src.env2llm.layout.clean_artifact_root → src.env2llm.layout.artifact_root
  src.env2llm.layout.clean_artifact_root → src.env2llm.layout._force_remove_path
  src.env2llm.layout.clean_all_example_artifacts → src.env2llm.layout.clean_artifact_root
  src.env2llm.layout.resolve_registry_path → src.env2llm.layout.artifact_root
  src.env2llm.layout.write_registry → src.env2llm.layout.ensure_layout
  src.env2llm.layout.run_dir → src.env2llm.layout.current_run_id
  src.env2llm.layout.write_turn_snapshot → src.env2llm.layout.run_dir
  src.env2llm.layout.write_reflection_snapshot → src.env2llm.layout.run_dir
  src.env2llm.layout.write_last_run_report → src.env2llm.layout.ensure_layout
  src.env2llm.bridge.task_context_to_system_map → src.env2llm.runtimes.load_example_profile
  src.env2llm.bridge.task_context_to_system_map → src.env2llm.policy.process.apply_process_policies
  src.env2llm.bridge.task_context_to_system_map → src.env2llm.bridge._command_to_ir
  src.env2llm.bridge._command_to_ir → src.env2llm.runtimes.resolve_command_runtime
  src.env2llm.bridge.doql_file_to_system_map → src.env2llm.doql.parse.load_doql_context
  src.env2llm.bridge.doql_file_to_system_map → src.env2llm.bridge.task_context_to_system_map
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
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

Generate environment maps (services, artifacts, env vars) for LLM decision-making
