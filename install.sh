#!/usr/bin/env bash
set -euo pipefail
PET_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
    exec python3 "$PET_SCRIPT_DIR/install.py" "$@"
else
    exec python "$PET_SCRIPT_DIR/install.py" "$@"
fi
