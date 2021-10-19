from ...kung_fu import styles, moves

# from ._constants import *
from ._exp_worth import ExpMethods
from ._quotes import QuoteMethods
from ._techs import TechMethods
from ._weapons import WeaponMethods


class Fighter(
    ExpMethods,
    QuoteMethods,
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
        self.name = name
        self.level = level
        self.rand_atts_mode = rand_atts_mode
        self.set_att_weights()
        self.set_atts(atts_tuple)
        self.set_style(style_name)
        self.set_techs(tech_names)
        self.set_moves(move_names)

    # def add_style_tech(self):
    #     self.add_tech(self.style.tech.name)

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

    # todo use methods from corresponding submodules, don't handle moves, etc. in this method
    def level_up(self, n=1):
        # print(self.style.move_strings)
        for i in range(n):
            self.level += 1

            # increase a stat
            self.choose_att_to_upgrade()

            # techs
            if self.style.is_tech_style:
                self.resolve_techs_on_level_up()

            # moves
            # todo wrap move acquisition on level up
            if self.level in self.style.move_strings:
                move_s = self.style.move_strings[self.level]
                moves.resolve_style_move(move_s, self)
            elif self.level in LVS_GET_NEW_ADVANCED_MOVE:
                move_s = str(NEW_MOVE_TIERS[self.level])
                moves.resolve_style_move(move_s, self)
            # NB! no need to refresh full atts here since they are refreshed when upgrading atts and
            # learning techs


class Challenger(Fighter):
    quotes = 'challenger'


class Master(Fighter):
    quotes = 'master'


class Thug(Fighter):
    quotes = 'thug'
