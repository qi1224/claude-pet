#!/usr/bin/env bash
# claude-pet installer — detects Python 3 and runs install.py
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "claude-pet installer"
echo "===================="

# Find a runnable Python 3 in this shell environment
if command -v python3 &>/dev/null; then
    python3 "$SCRIPT_DIR/install.py"
elif command -v python &>/dev/null; then
    python "$SCRIPT_DIR/install.py"
elif [ -f "/c/Windows/py.exe" ]; then
    # Windows: py.exe launcher lives here but isn't in Git Bash PATH
    /c/Windows/py.exe -3 "$SCRIPT_DIR/install.py"
else
    echo "Error: Python 3 not found."
    echo "Install Python 3 from https://www.python.org and re-run this script."
    exit 1
fi
