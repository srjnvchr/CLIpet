"""Registry of available scenes. Add a module here and register it below
to make it selectable via pet.py's PET_SCENE env var. A name that isn't
registered here also gets a fallback lookup in renderer/packs/<name>/ -
see image_asset.py and design/import_image.py for how those are made."""
from . import couch_desk
import image_asset

SCENES = {
    "couch_desk": couch_desk,
}


def get_scene(name):
    if name in SCENES:
        return SCENES[name]
    packed = image_asset.pack_scene(name)
    if packed is not None:
        return packed
    raise SystemExit(
        f"Unknown scene {name!r}. Available: {', '.join(sorted(SCENES))}, "
        f"or any pack under renderer/packs/<name>/background.json"
    )
