from ...fighting.distances import VALID_DISTANCES, DISTANCES_VISUALIZATION
from ...fighting.fight import fight
from ...ai.fight_ai import DefaultFightAI
from ...kung_fu import styles, moves, ascii_art
from ...utils import exceptions
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

        # AI
        self.fight_ai = None
        self.set_fight_ai(DefaultFightAI)

        # attributes
        self.rand_atts_mode = rand_atts_mode
        self.att_names = ('strength', 'agility', 'speed', 'health')
        self.att_names_short = ('Str', 'Agi', 'Spd', 'Hlt')
        self.strength = 0
        self.strength_full = 0
        self.agility = 0
        self.agility_full = 0
        self.speed = 0
        self.speed_full = 0
        self.health = 0
        self.health_full = 0

        self.att_weights = {}
        self.set_att_weights()
        self.set_atts(atts_tuple)

        # style
        self.style = None  # Style object
        self.set_style(style_name)

        # in fight attributes (refreshed)
        self.act_allies = []
        self.act_targets = []
        self.action = None
        self.ascii_l = ''
        self.ascii_r = ''
        self.ascii_name = ''
        self.atk_pwr = 0
        self.atk_bonus = 0
        self.av_moves = []
        self.counter_chance = 0.0
        self.current_fight = None  # ...Fight object
        self.dam = 0
        self.defended = False
        self.dfs_bonus = 1.0  # for moves like Guard
        self.dfs_penalty_mult = 1.0
        self.dfs_pwr = 0
        self.distances = {}  # fighter_obj: int
        self.hp = 0
        self.hp_max = 0
        self.hp_gain = 0
        self.is_auto_fighting = True
        self.kos_this_fight = 0
        self.qp = 0
        self.qp_gain = 0
        self.qp_max = 0
        self.qp_start = 0.0  # portion of total
        self.previous_actions = ['', '', '']
        self.stamina_gain = 0
        self.stamina_max = 0
        self.stamina = 0
        self.stamina_factor = 1.0
        self.status = {}  # {'status_name': status_dur}
        self.target = None  # both for attacker and defender
        self.to_block = 0
        self.to_dodge = 0
        self.to_hit = 0

        # techniques
        self.set_techs(tech_names)

        # moves
        self.moves = []  # Move objects
        for m in moves.BASIC_MOVES:
            self.learn_move(m.name, silent=True)  # silent = don't write log
        self.set_moves(move_names)

    def __repr__(self):
        return self.get_init_string()

    # def add_style_tech(self):
    #     self.add_tech(self.style.tech.name)

    def add_status(self, status, dur):
        if status not in self.status:
            self.status[status] = 0
        self.status[status] += dur

    def boost(self, **kwargs):
        """Boost fighter's attribute(s); k = att_name, v = quantity"""
        for k, v in kwargs.items():
            curr_v = getattr(self, k)
            setattr(self, k, curr_v + v)
        self.refresh_full_atts()

    def change_att(self, att, amount):
        setattr(self, att, getattr(self, att) + amount)
        self.refresh_full_atts()

    def change_distance(self, dist, targ):
        dist = self.distances[targ] + dist
        if dist < 1:
            dist = 1  # don't just skip turn, as some maneuvers may still work, e.g. 2 - 2 = 0 -> 1
        elif dist > 4:
            dist = 4  # e.g. 3 + 2 = 5 -> 4
        self.distances[targ] = targ.distances[self] = dist

    def change_hp(self, amount):
        self.hp += amount
        if self.hp > self.hp_max:
            self.hp = self.hp_max
        elif self.hp < 0:
            self.hp = 0
            # set qp to zero too
            self.qp = 0

    def change_qp(self, amount):
        self.qp += amount
        if self.qp > self.qp_max:
            self.qp = self.qp_max
        elif self.qp < 0:
            self.qp = 0

    def change_stamina(self, amount):
        self.stamina += amount
        if self.stamina > self.stamina_max:
            self.stamina = self.stamina_max
        elif self.stamina < 0:
            self.stamina = 0

    def change_stat(self, *args):
        pass

    def check_lv(self, minlv, maxlv=None):
        if maxlv is None:
            return self.level >= minlv
        else:
            return minlv <= self.level <= maxlv

    def check_move_failed(self):
        compl = self.action.complexity
        f_ch = self.get_move_fail_chance(self.action)
        if rnd() <= f_ch:
            if self.action.power:
                self.to_hit = 0
                if compl >= 1:
                    self.current_fight.display('Miss!')
                    self.cause_off_balance()
            if self.action.dist_change:
                self.current_fight.display('Fail!')
                if compl >= 3:
                    self.cause_fall()
                else:
                    self.cause_off_balance()
            return True
        else:
            return False

    def check_stamina(self, amount):
        return self.stamina >= amount

    def check_status(self, status):
        return self.status.get(status, False)

    def choose_att_to_upgrade(self):
        atts = self.get_atts_to_choose()
        att = self.choose_better_att(atts)
        self.change_att(att, 1)

    def choose_better_att(self, atts):
        temp_dict = {}
        for att in atts:
            weight = self.att_weights[att]
            if weight in temp_dict:
                temp_dict[weight].append(att)
            else:
                temp_dict[weight] = [att]
        weights = sorted([w for w in temp_dict.keys()])
        att = random.choice(temp_dict[weights[-1]])  # several atts might have the same weight
        return att

    def choose_new_move(self, sample):
        self.learn_move(random.choice(sample).name)

    def cls(self):
        """Empty method for convenience"""
        pass

    def fight(self, en, allies=None, en_allies=None, *args, **kwargs):
        return fight(self, en, allies, en_allies, *args, **kwargs)

    def get_all_atts_str(self):
        atts_info = []
        for i, att in enumerate(self.att_names):
            short = self.att_names_short[i]
            v = self.get_att_str(att)
            atts_info.append(f'{short}:{v}')
        return ' '.join(atts_info)

    def get_att_str(self, att):
        base, full = self.get_base_att_value(att), self.get_full_att_value(att)
        return f'{full}({base})' if full > base else str(base)

    def get_att_str_prefight(self, att, hide=False):
        base, full = self.get_base_att_value(att), self.get_full_att_value(att)
        s = str(full) if not hide else '?'
        aster = '*' if full > base else ''
        return s + aster

    def get_att_values_full(self):
        return tuple(self.get_full_att_value(att) for att in self.att_names)

    def get_atts_to_choose(self):
        return random.sample(self.att_names, self.num_atts_choose)

    def get_base_att_value(self, att):
        return getattr(self, att)

    def get_base_atts_tup(self):
        return self.strength, self.agility, self.speed, self.health

    def get_full_att_value(self, att):
        return getattr(self, att + '_full')

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

    def get_max_att_value(self):
        return max(self.get_base_atts_tup())

    def get_move_fail_chance(self, move_obj):
        return move_obj.complexity ** 2 / self.agility_full ** 2

    @staticmethod
    def get_move_tier_string(move_obj):
        t = move_obj.tier
        return f' ({roman(t)})' if t else ''

    def get_move_time_cost(self, move_obj):
        if self.check_status('slowed down'):
            mob_mod = 1 - MOB_DAM_PENALTY
        else:
            mob_mod = 1
        cost = round(move_obj.time_cost / (self.speed_full * mob_mod))
        return cost

    def get_moves_to_choose(self, tier):
        return moves.get_rand_moves(self, self.num_moves_choose, tier)

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

    def get_style_string(self, show_emph=False):
        if show_emph:
            emph_info = f'\n {self.style.descr_short}'
        else:
            emph_info = ''
        return f'{self.style.name}{emph_info}'

    @staticmethod
    def get_vis_distance(dist):
        return DISTANCES_VISUALIZATION[dist]

    def learn_move(self, move, silent=False):
        """move can be a Move object or a move name string"""
        if isinstance(move, str):
            try:
                move = moves.get_move_obj(move)
            except exceptions.MoveNotFoundError as e:
                print(e)
                pak()
                return
        self.moves.append(move)
        if not silent:
            self.show(f'{self.name} learns {move.name} ({move.descr}).')
            self.log(f'Learns {move.name} ({move.descr})')
            self.pak()

    def learn_random_move(self, move_tier, silent=False):
        try:
            move_obj = moves.get_rand_move(self, move_tier)
        except exceptions.MoveNotFoundError as e:
            print(e)
            pak()
            return
        self.learn_move(move_obj, silent=silent)

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

    def refresh_ascii(self):
        self.ascii_l, self.ascii_r = self.action.ascii_l, self.action.ascii_r
        targ = self.target
        if targ.check_status('lying'):
            targ.set_ascii('Lying')
        else:
            targ.set_ascii('Stance')

    def refresh_full_atts(self):
        for att in self.att_names:
            base = getattr(self, att)
            mult = getattr(self, att + '_mult')
            setattr(self, att + '_full', round(base * mult))
        self.hp_max = self.health_full * HP_PER_HEALTH_LV
        self.stamina_max = round(
            (STAMINA_BASE + STAMINA_INCR_PER_LV * self.level) * self.stamina_max_mult
        )
        self.stamina_gain = round(self.stamina_max / 10 * self.stamina_gain_mult)
        self.qp_max = round(
            (QP_BASE + QP_INCR_PER_LV * self.level) * self.qp_max_mult
        )
        self.qp_gain = round(self.qp_max / 5 * self.qp_gain_mult)
        self.counter_chance = (
            (COUNTER_CHANCE_BASE + COUNTER_CHANCE_INCR_PER_LV * self.level) *
            self.counter_chance_mult
        )

    def replace_move(self, rep_mv, rep_with):
        def _rep_in_list(mv_a, mv_b, move_list):
            i = move_list.index(mv_a)
            move_list.remove(mv_a)
            move_list.insert(i, mv_b)
        _rep_in_list(rep_mv, rep_with, self.moves)

    def set_ascii(self, ascii_name):
        self.ascii_l, self.ascii_r = ascii_art.get_ascii(ascii_name)
        self.ascii_name = ascii_name

    def set_att_weights(self):
        """This is used for choosing better atts when upgrading / randomly generating fighters"""
        for att in self.att_names:
            setattr(self, att, 3)
            self.att_weights[att] = 0  # default weights

        # default, 'old' method
        if self.rand_atts_mode == 0:
            pass
        # random weights
        elif self.rand_atts_mode in {1, 2}:
            for att in self.att_names:
                # self.att_weights[att] = random.randint(1, 2)
                self.att_weights[att] = 1
        # TODO: more intelligent att selection depending on the style perks

    def set_atts(self, atts):
        if not atts:
            self.set_rand_atts()
        else:
            for i, att in enumerate(self.att_names):
                setattr(self, att, atts[i])

    def set_fight_ai(self, ai_class, write_log=False):
        self.fight_ai = ai_class(self, write_log)

    def set_moves(self, move_names):
        if not move_names:
            self.set_rand_moves()
        else:
            for mn in move_names:
                self.learn_move(mn, silent=True)

    def set_rand_atts(self):
        for i in range(self.level + 2):
            atts = self.get_atts_to_choose()
            att = self.choose_better_att(atts)
            value = getattr(self, att)
            setattr(self, att, value + 1)

    def set_rand_moves(self):
        for lv in LVS_GET_NEW_ADVANCED_MOVE:
            if self.level >= lv:
                tier = NEW_MOVE_TIERS[lv]
                self.learn_move(moves.get_rand_moves(self, 1, tier)[0])
            else:
                break
        for lv, moves_to_learn in self.style.move_strings.items():
            if self.level >= lv:
                if isinstance(moves_to_learn, str):  # can be a tuple, can be a string
                    moves_to_learn = (moves_to_learn,)
                for move_s in moves_to_learn:
                    moves.resolve_style_move(move_s, self)

    def set_style(self, style_name):
        if style_name is not None:
            style_obj = styles.get_style_obj(style_name)
        else:
            style_obj = styles.FLOWER_KUNGFU
        self.style = style_obj

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

    def unboost(self, **kwargs):
        """'Unboost' fighter's attributes."""
        kwargs_copy = {}
        for k, v in kwargs.items():
            kwargs_copy[k] = -v
        self.boost(**kwargs_copy)
        self.refresh_full_atts()


class Challenger(Fighter):
    quotes = 'challenger'


class Master(Fighter):
    quotes = 'master'


class Thug(Fighter):
    quotes = 'thug'
