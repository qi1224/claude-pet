Launch the worm pet in a split pane (Windows) or new pane/window (Mac/Linux).

Run the following bash commands in order:

```bash
echo "running:1" > ~/.claude/pet/state
```

```bash
PY="{{PYTHON_EXE}}"; WORM="$HOME/.claude/pet/worm.py"; if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || -n "$LOCALAPPDATA" ]]; then worm_win=$(cygpath -m "$WORM"); WT=$(which wt.exe 2>/dev/null || cygpath -u "$LOCALAPPDATA/Microsoft/WindowsApps/wt.exe"); "$WT" -w 0 split-pane -H --size 0.08 -- "$PY" "$worm_win" && sleep 0.3 && "$WT" -w 0 focus-pane --target 0; elif [ -n "$TMUX" ]; then tmux split-window -h "$PY $WORM"; else osascript -e "tell application \"Terminal\" to do script \"$PY $WORM; exit\"" 2>/dev/null || $PY "$WORM" &; fi
```

After running, tell the user: "宠物虫子已启动！"
