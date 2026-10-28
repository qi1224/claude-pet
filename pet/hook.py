#!/usr/bin/env python3
"""Translate Claude/Codex lifecycle events into terminal-pet state."""
import argparse
import json
from pathlib import Path
import sys
from runtime import root_dir, session_path, write_atomic

HEAVY = {'Bash', 'PowerShell', 'Agent', 'spawn_agent', 'exec_command',
         'TaskCreate', 'TaskUpdate', 'TaskStop'}
EVENTS = {'submit': 'UserPromptSubmit', 'pre': 'PreToolUse',
          'post': 'PostToolUse', 'stop': 'Stop', 'permission': 'PermissionRequest'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('event', nargs='?')
    parser.add_argument('--provider', choices=['claude', 'codex'], default='claude')
    parser.add_argument('--root', type=Path)
    parser.add_argument('--state-file', type=Path)
    args = parser.parse_args()
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    event = EVENTS.get(args.event, args.event) or data.get('hook_event_name', '')
    root = args.root or root_dir(args.provider)
    state = args.state_file or session_path(root, data.get('session_id', ''))
    if event in {'SessionStart', 'UserPromptSubmit'}:
        write_atomic(root / 'latest-session', str(state.resolve()))
    if event in {'SessionStart', 'Stop', 'Interrupt', 'SessionEnd'}:
        value = 'idle'
    elif event == 'PermissionRequest':
        value = 'waiting'
    elif event == 'PreToolUse':
        value = 'running:3' if data.get('tool_name') in HEAVY else 'running:1'
    elif event in {'UserPromptSubmit', 'PostToolUse'}:
        value = 'running:1'
    else:
        return
    write_atomic(state, value)

if __name__ == '__main__':
    main()
