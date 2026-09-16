#!/usr/bin/env python3
"""
Shared by mark-busy.py / mark-idle.py / cleanup.py. Deliberately
self-contained (no imports from outside this plugin folder) since only
this folder is guaranteed to move together when the plugin is copied
to ~/.claude/skills/deskbot-pet/.
"""
import os
import json
import tempfile

STATE_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "deskbot-pet-state")
WALK_DURATION = 3.0  # seconds for a full couch<->desk walk


def state_path(session_id):
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "default"
    return os.path.join(STATE_DIR, f"{safe}.json")


def default_state(now):
    return {"mode": "at_couch", "anchor_pos": 0.0, "anchor_time": now, "walk_duration": WALK_DURATION}


def load_state(session_id, now):
    path = state_path(session_id)
    try:
        with open(path) as f:
            data = json.load(f)
        data.setdefault("walk_duration", WALK_DURATION)
        return data
    except (OSError, json.JSONDecodeError):
        return default_state(now)


def save_state(session_id, state):
    os.makedirs(STATE_DIR, exist_ok=True)
    path = state_path(session_id)
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR)
    with os.fdopen(fd, "w") as f:
        json.dump(state, f)
    os.replace(tmp, path)  # atomic on POSIX, avoids a half-written read


def interpolated_pos(state, now):
    """0.0 = at couch, 1.0 = at desk."""
    mode = state.get("mode", "at_couch")
    if mode == "at_couch":
        return 0.0
    if mode == "at_desk":
        return 1.0
    elapsed = now - state.get("anchor_time", now)
    duration = state.get("walk_duration", WALK_DURATION)
    if mode == "to_desk":
        return min(1.0, state.get("anchor_pos", 0.0) + elapsed / duration)
    if mode == "to_couch":
        return max(0.0, state.get("anchor_pos", 1.0) - elapsed / duration)
    return 0.0


def read_session_id(input_json):
    try:
        data = json.loads(input_json)
        return str(data.get("session_id") or "default")
    except json.JSONDecodeError:
        return "default"
