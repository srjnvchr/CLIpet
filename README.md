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

`renderer/` splits into three independent pieces: a **scene** (the room),
a **character** (the thing walking around in it), and a generic
**composer** that draws whatever pair of those it's given. Pick which
pair `pet.py` uses with two env vars (both optional, default to the
originals):

```bash
PET_SCENE=couch_desk PET_CHARACTER=bot ./start.sh   # the defaults
PET_CHARACTER=orb ./start.sh                        # try the other character
```

- **Adding a scene**: create `renderer/scenes/your_scene.py` exposing
  `CANVAS_W`, `CANVAS_H`, `BG`, `SPOTS = {"idle": (x, y), "work": (x, y)}`,
  `draw_background(c)` (static geometry), and `draw_props(c, phase, t)`
  (anything that reacts to `phase` — see `phase.py` for the vocabulary).
  Register it in `renderer/scenes/__init__.py`'s `SCENES` dict.
  `renderer/scenes/couch_desk.py` is the reference implementation — its
  palette and room-corner constants (`BACK`, `LEFT`, `RIGHT`, `FRONT`,
  `WALL_H`) live there now, not in a shared `scene.py`.
- **Adding a character**: create `renderer/characters/your_character.py`
  exposing `draw(c, pos, phase, t)` and, optionally, `idle_activity(c, spot, t)`
  (only called when idle — a character without one, like
  `renderer/characters/orb.py`, just doesn't do anything extra while idle).
  Register it in `renderer/characters/__init__.py`'s `CHARACTERS` dict.
  `renderer/characters/bot.py` is the reference implementation.
- **Shared drawing primitives**: `renderer/canvas.py` (`fill_rect`,
  `fill_circle`, `fill_polygon`, etc.) — scene- and character-agnostic,
  used by both sides.
- **Using your own art instead of code**: you don't have to hand-write a
  scene/character module at all — turn an image into one with:
  ```bash
  python design/import_image.py room.png --as background --name myroom
  python design/import_image.py cat.png  --as character --name myroom
  PET_SCENE=myroom PET_CHARACTER=myroom ./start.sh
  ```
  This writes `renderer/packs/myroom/{background,character}.json`; a
  pack only needs whichever half you made art for, and mixes freely
  with the built-ins (`PET_CHARACTER=myroom` with the default
  `couch_desk` scene works fine). `design/import_image.py` is the only
  place PIL is needed — `pet.py` itself stays stdlib-only, reading the
  plain JSON these packs are made of. See `renderer/packs/README.md`
  for the file format if you'd rather hand-edit or generate one
  yourself.

  Current limitation: a pack's `idle`/`work` spots default to fixed
  fractions of the image (roughly the bottom-left/right quarters) and
  the walk is always a straight line between them, so art with the
  desk on the left or furniture in the way won't look right yet. See
  "Roadmap" below for the fix in progress.
- **Walk speed**: `plugin/scripts/state_lib.py`, the `WALK_DURATION`
  constant (seconds for a full idle <-> work walk). This is the only
  place to change it, `pet.py` just reads whatever duration the state
  file says.
- **Frame rate**: `renderer/pet.py`, the `TICK` constant (seconds
  between frames). 0.15 is a reasonable balance; going much below
  that mostly just burns CPU without looking smoother at this
  resolution.
- **Preview without tmux**: `design/preview.py` renders any state to a
  PNG using PIL, if you have it installed, useful for iterating on the
  art without waiting on a live session. Not needed to run the actual
  pet, that's PNG-export only.

## Roadmap: standardizing custom art

The pack format above works, but it assumes every scene is laid out
enough like `couch_desk` that a fixed corner of the image is a
reasonable guess for "idle" and "work". That's not a real standard —
it breaks for a scene with the desk on the left, or furniture between
the two spots. The plan to fix it, decided but not yet built:

- **Spots are declared, never guessed from a fixed layout.** Either in
  `pack.json`, or by painting a pure-magenta pixel for `idle` and a
  pure-cyan pixel for `work` directly in the source image — the
  importer detects and removes them before resizing. A pack without
  either gets today's corner-fraction default plus a warning, not a
  silent guess.
- **An optional `path` of waypoints** (also in `pack.json`) lets the
  walk follow a polyline from `idle` to `work` instead of a straight
  line, for scenes where a straight line would cut through a wall.
- **Facing direction comes from the path**, not a hardcoded "right
  means heading to work" — the assumption `characters/bot.py` makes
  today, which is wrong for a scene where work is on the left.
- **Pets get a fixed 16x16 frame** authored facing right (mirrored for
  left), transparent background, feet at bottom-center — the one
  thing that has to be consistent for a pet to work in any scene. A
  sprite sheet can add `idle`/`walk`/`work` animation rows; a single
  static image stays valid and keeps today's procedural bob as a
  fallback.
- **`renderer/config.json`** picks the active scene/character (checked
  for changes every frame, no restart needed), with the
  `PET_SCENE`/`PET_CHARACTER` env vars still available for quick
  overrides.
- **Nearest-neighbor resampling** replaces `import_image.py`'s current
  `LANCZOS`, which blurs pixel art on resize.

See `CHANGELOG.md` for the full write-up of these decisions and the
project's history in general.

## Uninstall

```bash
claude plugin disable deskbot-pet@skills-dir
rm -rf ~/.claude/skills/deskbot-pet
tmux kill-session -t deskbot
```
