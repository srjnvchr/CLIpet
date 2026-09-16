#!/usr/bin/env python3
"""Fires on Stop: Claude just finished responding."""
import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from state_lib import load_state, save_state, interpolated_pos, read_session_id

raw = sys.stdin.read()
session_id = read_session_id(raw)
now = time.time()

state = load_state(session_id, now)
mode = state.get("mode", "at_couch")

if mode in ("at_desk", "to_desk"):
    pos = interpolated_pos(state, now)  # 1.0 if at_desk, current spot if turning around
    save_state(session_id, {
        "mode": "to_couch",
        "anchor_pos": pos,
        "anchor_time": now,
        "walk_duration": state.get("walk_duration", 3.0),
    })
# else already heading to / at the couch: leave it alone

sys.exit(0)
