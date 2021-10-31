from ...kung_fu import styles

from ._ai import FightAIMethods
from ._fight_actions import FighterWithActions
from ._fight_utils import FightUtils
from ._moves import MoveMethods
from ._quotes import QuoteMethods
from ._stats import FighterStats
from ._style import StyleMethods
from ._techs import TechMethods
from ._weapons import WeaponMethods


class Fighter(
    FightAIMethods,
    FighterStats,
    FighterWithActions,
    FightUtils,
    MoveMethods,
    QuoteMethods,
    StyleMethods,
    TechMethods,
    WeaponMethods,
):
    is_human = False
    is_player = False

    # the order of arguments should not be changed, or saving will break
    def __init__(
        self,
        name='',
        style_name=styles.FLOWER_KUNGFU.name,
        level=1,
        atts_tuple=None,
        tech_names=None,
        move_names=None,
        rand_atts_mode=0,
    ):
        super().__init__()
        self.name = name
        self.level = level
        self.rand_atts_mode = rand_atts_mode
        self.set_att_weights()
        self.set_atts(atts_tuple)
        self.set_style(style_name)
        self.set_techs(tech_names)
        self.set_moves(move_names)
        self.set_fight_ai()
        self.refresh_full_atts()

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
            self.resolve_techs_on_level_up()
            self.resolve_moves_on_level_up()
            # NB! no need to refresh full atts here since they are refreshed when upgrading atts and
            # learning techs


class Challenger(Fighter):
    quotes = 'challenger'


class Master(Fighter):
    quotes = 'master'


class Thug(Fighter):
    quotes = 'thug'
