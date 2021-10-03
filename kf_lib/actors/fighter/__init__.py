from ...fighting.distances import VALID_DISTANCES, DISTANCES_VISUALIZATION
from ...fighting.fight import fight
from ...ai.fight_ai import DefaultFightAI
from ...kung_fu import styles, moves
from ...utils.utilities import *

from ._constants import *
from ._exp_worth import ExpWorthUser
from ._quotes import QuoteUser
from ._techs import TechUser
from ._weapons import WeaponUser


class Fighter(
    ExpWorthUser,
    QuoteUser,
    TechUser,
    WeaponUser,
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
        self.set_fight_ai(DefaultFightAI)
        self.rand_atts_mode = rand_atts_mode
        self.set_att_weights()
        self.set_atts(atts_tuple)
        self.set_style(style_name)

        # in fight attributes (refreshed)
        self.act_allies = []
        self.act_targets = []
        self.action = None
        self.atk_pwr = 0
        self.atk_bonus = 0
        self.av_moves = []
        self.current_fight = None  # ...Fight object
        self.dam = 0
        self.defended = False
        self.dfs_bonus = 1.0  # for moves like Guard
        self.dfs_penalty_mult = 1.0
        self.dfs_pwr = 0
        self.distances = {}  # fighter_obj: int
        self.is_auto_fighting = True
        self.qp_start = 0.0  # portion of total
        self.previous_actions = ['', '', '']
        self.stamina_factor = 1.0
        self.status = {}  # {'status_name': status_dur}
        self.target = None  # both for attacker and defender
        self.to_block = 0
        self.to_dodge = 0
        self.to_hit = 0

        self.set_techs(tech_names)
        self.set_moves(move_names)

    def __repr__(self):
        return self.get_init_string()

    # def add_style_tech(self):
    #     self.add_tech(self.style.tech.name)

    def add_status(self, status, dur):
        if status not in self.status:
            self.status[status] = 0
        self.status[status] += dur

    def change_distance(self, dist, targ):
        dist = self.distances[targ] + dist
        if dist < 1:
            dist = 1  # don't just skip turn, as some maneuvers may still work, e.g. 2 - 2 = 0 -> 1
        elif dist > 4:
            dist = 4  # e.g. 3 + 2 = 5 -> 4
        self.distances[targ] = targ.distances[self] = dist

    def change_stat(self, *args):
        pass

    def check_status(self, status):
        return self.status.get(status, False)

    def fight(self, en, allies=None, en_allies=None, *args, **kwargs):
        return fight(self, en, allies, en_allies, *args, **kwargs)

    def get_numerical_status(self):
        """This can be used as a simple metric for how 'well' the fighter is."""
        # todo make this metric weighted, as hp is more important than stamina / qp
        return mean((self.hp / self.hp_max, self.stamina / self.stamina_max, self.qp / self.qp_max))

    def get_rep_actions_factor(self, move):
        n = self.previous_actions.count(move.name)  # 0-3
        return 1.0 + n * 0.33  # up to 1.99

    def get_status_marks(self):
        slowed_down = ',' if self.check_status('slowed down') else ''
        off_bal = '\'' if self.check_status('off-balance') else ''
        lying = '...' if self.check_status('lying') else ''
        excl = 0
        if self.check_status('shocked'):
            excl = 2
        elif self.check_status('stunned'):
            excl = 1
        # inact = '{}'.format('!' * excl) if excl else ''
        inact = '!' * excl
        padding = ' ' if lying or inact else ''
        return f'{padding}{slowed_down}{off_bal}{lying}{inact}'

    @staticmethod
    def get_vis_distance(dist):
        return DISTANCES_VISUALIZATION[dist]

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
            if self.level in self.style.move_strings:
                move_s = self.style.move_strings[self.level]
                moves.resolve_style_move(move_s, self)
            elif self.level in LVS_GET_NEW_ADVANCED_MOVE:
                move_s = str(NEW_MOVE_TIERS[self.level])
                moves.resolve_style_move(move_s, self)
            # no need to refresh full atts here since they are refreshed when upgrading atts and
            # learning techs

    def set_target(self, target):
        self.target = target
        target.target = self

    def spar(
        self,
        en,
        allies=None,
        en_allies=None,
        auto_fight=False,
        af_option=True,
        hide_stats=False,
        environment_allowed=True,
    ):
        from kf_lib.fighting.fight import spar as f_spar

        return f_spar(
            self, en, allies, en_allies, auto_fight, af_option, hide_stats, environment_allowed
        )


class Challenger(Fighter):
    quotes = 'challenger'


class Master(Fighter):
    quotes = 'master'


class Thug(Fighter):
    quotes = 'thug'
