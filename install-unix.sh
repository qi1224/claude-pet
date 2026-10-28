#!/usr/bin/env bash
set -euo pipefail
PET_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$PET_SCRIPT_DIR/install.sh" "$@"
