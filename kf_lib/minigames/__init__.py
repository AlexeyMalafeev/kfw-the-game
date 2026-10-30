"""Standalone mini-games built on the main game's fighters, fights and UI.

Run them with `python kfw.py --minigame NAME`; they don't touch saves or a Game.
"""
from ._chocolate import play_chocolate
from ._ring import play_ring

MINIGAMES = {
    'chocolate': play_chocolate,
    'ring': play_ring,
}
