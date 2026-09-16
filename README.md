# deskbot-pet

An animated pixel-art companion that lives in a pinned tmux pane above
your Claude Code session. It sits on the couch reading (or gaming)
while idle, and walks over to the desk to work whenever you give
Claude something to do. If a new task lands while it's mid-walk, it
turns around from exactly where it is instead of teleporting.

## Architecture (why it's two folders, not one plugin)

Claude Code's own UI has no "pinned pane" extension point, and its
statusLine only lives at the bottom and can't do real animation
reliably. So this splits the problem:

- **`plugin/`** — a tiny Claude Code plugin. Its only job is hooks
  that write `{mode, anchor_pos, anchor_time, walk_duration}` to a
  small JSON file per session. `mode` is one of `at_couch`,
  `to_desk`, `at_desk`, `to_couch`.
- **`renderer/`** — a standalone Python script (`pet.py`) that has
  nothing to do with Claude Code. It polls that JSON file ~6-7 times
  a second, interpolates the walk from the timestamp, and draws the
  scene as 24-bit-color half-block characters (`▀`), a technique that
  works in plain PowerShell and GNOME Terminal, not just fancy ones.
- **`start.sh`** — wires the two together with tmux: pet pinned in a
  pane on top, a normal shell below where you run `claude` yourself.

The plugin and the renderer never talk to each other directly, they
only agree on a file. That's what makes the animation smooth and
independent of whatever Claude Code's own UI is doing.

## Requirements

- `python3` (stdlib only, no pip installs)
- `tmux`
- A terminal that does 24-bit color (nearly all of them do; see the
  table from our last chat if you want the details on which ones also
  support Sixel/Kitty image protocols on top of this — you don't need
  those for this project, half-blocks are enough)

**Windows users**: tmux doesn't run natively. Do this whole thing
inside WSL, including running `claude` itself from the same WSL
shell — if Claude Code runs on native Windows while the pet runs in
WSL, they'll write to two different filesystems and never see each
other's state file.

## Install

```bash
mkdir -p ~/.claude/skills
cp -r plugin ~/.claude/skills/deskbot-pet
chmod +x ~/.claude/skills/deskbot-pet/scripts/*.py
```

That's the whole install, the plugin has no settings to wire up (no
statusLine, nothing to add to `settings.json`), it just needs to exist
under `~/.claude/skills/` so Claude Code loads its hooks.

## Run

From this project folder:

```bash
./start.sh
```

This opens tmux with the pet pinned on top and a shell below. In the
bottom pane, run `claude` as you normally would, and give it
something to do. First run: the bot starts on the couch. Detach with
`Ctrl+b d` any time; `./start.sh` again re-attaches to the same
session.

## Customizing

- **Walk speed**: `plugin/scripts/state_lib.py`, the `WALK_DURATION`
  constant (seconds for a full couch <-> desk walk). This is the only
  place to change it, `pet.py` just reads whatever duration the state
  file says.
- **Colors**: `renderer/scene.py`, the palette constants near the top
  (`BOT_BODY`, `COUCH`, `FLOOR`, etc.) are plain `(r, g, b)` tuples.
- **Room layout / size**: also in `scene.py`. `BACK`, `LEFT`, `RIGHT`,
  `FRONT` are the four floor corners in pixel space, `WALL_H` is wall
  height. `CANVAS_W`/`CANVAS_H` set the overall size — if you change
  those, rescale the corner coordinates proportionally too, they're
  absolute, not relative.
- **Frame rate**: `renderer/pet.py`, the `TICK` constant (seconds
  between frames). 0.15 is a reasonable balance; going much below
  that mostly just burns CPU without looking smoother at this
  resolution.
- **Preview without tmux**: `design/preview.py` renders any state to a
  PNG using PIL, if you have it installed, useful for iterating on the
  art without waiting on a live session. Not needed to run the actual
  pet, that's PNG-export only.

## Uninstall

```bash
claude plugin disable deskbot-pet@skills-dir
rm -rf ~/.claude/skills/deskbot-pet
tmux kill-session -t deskbot
```
