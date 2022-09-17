from __future__ import annotations
from abc import ABC, abstractmethod
from typing import (
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Set,
    Text,
    Tuple,
    TYPE_CHECKING,
    Type,
    Union,
)

if TYPE_CHECKING:
    # todo refactor - use base classes in separate files
    from kf_lib.ai.fight_ai import BaseAI
    from kf_lib.fighting.fight import BaseFight
    from kf_lib.kung_fu.moves import Move
    from kf_lib.kung_fu.styles import Style
    from kf_lib.kung_fu.techniques import Tech
    from kf_lib.things.weapons import Weapon


class FighterAPI(ABC):
    act_allies: List[FighterAPI] = None
    act_targets: List[FighterAPI] = None
    action: Move = None
    agility: int = None
    agility_full: int = None
    ascii_buffer: int = None
    ascii_l: Text = None
    ascii_name: Text = None
    ascii_r: Text = None
    att_names: Tuple[Text, Text, Text, Text] = None
    att_names_short: Tuple[Text, Text, Text, Text] = None
    att_weights: Dict[Text, int] = None
    current_fight: BaseFight = None
    distances: Dict[FighterAPI, int] = None
    exp_yield: int = None
    fav_move_features: Set[Text] = None
    fight_ai: BaseAI = None
    health: int = None
    health_full: int = None
    level: int = None
    momentum: int = None
    moves: List[Move] = None
    name: Text = None
    num_atts_choose: int = None
    rand_atts_mode: Literal[0, 1, 2] = None
    speed: int = None
    speed_full: int = None
    strength: int = None
    strength_full: int = None
    style: Style = None
    target: FighterAPI = None
    techs: List[Tech] = None
    weapon: Weapon = None

    # noinspection PyUnusedLocal
    @abstractmethod
    def __init__(
            self,
            name: str = '',
            style: Union[str, Style] = None,
            level: int = 1,
            atts_tuple: Tuple[int, int, int, int] = None,
            tech_names: List[str] = None,
            move_names: List[str] = None,
            rand_atts_mode: int = 0,
    ) -> None:
        pass

    @abstractmethod
    def __repr__(self) -> Text:
        pass

    @abstractmethod
    def change_att(
            self,
            att: Text,
            amount: int,
    ) -> None:
        pass

    @abstractmethod
    def change_distance(
        self,
        dist: int,
        targ: FighterAPI,
    ) -> None:
        pass

    @abstractmethod
    def check_lv(
            self,
            minlv: int,
            maxlv: Optional[int] = None,
    ) -> bool:
        pass

    @abstractmethod
    def choose_better_att(
            self,
            atts: List[Text],
    ) -> Text:
        pass

    @abstractmethod
    def cls(self):
        pass

    @abstractmethod
    def get_all_atts_str(self) -> Text:
        pass

    @abstractmethod
    def get_allies_power(self) -> int:
        pass

    @abstractmethod
    def get_att_str(self, att: Text) -> Text:
        pass

    @abstractmethod
    def get_att_str_prefight(
            self,
            att: Text,
            hide: bool = False,
    ) -> Text:
        pass

    @abstractmethod
    def get_att_values_full(self) -> Tuple[int, int, int, int]:
        pass

    @abstractmethod
    def get_atts_to_choose(self) -> List[Text]:
        pass

    @abstractmethod
    def get_base_att_value(
            self,
            att: Text,
    ) -> int:
        pass

    @abstractmethod
    def get_base_atts_tup(self) -> Tuple[int, int, int, int]:
        pass

    @abstractmethod
    def get_exp_worth(self) -> int:
        pass

    @abstractmethod
    def get_full_att_value(
            self,
            att: Text,
    ) -> int:
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
    def get_opponents_power(self) -> int:
        pass

    @abstractmethod
    def get_rel_strength(
        self,
        *opp: FighterAPI,
        allies=Optional[Iterable[FighterAPI]],
    ) -> Tuple[float, str]:
        pass

    @staticmethod
    @abstractmethod
    def get_vis_distance(dist: int) -> str:
        pass

    @abstractmethod
    def log(self, text: str) -> None:
        pass

    @abstractmethod
    def msg(self, *args, **kwargs):
        pass

    @abstractmethod
    def pak(self):
        pass

    @abstractmethod
    def refresh_ascii(self) -> None:
        pass

    @abstractmethod
    def refresh_full_atts(self) -> None:
        pass

    @abstractmethod
    def set_ascii(self, ascii_name: Text) -> None:
        pass

    @abstractmethod
    def set_att_weights(self) -> None:
        pass

    @abstractmethod
    def set_atts(
            self,
            atts: Tuple[int, int, int, int],
    ) -> None:
        pass

    @abstractmethod
    def set_distance(self, targ: FighterAPI, dist: int) -> None:
        pass

    def set_distances_before_fight(self) -> None:
        pass

    @abstractmethod
    def set_fight_ai(
            self,
            ai_class: Optional[Type[BaseAI]] = None,
            write_log: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def set_rand_atts(self) -> None:
        pass

    @abstractmethod
    def show(self, text, align=False):
        pass

    @abstractmethod
    def show_ascii(self) -> None:
        pass

    @abstractmethod
    def upgrade_att(self) -> None:
        pass

    @abstractmethod
    def write(self, *args, **kwargs):
        pass
