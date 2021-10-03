from ...kung_fu import moves


from ._attributes import Attributes


class BaseFighter(
    Attributes,
):
    name = ''
    style = None
    techs = []
    moves = []

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
