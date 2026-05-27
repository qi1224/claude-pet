# claude-pet 🐛

A tiny animated worm that lives in the bottom of your Claude Code terminal.  
It reacts to Claude's activity in real-time:

| State | Look | Meaning |
|-------|------|---------|
| Idle | white slow crawl | waiting for you |
| Waiting | frozen + `?` | tool needs your confirmation |
| Running (slow) | yellow | reading / writing files |
| Running (fast) | red | running shell commands / agents |

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Python 3.8+
- **Windows**: [Windows Terminal](https://aka.ms/terminal) (`wt.exe`)
- **Mac/Linux**: not yet supported (contributions welcome)

## Install

```bash
git clone https://github.com/YOUR_USERNAME/claude-pet
cd claude-pet
bash install.sh
```

Then **restart Claude Code** and run:

```
/pet
```

## What the installer does

1. Copies `worm.py` and `hook.py` into `~/.claude/pet/`
2. Writes `~/.claude/commands/pet.md` (the `/pet` skill) with your Python path filled in
3. Adds four hooks to `~/.claude/settings.json` — existing settings are preserved

## Uninstall

```bash
rm -rf ~/.claude/pet
rm ~/.claude/commands/pet.md
```

Then remove the `UserPromptSubmit`, `Stop`, `PreToolUse`, and `PostToolUse` hook entries
added by this installer from `~/.claude/settings.json`.

## How it works

```
Claude Code events → hook.py → ~/.claude/pet/state → worm.py
```

`hook.py` is called by Claude Code on every tool use and session stop.  
It writes a state string (`idle` / `waiting` / `running:1` / `running:3`) to a file.  
`worm.py` reads that file in a tight loop and adjusts animation speed and color.
