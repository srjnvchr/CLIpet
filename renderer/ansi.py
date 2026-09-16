#!/usr/bin/env python3
"""
Renders a pixel canvas (list of rows of (r,g,b)) to ANSI text using the
upper-half-block trick: each terminal cell shows two vertical pixels,
foreground = top pixel, background = bottom pixel. Pure ANSI SGR codes,
no Sixel/Kitty/iTerm2 protocol required, so it works in plain
PowerShell, GNOME Terminal, macOS Terminal.app, etc. - not just the
fancy terminals.
"""

RESET = "\x1b[0m"
HOME = "\x1b[H"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
ENTER_ALT_SCREEN = "\x1b[?1049h"
EXIT_ALT_SCREEN = "\x1b[?1049l"
CLEAR = "\x1b[2J"


def _sgr(fg, bg):
    fr, fg_, fb = fg
    br, bg_, bb = bg
    return f"\x1b[38;2;{fr};{fg_};{fb};48;2;{br};{bg_};{bb}m"


def canvas_to_ansi(canvas):
    h = len(canvas)
    w = len(canvas[0]) if h else 0
    lines = []
    for y in range(0, h, 2):
        top = canvas[y]
        bottom = canvas[y + 1] if y + 1 < h else [(0, 0, 0)] * w
        parts = []
        last_pair = None
        for x in range(w):
            pair = (top[x], bottom[x])
            if pair != last_pair:
                parts.append(_sgr(*pair))
                last_pair = pair
            parts.append("\u2580")  # upper half block
        parts.append(RESET)
        lines.append("".join(parts))
    return "\n".join(lines)
