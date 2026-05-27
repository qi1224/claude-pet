#!/usr/bin/env python3
"""Claude Code hook — writes worm state file based on Claude's activity.

Events:
  submit        — UserPromptSubmit: start crawling immediately
  stop          — Claude finished responding; keep crawling briefly then go idle
  delayed_idle  — background timer: write idle if no newer activity occurred
  pre           — PreToolUse: write waiting or running:<speed>
  post          — PostToolUse: write running:<speed>
"""

import sys
import os
import json
import time
import subprocess

STATE_FILE = os.path.expanduser('~/.claude/pet/state')

# Tools that never need user confirmation
SAFE_TOOLS = {'Read', 'Glob', 'Grep', 'ToolSearch'}

# Two-speed model matching Claude Code's visual status colours:
#   1 = yellow (light): thinking, text generation, read/write tools
#   3 = red   (heavy): shell execution, subagents, task management
TOOL_SPEED = {
    'Read': 1, 'Glob': 1, 'Grep': 1, 'ToolSearch': 1,
    'Edit': 1, 'Write': 1, 'WebFetch': 1, 'WebSearch': 1,
    'NotebookEdit': 1,
    'Bash': 3, 'PowerShell': 3, 'Agent': 3,
    'TaskCreate': 3, 'TaskUpdate': 3, 'TaskStop': 3,
    'TaskGet': 1, 'TaskList': 1, 'TaskOutput': 1,
}

# How long (seconds) to keep crawling after Claude stops, to cover the
# "Claude is generating text / user just sent a new message" gap.
IDLE_DELAY = 4.0


def write_state(state: str) -> None:
    try:
        with open(STATE_FILE, 'w') as f:
            f.write(state)
    except Exception:
        pass


def spawn_delayed_idle(sleep_start: float) -> None:
    """Start a detached background process that writes idle after IDLE_DELAY."""
    kwargs: dict = {
        'stdin': subprocess.DEVNULL,
        'stdout': subprocess.DEVNULL,
        'stderr': subprocess.DEVNULL,
    }
    if sys.platform == 'win32':
        kwargs['creationflags'] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        )
    else:
        kwargs['close_fds'] = True

    subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), 'delayed_idle', str(sleep_start)],
        **kwargs,
    )


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else ''

    # Read stdin JSON (present for pre/post/stop events)
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    if event == 'submit':
        write_state('running:1')

    elif event == 'stop':
        # Keep crawling (yellow/slow) while Claude may be starting a new response.
        write_state('running:1')
        time.sleep(0.05)            # ensure mtime of the write above < sleep_start
        sleep_start = time.time()
        spawn_delayed_idle(sleep_start)

    elif event == 'delayed_idle':
        # Fired by spawn_delayed_idle; goes idle only if nothing happened since.
        sleep_start = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
        time.sleep(IDLE_DELAY)
        try:
            mtime = os.path.getmtime(STATE_FILE)
            if mtime > sleep_start:
                return          # Newer hook wrote state — don't override
        except Exception:
            pass
        write_state('idle')

    elif event == 'pre':
        tool = data.get('tool_name', '')
        if tool in SAFE_TOOLS:
            write_state(f'running:{TOOL_SPEED.get(tool, 1)}')
        else:
            write_state('waiting')  # May need user confirmation

    elif event == 'post':
        tool = data.get('tool_name', '')
        write_state(f'running:{TOOL_SPEED.get(tool, 1)}')


if __name__ == '__main__':
    main()
