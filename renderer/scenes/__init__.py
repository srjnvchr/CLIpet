"""Registry of available scenes. Add a module here and register it below
to make it selectable via pet.py's PET_SCENE env var."""
from . import couch_desk

SCENES = {
    "couch_desk": couch_desk,
}


def get_scene(name):
    try:
        return SCENES[name]
    except KeyError:
        raise SystemExit(f"Unknown scene {name!r}. Available: {', '.join(sorted(SCENES))}")
