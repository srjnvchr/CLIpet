#!/bin/bash
# Launches (or attaches to) a tmux session with the deskbot-pet pinned
# in a pane at the top and a normal shell below it, where you run
# `claude` yourself. The pet and Claude Code are two independent
# processes; they only communicate through the small state file that
# the deskbot-pet plugin's hooks write.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PET_PY="$SCRIPT_DIR/renderer/pet.py"
SESSION="deskbot"
PET_PANE_LINES=34

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is required for the pinned pane. Install it, e.g.:" >&2
  echo "  macOS:   brew install tmux" >&2
  echo "  Ubuntu:  sudo apt install tmux" >&2
  echo "  Windows: use WSL, then the Ubuntu instructions above" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to run the renderer." >&2
  exit 1
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session '$SESSION' already exists, attaching..."
  exec tmux attach -t "$SESSION"
fi

tmux new-session -d -s "$SESSION" -n main
tmux split-window -v -b -l "$PET_PANE_LINES" -t "${SESSION}:main" "python3 '$PET_PY'"
tmux select-pane -t "${SESSION}:main.1"   # focus the shell pane, not the pet
exec tmux attach -t "$SESSION"
