# Claude Pet — Terminal Worm for Claude Code

A terminal worm animation that lives in a split pane and reacts to [Claude Code](https://claude.ai/code)'s activity in real time.

```
running (red/fast):   _/\_(>.<)_________________________
idle    (white/slow): _____________________________(o.o)_____
waiting (frozen+?):   _____(o.o)?______________________
```

## Platforms

| Platform | Split pane | Status |
|----------|-----------|--------|
| Windows (Windows Terminal) | `wt.exe` split | ✅ |
| macOS / Linux (tmux) | `tmux split-window` | ✅ |
| iOS — iSH Shell (tmux) | `tmux split-window` | ✅ |
| iOS — a-Shell | Background process | ✅ |
| SSH from iOS (any terminal) | Inherits server env | ✅ |

## Worm states

| State | Color | Speed | Meaning |
|-------|-------|-------|---------|
| `idle` | white | slow crawl | Waiting for your input |
| `waiting` | white + `?` | frozen | Tool needs your confirmation |
| `running:1` | yellow | moderate | Thinking / reading / writing |
| `running:3` | red | fast | Shell commands / agents running |

## Installation

### macOS / Linux / iOS (iSH)

```bash
git clone https://github.com/qi1224/claude-pet.git
cd claude-pet
bash install-unix.sh
```

For split-pane view, run Claude Code inside tmux:

```bash
tmux new-session -s claude 'claude'
# then /pet inside Claude Code
```

On **iSH** (iOS): install tmux first: `apk add tmux python3`

### Windows

```powershell
git clone https://github.com/qi1224/claude-pet.git
cd claude-pet
.\install-windows.ps1
```

Requires [Windows Terminal](https://aka.ms/terminal).

## Manual installation

Copy files to `~/.claude/pet/` and `~/.claude/commands/`:

```
~/.claude/
├── pet/
│   ├── worm.py       ← animation process
│   ├── hook.py       ← Claude Code event hook
│   ├── launch.sh     ← platform-aware launcher
│   └── state         ← runtime state file (auto-created)
└── commands/
    └── pet.md        ← /pet skill command
```

Add hooks to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop":             [{"matcher":"","hooks":[{"type":"command","command":"python3 ~/.claude/pet/hook.py stop"}]}],
    "PreToolUse":       [{"matcher":"","hooks":[{"type":"command","command":"python3 ~/.claude/pet/hook.py pre"}]}],
    "PostToolUse":      [{"matcher":"","hooks":[{"type":"command","command":"python3 ~/.claude/pet/hook.py post"}]}],
    "UserPromptSubmit": [{"matcher":"","hooks":[{"type":"command","command":"python3 ~/.claude/pet/hook.py submit"}]}]
  }
}
```

## Usage

Inside Claude Code, type:

```
/pet
```

## Environment variable

Set `CLAUDE_CONFIG_DIR` to override the default `~/.claude` path.

## Requirements

- Python 3.8+
- A terminal that supports ANSI escape codes
- tmux (for split-pane on Unix/iOS) or Windows Terminal (on Windows)
