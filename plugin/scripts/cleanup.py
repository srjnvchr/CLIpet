#!/usr/bin/env python3
"""Fires on SessionEnd: don't leave stale state files lying around."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from state_lib import state_path, read_session_id

raw = sys.stdin.read()
session_id = read_session_id(raw)
try:
    os.remove(state_path(session_id))
except OSError:
    pass
sys.exit(0)
