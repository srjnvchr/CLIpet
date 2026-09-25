#!/usr/bin/env python3
"""
The original deskbot-pet room: a couch on one side, a desk with a
monitor on the other. Implements the Scene contract compose.py expects:

  CANVAS_W, CANVAS_H  - pixel dimensions of this scene
  BG                  - background color new_canvas() is filled with
  SPOTS               - {"idle": (x, y), "work": (x, y)} in pixel space
  draw_background(c)          - static geometry, drawn every frame first
  draw_props(c, phase, t)     - state-dependent scene elements (monitor)
"""
import phase as Phase
from canvas import fill_rect, fill_polygon, set_px, lerp

CANVAS_W = 72
CANVAS_H = 64

# --- palette -------------------------------------------------------------
BG          = (18, 18, 24)
FLOOR       = (196, 158, 108)
FLOOR_LINE  = (168, 130, 82)
WALL_LEFT   = (99, 121, 146)
WALL_RIGHT  = (78, 98, 122)
BASEBOARD   = (60, 46, 34)
DESK_WOOD   = (120, 84, 56)
DESK_EDGE   = (90, 62, 40)
MONITOR_OFF = (40, 42, 48)
MONITOR_ON  = (120, 200, 210)
SCREEN_GLOW = (200, 240, 245)
COUCH       = (176, 92, 92)
COUCH_DARK  = (140, 68, 68)
COUCH_CUSH  = (196, 116, 116)

# --- room geometry (pixel space, no rounding headaches) -------------------
BACK  = (36, 26)
RIGHT = (66, 42)
LEFT  = (6, 42)
FRONT = (36, 58)
WALL_H = 22


def floor_point(u, v):
    """u: 0(back)->1(right) fraction, v: 0(back)->1(left) fraction."""
    x = BACK[0] + u * (RIGHT[0] - BACK[0]) + v * (LEFT[0] - BACK[0])
    y = BACK[1] + u * (RIGHT[1] - BACK[1]) + v * (LEFT[1] - BACK[1])
    return (x, y)


COUCH_SPOT = floor_point(0.16, 0.66)
DESK_SPOT = floor_point(0.72, 0.16)     # where the furniture sits
DESK_STAND = floor_point(0.72, 0.36)    # where the character stands, a step forward

SPOTS = {"idle": COUCH_SPOT, "work": DESK_STAND}


def draw_background(c):
    _draw_room(c)
    _draw_couch(c)


def draw_props(c, phase, t):
    _draw_desk(c, screen_on=phase == Phase.WORKING)


def _draw_room(c):
    fill_polygon(c, [BACK, RIGHT, FRONT, LEFT], FLOOR)
    # a couple of floor plank lines for texture
    for v in (0.35, 0.65):
        p1 = floor_point(0.0, v)
        p2 = floor_point(1.0, v)
        for t in [i / 40 for i in range(41)]:
            set_px(c, *lerp(p1, p2, t), FLOOR_LINE)
    back_top = (BACK[0], BACK[1] - WALL_H)
    left_top = (LEFT[0], LEFT[1] - WALL_H)
    right_top = (RIGHT[0], RIGHT[1] - WALL_H)
    fill_polygon(c, [back_top, left_top, LEFT, BACK], WALL_LEFT)
    fill_polygon(c, [back_top, right_top, RIGHT, BACK], WALL_RIGHT)
    # baseboards where wall meets floor
    for t in [i / 40 for i in range(41)]:
        set_px(c, *lerp(BACK, LEFT, t), BASEBOARD)
        set_px(c, *lerp(BACK, RIGHT, t), BASEBOARD)


def _draw_desk(c, screen_on):
    x, y = DESK_SPOT
    fill_rect(c, x - 8, y - 2, x + 8, y + 3, DESK_EDGE)
    fill_rect(c, x - 7, y - 3, x + 7, y + 2, DESK_WOOD)
    fill_rect(c, x - 3, y - 4, x - 2, y - 2, DESK_EDGE)
    fill_rect(c, x + 2, y - 4, x + 3, y - 2, DESK_EDGE)
    mon_color = MONITOR_ON if screen_on else MONITOR_OFF
    fill_rect(c, x - 5, y - 12, x + 5, y - 4, DESK_EDGE)
    fill_rect(c, x - 4, y - 11, x + 4, y - 5, mon_color)
    if screen_on:
        fill_rect(c, x - 3, y - 10, x + 1, y - 9, SCREEN_GLOW)
        fill_rect(c, x - 3, y - 8, x + 2, y - 7, SCREEN_GLOW)


def _draw_couch(c):
    x, y = COUCH_SPOT
    fill_rect(c, x - 12, y - 6, x + 12, y + 4, COUCH_DARK)
    fill_rect(c, x - 11, y - 8, x - 8, y + 2, COUCH_DARK)   # left armrest
    fill_rect(c, x + 8, y - 8, x + 11, y + 2, COUCH_DARK)   # right armrest
    fill_rect(c, x - 9, y - 4, x + 9, y + 2, COUCH)
    for cx in (x - 5, x, x + 5):
        fill_rect(c, cx - 2, y - 2, cx + 2, y + 1, COUCH_CUSH)
