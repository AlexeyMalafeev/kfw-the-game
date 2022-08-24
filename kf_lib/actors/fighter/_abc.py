from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Text, Tuple, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from kf_lib.ai.fight_ai import BaseAI


class FighterAPI(ABC):
    action = None
    ascii_buffer = None
    ascii_l = None
    ascii_name = None
    ascii_r = None
    current_fight = None
    exp_yield = None
    fav_move_features = None
    fight_ai = None
    level = None
    moves = None
    name = None
    style = None
    target = None
    techs = None

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def __repr__(self) -> Text:
        pass

    @abstractmethod
    def get_base_atts_tup(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_init_atts(self) -> Tuple[
        Text,
        Text,
        int,
        Tuple[int, int, int, int],
        List[Text],
        List[Text],
    ]:
        pass

    @abstractmethod
    def get_init_string(self) -> Text:
        pass

    @abstractmethod
    def refresh_ascii(self) -> None:
        pass

    @abstractmethod
    def set_ascii(
            self,
            ascii_name: Text,
    ) -> None:
        pass

    @abstractmethod
    def set_fight_ai(
            self,
            ai_class: Optional[Type[BaseAI]] = None,
            write_log: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def show_ascii(self) -> None:
        pass
