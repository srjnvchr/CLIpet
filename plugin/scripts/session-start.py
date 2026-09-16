#!/usr/bin/env python3
"""Fires on SessionStart."""
import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from state_lib import default_state, save_state, read_session_id

raw = sys.stdin.read()
session_id = read_session_id(raw)
save_state(session_id, default_state(time.time()))
sys.exit(0)
