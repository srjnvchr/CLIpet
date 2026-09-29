# Changelog

Notable updates to deskbot-pet, newest first. This project has no
version numbers yet, so entries are dated instead.

## 2026-09-29 — Planned: standardized pack format v2

Decided the direction for making custom scene/pet art actually
portable across authors, instead of the current pack format's
assumption that every scene looks roughly like `couch_desk`. Not yet
implemented — tracked here so the decisions aren't lost, and written up
in the README's "Roadmap" section under Customizing.

Key decisions:
- A pack's two spots (`idle` / `work`) are declared per-scene, either
  in `pack.json` or via magenta/cyan marker pixels in the source image
  — never assumed from a fixed layout.
- An optional `path` of waypoints lets the walk avoid furniture/walls
  instead of assuming a straight line between the two spots.
- Facing direction is derived from the path, not hardcoded to "right
  means heading to work" the way `characters/bot.py` does today.
- Pets get a fixed 16x16 frame size with three optional animation
  states (`idle`, `walk`, `work`) as rows of a sprite sheet; a single
  static image remains valid and falls back to the current procedural
  bob.
- A `renderer/config.json` (checked for changes every frame, so no
  restart needed) picks the active scene/character, with env vars still
  taking precedence for quick overrides.
- Nearest-neighbor resampling replaces `import_image.py`'s current
  LANCZOS, which blurs pixel art on resize.

## 2026-09-25 — Image-to-pack pipeline

`design/import_image.py` (PIL, dev-time only) turns an image into a
pack — `background.json` and/or `character.json` under
`renderer/packs/<name>/` — that `renderer/image_asset.py` (stdlib only)
loads at runtime. `scenes/` and `characters/` registries fall back to
packs for any name not built in, so a pack can supply just one half and
pair with a built-in for the other.

## 2026-09-25 — Renderer split into swappable scenes and characters

Extracted generic pixel primitives into `renderer/canvas.py` and a
neutral `IDLE`/`TO_WORK`/`WORKING`/`TO_HOME` vocabulary into
`renderer/phase.py`, so the room (`scenes/couch_desk.py`) and the bot
(`characters/bot.py`) no longer need to know about each other or about
the plugin's own mode strings. `pet.py` picks a pair via
`PET_SCENE`/`PET_CHARACTER` env vars, defaulting to the originals.
`plugin/` (hooks, state file format) was untouched.

## 2026-09-16 — Fixed render jitter and WezTerm pane crash

- Render canvas now crops to the terminal's live size each frame
  instead of a fixed 72x64, so resizing the window doesn't jitter.
- `start.ps1` clamps the pet pane height to what the current WezTerm
  window can actually fit, instead of a hardcoded 34 rows that crashed
  pseudo-console creation on smaller windows.

## 2026-09-16 — Initial commit
