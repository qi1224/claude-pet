#!/usr/bin/env bash
# claude-pet installer — detects Python 3 and runs install.py
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "claude-pet installer"
echo "===================="

# Find a runnable Python 3 in this shell environment
find_python() {
    # Standard Unix / PATH lookup
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then echo "$cmd"; return; fi
    done
    # Windows: py.exe launcher
    for win_py in "/c/Windows/py.exe" "/c/Windows/System32/py.exe"; do
        if [ -f "$win_py" ]; then echo "$win_py -3"; return; fi
    done
    # Windows: search user AppData install (most common location)
    if [ -n "${LOCALAPPDATA:-}" ]; then
        local localappdata_unix
        localappdata_unix=$(cygpath -u "$LOCALAPPDATA" 2>/dev/null || echo "$LOCALAPPDATA")
        for f in "$localappdata_unix"/Programs/Python/Python3*/python.exe; do
            [ -f "$f" ] && echo "$f" && return
        done
    fi
    # Windows: system-wide installs
    for f in /c/Python3*/python.exe "/c/Program Files/Python3"/python.exe; do
        [ -f "$f" ] && echo "$f" && return
    done
    # Windows: ask PowerShell
    local found
    found=$(powershell.exe -NoProfile -Command \
        "Get-Command python,python3 -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source" \
        2>/dev/null | tr -d '\r') || true
    if [ -n "$found" ]; then
        echo "$(cygpath -u "$found" 2>/dev/null || echo "$found")"
        return
    fi
    return 1
}

PY_CMD=$(find_python) || {
    echo "Error: Python 3 not found."
    echo "Install Python 3 from https://www.python.org and re-run this script."
    exit 1
}

# shellcheck disable=SC2086
$PY_CMD "$SCRIPT_DIR/install.py"
