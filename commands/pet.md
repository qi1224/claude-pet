Launch the worm pet in a split pane at the bottom of the current terminal window.

Run the following bash commands in order:

```bash
echo "running:1" > ~/.claude/pet/state
```

```bash
worm_win=$(cygpath -m ~/.claude/pet/worm.py); PY="{{PYTHON_EXE}}"; WT=$(which wt.exe 2>/dev/null || cygpath -u "$LOCALAPPDATA/Microsoft/WindowsApps/wt.exe"); "$WT" -w 0 split-pane -H --size 0.08 -- "$PY" "$worm_win"
```

```bash
sleep 0.3 && { WT=$(which wt.exe 2>/dev/null || cygpath -u "$LOCALAPPDATA/Microsoft/WindowsApps/wt.exe"); "$WT" -w 0 focus-pane --target 0; }
```

After running, tell the user: "宠物虫子已启动！"
