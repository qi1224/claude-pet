#!/usr/bin/env python3
"""Terminal worm pet — crawls left and right in its own pane.

Speed and colour are driven by ~/.claude/pet/state (or $CLAUDE_CONFIG_DIR/pet/state):
  idle        — frozen, white  (Claude waiting for user input)
  waiting     — frozen, white + "?" (awaiting tool confirmation)
  running:1   — slow,  yellow  (thinking / text generation / light tools)
  running:3   — fast,  red     (Bash / Agent / heavy execution)

Platform support: Windows, macOS, Linux, iOS (iSH / a-Shell)
"""

import sys
import os
import time
import shutil
import signal

# UTF-8 output — required for iOS terminals and some Windows codepage configs
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_config_dir = os.environ.get('CLAUDE_CONFIG_DIR', os.path.expanduser('~/.claude'))
STATE_FILE = os.path.join(_config_dir, 'pet', 'state')

SHAPES = {
    (1,  'A'): '_____' + '(o.o)',
    (1,  'B'): '_/\\_' + '(>.<)',
    (1,  'C'): '_____' + '(*.*)',
    (-1, 'A'): '(o.o)' + '_____',
    (-1, 'B'): '(>.<)' + '_/\\_',
    (-1, 'C'): '(*.*)'  + '_____',
}
STEP = 4

# Sleep (seconds) per animation sub-step at each speed level
SPEED_SLEEP = {1: 0.15, 3: 0.05}

# ANSI colours: yellow = light/thinking, bright-red = heavy/execution
YELLOW = '\033[33m'
RED    = '\033[91m'
RESET  = '\033[0m'
SPEED_COLOR = {1: YELLOW, 3: RED}

# Track terminal size for SIGWINCH (iOS orientation changes resize the terminal)
_cols = shutil.get_terminal_size((80, 3)).columns


def _update_cols(*_):
    global _cols
    _cols = shutil.get_terminal_size((80, 3)).columns


def read_state():
    """Return (mode, speed): mode='idle'|'waiting'|'running', speed=1..3."""
    try:
        with open(STATE_FILE) as f:
            s = f.read().strip()
        if s == 'idle':
            return 'idle', 1
        if s == 'waiting':
            return 'waiting', 1
        if s.startswith('running:'):
            return 'running', int(s.split(':')[1])
    except Exception:
        pass
    return 'idle', 1


def draw_text(pos, text, color=''):
    """Write `text` at column `pos`, optionally wrapped in an ANSI colour."""
    cols = _cols
    tlen = len(text)                         # visible width (no ANSI codes)
    pos  = max(0, min(pos, cols - tlen))
    before = ' ' * pos
    after  = ' ' * (cols - pos - tlen)
    body   = f'{color}{text}{RESET}' if color else text
    sys.stdout.write('\r' + before + body + after)
    sys.stdout.flush()


def draw(pos, direction, state, color=''):
    draw_text(pos, SHAPES[(direction, state)], color)


def draw_waiting(pos, direction, is_dizzy):
    """Frozen white frame. Adds '?' in front of the worm if not dizzy."""
    if is_dizzy:
        draw(pos, direction, 'C')
        return
    if direction == 1:
        draw_text(pos, SHAPES[(1, 'A')] + '?')
    else:
        draw_text(max(0, pos - 1), '?' + SHAPES[(-1, 'A')])


def main():
    global _cols
    sys.stdout.write('\033[?25l')  # hide cursor
    sys.stdout.flush()

    def cleanup(*_):
        cols = shutil.get_terminal_size((80, 3)).columns
        sys.stdout.write('\r' + ' ' * cols + '\r\033[?25h')
        sys.stdout.flush()
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    # SIGWINCH: terminal resize (iOS orientation change, window resize)
    if hasattr(signal, 'SIGWINCH'):
        signal.signal(signal.SIGWINCH, _update_cols)

    _cols = shutil.get_terminal_size((80, 3)).columns
    pos = 0
    direction = 1
    is_dizzy = False

    try:
        while True:
            mode, speed = read_state()
            cols = _cols
            wlen = len(SHAPES[(direction, 'A')])  # always 10

            # ── Idle: slow white crawl ────────────────────────────────────────
            if mode == 'idle':
                b_pos = pos + (1 if direction == 1 else 0)
                draw(b_pos, direction, 'B')          # no colour = white
                time.sleep(0.25)
                next_pos = pos + direction * STEP
                if direction == 1 and next_pos + wlen > cols:
                    next_pos = cols - wlen
                    draw(next_pos, direction, 'C')
                    time.sleep(0.5)
                    direction = -1
                elif direction == -1 and next_pos < 0:
                    next_pos = 0
                    draw(next_pos, direction, 'C')
                    time.sleep(0.5)
                    direction = 1
                pos = next_pos
                draw(pos, direction, 'A')
                time.sleep(0.25)
                continue

            # ── Waiting: frozen + "?" indicator ──────────────────────────────
            if mode == 'waiting':
                draw_waiting(pos, direction, is_dizzy)
                time.sleep(0.05)
                continue

            # ── Running: animate at speed-adjusted rate ───────────────────────
            is_dizzy = False
            sl    = SPEED_SLEEP.get(speed, 0.2)
            color = SPEED_COLOR.get(speed, '')

            # State B — curled (offset right by 1 when facing right to pin head)
            b_pos = pos + (1 if direction == 1 else 0)
            draw(b_pos, direction, 'B', color)
            time.sleep(sl)

            # Advance position
            next_pos = pos + direction * STEP

            # Boundary check — dizzy state has no colour (neutral)
            if direction == 1 and next_pos + wlen > cols:
                next_pos = cols - wlen
                is_dizzy = True
                draw(next_pos, direction, 'C')
                time.sleep(0.5)
                direction = -1
            elif direction == -1 and next_pos < 0:
                next_pos = 0
                is_dizzy = True
                draw(next_pos, direction, 'C')
                time.sleep(0.5)
                direction = 1

            pos = next_pos

            # State A — stretched
            draw(pos, direction, 'A', color)
            time.sleep(sl)

    except (KeyboardInterrupt, SystemExit):
        cleanup()


if __name__ == '__main__':
    main()
