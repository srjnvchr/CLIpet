#!/usr/bin/env python3
"""
Runtime (stdlib-only) loader for image-derived scenes/characters. A
"pack" is a folder under renderer/packs/<name>/ holding background.json
and/or character.json - plain pixel data, no PIL needed to read it back.

Generate a pack from your own artwork with design/import_image.py (that
script is the only place PIL is required); see renderer/packs/README.md
for the JSON shape if you'd rather hand-edit or generate one yourself.
"""
import json
import math
import os

import phase as Phase
from canvas import set_px

PACKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "packs")


def _load(pack_name, filename):
    path = os.path.join(PACKS_DIR, pack_name, filename)
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return json.load(f)


def pack_scene(pack_name):
    data = _load(pack_name, "background.json")
    return _ImageScene(data) if data else None


def pack_character(pack_name):
    data = _load(pack_name, "character.json")
    return _ImageCharacter(data) if data else None


class _ImageScene:
    """Scene backed by a single static image. draw_props is a no-op -
    a flat picture has nothing state-dependent to redraw each frame,
    unlike scenes/couch_desk.py's monitor-on/off desk."""

    def __init__(self, data):
        self.CANVAS_W = data["width"]
        self.CANVAS_H = data["height"]
        self._rows = data["pixels"]
        first_px = next((px for row in self._rows for px in row if px is not None), (0, 0, 0))
        self.BG = tuple(first_px)
        spots = data.get("spots") or {}
        self.SPOTS = {
            "idle": tuple(spots.get("idle", (self.CANVAS_W * 0.25, self.CANVAS_H * 0.8))),
            "work": tuple(spots.get("work", (self.CANVAS_W * 0.75, self.CANVAS_H * 0.8))),
        }

    def draw_background(self, c):
        for y, row in enumerate(self._rows):
            for x, px in enumerate(row):
                if px is not None:
                    c[y][x] = tuple(px)

    def draw_props(self, c, phase, t):
        pass


class _ImageCharacter:
    """Character backed by a single static sprite, mirrored left/right
    by facing direction and bobbing the same way characters/bot.py does.
    Pixels stored as null (transparent) are skipped so the scene shows
    through around the sprite's silhouette."""

    def __init__(self, data):
        self._w = data["width"]
        self._h = data["height"]
        self._rows = data["pixels"]
        ax, ay = data.get("anchor", (self._w / 2, self._h - 1))
        self._ax, self._ay = ax, ay

    def draw(self, c, pos, phase, t):
        x0, y0 = pos
        walking = phase in Phase.WALKING
        working = phase == Phase.WORKING
        bob = math.sin(t * 6.0) * 0.8 if walking else (math.sin(t * 3.0) * 0.4 if working else 0)
        facing_right = phase in (Phase.TO_WORK, Phase.WORKING)
        top_left_x = x0 - self._ax
        top_left_y = y0 - self._ay + bob
        for sy, row in enumerate(self._rows):
            for sx, px in enumerate(row):
                if px is None:
                    continue
                dx = sx if facing_right else (self._w - 1 - sx)
                set_px(c, top_left_x + dx, top_left_y + sy, tuple(px))
