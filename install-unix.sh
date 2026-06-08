#!/usr/bin/env bash
# Install claude-pet for macOS / Linux / iOS (iSH / a-Shell)
# Usage: bash install-unix.sh

set -e

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PET_DIR="$CLAUDE_DIR/pet"
CMD_DIR="$CLAUDE_DIR/commands"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing claude-pet to $PET_DIR"
mkdir -p "$PET_DIR" "$CMD_DIR"

cp "$SCRIPT_DIR/worm.py"   "$PET_DIR/"
cp "$SCRIPT_DIR/hook.py"   "$PET_DIR/"
cp "$SCRIPT_DIR/launch.sh" "$PET_DIR/"
chmod +x "$PET_DIR/worm.py" "$PET_DIR/hook.py" "$PET_DIR/launch.sh"

echo "idle" > "$PET_DIR/state"

cp "$SCRIPT_DIR/pet.md" "$CMD_DIR/"

echo "==> Updating hooks in settings.json"

SETTINGS="$CLAUDE_DIR/settings.json"
PY="$(command -v python3 || command -v python)"

$PY - "$SETTINGS" "$PET_DIR/hook.py" <<'PYEOF'
import sys, json, os

settings_path = sys.argv[1]
hook_path     = sys.argv[2]

try:
    with open(settings_path) as f:
        cfg = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    cfg = {}

py_exe = sys.executable
hook_events = {
    "Stop":            f"{py_exe} {hook_path} stop",
    "PreToolUse":      f"{py_exe} {hook_path} pre",
    "PostToolUse":     f"{py_exe} {hook_path} post",
    "UserPromptSubmit":f"{py_exe} {hook_path} submit",
}

cfg.setdefault("hooks", {})
for event, cmd in hook_events.items():
    entry = {"type": "command", "command": cmd}
    existing = cfg["hooks"].get(event, [])
    # Remove any old claude-pet hook entries before re-adding
    cleaned = [
        h for h in existing
        if not any(
            "hook.py" in hk.get("command", "")
            for hk in h.get("hooks", [])
        )
    ]
    cleaned.append({"matcher": "", "hooks": [entry]})
    cfg["hooks"][event] = cleaned

with open(settings_path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")

print(f"  hooks written to {settings_path}")
PYEOF

echo ""
echo "Done! Start the worm with /pet in Claude Code, or:"
echo "  bash $PET_DIR/launch.sh"
echo ""
echo "For split-pane view, run Claude Code inside tmux:"
echo "  tmux new-session -s claude 'claude'"
