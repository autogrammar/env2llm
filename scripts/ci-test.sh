#!/usr/bin/env bash
# Repo-local unit tests — used by pyqual.yaml and .planfile/.koru/policy.yaml.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
python -m pytest tests/ -q --tb=short
