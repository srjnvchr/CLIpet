#!/usr/bin/env python3
"""
A minimal second character, mostly here to prove the Character contract
compose.py expects is actually swappable independently of the scene: a
small hovering orb. It has no idle_activity - that hook is optional,
compose.py just skips it when a character doesn't define one.
"""
import math

import phase as Phase
from canvas import fill_circle, fill_ellipse, set_px

ORB_BODY = (150, 130, 220)
ORB_CORE = (230, 220, 255)
ORB_EYE  = (30, 20, 40)
SHADOW   = (0, 0, 0)


def draw(c, pos, phase, t):
    x, y = pos
    walking = phase in Phase.WALKING
    working = phase == Phase.WORKING
    bob = math.sin(t * 6.0) * 0.6 if (walking or working) else math.sin(t * 4.0) * 1.2
    y = y - 8 + bob

    fill_ellipse(c, x, y + 9, 4, 1.3, SHADOW)
    fill_circle(c, x, y, 4, ORB_BODY)
    fill_circle(c, x, y - 1, 2.4, ORB_CORE)
    ex = 1.2 if phase in (Phase.TO_WORK, Phase.WORKING) else -1.2
    set_px(c, x + ex, y - 1, ORB_EYE)
