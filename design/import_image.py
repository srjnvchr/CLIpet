#!/usr/bin/env python3
"""
Turn a source image into a deskbot-pet "pack": a background.json and/or
character.json under renderer/packs/<name>/ that pet.py can load with
zero extra dependencies. This script is the only place PIL is needed -
everything it writes out is plain JSON the renderer reads with the
stdlib alone (see renderer/image_asset.py).

Usage:
    python design/import_image.py room.png --as background --name myroom
    python design/import_image.py cat.png  --as character --name myroom

Then run the pet with:
    PET_SCENE=myroom PET_CHARACTER=myroom python renderer/pet.py
(mix and match pack names with the built-ins "couch_desk" / "bot" freely -
a pack only needs to define whichever half you actually made art for)
"""
import argparse
import json
import os

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
PACKS_DIR = os.path.join(os.path.dirname(HERE), "renderer", "packs")

DEFAULT_BACKGROUND_SIZE = (72, 64)  # matches renderer/scenes/couch_desk.py
DEFAULT_CHARACTER_SIZE = (16, 16)
ALPHA_THRESHOLD = 128  # pixels less opaque than this become transparent


def fit_cover(img, size):
    """Crop-to-fill, centered - no letterboxing, some cropping if the
    aspect ratio doesn't match. Good for backgrounds, which should fill
    the whole scene."""
    return ImageOps.fit(img, size, Image.LANCZOS)


def fit_contain(img, size):
    """Preserve the whole sprite at its own aspect ratio, padded with
    transparency to the exact target size. Good for characters, where
    cropping would cut off part of the subject."""
    img = img.copy()
    img.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    ox = (size[0] - img.width) // 2
    oy = (size[1] - img.height) // 2
    canvas.paste(img, (ox, oy), img)
    return canvas


def flatten_onto(img, bg=(0, 0, 0, 255)):
    base = Image.new("RGBA", img.size, bg)
    return Image.alpha_composite(base, img)


def to_pixel_grid(img, transparent):
    w, h = img.size
    px = img.load()
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b, a = px[x, y]
            row.append(None if (transparent and a < ALPHA_THRESHOLD) else [r, g, b])
        grid.append(row)
    return grid


def import_background(path, name, size):
    img = Image.open(path).convert("RGBA")
    fitted = flatten_onto(fit_cover(img, size))
    data = {"width": size[0], "height": size[1], "pixels": to_pixel_grid(fitted, transparent=False)}
    _write(name, "background.json", data)


def import_character(path, name, size):
    img = Image.open(path).convert("RGBA")
    fitted = fit_contain(img, size)
    data = {
        "width": size[0],
        "height": size[1],
        "anchor": [size[0] / 2, size[1] - 1],  # bottom-center, matching where scenes place their spots
        "pixels": to_pixel_grid(fitted, transparent=True),
    }
    _write(name, "character.json", data)


def _write(name, filename, data):
    out_dir = os.path.join(PACKS_DIR, name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w") as f:
        json.dump(data, f)
    print(f"wrote {out_path}  ({data['width']}x{data['height']})")


def parse_size(s):
    w, h = s.lower().split("x")
    return int(w), int(h)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", help="source image file (any format PIL can read)")
    parser.add_argument("--as", dest="kind", choices=("background", "character"), required=True)
    parser.add_argument("--name", required=True, help="pack name - creates/updates renderer/packs/<name>/")
    parser.add_argument(
        "--size", type=parse_size, default=None,
        help="WxH in pixels, e.g. 72x64 (defaults: 72x64 for background, 16x16 for character)",
    )
    args = parser.parse_args()

    size = args.size or (DEFAULT_BACKGROUND_SIZE if args.kind == "background" else DEFAULT_CHARACTER_SIZE)
    if args.kind == "background":
        import_background(args.image, args.name, size)
    else:
        import_character(args.image, args.name, size)


if __name__ == "__main__":
    main()
