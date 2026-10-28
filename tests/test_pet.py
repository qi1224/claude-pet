import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pet'))
import runtime
import launch

spec = importlib.util.spec_from_file_location('installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class PetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pet test ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def hook(self, event, session='a', tool='Bash', provider='codex'):
        subprocess.run([sys.executable, str(ROOT / 'pet/hook.py'), '--provider', provider,
                        '--root', str(self.root)], input=json.dumps({
                            'hook_event_name': event, 'session_id': session,
                            'tool_name': tool}), text=True, capture_output=True, check=True)
        return runtime.session_path(self.root, session).read_text()

    def test_real_hook_lifecycle(self):
        for provider in ['claude', 'codex']:
            for event, value in [('SessionStart', 'idle'), ('UserPromptSubmit', 'running:1'),
                                 ('PreToolUse', 'running:3'), ('PermissionRequest', 'waiting'),
                                 ('PostToolUse', 'running:1'), ('Stop', 'idle'),
                                 ('Interrupt', 'idle'), ('SessionEnd', 'idle')]:
                with self.subTest(provider=provider, event=event):
                    self.assertEqual(self.hook(event, provider=provider), value)

    def test_sessions_and_light_tools(self):
        self.hook('PermissionRequest', session='a')
        self.assertEqual(self.hook('PreToolUse', session='../b', tool='apply_patch'), 'running:1')
        self.assertEqual(runtime.session_path(self.root, 'a').read_text(), 'waiting')
        self.assertEqual(runtime.session_path(self.root, '../b').parent, self.root / 'sessions')

    def test_install_preserves_other_hooks_and_is_repeatable(self):
        for provider, filename in [('claude', 'settings.json'), ('codex', 'hooks.json')]:
            config = self.root / provider
            config.mkdir()
            settings = config / filename
            unrelated = {'type': 'command', 'command': 'python other/hook.py'}
            old = {'type': 'command', 'command': str(config / 'pet/hook.py') + ' pre'}
            settings.write_text(json.dumps({'custom': 42, 'hooks': {'PreToolUse': [
                {'matcher': 'Bash', 'hooks': [unrelated, old]}]}}))
            installer.install(provider, config)
            installer.install(provider, config)
            result = json.loads(settings.read_text())
            self.assertEqual(result['custom'], 42)
            groups = result['hooks']['PreToolUse']
            self.assertEqual(groups[0]['hooks'], [unrelated])
            self.assertEqual(len(groups), 2)
            # Exercise the installed hook command through the actual host shell.
            command = groups[1]['hooks'][0]['command']
            subprocess.run(command, shell=True, input=json.dumps({
                'hook_event_name': 'PreToolUse', 'session_id': 'installed', 'tool_name': 'Bash'}),
                text=True, capture_output=True, check=True)
            state = runtime.session_path(config / 'pet', 'installed')
            self.assertEqual(state.read_text(), 'running:3')
            command = [sys.executable, str(config / 'pet/launch.py'), '--provider', provider,
                       '--root', str(config / 'pet'), '--session-id', 'installed', '--dry-run']
            planned = json.loads(subprocess.check_output(command, text=True))
            self.assertEqual(planned[-1], str(state))

    def test_invalid_settings_not_overwritten(self):
        path = self.root / 'hooks.json'
        path.write_text('{bad')
        with self.assertRaises(ValueError):
            installer.install('codex', self.root)
        self.assertEqual(path.read_text(), '{bad')
        self.assertFalse((self.root / 'pet').exists())

    def test_launch_backends_and_fallback(self):
        with patch('launch.shutil.which', return_value='/bin/tool'):
            command = launch.launch_command(Path('worm.py'), Path('state file'), 'win32', {})
            self.assertEqual(command[0], 'wt.exe')
            self.assertEqual(command[-1], 'state file')
            command = launch.launch_command(Path('worm.py'), Path('state file'), 'linux', {'TMUX': '1'})
            self.assertEqual(command[0], 'tmux')
            self.assertIn("'state file'", command[-1])
        with patch('launch.shutil.which', return_value=None):
            self.assertEqual(launch.launch_command(Path('worm.py'), Path('state'), 'linux', {})[0], sys.executable)

    def test_latest_session_and_legacy_explicit_file(self):
        self.hook('UserPromptSubmit', session='latest')
        planned = json.loads(subprocess.check_output([
            sys.executable, str(ROOT / 'pet/launch.py'), '--root', str(self.root),
            '--dry-run'], text=True))
        self.assertEqual(planned[-1], str(runtime.session_path(self.root, 'latest').resolve()))
        state = self.root / 'custom.state'
        subprocess.run([sys.executable, str(ROOT / 'pet/hook.py'), 'pre',
                        '--state-file', str(state)], input='{"tool_name":"Bash"}',
                       text=True, capture_output=True, check=True)
        self.assertEqual(state.read_text(), 'running:3')

    def test_animation_real_process(self):
        # Capture real ANSI frames in each mode; no terminal windows are needed.
        state = self.root / 'state'
        for value, expected in [('idle', '(o.o)'), ('waiting', '?'),
                                ('running:1', '\x1b[33m'), ('running:3', '\x1b[91m')]:
            state.write_text(value)
            process = subprocess.Popen([sys.executable, str(ROOT / 'pet/worm.py'),
                                        '--state-file', str(state)], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            try:
                output, error = process.communicate(timeout=0.8)
                self.fail('Animation exited unexpectedly: ' + repr(error))
            except subprocess.TimeoutExpired:
                process.terminate()
                output, error = process.communicate(timeout=5)
            self.assertIn(expected, output.decode('utf-8'))
            self.assertFalse(error)

if __name__ == '__main__':
    unittest.main()
