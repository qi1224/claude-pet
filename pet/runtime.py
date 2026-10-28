"""Shared state paths and atomic writes, Python 3.8+."""
import hashlib
import os
from pathlib import Path
import tempfile

def root_dir(provider):
    variable = 'CODEX_HOME' if provider == 'codex' else 'CLAUDE_CONFIG_DIR'
    return Path(os.environ.get(variable, str(Path.home() / ('.' + provider)))) / 'pet'

def session_path(root, session):
    if not session:
        return root / 'state'
    key = hashlib.sha256(str(session).encode('utf-8')).hexdigest()
    return root / 'sessions' / (key + '.state')

def write_atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix='.pet-', dir=str(path.parent))
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(value)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
