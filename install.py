#!/usr/bin/env python3
"""Install terminal-pet for Claude Code or Codex without dependencies."""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import sys

SOURCE = Path(__file__).resolve().parent
EVENTS = ['SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PermissionRequest',
          'PostToolUse', 'Stop', 'SessionEnd']

def quote_command(parts):
    # Hook runners use cmd.exe on Windows and a POSIX shell on Unix.
    if os.name == 'nt':
        import subprocess
        return subprocess.list2cmdline([str(p) for p in parts])
    return ' '.join(shlex.quote(str(p)) for p in parts)

def install(provider, config):
    pet = config / 'pet'
    settings_path = config / ('hooks.json' if provider == 'codex' else 'settings.json')
    # Invalid existing configuration must fail before any installation writes.
    settings = json.loads(settings_path.read_text(encoding='utf-8-sig')) if settings_path.exists() else {}
    hooks = settings.setdefault('hooks', {})
    pet.mkdir(parents=True, exist_ok=True)
    for filename in ['worm.py', 'hook.py', 'runtime.py', 'launch.py', 'launch.sh']:
        shutil.copy2(SOURCE / 'pet' / filename, pet / filename)
    command = quote_command([sys.executable, pet / 'hook.py', '--provider', provider, '--root', pet])
    for event in EVENTS + (['Interrupt'] if provider == 'codex' else []):
        cleaned = []
        for group in hooks.get(event, []):
            remaining = [h for h in group.get('hooks', [])
                         if not owns_hook(h.get('command', ''), pet)]
            if remaining:
                cleaned.append(dict(group, hooks=remaining))
        cleaned.append({'hooks': [{'type': 'command', 'command': command}]})
        hooks[event] = cleaned
    if settings_path.exists():
        shutil.copy2(settings_path, settings_path.with_suffix(settings_path.suffix + '.bak'))
    settings_path.write_text(json.dumps(settings, indent=2) + '\n', encoding='utf-8')
    launch = quote_command([sys.executable, pet / 'launch.py', '--provider', provider])
    instructions = ('Launch the terminal worm pet.\n\nRun this command using the shell tool:\n\n'
                    '```\n' + launch + '\n```\n\n'
                    'It defaults to the most recently started/submitted session. For multiple sessions, '
                    'append --session-id with the current session ID when known. '
                    'Do not invent a session ID. If no split pane is available, tell the user to '
                    'run the command in a separate terminal; do not start an invisible background process.\n')
    if provider == 'codex':
        destination = config / 'skills' / 'pet' / 'SKILL.md'
        instructions = ('---\nname: pet\ndescription: Launch a terminal worm that reacts to Codex activity.\n---\n\n' + instructions)
    else:
        destination = config / 'commands' / 'pet.md'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(instructions, encoding='utf-8')
    print('Installed {} pet into {}'.format(provider, pet))
    if provider == 'codex':
        print('Restart Codex, review/trust the pet hooks using /hooks, then invoke $pet.')
    else:
        print('Restart Claude Code, then invoke /pet.')

def owns_hook(command, pet):
    normalized = command.replace('\\', '/').lower()
    target = str(pet / 'hook.py').replace('\\', '/').lower()
    # Also migrate legacy commands using the default home-relative path.
    return target in normalized or '~/.claude/pet/hook.py' in normalized

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=['claude', 'codex', 'all'], default='claude')
    parser.add_argument('--config-dir', type=Path, help='Override config directory for one provider')
    args = parser.parse_args()
    if args.provider == 'all' and args.config_dir:
        parser.error('--config-dir requires a single provider')
    for provider in (['claude', 'codex'] if args.provider == 'all' else [args.provider]):
        variable = 'CODEX_HOME' if provider == 'codex' else 'CLAUDE_CONFIG_DIR'
        config = args.config_dir or Path(os.environ.get(variable, str(Path.home() / ('.' + provider))))
        install(provider, config.resolve())

if __name__ == '__main__':
    main()
