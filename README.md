# Terminal Pet — Claude Code and Codex

A terminal worm in a split pane that reacts to AI activity. Python 3.8+, no third-party Python dependencies.

| State | Appearance | Meaning |
|---|---|---|
| idle | white, slow crawl | ready for input |
| waiting | frozen with `?` | permission approval requested |
| running:1 | yellow | thinking, generation, light tools |
| running:3 | red, fast | shell commands or agents |

## Install

```sh
git clone https://github.com/qi1224/claude-pet.git
cd claude-pet
python install.py --provider claude
python install.py --provider codex
# Or both:
python install.py --provider all
```

On Unix use `python3`, or `bash install-unix.sh --provider all`.
On Windows use `py -3`, or `.\install-windows.ps1 -Provider all`.

Restart Claude Code and invoke `/pet`. Restart Codex, review and trust the
installed hooks using `/hooks`, then invoke `$pet`. Codex must support the lifecycle
hooks documented at https://learn.chatgpt.com/docs/hooks; older versions may need an update.
This installs a local skill and hook configuration, not a marketplace plugin.

The installer preserves unrelated hooks and settings, replaces only this pet's
hooks, and backs up existing configuration to `settings.json.bak` or `hooks.json.bak`
before writing. The backup is the configuration before the most recent install.
Malformed JSON is rejected without overwriting it.

`CLAUDE_CONFIG_DIR` and `CODEX_HOME` override the default `~/.claude` and `~/.codex`
directories. `--config-dir PATH` selects an explicit directory for one provider.
Scripts live under `<config>/pet`; Claude uses `commands/pet.md` and `settings.json`,
Codex uses `skills/pet/SKILL.md` and `hooks.json`.

## Terminal and session selection

Windows uses `wt.exe` when available (run inside Windows Terminal). Unix uses a
bottom pane when inside tmux. Otherwise animation stays visible in the current
terminal; run it in a separate terminal and press Ctrl+C to stop it.
It never silently redirects the animation to an invisible background process.

```sh
python ~/.codex/pet/launch.py --provider codex
python ~/.codex/pet/launch.py --provider codex --session-id SESSION_ID
python ~/.codex/pet/launch.py --provider codex --inline
```

By default the launcher binds to the most recently started/submitted session for
that provider at launch time. With concurrent sessions, pass `--session-id` explicitly.
Each session has a hashed state filename, so different sessions cannot overwrite
one another. Hooks use atomic writes. Stop/interrupt events return to idle immediately.
Simultaneous tools within one session use the latest received event; this is an
activity indicator, not a count of running jobs. Hosted tools without lifecycle
hook coverage remain at the turn's thinking state.

## Other command-line AI programs

Animation is independent of the AI. Any program can write one of the four state
strings to its own file and run:

```sh
python pet/worm.py --state-file /path/to/my-ai.state
python pet/launch.py --state-file /path/to/my-ai.state
```

Or send lifecycle JSON on stdin to the adapter:

```sh
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","session_id":"demo"}' | python pet/hook.py --state-file /path/to/my-ai.state
```

Supported events: SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest,
PostToolUse, Stop, Interrupt, SessionEnd. Legacy positional aliases `submit`, `pre`,
`post`, `permission`, `stop` still work. Only PermissionRequest sets waiting;
PreToolUse sets running, and PostToolUse returns to thinking.
Other AI programs need their own event integration; arbitrary terminal output
cannot reliably identify permission or thinking states.

## Tests

```sh
python -m unittest discover -s tests -v
```

Tests exercise real hook subprocesses, installed hooks through the host shell,
configuration preservation, session isolation, launch command construction and
real ANSI animation output. GUI pane rendering still needs a manual check on each
target terminal; command construction tests do not establish that it rendered.

## Uninstall

Remove only hook handlers whose command points to this installation's
`pet/hook.py` from `settings.json` (Claude) or `hooks.json` (Codex). Preserve all
other handlers. Then remove the `pet` directory and `commands/pet.md` (Claude)
or `skills/pet` (Codex), and restart the AI program.
