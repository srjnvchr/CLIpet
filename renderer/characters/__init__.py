"""Registry of available characters. Add a module here and register it
below to make it selectable via pet.py's PET_CHARACTER env var. A name
that isn't registered here also gets a fallback lookup in
renderer/packs/<name>/ - see image_asset.py and design/import_image.py
for how those are made."""
from . import bot
from . import orb
import image_asset

CHARACTERS = {
    "bot": bot,
    "orb": orb,
}


def get_character(name):
    if name in CHARACTERS:
        return CHARACTERS[name]
    packed = image_asset.pack_character(name)
    if packed is not None:
        return packed
    raise SystemExit(
        f"Unknown character {name!r}. Available: {', '.join(sorted(CHARACTERS))}, "
        f"or any pack under renderer/packs/<name>/character.json"
    )
