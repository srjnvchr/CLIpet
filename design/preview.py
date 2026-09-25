import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "renderer"))
import phase as Phase
from canvas import lerp
from compose import compose_frame
from scenes import get_scene
from characters import get_character
from PIL import Image

SCALE = 8
scene = get_scene("couch_desk")
character = get_character("bot")
idle_spot = scene.SPOTS["idle"]
work_spot = scene.SPOTS["work"]


def save(canvas, name):
    h = len(canvas)
    w = len(canvas[0])
    img = Image.new("RGB", (w, h))
    for y in range(h):
        for x in range(w):
            img.putpixel((x, y), canvas[y][x])
    img = img.resize((w * SCALE, h * SCALE), Image.NEAREST)
    img.save(os.path.join(HERE, f"preview_{name}.png"))
    print("saved", name)


save(compose_frame(scene, character, idle_spot, Phase.IDLE, t=0.0), "couch_book")
save(compose_frame(scene, character, idle_spot, Phase.IDLE, t=5.0), "couch_pad")
save(compose_frame(scene, character, lerp(idle_spot, work_spot, 0.5), Phase.TO_WORK, t=1.0), "walking_mid")
save(compose_frame(scene, character, work_spot, Phase.WORKING, t=0.0), "at_desk")
