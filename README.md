# env2llm


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.12-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$1.66-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-6.4h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $1.6644 (7 commits)
- 👤 **Human dev:** ~$644 (6.4h @ $100/h, 30min dedup)

Generated on 2026-06-08 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

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

# Optional: attach live Linux desktop snapshot (GNOME/X11 via wmctrl/xdotool)
env2llm . --probe-desktop
# or: ENV2LLM_DESKTOP_PROBE=1 env2llm .

# Koru projects: auto-attach MCP tool catalog (koru_list_tickets, …) when koruapi installed
env2llm . --probe-mcp
# or auto when cwd is a Koru repo with koruapi on PYTHONPATH
```

Writes to `.nlp2dsl/registry/environment.<ext>` (and mirrors legacy paths for DOQL).

### Desktop / GUI probe (optional)

When `--probe-desktop` or `ENV2LLM_DESKTOP_PROBE=1` is set, env2llm adds:

- `desktop { canvas_width, canvas_height, compositor, display_server, ... }`
- `desktop_displays[N] { id, output, left, top, width, height, is_primary, index }` — full multi-monitor layout (`xrandr` or `mss`)
- `desktop_pointer { x, y, display_id, display_x, display_y, ... }` — mouse position in global and display-local coords (`xdotool`)
- `desktop_ide_calibrations[N] { ide, chat_x, chat_y, config_path, display_id, ... }` — Koru OS-injector chat anchors from `~/.koru/ide-os-injector.json` and `<project>/.koru/ide-os-injector.json`
- `desktop_windows[N] { title, x, y, width, height, ... }` — top-level windows (`wmctrl`)
- runtime `probe:desktop` (`desktop://session`) for GUI automation via nlp2uri
- commands `desktop_focus_window`, `desktop_move_window`, `desktop_screenshot_*`, `desktop_open_app`
- summary keys in `data` (`desktop.displays`, `desktop.pointer`, `desktop.pointer_display`, `desktop.window_titles`, …)

**Requires** (Linux): `xrandr` (preferred) or Python `mss` for monitor layout; `xdotool` for pointer;
`wmctrl` for window titles/geometry. Headless hosts get `status: unknown` without failing workflow maps.

### Host probe (cron, ports, processes, containers, agents)

When `--probe-host` or `ENV2LLM_HOST_PROBE=1` (default **on** for project dirs), env2llm adds:

- `host { hostname, cron_taskinity_installed, capabilities_available, … }`
- `host_cron[N] { schedule, command, marker }` — parsed from `crontab -l`
- `host_endpoint[N] { id, url, ok }` — agents `:8101–8130`, WWW `:8788`
- `host_port[N] { port, address, pid, process }` — selected listening ports from `ss -ltnp`
- `host_process[N] { pid, command, args }` — relevant runtime processes (`uvicorn`, `docker`, `hypervisor`, monitors)
- `host_container[N] { name, image, state, project, service }` — current `docker ps` snapshot
- `host_agent[N] { id, ok, runtime_status, effective_health_uri, recommended_action }` — `hypervisor inspect-agent`
- `host_examples_test { pass, fail, skip, … }` — from `output/examples/comprehensive_report.json` when present
- `host_monitor_log_tail { line_N }` — tail of `/tmp/taskinity-monitor.log`
- `schedules[N]` — cron lines mirrored for workflow planners

```bash
env2llm /path/to/hypervisor --probe-host
ENV2LLM_HOST_PROBE=1 env2llm . -f json
```

**Browser window titles** are detected heuristically (Firefox, Chrome, Edge, …). Page DOM/content
is not scraped — use **testql** / Playwright for that layer.

## Python API

```python
from env2llm import RegistryService, ensure_environment_map, render_format, generate_system_map

path = ensure_environment_map("examples/03-report-and-notify")
ir = generate_system_map("examples/03-report-and-notify", example_id="03-report-and-notify")
yaml_text = render_format(ir, "yaml")

# Live registry service (load / refresh / render / MQTT)
service = RegistryService(".", project_id="my-app")
registry_json = service.render("json")
```

## REST API (`env2llm-serve`)

```bash
env2llm-serve --project . --port 8770
# optional MQTT fan-out:
ENV2LLM_MQTT_ENABLED=1 env2llm-serve --project . --mqtt
```

| Method | Path | Opis |
|--------|------|------|
| `GET` | `/health` | status |
| `GET` | `/v1/registry?format=json\|yaml\|doql\|md&refresh=1` | registry |
| `POST` | `/v1/registry/refresh` | regenerate + persist (+ MQTT) |
| `GET` | `/v1/registry/desktop` | desktop probe slice |
| `GET` | `/v1/registry/commands` | command schemas |
| `GET` | `/v1/registry/uris` | nlp2uri URI index (needs `nlp2uri[envmap]`) |
| `GET` | `/v1/registry/mqtt` | MQTT bridge status |

## MCP (`env2llm-mcp`)

```json
{
  "mcpServers": {
    "env2llm": {
      "command": "env2llm-mcp",
      "args": ["--project", "/path/to/project"],
      "env": { "ENV2LLM_MQTT_ENABLED": "1" }
    }
  }
}
```

Tools: `env2llm_get_registry`, `env2llm_render_registry`, `env2llm_refresh_registry`,
`env2llm_get_desktop`, `env2llm_list_commands`, `env2llm_list_uris`, `env2llm_mqtt_status`.

## MQTT (`env2llm-mqtt`)

Requires `pip install 'env2llm[mqtt]'` (paho-mqtt).

```bash
# Standalone bridge: listen for refresh, publish retained snapshots
ENV2LLM_MQTT_ENABLED=1 env2llm-mqtt bridge --project .

# One-shot publish
env2llm-mqtt publish --project . --probe-desktop
```

Topics (prefix `env2llm`):

| Topic | Retain | Zawartość |
|-------|--------|-----------|
| `{prefix}/{project}/registry` | yes | full `SystemMapIR` JSON |
| `{prefix}/{project}/registry/desktop` | yes | desktop probe slice |
| `{prefix}/{project}/events` | no | refresh/metadata events |
| `{prefix}/{project}/registry/refresh` | — | subscribe: trigger refresh |

| Variable | Default |
|----------|---------|
| `ENV2LLM_MQTT_ENABLED` | off |
| `ENV2LLM_MQTT_HOST` | `127.0.0.1` |
| `ENV2LLM_MQTT_PORT` | `1883` |
| `ENV2LLM_MQTT_TOPIC_PREFIX` | `env2llm` |
| `ENV2LLM_MQTT_USERNAME` / `PASSWORD` | optional |

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
| `ENV2LLM_DESKTOP_PROBE` | `1` to attach live desktop snapshot (same as `--probe-desktop`) |
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
