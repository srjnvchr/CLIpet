import sys
sys.path.insert(0, "/home/claude/deskbot-pet/renderer")
from scene import compose_frame, COUCH_SPOT, DESK_STAND, lerp
from PIL import Image

SCALE = 8

def save(canvas, name):
    h = len(canvas)
    w = len(canvas[0])
    img = Image.new("RGB", (w, h))
    for y in range(h):
        for x in range(w):
            img.putpixel((x, y), canvas[y][x])
    img = img.resize((w * SCALE, h * SCALE), Image.NEAREST)
    img.save(f"/home/claude/deskbot-pet/design/preview_{name}.png")
    print("saved", name)

save(compose_frame(COUCH_SPOT, "at_couch", t=0.0), "couch_book")
save(compose_frame(COUCH_SPOT, "at_couch", t=5.0), "couch_pad")
save(compose_frame(lerp(COUCH_SPOT, DESK_STAND, 0.5), "to_desk", t=1.0), "walking_mid")
save(compose_frame(DESK_STAND, "at_desk", t=0.0), "at_desk")
