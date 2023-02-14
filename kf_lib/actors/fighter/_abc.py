from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from typing import (
    Dict,
    Final,
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
    ADVANCED_TECH_AT_LV: Final[int] = 19
    LVS_GET_GENERAL_TECH: Final[Set[int]] = {13, 15, 17}

    act_allies: List[FighterAPI] = None
    act_targets: List[FighterAPI] = None
    action: Optional[Move] = None
    agility: int = None
    agility_full: int = 0
    agility_mult: float = None
    ascii_buffer: int = None
    ascii_l: Text = None
    ascii_name: Text = None
    ascii_r: Text = None
    atk_mult: float = None
    att_names: Tuple[Text, Text, Text, Text] = None
    att_names_short: Tuple[Text, Text, Text, Text] = None
    att_weights: Dict[Text, int] = None
    av_moves: List[Move] = None
    bleeding: int = None
    block_chance: float = 0.0  # refreshed per attack
    block_disarm: float = None
    block_mult: float = None
    chance_cause_bleeding: float = None
    counter_chance: float = None
    counter_chance_mult: float = None
    critical_chance: float = None
    critical_chance_mult: float = None
    critical_dam_mult: float = None
    curr_atk_mult: float = 1.0  # refreshed per attack
    curr_dfs_mult: float = 1.0  # refreshed even more often than per attack
    current_fight: Optional[BaseFight] = None
    dam: int = None
    dam_reduc: float = None
    defended: bool = None
    dfs_bonus_from_guarding: float = 1.0
    dfs_mult: float = None
    dfs_penalty_mult: float = None
    dfs_penalty_step: float = None
    block_pwr: float = None
    distances: Dict[FighterAPI, int] = None
    dodge_chance: float = 0.0  # refreshed per attack
    dodge_mult: float = None
    environment_chance: float = None
    epic_chance: float = None
    epic_chance_mult: float = None
    epic_dam_mult: float = None
    exp_yield: int = None
    fall_damage_mult: float = None  # descriptor
    fav_move_features: Set[Text] = None
    fight_ai: BaseAI = None
    fury_chance: float = None
    fury_to_all_mult: float = None
    guard_dfs_bonus: float = None
    guard_while_attacking: float = None
    health: int = None
    health_full: int = None
    health_mult: float = None
    hit_disarm: float = None
    hp: int = None
    hp_gain: int = None
    hp_gain_mult: float = None
    hp_max: int = None
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
    num_techs_choose: int = 3
    num_techs_choose_upgrade: int = 3
    off_balance_atk_mult: float = None
    off_balance_dfs_mult: float = None
    potential_dam: float = None  # computed per strike, before it connects
    preemptive_chance: float = None
    previous_actions: deque = None
    qp: int = None
    qp_gain: int = None
    qp_gain_mult: float = None
    qp_max: int = None
    qp_max_mult: float = None
    qp_start: float = None  # descriptor
    quotes: str = None
    rand_atts_mode: Literal[0, 1, 2] = None
    resist_ko: float = None  # descriptor
    speed: int = None
    speed_full: int = None
    speed_mult: float = None
    stamina: int = None  # descriptor
    stamina_factor: float = None
    stamina_gain: int = None
    stamina_gain_mult: float = None
    stamina_max: int = None
    stamina_max_mult: float = None
    status: Dict[str, int] = None
    strength: int = None
    strength_full: int = None
    strength_mult: float = None
    strike_time_cost_mult: float = None  # descriptor
    stun_chance: float = None
    style: Style = None
    target: Optional[FighterAPI] = None
    techs: Set[Tech] = None
    to_block: float = None
    to_dodge: float = None
    to_hit: float = None
    took_damage: bool = None
    toughness: int = None
    unblock_chance: float = None
    weapon: Optional[Weapon] = None
    weapon_bonus: Dict[str, List[float, float]] = None
    wp_dfs_bonus: float = None

    # noinspection PyUnusedLocal
    @abstractmethod
    def __init__(
            self,
            name: str,
            style: Union[str, Style],
            level: int,
            atts_tuple: Tuple[int, int, int, int],
            tech_names: List[str],
            move_names: List[str],
            rand_atts_mode: int,
    ) -> None:
        pass

    @abstractmethod
    def __repr__(self) -> Text:
        pass

    @abstractmethod
    def add_status(self, status: str, dur: int) -> None:
        pass

    @abstractmethod
    def add_tech(self, tech: Tech) -> None:
        pass

    @abstractmethod
    def apply_bleeding(self) -> None:
        pass

    @abstractmethod
    def apply_dfs_penalty(self) -> None:
        pass

    @abstractmethod
    def _apply_fury_for_atk(self) -> None:
        pass

    @abstractmethod
    def _apply_fury_for_dfs(self) -> None:
        pass

    @abstractmethod
    def _apply_momentum_for_atk(self) -> None:
        pass

    @abstractmethod
    def apply_move_cost(self) -> None:
        pass

    @abstractmethod
    def apply_tech(self, *techs: Tech) -> None:
        pass

    @abstractmethod
    def arm(self, weapon: Optional[Union[Weapon, str]] = None) -> None:
        pass

    @abstractmethod
    def arm_improv(self) -> None:
        pass

    @abstractmethod
    def arm_normal(self) -> None:
        pass

    @abstractmethod
    def arm_police(self) -> None:
        pass

    @abstractmethod
    def arm_robber(self) -> None:
        pass

    @abstractmethod
    def attack(self) -> None:
        pass

    @abstractmethod
    def boost(self, **kwargs: Union[int, float]) -> None:
        pass

    @abstractmethod
    def calc_atk(self, action: Move) -> None:
        pass

    def _calc_block_pwr(self) -> None:
        pass

    @abstractmethod
    def _calc_curr_atk_mult(self, action: Move) -> None:
        pass

    @abstractmethod
    def _calc_curr_dfs_mult(self) -> None:
        pass

    @abstractmethod
    def calc_dfs(self) -> None:
        pass

    @abstractmethod
    def calc_move_complexity(self, move_obj: Move) -> float:
        pass

    @abstractmethod
    def _calc_potential_dam(self, action: Move) -> None:
        pass

    @abstractmethod
    def calc_stamina_factor(self) -> None:
        pass

    @abstractmethod
    def _calc_to_block(self) -> None:
        pass

    @abstractmethod
    def _calc_to_dodge(self) -> None:
        pass

    @abstractmethod
    def _calc_to_hit(self, action: Move) -> None:
        pass

    @abstractmethod
    def can_use_move_now(self, m: Move) -> bool:
        pass

    @abstractmethod
    def cause_bleeding(self) -> None:
        pass

    @abstractmethod
    def cause_fall(self) -> None:
        pass

    @abstractmethod
    def cause_knockback(self, dist: int) -> None:
        pass

    @abstractmethod
    def cause_off_balance(self) -> None:
        pass

    @abstractmethod
    def cause_shock(self) -> None:
        pass

    @abstractmethod
    def cause_slow_down(self) -> None:
        pass

    @abstractmethod
    def cause_stun(self) -> None:
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
    def change_stat(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def check_lv(self, minlv: int, maxlv: int) -> bool:
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
    def choose_best_norm_wp(self) -> None:
        pass

    @abstractmethod
    def choose_better_att(self, atts: List[Text]) -> Text:
        pass

    @abstractmethod
    def choose_move(self) -> None:
        """Called in a fight at the beginning of a turn."""
        pass

    @abstractmethod
    def choose_new_move(self, sample: List[Move]) -> None:
        pass

    @abstractmethod
    def choose_new_tech(self) -> None:
        pass

    @abstractmethod
    def choose_target(self) -> None:
        pass

    @abstractmethod
    def choose_tech_to_upgrade(self) -> None:
        pass

    @abstractmethod
    def cls(self):
        pass

    @abstractmethod
    def disarm(self) -> None:
        pass

    @abstractmethod
    def display_bleed_pass_out(self) -> None:
        pass

    @abstractmethod
    def display_block(self) -> None:
        pass

    @abstractmethod
    def display_block_disarm(self) -> None:
        pass

    @abstractmethod
    def display_counter(self) -> None:
        pass

    @abstractmethod
    def display_dodge(self) -> None:
        pass

    @abstractmethod
    def display_fail(self) -> None:
        pass

    @abstractmethod
    def display_fury(self) -> None:
        pass

    @abstractmethod
    def display_grab_impro_wp(self) -> None:
        pass

    @abstractmethod
    def display_hit(self) -> None:
        pass

    @abstractmethod
    def display_ko(self) -> None:
        pass

    @abstractmethod
    def display_miss(self) -> None:
        pass

    @abstractmethod
    def display_preemptive(self) -> None:
        pass

    @abstractmethod
    def display_resist_ko(self) -> None:
        pass

    @abstractmethod
    def display_start_of_attack(self) -> None:
        pass

    @abstractmethod
    def display_start_of_maneuver(self) -> None:
        pass

    @abstractmethod
    def do_agility_based_dam(self) -> None:
        pass

    @abstractmethod
    def do_block(self) -> None:
        pass

    @abstractmethod
    def do_counter(self) -> None:
        pass

    @abstractmethod
    def do_dodge(self) -> None:
        pass

    @abstractmethod
    def do_knockback(self) -> None:
        pass

    @abstractmethod
    def do_level_based_dam(self) -> None:
        pass

    @abstractmethod
    def do_mob_dam(self) -> None:
        pass

    @abstractmethod
    def do_move_functions(self, m: Move) -> None:
        pass

    @abstractmethod
    def do_on_strike_end(self) -> None:
        pass

    @abstractmethod
    def do_per_turn_actions(self) -> None:
        pass

    @abstractmethod
    def do_preemptive(self) -> None:
        pass

    @abstractmethod
    def do_qi_based_dam(self) -> None:
        pass

    @abstractmethod
    def do_shock_move(self) -> None:
        pass

    @abstractmethod
    def do_speed_based_dam(self) -> None:
        pass

    @abstractmethod
    def do_stam_dam(self) -> None:
        pass

    @abstractmethod
    def do_strength_based_dam(self) -> None:
        pass

    @abstractmethod
    def do_strike(self) -> None:
        pass

    @abstractmethod
    def do_takedown(self) -> None:
        pass

    @abstractmethod
    def exec_move(self) -> None:
        pass

    @abstractmethod
    def fight(
        self,
        en: FighterAPI,
        allies: List[FighterAPI],
        en_allies: List[FighterAPI],
        *args,
        **kwargs,
    ) -> bool:
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
    def get_att_str_prefight(self, att: Text, hide: bool) -> Text:
        pass

    @abstractmethod
    def get_att_values_full(self) -> Tuple[int, int, int, int]:
        pass

    @abstractmethod
    def get_atts_to_choose(self) -> List[Text]:
        pass

    @abstractmethod
    def get_av_moves(self, attack_moves_only: bool) -> List[Move]:
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
    def get_move_fail_chance(self, move_obj: Move) -> float:
        pass

    @abstractmethod
    def get_moves_to_choose(self, tier: int) -> List[Move]:
        pass

    @abstractmethod
    def get_move_tier_for_lv(self, level: int = None) -> int:
        pass

    @staticmethod
    @abstractmethod
    def get_move_tier_string(move_obj: Move) -> str:
        pass

    @abstractmethod
    def get_move_time_cost(self, move_obj: Move) -> int:
        pass

    @abstractmethod
    def get_opponents_power(self) -> int:
        pass

    @abstractmethod
    def get_rel_strength(
        self,
        *opp: FighterAPI,
        allies: Optional[Iterable[FighterAPI]] = None,
    ) -> Tuple[float, str]:
        pass

    @abstractmethod
    def get_rep_actions_factor(self, move: Move) -> float:
        pass

    @abstractmethod
    def get_status_marks(self, right: bool) -> str:
        pass

    @abstractmethod
    def get_style_string(self, show_emph: bool = False) -> str:
        pass

    @abstractmethod
    def get_style_tech_if_any(self) -> Optional[Tech]:
        pass

    @abstractmethod
    def get_techs_string(self, show_descr: bool = True, header: Text = 'Techniques:') -> Text:
        pass

    @abstractmethod
    def get_techs_to_choose(self, annotated: bool = False, for_upgrade: bool = False) -> List[Tech]:
        pass

    @abstractmethod
    def get_tier_str_for_lv(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_vis_distance(dist: int) -> str:
        pass

    @abstractmethod
    def get_weapon_techs(self) -> List[Tech]:
        pass

    @abstractmethod
    def guard(self) -> None:
        pass

    @abstractmethod
    def init_fight_attributes(self) -> None:
        pass

    @abstractmethod
    def learn_move(self, move: Union[Move, str], silent: bool = False) -> None:
        pass

    @abstractmethod
    def learn_move_from(self, other: FighterAPI) -> None:
        pass

    @abstractmethod
    def learn_random_move(self, move_tier: int, silent: bool = False) -> None:
        pass

    @abstractmethod
    def learn_random_new_tech(self) -> None:
        pass

    @abstractmethod
    def learn_tech(self, *techs: Tech) -> None:
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
    def replace_move(self, rep_mv: Move, rep_with: Move) -> None:
        pass

    @abstractmethod
    def resolve_moves_on_level_up(self) -> None:
        pass

    @abstractmethod
    def refresh_per_turn_attributes(self) -> None:
        pass

    @abstractmethod
    def resolve_techs_on_level_up(self) -> None:
        pass

    @abstractmethod
    def say_prefight_quote(self) -> bool:
        pass

    @abstractmethod
    def say_win_quote(self) -> None:
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
            ai_class: Type[BaseAI],
            write_log: bool,
    ) -> None:
        pass

    @abstractmethod
    def set_moves(self, move_objs: List[Move]) -> None:
        pass

    @abstractmethod
    def set_rand_atts(self) -> None:
        pass

    @abstractmethod
    def set_rand_moves(self) -> None:
        pass

    @abstractmethod
    def set_rand_techs(self, forced: bool = False) -> None:
        pass

    @abstractmethod
    def set_style(self, style: Union[Style, str]) -> None:
        pass

    @abstractmethod
    def set_target(self, target: FighterAPI) -> None:
        pass

    @abstractmethod
    def set_techs(self, tech_names: List[Text]) -> None:
        pass

    @abstractmethod
    def show(self, text: str, align: bool = False) -> None:
        pass

    @abstractmethod
    def show_ascii(self) -> None:
        pass

    @abstractmethod
    def spar(
        self,
        en: FighterAPI,
        allies: List[FighterAPI],
        en_allies: List[FighterAPI],
        auto_fight: bool,
        af_option: bool,
        hide_stats: bool,
        environment_allowed: bool,
    ) -> bool:
        pass

    @abstractmethod
    def start_fight_turn(self) -> None:
        pass

    @abstractmethod
    def take_damage(self, dam: int) -> None:
        pass

    @abstractmethod
    def try_block_disarm(self) -> None:
        pass

    @abstractmethod
    def try_cause_bleeding(self) -> None:
        pass

    @abstractmethod
    def try_counter(self) -> None:
        pass

    @abstractmethod
    def try_critical(self) -> None:
        pass

    @abstractmethod
    def try_defend(self) -> None:
        pass

    @abstractmethod
    def try_environment(self, mode: str) -> None:
        pass

    @abstractmethod
    def try_epic(self) -> None:
        pass

    @abstractmethod
    def try_fury(self) -> None:
        pass

    @abstractmethod
    def try_hit(self) -> None:
        pass

    @abstractmethod
    def try_in_fight_impro_wp(self) -> None:
        pass

    @abstractmethod
    def try_insta_ko(self) -> None:
        pass

    @abstractmethod
    def try_hit_disarm(self) -> None:
        pass

    @abstractmethod
    def try_knockback(self) -> None:
        pass

    @abstractmethod
    def try_knockdown(self) -> None:
        pass

    @abstractmethod
    def try_ko(self) -> None:
        pass

    @abstractmethod
    def try_shock_move(self) -> None:
        pass

    @abstractmethod
    def try_strike(self) -> None:
        pass

    @abstractmethod
    def try_stun(self) -> None:
        pass

    @abstractmethod
    def try_unblockable(self) -> None:
        pass

    @abstractmethod
    def unboost(self, **kwargs: Union[int, float]) -> None:
        pass

    @abstractmethod
    def unlearn_tech(self, tech: Tech) -> None:
        pass

    @abstractmethod
    def upgrade_att(self) -> None:
        pass

    @abstractmethod
    def upgrade_tech(self, tech: Tech) -> None:
        pass

    @abstractmethod
    def visualize_fight_state(self) -> str:
        pass

    @abstractmethod
    def write(self, *args, **kwargs):
        pass
