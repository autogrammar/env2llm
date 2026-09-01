#!/usr/bin/env bash
# Pfix/pyqual-compatible wrapper — delegates to scripts/ci-test.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${ROOT}/scripts/ci-test.sh"
