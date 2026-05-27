#!/usr/bin/env python3
"""Installer for claude-pet — works on Windows (Git Bash / PowerShell) and Unix."""

import sys
import os
import json
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PLACEHOLDER = '{{PYTHON_EXE}}'


def get_claude_dir() -> Path:
    env = os.environ.get('CLAUDE_CONFIG_DIR')
    return Path(env) if env else Path.home() / '.claude'


def fwd(path: Path) -> str:
    """Return path string with forward slashes (required in settings.json on Windows)."""
    return str(path).replace('\\', '/')


def merge_hooks(settings: dict, py_path: str, hook_path: str) -> None:
    hooks = settings.setdefault('hooks', {})
    events = {
        'UserPromptSubmit': f'{py_path} {hook_path} submit',
        'Stop':             f'{py_path} {hook_path} stop',
        'PreToolUse':       f'{py_path} {hook_path} pre',
        'PostToolUse':      f'{py_path} {hook_path} post',
    }
    for event, cmd in events.items():
        event_list = hooks.setdefault(event, [])
        already = any(
            h.get('command') == cmd
            for entry in event_list
            for h in entry.get('hooks', [])
        )
        if not already:
            event_list.append({'matcher': '', 'hooks': [{'type': 'command', 'command': cmd}]})


def main() -> None:
    claude_dir = get_claude_dir()
    pet_dir     = claude_dir / 'pet'
    commands_dir = claude_dir / 'commands'

    pet_dir.mkdir(parents=True, exist_ok=True)
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Copy scripts
    shutil.copy2(SCRIPT_DIR / 'pet' / 'worm.py', pet_dir / 'worm.py')
    shutil.copy2(SCRIPT_DIR / 'pet' / 'hook.py', pet_dir / 'hook.py')
    print(f'  Copied worm.py + hook.py  ->  {pet_dir}')

    # Python exe path in forward-slash form for settings.json
    py_path   = fwd(Path(sys.executable))
    hook_path = fwd(pet_dir / 'hook.py')

    # Generate pet.md from template
    template = (SCRIPT_DIR / 'commands' / 'pet.md').read_text(encoding='utf-8')
    (commands_dir / 'pet.md').write_text(
        template.replace(PLACEHOLDER, py_path), encoding='utf-8'
    )
    print(f'  Written pet.md            ->  {commands_dir / "pet.md"}')

    # Merge hooks into settings.json
    settings_path = claude_dir / 'settings.json'
    settings = {}
    if settings_path.exists():
        with open(settings_path, encoding='utf-8') as f:
            settings = json.load(f)
    merge_hooks(settings, py_path, hook_path)
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)
    print(f'  Updated hooks             ->  {settings_path}')

    print()
    print('Installation complete!')
    print('Restart Claude Code, then run /pet to launch your worm.')


if __name__ == '__main__':
    main()
