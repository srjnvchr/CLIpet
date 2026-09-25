"""Registry of available characters. Add a module here and register it
below to make it selectable via pet.py's PET_CHARACTER env var."""
from . import bot
from . import orb

CHARACTERS = {
    "bot": bot,
    "orb": orb,
}


def get_character(name):
    try:
        return CHARACTERS[name]
    except KeyError:
        raise SystemExit(f"Unknown character {name!r}. Available: {', '.join(sorted(CHARACTERS))}")
