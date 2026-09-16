#!/usr/bin/env python3
"""
Pure-Python pixel scene for the deskbot pet. No third-party dependencies
so it runs on any machine with python3 alone. Produces a 2D grid of
(r,g,b) tuples; rendering that grid to a terminal or a PNG is handled
elsewhere (this file only draws).
"""
import math

CANVAS_W = 72
CANVAS_H = 64

# --- palette -----------------------------------------------------------
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
COUCH       = (176, 92, 92)
COUCH_DARK  = (140, 68, 68)
COUCH_CUSH  = (196, 116, 116)
BOT_BODY    = (240, 176, 90)
BOT_DARK    = (200, 138, 62)
BOT_EYE     = (40, 30, 20)
SHADOW      = (0, 0, 0)
BOOK_COVER  = (90, 140, 110)
BOOK_PAGE   = (235, 230, 210)
PAD_BODY    = (70, 70, 80)
PAD_BTN     = (220, 90, 90)

# --- room geometry (pixel space, no rounding headaches) -----------------
BACK  = (36, 26)
RIGHT = (66, 42)
LEFT  = (6, 42)
FRONT = (36, 58)
WALL_H = 22


def new_canvas():
    return [[BG for _ in range(CANVAS_W)] for _ in range(CANVAS_H)]


def set_px(c, x, y, color):
    x, y = int(round(x)), int(round(y))
    if 0 <= y < CANVAS_H and 0 <= x < CANVAS_W:
        c[y][x] = color


def fill_rect(c, x0, y0, x1, y1, color):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            set_px(c, x, y, color)


def fill_circle(c, cx, cy, r, color):
    r2 = r * r
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                set_px(c, x, y, color)


def fill_ellipse(c, cx, cy, rx, ry, color):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            dx = (x - cx) / rx if rx else 0
            dy = (y - cy) / ry if ry else 0
            if dx * dx + dy * dy <= 1.0:
                set_px(c, x, y, color)


def fill_polygon(c, points, color):
    ys = [p[1] for p in points]
    y_min, y_max = int(min(ys)), int(max(ys))
    n = len(points)
    for y in range(y_min, y_max + 1):
        xs = []
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if y1 == y2:
                continue
            if min(y1, y2) <= y < max(y1, y2):
                t = (y - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(c, xs[i], y, xs[i + 1], y, color)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def floor_point(u, v):
    """u: 0(back)->1(right) fraction, v: 0(back)->1(left) fraction."""
    x = BACK[0] + u * (RIGHT[0] - BACK[0]) + v * (LEFT[0] - BACK[0])
    y = BACK[1] + u * (RIGHT[1] - BACK[1]) + v * (LEFT[1] - BACK[1])
    return (x, y)


# named floor spots
COUCH_SPOT = floor_point(0.16, 0.66)
DESK_SPOT = floor_point(0.72, 0.16)     # where the furniture sits
DESK_STAND = floor_point(0.72, 0.36)    # where the bot stands, a step forward


def draw_room(c):
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


def draw_desk(c, screen_on):
    x, y = DESK_SPOT
    fill_rect(c, x - 8, y - 2, x + 8, y + 3, DESK_EDGE)
    fill_rect(c, x - 7, y - 3, x + 7, y + 2, DESK_WOOD)
    fill_rect(c, x - 3, y - 4, x - 2, y - 2, DESK_EDGE)
    fill_rect(c, x + 2, y - 4, x + 3, y - 2, DESK_EDGE)
    mon_color = MONITOR_ON if screen_on else MONITOR_OFF
    fill_rect(c, x - 5, y - 12, x + 5, y - 4, DESK_EDGE)
    fill_rect(c, x - 4, y - 11, x + 4, y - 5, mon_color)
    if screen_on:
        fill_rect(c, x - 3, y - 10, x + 1, y - 9, (200, 240, 245))
        fill_rect(c, x - 3, y - 8, x + 2, y - 7, (200, 240, 245))


def draw_couch(c):
    x, y = COUCH_SPOT
    fill_rect(c, x - 12, y - 6, x + 12, y + 4, COUCH_DARK)
    fill_rect(c, x - 11, y - 8, x - 8, y + 2, COUCH_DARK)   # left armrest
    fill_rect(c, x + 8, y - 8, x + 11, y + 2, COUCH_DARK)   # right armrest
    fill_rect(c, x - 9, y - 4, x + 9, y + 2, COUCH)
    for cx in (x - 5, x, x + 5):
        fill_rect(c, cx - 2, y - 2, cx + 2, y + 1, COUCH_CUSH)


def draw_book(c, x, y):
    fill_rect(c, x - 3, y - 2, x + 3, y + 1, BOOK_COVER)
    fill_rect(c, x - 2, y - 1, x + 2, y, BOOK_PAGE)


def draw_pad(c, x, y):
    fill_rect(c, x - 4, y - 1, x + 4, y + 1, PAD_BODY)
    set_px(c, x - 3, y, PAD_BTN)
    set_px(c, x + 3, y, PAD_BTN)


def draw_bot(c, pos, bob, facing_right=True):
    x, y = pos
    y = y - 5 + bob  # lift bot to stand "on" the floor point, apply bob
    fill_ellipse(c, x, y + 6, 5, 1.6, SHADOW)
    fill_circle(c, x, y, 5, BOT_DARK)
    fill_circle(c, x, y - 1, 5, BOT_BODY)
    ex = 1.6 if facing_right else -1.6
    set_px(c, x - 1.6 + ex, y - 1.5, BOT_EYE)
    set_px(c, x + 1.6 + ex, y - 1.5, BOT_EYE)
    fill_rect(c, x - 0.5, y - 6, x + 0.5, y - 7, BOT_DARK)
    set_px(c, x, y - 8, (250, 210, 130))


def compose_frame(bot_pos, mode, t):
    """
    bot_pos: (x, y) in pixel space, already interpolated by the caller.
    mode: 'at_couch' | 'to_desk' | 'at_desk' | 'to_couch'
    t: seconds, monotonically increasing, used only to animate in place
       (bob, screen flicker, idle prop swap) - never to move the bot.
    """
    c = new_canvas()
    draw_room(c)
    walking = mode in ("to_desk", "to_couch")
    working = mode == "at_desk"
    chilling = mode == "at_couch"

    draw_desk(c, screen_on=working)
    draw_couch(c)

    bob = math.sin(t * 6.0) * 0.8 if walking else (math.sin(t * 3.0) * 0.4 if working else 0)
    facing_right = mode in ("to_desk",) or (mode == "at_desk")
    draw_bot(c, bot_pos, bob, facing_right)

    if chilling:
        cx, cy = COUCH_SPOT
        if int(t / 4) % 2 == 0:
            draw_book(c, cx + 9, cy + 1)
        else:
            draw_pad(c, cx + 9, cy + 1)

    return c
