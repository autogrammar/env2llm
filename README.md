# env2llm


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.1-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.02-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-2.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.0203 (1 commits)
- 👤 **Human dev:** ~$200 (2.0h @ $100/h, 30min dedup)

Generated on 2026-06-06 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---



Generate **environment maps** for LLM agents: available services, commands, artifacts,
masked environment variables, and runtime policies.

Default output is DOQL-flavored LESS (`environment.doql.less`), compatible with
[nlp2dsl](https://github.com/wronai/nlp2dsl) examples:

```less
environment[name="03-report-and-notify"] {
  NLP2DSL_BACKEND_URL: "http://localhost:8010";
  LLM_MODEL: "openrouter/...";
}

runtimes[0] { id: "orchestrator:nlp-service"; kind: "orchestrator"; ... }
commands[3] { name: "generate_report"; required: "report_type"; ... }
```

## Install

```bash
cd env2llm
pip install -e ".[dev]"
```

## CLI

```bash
# From an nlp2dsl example directory
env2llm /path/to/nlp2dsl/examples/03-report-and-notify

# Other formats
env2llm . --format yaml
env2llm . --format json
env2llm . --format markdown
```

Writes to `.nlp2dsl/registry/environment.<ext>` (and mirrors legacy paths for DOQL).

## Python API

```python
from env2llm import ensure_environment_map, render_format, generate_system_map

path = ensure_environment_map("examples/03-report-and-notify")
ir = generate_system_map("examples/03-report-and-notify", example_id="03-report-and-notify")
yaml_text = render_format(ir, "yaml")
```

## Output formats

| Format | File | Use case |
|--------|------|----------|
| `doql.less` | `environment.doql.less` | LLM + nlp2dsl orchestrator (default) |
| `yaml` | `environment.yaml` | Tooling, human edit |
| `json` | `environment.json` | APIs, CI |
| `markdown` | `environment.md` | Prompt injection summary |

## Environment variables

| Variable | Purpose |
|----------|---------|
| `NLP2DSL_BACKEND_URL` | Gateway service URL |
| `NLP2DSL_NLP_SERVICE_URL` | NLP orchestrator URL |
| `NLP2DSL_WORKER_URL` | Worker executor URL |
| `LLM_MODEL` | LLM provider/model id |
| `ENV2LLM_CONTEXT` | Path to generated map (set after bootstrap) |
| `NLP2DSL_DOQL_CONTEXT` | Alias for nlp2dsl compatibility |

Secrets (`*_KEY`, `*_TOKEN`) are masked in output.

## Extraction from nlp2dsl

This package contains the former `nlp2dsl_sdk` modules:

- `doql/` — parse/render runtime context
- `ir.py` — `SystemMapIR` schema (`env2llm.system_map.v1`)
- `generate.py`, `bridge.py`, `runtimes.py` — introspection pipeline
- `registry.py` — live registry refresh after workflow steps
- `policy/` — process and invoice policies from `example-profiles.yaml`

nlp2dsl can depend on `env2llm` and replace direct imports over time.


## License

Licensed under Apache-2.0.
