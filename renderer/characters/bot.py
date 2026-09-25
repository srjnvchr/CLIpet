#!/usr/bin/env python3
"""
The original deskbot: a round little robot that bobs while it walks or
works, and reads/games while idle. Implements the Character contract
compose.py expects:

  draw(c, pos, phase, t)        - draw the character at pos
  idle_activity(c, spot, t)     - optional: extra idle-only drawing,
                                   called with the scene's "idle" spot
"""
import math

import phase as Phase
from canvas import fill_ellipse, fill_circle, fill_rect, set_px

# --- palette ---------------------------------------------------------------
BOT_BODY        = (240, 176, 90)
BOT_DARK        = (200, 138, 62)
BOT_EYE         = (40, 30, 20)
BOT_ANTENNA_TIP = (250, 210, 130)
SHADOW          = (0, 0, 0)
BOOK_COVER      = (90, 140, 110)
BOOK_PAGE       = (235, 230, 210)
PAD_BODY        = (70, 70, 80)
PAD_BTN         = (220, 90, 90)


def draw(c, pos, phase, t):
    x, y = pos
    walking = phase in Phase.WALKING
    working = phase == Phase.WORKING
    bob = math.sin(t * 6.0) * 0.8 if walking else (math.sin(t * 3.0) * 0.4 if working else 0)
    facing_right = phase in (Phase.TO_WORK, Phase.WORKING)

    y = y - 5 + bob  # lift bot to stand "on" the floor point, apply bob
    fill_ellipse(c, x, y + 6, 5, 1.6, SHADOW)
    fill_circle(c, x, y, 5, BOT_DARK)
    fill_circle(c, x, y - 1, 5, BOT_BODY)
    ex = 1.6 if facing_right else -1.6
    set_px(c, x - 1.6 + ex, y - 1.5, BOT_EYE)
    set_px(c, x + 1.6 + ex, y - 1.5, BOT_EYE)
    fill_rect(c, x - 0.5, y - 6, x + 0.5, y - 7, BOT_DARK)
    set_px(c, x, y - 8, BOT_ANTENNA_TIP)


def idle_activity(c, spot, t):
    x, y = spot[0] + 9, spot[1] + 1
    if int(t / 4) % 2 == 0:
        _draw_book(c, x, y)
    else:
        _draw_pad(c, x, y)


def _draw_book(c, x, y):
    fill_rect(c, x - 3, y - 2, x + 3, y + 1, BOOK_COVER)
    fill_rect(c, x - 2, y - 1, x + 2, y, BOOK_PAGE)


def _draw_pad(c, x, y):
    fill_rect(c, x - 4, y - 1, x + 4, y + 1, PAD_BODY)
    set_px(c, x - 3, y, PAD_BTN)
    set_px(c, x + 3, y, PAD_BTN)
