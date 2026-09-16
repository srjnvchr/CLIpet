#!/usr/bin/env python3
"""
Standalone pet renderer. Run this in its own tmux pane (see start.sh).
It does not talk to Claude Code directly - it just polls the small
state file that the plugin's hooks write to, and animates from that.
Ctrl+C to stop.
"""
import os
import sys
import time
import glob
import json
import signal
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import compose_frame, COUCH_SPOT, DESK_STAND, lerp
from ansi import (
    canvas_to_ansi, HOME, HIDE_CURSOR, SHOW_CURSOR, RESET,
    ENTER_ALT_SCREEN, EXIT_ALT_SCREEN, CLEAR,
)

STATE_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "deskbot-pet-state")
TICK = 0.15  # seconds between frames, ~6-7 fps

CAPTIONS = {
    "at_couch": None,          # set per idle sub-frame below
    "to_desk": "heading to the desk...",
    "at_desk": "working...",
    "to_couch": "heading back to the couch...",
}


def latest_state():
    """Pick whichever session's state file changed most recently.
    Good enough for a single active Claude Code session in this pane;
    see README if you run several sessions at once."""
    files = glob.glob(os.path.join(STATE_DIR, "*.json"))
    if not files:
        return None, None
    newest = max(files, key=os.path.getmtime)
    try:
        with open(newest) as f:
            return newest, json.load(f)
    except (OSError, json.JSONDecodeError):
        return None, None


def settle_if_arrived(path, state, pos):
    """Once the interpolated walk reaches an endpoint, write that back
    as the real mode (at_desk / at_couch) so the monitor-on state and
    the idle reading/gaming props switch on correctly, and so a
    restarted pet.py picks up the right resting state."""
    mode = state.get("mode")
    if mode == "to_desk" and pos >= 1.0 and path:
        state = {**state, "mode": "at_desk", "anchor_pos": 1.0}
        _atomic_write(path, state)
    elif mode == "to_couch" and pos <= 0.0 and path:
        state = {**state, "mode": "at_couch", "anchor_pos": 0.0}
        _atomic_write(path, state)
    return state


def _atomic_write(path, state):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d)
    with os.fdopen(fd, "w") as f:
        json.dump(state, f)
    os.replace(tmp, path)


def interpolated_pos(state, now):
    mode = state.get("mode", "at_couch")
    anchor_pos = state.get("anchor_pos", 0.0)
    anchor_time = state.get("anchor_time", now)
    duration = state.get("walk_duration", 3.0)

    if mode == "at_couch":
        return 0.0
    if mode == "at_desk":
        return 1.0
    elapsed = now - anchor_time
    if mode == "to_desk":
        return min(1.0, anchor_pos + elapsed / duration)
    if mode == "to_couch":
        return max(0.0, anchor_pos - elapsed / duration)
    return 0.0


def caption_for(mode, t):
    if mode == "at_couch":
        return "reading a book..." if int(t / 4) % 2 == 0 else "playing a game..."
    return CAPTIONS.get(mode, "")


def main():
    # The alternate screen buffer is what full-screen terminal apps
    # (vim, less, htop) use: a separate canvas with no scrollback of
    # its own. Without it, any frame taller than the visible window
    # permanently scrolls the previous frame's top rows into your
    # normal scrollback instead of being overwritten - which is
    # exactly the "endless stream of stacked frames" bug.
    sys.stdout.write(ENTER_ALT_SCREEN + HIDE_CURSOR + CLEAR + HOME)
    sys.stdout.flush()

    def handle_signal(*_):
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        t0 = time.time()
        while True:
            now = time.time()
            path, state = latest_state()
            if state is None:
                state = {"mode": "at_couch", "anchor_pos": 0.0, "anchor_time": now}

            pos = interpolated_pos(state, now)
            state = settle_if_arrived(path, state, pos)
            bot_pos = lerp(COUCH_SPOT, DESK_STAND, pos)
            t = now - t0
            canvas = compose_frame(bot_pos, state.get("mode", "at_couch"), t)

            frame = canvas_to_ansi(canvas)
            caption = caption_for(state.get("mode", "at_couch"), t)
            # No trailing newline after the caption - that would push
            # the cursor one row past the last line of content for no
            # reason, and inside a tight pane that's one more line
            # than necessary competing for space.
            sys.stdout.write(HOME + frame + "\n" + RESET + caption.ljust(40))
            sys.stdout.flush()
            time.sleep(TICK)
    finally:
        # Runs exactly once, however we get here: Ctrl+C, SIGTERM, or
        # an unexpected crash - always leave the terminal the way we
        # found it.
        sys.stdout.write(SHOW_CURSOR + EXIT_ALT_SCREEN + RESET)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
