from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
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
    action: Optional[Move] = None
    agility: int = None
    agility_full: int = None
    agility_mult: float = None
    ascii_buffer: int = None
    ascii_l: Text = None
    ascii_name: Text = None
    ascii_r: Text = None
    atk_bonus: float = None
    atk_mult: float = None
    atk_pwr: float = None
    att_names: Tuple[Text, Text, Text, Text] = None
    att_names_short: Tuple[Text, Text, Text, Text] = None
    att_weights: Dict[Text, int] = None
    av_moves: List[Move] = None
    bleeding: int = None
    block_disarm: float = None
    block_mult: float = None
    chance_cause_bleeding: float = None
    counter_chance: float = None
    counter_chance_mult: float = None
    critical_chance: float = None
    critical_chance_mult: float = None
    critical_dam_mult: float = None
    current_fight: Optional[BaseFight] = None
    dam: int = None
    dam_reduc: float = None
    defended: bool = None
    dfs_bonus: float = None
    dfs_mult: float = None
    dfs_penalty_mult: float = None
    dfs_penalty_step: float = None
    dfs_pwr: float = None
    distances: Dict[FighterAPI, int] = None
    dodge_mult: float = None
    environment_chance: float = None
    epic_chance: float = None
    epic_chance_mult: float = None
    epic_dam_mult: float = None
    exp_yield: int = None
    fall_damage_mult: float = None  # descriptor
    fav_move_features: Set[Text] = None
    fight_ai: BaseAI = None
    fury_to_all_mult: float = None
    fury_chance: float = None
    guard_dfs_bonus: float = None
    guard_while_attacking: float = None
    health: int = None
    health_full: int = None
    health_mult: float = None
    hit_disarm: float = None
    hp: int = None
    hp_max: int = None
    hp_gain: int = None
    hp_gain_mult: float = None
    in_fight_impro_wp_chance: float = None
    is_auto_fighting: bool = None
    kos_this_fight: int = None
    level: int = None
    lying_dfs_mult: float = None
    maneuver_time_cost_mult: float = None  # descriptor
    momentum: int = None
    move_complexity_mult: float = None  # descriptor
    moves: List[Move] = None
    name: Text = None
    num_atts_choose: int = None
    num_moves_choose: int = None
    off_balance_atk_mult: float = None
    off_balance_dfs_mult: float = None
    preemptive_chance: float = None
    previous_actions: deque = None
    qp: int = None
    qp_gain: int = None
    qp_gain_mult: float = None
    qp_max: int = None
    qp_max_mult: float = None
    qp_start: float = None  # descriptor
    rand_atts_mode: Literal[0, 1, 2] = None
    resist_ko: float = None  # descriptor
    speed: int = None
    speed_mult: float = None
    speed_full: int = None
    stamina: int = None  # descriptor
    stamina_factor: float = None
    stamina_gain: int = None
    stamina_gain_mult: float = None
    stamina_max: int = None
    stamina_max_mult: float = None
    status: Dict[str, int] = None
    strength: int = None
    strength_mult: float = None
    strength_full: int = None
    strike_time_cost_mult: float = None  # descriptor
    stun_chance: float = None
    style: Style = None
    target: Optional[FighterAPI] = None
    techs: List[Tech] = None
    to_block: float = None
    to_dodge: float = None
    to_hit: float = None
    toughness: int = None
    unblock_chance: float = None
    weapon: Optional[Weapon] = None
    weapon_bonus: Dict[str, List[float, float]] = None
    wp_dfs_bonus: float = None

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
    def add_status(self, status: str, dur: int) -> None:
        pass

    @abstractmethod
    def apply_bleeding(self) -> None:
        pass

    @abstractmethod
    def apply_dfs_penalty(self) -> None:
        pass

    @abstractmethod
    def apply_move_cost(self) -> None:
        pass

    @abstractmethod
    def attack(self) -> None:
        pass

    @abstractmethod
    def boost(self, **kwargs: Union[int, float]) -> None:
        pass

    @abstractmethod
    def change_att(self, att: Text, amount: int) -> None:
        pass

    @abstractmethod
    def change_distance(self, dist: int, targ: FighterAPI) -> None:
        pass

    @abstractmethod
    def change_hp(self, amount: int) -> None:
        pass

    @abstractmethod
    def change_qp(self, amount: int) -> None:
        pass

    @abstractmethod
    def change_stamina(self, amount: int) -> None:
        pass

    @abstractmethod
    def check_lv(self, minlv: int, maxlv: Optional[int] = None) -> bool:
        pass

    @abstractmethod
    def check_move_failed(self) -> bool:
        pass

    @abstractmethod
    def check_preemptive(self) -> bool:
        pass

    @abstractmethod
    def check_stamina(self, amount: int) -> bool:
        pass

    @abstractmethod
    def check_status(self, status: str) -> bool:
        pass

    @abstractmethod
    def choose_better_att(self, atts: List[Text]) -> Text:
        pass

    @abstractmethod
    def choose_move(self) -> None:
        pass

    @abstractmethod
    def choose_target(self) -> None:
        pass

    @abstractmethod
    def cls(self):
        pass

    @abstractmethod
    def defend(self) -> None:
        pass

    @abstractmethod
    def do_counter(self) -> None:
        pass

    @abstractmethod
    def do_preemptive(self) -> None:
        pass

    @abstractmethod
    def do_strike(self) -> None:
        pass

    @abstractmethod
    def exec_move(self) -> None:
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
    def get_att_str_prefight(self, att: Text, hide: bool = False,) -> Text:
        pass

    @abstractmethod
    def get_att_values_full(self) -> Tuple[int, int, int, int]:
        pass

    @abstractmethod
    def get_atts_to_choose(self) -> List[Text]:
        pass

    @abstractmethod
    def get_av_moves(self, attack_moves_only: bool = False) -> List[Move]:
        pass

    @abstractmethod
    def get_base_att_value(self, att: Text,) -> int:
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

    @abstractmethod
    def get_status_marks(self, right: bool = False) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_vis_distance(dist: int) -> str:
        pass

    @abstractmethod
    def guard(self) -> None:
        pass

    @abstractmethod
    def hit_or_miss(self) -> None:
        pass

    @abstractmethod
    def init_fight_attributes(self) -> None:
        pass

    @abstractmethod
    def log(self, text: str) -> None:
        pass

    @abstractmethod
    def maneuver(self) -> None:
        pass

    @abstractmethod
    def msg(self, *args, **kwargs):
        pass

    @abstractmethod
    def pak(self):
        pass

    @abstractmethod
    def prepare_for_fight(self) -> None:
        pass

    @abstractmethod
    def refresh_ascii(self) -> None:
        pass

    @abstractmethod
    def refresh_dependent_atts(self) -> None:
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
    def set_atts(self, atts: Tuple[int, int, int, int]) -> None:
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
    def set_target(self, target: FighterAPI) -> None:
        pass

    @abstractmethod
    def show(self, text, align=False):
        pass

    @abstractmethod
    def show_ascii(self) -> None:
        pass

    @abstractmethod
    def start_fight_turn(self) -> None:
        pass

    @abstractmethod
    def try_block_disarm(self) -> None:
        pass

    @abstractmethod
    def try_counter(self) -> None:
        pass

    @abstractmethod
    def try_fury(self) -> None:
        pass

    @abstractmethod
    def try_in_fight_impro_wp(self) -> None:
        pass

    @abstractmethod
    def try_ko(self) -> None:
        pass

    @abstractmethod
    def try_strike(self) -> None:
        pass

    @abstractmethod
    def unboost(self, **kwargs: Union[int, float]) -> None:
        pass

    @abstractmethod
    def upgrade_att(self) -> None:
        pass

    @abstractmethod
    def visualize_fight_state(self) -> str:
        pass

    @abstractmethod
    def write(self, *args, **kwargs):
        pass
