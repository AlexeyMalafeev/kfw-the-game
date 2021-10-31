from ._basic_attributes import BasicAttributes
from ._blank_ui import BlankFighterUI
from ._fight_attributes import FightAttributes
from ...kung_fu import moves


class BaseFighter(
    BasicAttributes,
    FightAttributes,
    BlankFighterUI,
):
    def __init__(self):
        BasicAttributes.__init__(self)
        FightAttributes.__init__(self)
        self.exp_yield = 0
        self.fight_ai = None
        self.moves = []
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
            self.techs,
            [m.name for m in self.moves if m not in moves.BASIC_MOVES],
        )

    def get_init_string(self):
        return f'{self.__class__.__name__}{self.get_init_atts()!r}'
