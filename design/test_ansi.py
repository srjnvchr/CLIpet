import sys, re
sys.path.insert(0, "/home/claude/deskbot-pet/renderer")
from scene import compose_frame, DESK_STAND
from ansi import canvas_to_ansi

canvas = compose_frame(DESK_STAND, "at_desk", t=0.0)
ansi = canvas_to_ansi(canvas)

# parse it back
pat = re.compile(r"\x1b\[38;2;(\d+);(\d+);(\d+);48;2;(\d+);(\d+);(\d+)m|\u2580|\x1b\[0m")
rebuilt = []
cur_fg = cur_bg = (0, 0, 0)
for line in ansi.split("\n"):
    top_row, bot_row = [], []
    for m in pat.finditer(line):
        if m.group(0) == "\u2580":
            top_row.append(cur_fg)
            bot_row.append(cur_bg)
        elif m.group(0) != "\x1b[0m":
            cur_fg = tuple(int(m.group(i)) for i in (1, 2, 3))
            cur_bg = tuple(int(m.group(i)) for i in (4, 5, 6))
    rebuilt.append(top_row)
    rebuilt.append(bot_row)

h = len(canvas)
ok = True
for y in range(h):
    for x in range(len(canvas[0])):
        if tuple(canvas[y][x]) != tuple(rebuilt[y][x]):
            ok = False
            print("MISMATCH at", x, y, canvas[y][x], rebuilt[y][x])

print("bytes of ansi output for one frame:", len(ansi.encode()))
print("ROUND TRIP OK" if ok else "ROUND TRIP FAILED")
