from ...ai.fight_ai import DefaultFightAI
from ._basic_attributes import BasicAttributes
from ._fight_attributes import FightAttributes
from ...kung_fu import moves


class BaseFighter(
    BasicAttributes,
    FightAttributes,
):
    fight_ai = DefaultFightAI
    moves = []
    name = ''
    style = None
    target = None
    techs = []

    def __repr__(self):
        return self.get_init_string()

    def get_init_atts(self):
        """Return tuple of attributes used by __init__"""
        return (
            self.name,
            self.style.name,
            self.level,
            self.get_base_atts_tup(),
            self.techs,
            [m.name for m in self.moves if m not in moves.BASIC_MOVES],
        )

    def get_init_string(self):
        return f'{self.__class__.__name__}{self.get_init_atts()!r}'

    def log(self, text):
        """Empty method for convenience."""
        pass
