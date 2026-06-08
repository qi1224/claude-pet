#!/usr/bin/env bash
# claude-pet launcher — platform-aware split pane for the worm animation
# Platforms: Windows (Git Bash/Cygwin), macOS, Linux, iOS (iSH with tmux)

PET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Find Python ───────────────────────────────────────────────────────────────
find_python() {
    # Windows: check common install path first (py.exe not in Git Bash PATH)
    local WIN_PY="C:/Users/wu78/AppData/Local/Programs/Python/Python312/python.exe"
    if [[ "$(uname -s)" == MINGW* ]] || [[ "$(uname -s)" == CYGWIN* ]] || [[ "$(uname -s)" == MSYS* ]]; then
        if [ -f "$(cygpath -u "$WIN_PY" 2>/dev/null || echo "$WIN_PY")" ]; then
            echo "$WIN_PY"; return
        fi
    fi
    command -v python3 2>/dev/null || command -v python 2>/dev/null || {
        echo "Error: Python not found" >&2; exit 1
    }
}

PY="$(find_python)"

# ── Platform detection ────────────────────────────────────────────────────────
OS="$(uname -s 2>/dev/null)"

case "$OS" in
    MINGW*|CYGWIN*|MSYS*)
        # ── Windows via Git Bash / Cygwin ─────────────────────────────────────
        worm_win="$(cygpath -m "$PET_DIR/worm.py")"
        WT="$(command -v wt.exe 2>/dev/null || cygpath -u "${LOCALAPPDATA}/Microsoft/WindowsApps/wt.exe" 2>/dev/null)"
        if [ -n "$WT" ] && [ -f "$(cygpath -u "$WT" 2>/dev/null || echo "$WT")" ]; then
            "$WT" -w 0 split-pane -H --size 0.08 -- "$PY" "$worm_win" &
            sleep 0.3
            "$WT" -w 0 focus-pane --target 0
        else
            echo "Windows Terminal not found — starting worm in background."
            nohup "$PY" "$(cygpath -m "$PET_DIR/worm.py")" >/dev/null 2>&1 &
        fi
        ;;

    Darwin|Linux)
        # ── macOS / Linux / iOS (iSH) ─────────────────────────────────────────
        if [ -n "$TMUX" ]; then
            # Inside an active tmux session: open a small bottom pane
            tmux split-window -vb -l "8%" "$PY '$PET_DIR/worm.py'"
            tmux select-pane -D
            sleep 0.2
            echo "虫子已在 tmux 底部启动！"
        elif command -v tmux >/dev/null 2>&1; then
            # tmux available but not running inside one
            echo "提示：在 tmux 中运行以获得分屏效果。"
            echo "  tmux new-session -d -s pet && tmux split-window -vb -l '8%' \"$PY '$PET_DIR/worm.py'\" && tmux attach"
            echo ""
            echo "直接启动虫子（后台）..."
            nohup "$PY" "$PET_DIR/worm.py" >/dev/null 2>&1 &
            echo "虫子已在后台启动 (PID: $!)"
        else
            # No tmux — run in background
            nohup "$PY" "$PET_DIR/worm.py" >/dev/null 2>&1 &
            echo "虫子已在后台启动 (PID: $!)"
            echo "提示：安装 tmux 可获得分屏效果。"
        fi
        ;;

    *)
        # Unknown platform — best-effort
        echo "Unknown platform '$OS', attempting background launch..."
        "$PY" "$PET_DIR/worm.py" &
        ;;
esac
