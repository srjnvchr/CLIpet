#!/usr/bin/env python3
"""
Generic animation phase. Scenes and characters are written against this
neutral vocabulary - not the plugin's own mode strings (at_couch/to_desk/
at_desk/to_couch, defined in plugin/scripts/state_lib.py) - so a new scene
never needs to know what its two named spots are called, or what a couch
even is. pet.py is the only place that translates between the two.
"""

IDLE = "idle"
TO_WORK = "to_work"
WORKING = "working"
TO_HOME = "to_home"

WALKING = (TO_WORK, TO_HOME)

_FROM_PLUGIN_MODE = {
    "at_couch": IDLE,
    "to_desk": TO_WORK,
    "at_desk": WORKING,
    "to_couch": TO_HOME,
}


def from_plugin_mode(mode):
    return _FROM_PLUGIN_MODE.get(mode, IDLE)
