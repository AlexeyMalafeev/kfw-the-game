from abc import ABC
from typing import List, Set, Text, Tuple

from kf_lib.actors.fighter._abc import FighterAPI


class BaseFighter(FighterAPI, ABC):
    def __repr__(self) -> Text:
        return self.get_init_string()

    def get_init_atts(self) -> Tuple[
        Text,
        Text,
        int,
        Tuple[int, int, int, int],
        List[Text],
        List[Text],
    ]:
        """Return tuple of attributes used by __init__"""
        return (
            self.name,
            self.style.name,
            self.level,
            self.get_base_atts_tup(),
            [t.name for t in self.techs],
            [m.name for m in self.moves if not m.is_basic],
        )

    def get_init_string(self) -> Text:
        return f'{self.__class__.__name__}{self.get_init_atts()!r}'
