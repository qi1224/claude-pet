#!/usr/bin/env python3
"""Launch in Windows Terminal, tmux, or the current terminal."""
import argparse
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import os
from runtime import root_dir, session_path

def launch_command(worm, state, platform=None, env=None):
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    command = [sys.executable, str(worm), '--state-file', str(state)]
    if platform == 'win32' and shutil.which('wt.exe'):
        return ['wt.exe', '-w', '0', 'split-pane', '-H', '--size', '0.12', '--'] + command
    if env.get('TMUX') and shutil.which('tmux'):
        return ['tmux', 'split-window', '-v', '-l', '12%', '-d',
                ' '.join(shlex.quote(part) for part in command)]
    return command

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=['claude', 'codex'], default='claude')
    parser.add_argument('--root', type=Path)
    parser.add_argument('--session-id')
    parser.add_argument('--state-file', type=Path)
    parser.add_argument('--inline', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    root = args.root or root_dir(args.provider)
    state = args.state_file
    if state is None and args.session_id:
        state = session_path(root, args.session_id)
    if state is None:
        try:
            state = Path((root / 'latest-session').read_text(encoding='utf-8').strip())
        except FileNotFoundError:
            state = root / 'state'
    worm = Path(__file__).with_name('worm.py')
    command = ([sys.executable, str(worm), '--state-file', str(state)] if args.inline
               else launch_command(worm, state))
    if args.dry_run:
        print(json.dumps(command))
        return
    if command[0] == sys.executable:
        print('Running in this terminal; Ctrl+C stops the pet.', flush=True)
    subprocess.run(command, check=True)

if __name__ == '__main__':
    main()
