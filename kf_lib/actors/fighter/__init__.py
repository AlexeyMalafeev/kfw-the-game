from typing import List, Set, Text, Tuple, Union

from kf_lib.kung_fu import styles
from kf_lib.actors.fighter._ai import FightAIMethods
from kf_lib.actors.fighter._ascii import FighterWithASCII
from kf_lib.actors.fighter._fighter_repr import FighterRepr
from kf_lib.actors.fighter._basic_attributes import BasicAttributes
from kf_lib.actors.fighter._blank_io import BlankFighterIO
from kf_lib.actors.fighter._distances import DistanceMethods
from kf_lib.actors.fighter._exp_worth import ExpMethods
from kf_lib.actors.fighter._fight_actions import FighterWithActions
from kf_lib.actors.fighter._fight_attributes import FightAttributes
from kf_lib.actors.fighter._fight_utils import FightUtils
from kf_lib.actors.fighter._moves import MoveMethods
from kf_lib.actors.fighter._quotes import QuoteMethods
from kf_lib.actors.fighter._stats import FighterStats
from kf_lib.actors.fighter._strike_mechanics import StrikeMechanics
from kf_lib.actors.fighter._style import StyleMethods
from kf_lib.actors.fighter._techs import TechMethods
from kf_lib.actors.fighter._weapons import WeaponMethods


class Fighter(
    FighterRepr,
    BasicAttributes,
    BlankFighterIO,
    DistanceMethods,
    ExpMethods,
    FightAIMethods,
    FightAttributes,
    FightUtils,
    FighterStats,
    FighterWithASCII,
    FighterWithActions,
    MoveMethods,
    QuoteMethods,
    StrikeMechanics,
    StyleMethods,
    TechMethods,
    WeaponMethods,
):
    is_human = False
    is_player = False

    # the order of arguments should not be changed, or saving will break
    def __init__(
            self,
            name: str = '',
            style: Union[str, styles.Style] = None,
            level: int = 1,
            atts_tuple: Tuple[int, int, int, int] = None,
            tech_names: List[str] = None,
            move_names: List[str] = None,
            rand_atts_mode: int = 0,  # todo give rand_atts_mode interpretable str values
    ) -> None:
        self.att_weights = {}
        self.strength = 0
        self.strength_full = 0
        self.agility = 0
        self.agility_full = 0
        self.speed = 0
        self.speed_full = 0
        self.health = 0
        self.health_full = 0

        self.level = 1
        self.num_atts_choose = 3
        self.rand_atts_mode = 0  # 0, 1, 2

        self.exp_yield = 0
        self.moves = []
        self.fav_move_features: Set[Text] = set()
        self.style = None
        self.techs = set()

        self.init_fight_attributes()

        self.name = name
        self.level = level
        self.rand_atts_mode = rand_atts_mode
        self.set_att_weights()
        self.set_atts(atts_tuple)
        self.set_style(style)
        self.set_techs(tech_names)
        self.set_moves(move_names)
        self.set_fight_ai()
        self.refresh_full_atts()
        self.refresh_dependent_atts()

    def get_f_info(self, short=False, show_st_emph=False):
        s = self
        if s.weapon:
            w_info = f', {s.weapon.name}'
        else:
            w_info = ''
        if short:
            info = f'{s.name}, lv.{s.level} {s.style.name}{w_info}'
        else:
            info = '{}, lv.{} {}{}\n{}'.format(
                s.name, s.level, s.get_style_string(show_st_emph), w_info, s.get_all_atts_str()
            )
        return info

    def level_up(self, n=1):
        for i in range(n):
            self.level += 1
            self.upgrade_att()
            self.refresh_dependent_atts()
            self.resolve_techs_on_level_up()
            self.resolve_moves_on_level_up()
            # NB! no need to refresh full atts here since they are refreshed when upgrading atts and
            # learning techs


# todo refactor: get rid of Challenger, Master, Thug, but set occupation (quotes) instead
class Challenger(Fighter):
    quotes = 'challenger'


class Master(Fighter):
    quotes = 'master'


class Thug(Fighter):
    quotes = 'thug'
