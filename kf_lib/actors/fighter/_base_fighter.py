from typing import Set, Text

from ._blank_io import BlankFighterIO
from ._fight_attributes import FightAttributes


class BaseFighter(
    FightAttributes,
    BlankFighterIO,
):
    def __init__(self):
        super().__init__()
        self.exp_yield = 0
        self.fight_ai = None
        self.moves = []
        self.fav_move_features: Set[Text] = set()
        self.name = ''
        self.style = None
        self.techs = []

    def __repr__(self):
        return self.get_init_string()

    def get_init_atts(self):
        """Return tuple of attributes used by __init__"""
        return (
            self.name,
            self.style.name,
            self.level,
            self.get_base_atts_tup(),
            [t.name for t in self.techs],
            [m.name for m in self.moves if not m.is_basic],
        )

    def get_init_string(self):
        return f'{self.__class__.__name__}{self.get_init_atts()!r}'
