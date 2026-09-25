#!/usr/bin/env python3
"""
Generic frame composer: draws whatever Scene and Character it's given,
using phase.py's neutral vocabulary. This is the only place that assumes
a Scene has draw_background/draw_props/SPOTS and a Character has draw/
(optionally) idle_activity - see renderer/scenes/couch_desk.py and
renderer/characters/bot.py for the reference implementations of each.
"""
from canvas import new_canvas
import phase as Phase


def compose_frame(scene, character, pos, phase, t):
    """
    scene, character: modules implementing the Scene / Character contract.
    pos: (x, y) in the scene's pixel space, already interpolated by the
         caller between scene.SPOTS["idle"] and scene.SPOTS["work"].
    phase: one of the constants in phase.py.
    t: seconds, monotonically increasing, used only to animate in place
       (bob, screen flicker, idle prop swap) - never to move the character.
    """
    c = new_canvas(scene.CANVAS_W, scene.CANVAS_H, scene.BG)
    scene.draw_background(c)
    scene.draw_props(c, phase, t)
    character.draw(c, pos, phase, t)
    if phase == Phase.IDLE:
        idle_activity = getattr(character, "idle_activity", None)
        if idle_activity:
            idle_activity(c, scene.SPOTS["idle"], t)
    return c
