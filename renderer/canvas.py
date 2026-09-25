#!/usr/bin/env python3
"""
Generic pixel-grid primitives shared by every scene and character: a 2D
list of (r,g,b) rows, plus the drawing/cropping operations that work on
one regardless of what's being drawn. Nothing here knows about couches,
desks, or bots - see renderer/scenes/ and renderer/characters/ for that.
"""


def new_canvas(w, h, bg):
    return [[bg for _ in range(w)] for _ in range(h)]


def crop_canvas(canvas, w, h):
    """Return a centered w x h window into canvas. Used to fit a scene
    into a terminal smaller than its native size without stretching or
    re-rendering at a different resolution - just show less of it,
    evenly trimmed from each edge so it stays centered as the terminal
    is resized."""
    full_h = len(canvas)
    full_w = len(canvas[0]) if full_h else 0
    w = max(1, min(w, full_w))
    h = max(1, min(h, full_h))
    x0 = (full_w - w) // 2
    y0 = (full_h - h) // 2
    return [row[x0:x0 + w] for row in canvas[y0:y0 + h]]


def set_px(c, x, y, color):
    h = len(c)
    w = len(c[0]) if h else 0
    x, y = int(round(x)), int(round(y))
    if 0 <= y < h and 0 <= x < w:
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
