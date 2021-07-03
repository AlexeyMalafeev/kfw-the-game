from ...fighting.distances import VALID_DISTANCES, DISTANCES_VISUALIZATION
from ...fighting.fight import fight
from ...actors import experience, quotes
from ...ai.fight_ai import DefaultFightAI
from ...kung_fu import styles, moves, techniques, ascii_art
from ...things import weapons
from ...utils import exceptions
from ...utils.utilities import *

from ._constants import *


class Fighter(object):
    is_human = False
    is_player = False

    # the following attribute values can be modified by Techs and Styles
    adv_tech_at_lv = ADVANCED_TECH_AT_LV
    agility_mult = 1.0
    atk_mult = 1.0
    atk_wp_bonus = 0
    block_disarm = 0.005
    block_power = 1.0
    counter_chance_mult = 1.0
    critical_chance = 0.05
    critical_mult = 1.5
    dam_reduc = 0  # todo adjust this and hp_gain in boosts.py
    dfs_mult = 1.0
    dfs_penalty_step = 0.2
    dfs_wp_bonus = 0  # todo not used; delete?
    environment_chance = 0.0  # todo get rid of this as it is just another critical?
    grab_chance = 0.0  # todo not used yet
    guard_dfs_bonus = 1.0
    guard_while_attacking = False
    health_mult = 1.0
    hit_disarm = 0.005
    in_fight_impro_wp_chance = 0.0
    lying_dfs_mult = 0.5
    num_atts_choose = 3
    num_moves_choose = 3
    num_techs_choose = 3
    num_techs_choose_upgrade = 3
    off_balance_atk_mult = 0.75
    off_balance_dfs_mult = 0.75
    speed_mult = 1.0
    stamina_gain_mult = 1.0
    stamina_max_mult = 1.0
    strength_mult = 1.0
    stun_chance = 0.0
    qp_gain_mult = 1.0
    qp_max_mult = 1.0
    quotes = 'fighter'
    resist_ko = 0.0
    unblock_chance = 0.0
    wp_dfs_bonus = 1.0

    # strike multipliers todo reimplement as a default dict? a data class?
    claw_strike_mult = 1.0
    dist1_bonus = 1.0
    dist2_bonus = 1.0
    dist3_bonus = 1.0
    elbow_strike_mult = 1.0
    exotic_strike_mult = 1.0
    flying_strike_mult = 1.0
    grappling_strike_mult = 1.0
    head_strike_mult = 1.0
    kick_strike_mult = 1.0
    knee_strike_mult = 1.0
    palm_strike_mult = 1.0
    punch_strike_mult = 1.0
    weapon_strike_mult = 1.0

    # dfs multipliers
    block_mult = 1.0
    dodge_mult = 1.0

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

        # weapon
        self.weapon = None
        self.weapon_bonus = {}  # {<weapon name OR type>: [atk_bonus, dfs_bonus]}

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
        self.exp_yield = 0
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
        self.took_damage = False

        # techniques
        self.techs = set()  # Tech names (strings)
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

    def apply_dfs_penalty(self):
        self.dfs_penalty_mult -= self.dfs_penalty_step
        if self.dfs_penalty_mult < 0:
            self.dfs_penalty_mult = 0

    def add_status(self, status, dur):
        if status not in self.status:
            self.status[status] = 0
        self.status[status] += dur

    def add_tech(self, tn):
        self.techs.add(tn)
        self.apply_tech(tn)

    def apply_tech(self, *tech_names):
        for tn in tech_names:
            techniques.apply(tn, self)
        self.refresh_full_atts()  # in case techs affects them

    def arm(self, weapon=None):
        """Arm fighter with weapon (default = random).
        weapon can also be weapon type"""
        # disarm fighter to avoid double weapon bonus
        self.disarm()
        # make new weapon
        if weapon is None:
            wp = random.choice(weapons.ALL_WEAPONS_LIST)
        elif weapon in weapons.WEAPON_TYPES:
            wp = weapons.get_rnd_wp_by_type(weapon)
        elif weapon in weapons.ALL_WEAPONS_SET:
            wp = weapon
        else:
            wp = weapons.get_wp(weapon)
        self.weapon = wp
        self.wp_dfs_bonus = wp.dfs_bonus

    def arm_improv(self):
        """Arm fighter with a random improvised weapon"""
        self.arm('improvised')

    def arm_normal(self):
        """Arm fighter with a random normal weapon"""
        self.arm('normal')

    def arm_police(self):
        """Arm fighter with a random police weapon"""
        self.arm('police')

    def arm_robber(self):
        """Arm fighter with a random robber weapon"""
        self.arm('robber')

    def attack(self):
        n1 = self.current_fight.get_f_name_string(self)
        n2 = self.current_fight.get_f_name_string(self.target)
        s = f'{n1}: {self.action.name} @ {n2}'
        self.current_fight.display(s)
        if self.guard_while_attacking:
            self.current_fight.display(f' (guarding while attacking)')
            self.dfs_bonus += self.guard_dfs_bonus * self.guard_while_attacking
        self.current_fight.display('=' * len(s))
        # print(n2, 'dfs_bonus', self.target.dfs_bonus)
        self.try_strike()
        self.target.try_counter()

    def boost(self, **kwargs):
        """Boost fighter's attribute(s); k = att_name, v = quantity"""
        for k, v in kwargs.items():
            curr_v = getattr(self, k)
            setattr(self, k, curr_v + v)
        self.refresh_full_atts()

    def calc_atk(self, action):
        """Calculate attack numbers w.r.t. some action (not necessarily action chosen)."""
        strike_mult = 1.0
        strike_mult *= getattr(self, f'dist{action.distance}_bonus', 1.0)
        for feature in action.features:
            # low-prio todo reimplement computing strike_mult without getattr, use dict
            strike_mult *= getattr(self, f'{feature}_strike_mult', 1.0)
        self.atk_bonus = self.atk_mult * strike_mult
        if self.check_status('off-balance'):
            self.atk_bonus *= self.off_balance_atk_mult
        self.atk_pwr = (
            self.strength_full * action.power * self.atk_bonus * self.stamina_factor / DAM_DIVISOR
        )
        self.to_hit = self.agility_full * action.accuracy * self.atk_bonus * self.stamina_factor

    # todo how is it used? why not relative to attacker?
    def calc_dfs(self):
        """Calculate defense numbers."""
        if self.check_status('shocked'):
            self.to_dodge = 0
            self.to_block = 0
        else:
            attacker = self.target
            atk_action = attacker.action
            rep_actions_factor = attacker.get_rep_actions_factor(atk_action)
            # todo recalc as a value in (0.0, 1.0)?
            # * 10 because of new system:
            x = self.dfs_penalty_mult * self.agility_full * self.dodge_mult * 10
            x *= self.stamina_factor * rep_actions_factor
            x *= self.dfs_bonus
            # print('x after dfs_bonus', x)
            if self.check_status('off-balance'):
                x *= self.off_balance_dfs_mult
            if self.check_status('lying'):
                x *= self.lying_dfs_mult
            self.to_dodge = x / DODGE_DIVISOR
            self.to_block = x / BLOCK_DIVISOR
            self.to_block *= self.wp_dfs_bonus  # no weapon bonus to dodging!
            # print('to dodge, to block', self.to_dodge, self.to_block)
            self.dfs_pwr = self.dfs_penalty_mult * self.block_power * self.strength_full
            self.dfs_pwr *= self.stamina_factor * self.wp_dfs_bonus  # todo divide by sth?

    def calc_stamina_factor(self):
        # todo docstring calc_stamina_factor
        self.stamina_factor = self.stamina / self.stamina_max / 2 + STAMINA_FACTOR_BIAS

    def cause_fall(self):
        lying_dur = rndint_2d(DUR_LYING_MIN, DUR_LYING_MAX) // self.speed_full
        self.add_status('lying', lying_dur)
        self.add_status('skip', lying_dur)
        fall_dam = rndint(*FALL_DAMAGE)
        self.change_hp(-fall_dam)
        self.set_ascii('Falling')
        self.current_fight.display(f' falls to the ground! -{fall_dam} HP ({self.hp})', align=False)
        # print('$$$', self.status)

    def cause_knockback(self, dist):
        opp = self.target
        self.change_distance(dist, opp)
        s = 's' if dist > 1 else ''
        self.set_ascii('Knockback')
        # self.current_fight.display('{} is knocked back {} step{}!'.format(self.name, dist, s))
        self.current_fight.display(f' knocked back {dist} step{s}!', align=False)

    def cause_off_balance(self):
        ob_dur = rndint_2d(DUR_OFF_BAL_MIN, DUR_OFF_BAL_MAX) // self.speed_full
        self.add_status('off-balance', ob_dur)
        # self.current_fight.display('{} is off-balance!'.format(self.name))
        self.current_fight.display(' off-balance!', align=False)
        # print('$$$', self.status)

    def cause_shock(self):
        """Shock is worse than stun."""
        shock_dur = rndint_2d(DUR_SHOCK_MIN, DUR_SHOCK_MAX) // self.speed_full
        self.add_status('shocked', shock_dur)
        self.add_status('skip', shock_dur)
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        # self.current_fight.display('{} is shocked!'.format(self.name))
        self.current_fight.display(' shocked!', align=False)
        # print('$$$', self.status)

    def cause_slow_down(self):
        slow_dur = rndint_2d(DUR_SLOW_MIN, DUR_SLOW_MAX) // self.speed_full
        self.add_status('slowed down', slow_dur)
        # todo do not repeat this line in all functions, use helper
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        # self.current_fight.display('{} is slowed down!'.format(self.name))
        self.current_fight.display(' slowed down!', align=False)

    def cause_stun(self):
        """Stun is not as bad as shock."""
        stun_dur = rndint_2d(DUR_STUN_MIN, DUR_STUN_MAX) // self.speed_full
        self.add_status('stunned', stun_dur)
        self.add_status('skip', stun_dur)
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        # self.current_fight.display('{} is stunned!'.format(self.name))
        self.current_fight.display(' stunned!', align=False)
        # print('$$$', self.status)

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

    def choose_best_norm_wp(self):
        wns = weapons.NORMAL_WEAPONS
        best_bonus = 0
        chosen_tech = None
        for t in techniques.get_weapon_techs(fighter=self):
            t = techniques.get_tech_obj(t)
            if t.wp_type == 'normal' or t.wp_type in wns:
                bon = t.wp_bonus[0] + t.wp_bonus[1]
                if bon > best_bonus:
                    best_bonus = bon
                    chosen_tech = t
        if chosen_tech:
            self.arm(chosen_tech.wp_type)
            return
        self.arm_normal()

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

    def choose_move(self):
        self.av_moves = self.get_av_moves()  # this depends on target
        self.action = self.fight_ai.choose_move()

    def choose_new_move(self, sample):
        self.learn_move(random.choice(sample).name)

    def choose_new_tech(self):
        sample = self.get_techs_to_choose()
        if not sample:
            return
        self.learn_tech(random.choice(sample))

    def choose_target(self):
        if len(self.act_targets) == 1:
            self.set_target(self.act_targets[0])
        else:
            self.set_target(self.fight_ai.choose_target())

    def choose_tech_to_upgrade(self):
        av_techs = self.get_techs_to_choose(for_upgrade=True)
        if not av_techs:
            return
        self.upgrade_tech(random.choice(av_techs))

    def cls(self):
        """Empty method for convenience"""
        pass

    def defend(self):
        atkr = self.target
        atkr.dam = atkr.atk_pwr
        dodge_chance = self.to_dodge / atkr.to_hit
        block_chance = self.to_block / atkr.to_hit
        roll = rnd()
        prefix = 'Lying ' if self.check_status('lying') else ''
        self.defended = False
        if roll <= dodge_chance:
            atkr.dam = 0
            self.change_qp(self.qp_gain)
            self.current_fight.display(
                '{} {}dodges!'.format(self.name, get_adverb(dodge_chance, 'barely', 'easily'))
            )
            self.set_ascii(prefix + 'Dodge')
            self.defended = True
        elif roll <= block_chance:
            atkr.dam = max(atkr.dam - self.dfs_pwr, 0)
            self.change_qp(self.qp_gain // 2)
            self.current_fight.display(
                '{} {}blocks!'.format(self.name, get_adverb(block_chance, 'barely', 'easily'))
            )
            self.set_ascii(prefix + 'Block')
            self.try_block_disarm()
            self.defended = True
        else:
            self.set_ascii(prefix + 'Hit')
        # todo handle the no defense case
        atkr.dam = round(atkr.dam)

    def disarm(self):
        if self.weapon:
            self.weapon = None
            self.wp_dfs_bonus = 1.0

    def do_agility_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.agility_full * STAT_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' agility-based -{dam} HP ({targ.hp})', align=False)

    def do_counter(self):
        cand_moves = self.get_av_moves(attack_moves_only=True)
        if cand_moves:
            self.current_fight.display('COUNTER!')
            new_action = random.choice(cand_moves)
            self.action = new_action
            s = f'{self.name}: {self.action.name} @ {self.target.name}'
            self.current_fight.display(s)
            self.do_strike()

    def do_knockback(self):
        dist = random.choice(KNOCKBACK_DIST_FORCED)
        self.target.cause_knockback(dist)

    def do_level_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.level * LEVEL_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' level-based -{dam} HP ({targ.hp})', align=False)

    def do_mob_dam(self):
        self.target.cause_slow_down()

    def do_move_functions(self, m):
        if m.functions:
            for fun_s in m.functions:
                fun = getattr(self, fun_s)
                fun()

    def do_qi_based_dam(self):
        targ = self.target
        dam = rndint_2d(self.qp, self.qp * QI_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' qi-based -{dam} HP ({targ.hp})', align=False)

    def do_shock_move(self):
        self.target.cause_shock()

    def do_speed_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.speed_full * STAT_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' speed-based -{dam} HP ({targ.hp})', align=False)

    def do_stam_dam(self):
        targ = self.target
        dam = round(targ.stamina_max * STAMINA_DAMAGE)
        targ.change_stamina(-dam)
        prefix = 'lying ' if targ.check_status('lying') else ''
        targ.set_ascii(prefix + 'Hit Effect')
        self.current_fight.display(' gasps for breath!', align=False)

    def do_strength_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.strength_full * STAT_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' strength-based -{dam} HP ({targ.hp})', align=False)

    def do_strike(self):
        m = self.action
        self.calc_atk(m)
        self.try_environment('attack')
        self.try_critical()
        self.target.calc_dfs()
        self.try_unblockable()
        self.target.try_environment('defense')
        self.target.defend()
        self.hit_or_miss()
        self.target.apply_dfs_penalty()
        if m.dist_change:
            self.change_distance(m.dist_change, self.target)
        self.previous_actions = self.previous_actions[1:] + [m.name]
        self.change_stamina(-m.stam_cost)
        self.change_qp(-m.qi_cost)

    def do_takedown(self):
        targ = self.target
        targ.cause_fall()

    def exec_move(self):
        m = self.action
        self.current_fight.cls()
        if m.power:
            self.attack()  # changing distance is included
        else:
            self.maneuver()
        self.current_fight.show(self.visualize_fight_state())
        self.show_ascii()

    def fight(self, en, allies=None, en_allies=None, *args, **kwargs):
        return fight(self, en, allies, en_allies, *args, **kwargs)

    def get_all_atts_str(self):
        atts_info = []
        for i, att in enumerate(self.att_names):
            short = self.att_names_short[i]
            v = self.get_att_str(att)
            atts_info.append(f'{short}:{v}')
        return ' '.join(atts_info)

    def get_allies_power(self):  # TBD: this is not used yet
        return sum([f.get_exp_worth() for f in self.act_allies])

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

    def get_av_moves(self, attack_moves_only=False):
        av_moves = []
        lying_op = self.target.check_status('lying')
        for m in self.moves + (self.weapon.moves if self.weapon else []):
            enough_stamina = self.stamina >= m.stam_cost
            enough_qi = self.qp >= m.qi_cost
            if enough_stamina and enough_qi:
                if m.distance:
                    right_distance = m.distance == self.distances[self.target]
                    if right_distance:
                        anti_ground = (
                            'antiground only' in m.features or 'also antiground' in m.features
                        ) and lying_op
                        anti_standing = 'antiground only' not in m.features and not lying_op
                        if anti_ground or anti_standing:
                            av_moves.append(m)
                else:
                    av_moves.append(m)
        if attack_moves_only:
            av_moves = [m for m in av_moves if m.power]
        return av_moves

    def get_base_att_value(self, att):
        return getattr(self, att)

    def get_base_atts_tup(self):
        return self.strength, self.agility, self.speed, self.health

    def get_exp_worth(self):
        """Return how many experience points the fighter is 'worth'."""
        return experience.fighter_to_exp(self)

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

    def get_opponents_power(self):  # TBD: this can be useful for AI
        return sum([f.get_exp_worth() for f in self.act_targets])

    def get_prefight_info(self, side_a, side_b=None, hide_enemy_stats=False, basic_info_only=False):
        fs = side_a[:]
        if side_b:
            fs.extend(side_b)
        s = ''
        size1 = max([len(s) for s in ['NAME '] + [f.name + '  ' for f in fs]])
        size2 = max([len(s) for s in ['LEV '] + [str(f.level) + ' ' for f in fs]])
        size3 = max([len(s) for s in ['STYLE '] + [f.style.name + ' ' for f in fs]])
        att_names = ' '.join(self.att_names_short) if not basic_info_only else ''
        s += 'NAME'.ljust(size1) + 'LEV'.ljust(size2) + 'STYLE'.ljust(size3) + att_names
        if any([f.weapon for f in fs]) and not basic_info_only:
            s += ' WEAPON'
        for f in fs:
            if side_b and f == side_b[0]:
                s += '\n-vs-'
            s += '\n{:<{}}{:<{}}{:<{}}'.format(
                f.name,
                size1,
                f.level,
                size2,
                f.style.name,
                size3,
            )
            if basic_info_only:
                continue
            if (
                (not hide_enemy_stats)
                or f.is_human
                or (f in side_a and any([ff.is_human for ff in side_a]))
                or (side_b and f in side_b and any([ff.is_human for ff in side_b]))
            ):
                atts_wb = (f.get_att_str_prefight(att) for att in self.att_names)
            else:
                atts_wb = (f.get_att_str_prefight(att, hide=True) for att in self.att_names)
            s += '{:<4}{:<4}{:<4}{:<4}'.format(*atts_wb)
            if f.weapon:
                s += f'{f.weapon.name} {f.weapon.descr_short}'
            s += f"\n{' ' * (size1 + size2)}{f.style.descr_short}"
        return s

    def get_rel_strength(self, *opp, allies=None):
        """Return ratio (number, the lower the weaker) and legend (string, e.g. 'very risky')"""
        pwr = sum([op.get_exp_worth() for op in opp])
        own_pwr = self.get_exp_worth()
        if allies:
            own_pwr += sum([al.get_exp_worth() for al in allies])
        ratio = round(pwr / own_pwr, 2)
        table = (
            (RATIO_EXTREMELY_RISKY, 'impossible'),
            (RATIO_VERY_RISKY, 'very risky'),
            (RATIO_RISKY, 'risky'),
            (RATIO_FAIR_FIGHT, 'fair fight'),
            (RATIO_LOW_RISK, 'low risk'),
            (RATIO_VERY_LOW_RISK, 'very low risk'),
            (RATIO_NO_RISK, 'no risk'),
        )
        for threshold, legend in table:
            if ratio >= threshold:
                return ratio, legend

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

    def get_techs_string(self, descr=True, header='Techniques:'):
        if not self.techs:
            return ''
        align = max((len(t) for t in self.techs)) + 1
        output = []
        d = ''
        for t in self.techs:
            if descr:
                d = f'- {techniques.get_descr(t)}'
            output.append('{:<{}}{}'.format(t, align, d))
        output = [header] + sorted(output)
        return '\n'.join(output)

    def get_techs_to_choose(self, annotated=False, for_upgrade=False):
        if for_upgrade:
            num = self.num_techs_choose_upgrade
            av_techs = techniques.get_upgradable_techs(self)
        else:
            num = self.num_techs_choose
            av_techs = techniques.get_learnable_techs(self)
        if annotated:
            d = techniques.get_descr
            av_techs = [('{} ({})'.format(t, d(t)), t) for t in av_techs]
        if 0 < len(av_techs) < num:
            return av_techs
        elif not av_techs:
            return []
        else:
            return random.sample(av_techs, num)

    @staticmethod
    def get_vis_distance(dist):
        return DISTANCES_VISUALIZATION[dist]

    # todo reimplement this as a multiplier, not an addition of guard_dfs_bonus to dfs_bonus,
    #  but careful with wp_dfs_bonus
    def guard(self):
        """This is called with eval as a function of the Guard move."""
        # print('giving guard dfs bonus:', self.dfs_bonus, '+', self.guard_dfs_bonus)
        self.dfs_bonus += self.guard_dfs_bonus

    def hit_or_miss(self):
        tgt = self.target
        if self.dam > 0:
            self.dam = max(self.dam - tgt.dam_reduc, 0)
            tgt.take_damage(self.dam)
            self.current_fight.display(f'hit: -{self.dam} HP ({tgt.hp})')
            self.try_hit_disarm()
            self.do_move_functions(self.action)
            self.try_stun()
            self.try_knockback()
            self.try_knockdown()
            self.try_ko()

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

    def learn_tech(self, *techs):
        """techs can be Tech objects or tech name strings (or mixed)"""
        for tn in techs:
            if isinstance(tn, techniques.Tech):
                tn = tn.name
            if tn not in self.techs:
                descr = techniques.get_descr(tn)
                self.add_tech(tn)
                self.show(f'{self.name} learns {tn} ({descr}).')
                self.log(f'Learns {tn} ({descr})')
                self.pak()

    def level_up(self, n=1):
        self.disarm()
        # print(self.style.move_strings)
        for i in range(n):
            self.level += 1

            # increase a stat
            self.choose_att_to_upgrade()

            # techs
            if self.style.is_tech_style:
                # learn new style tech if possible
                t = self.style.techs.get(self.level)
                if t:
                    self.learn_tech(t.name)
                # upgrade tech if possible
                if self.check_lv(self.adv_tech_at_lv, self.adv_tech_at_lv):
                    self.choose_tech_to_upgrade()
                # learn new tech if possible
                if self.level in LVS_GET_NEW_TECH:
                    self.choose_new_tech()

            # moves
            if self.level in self.style.move_strings:
                move_s = self.style.move_strings[self.level]
                moves.resolve_style_move(move_s, self)
            elif self.level in LVS_GET_NEW_ADVANCED_MOVE:
                move_s = str(NEW_MOVE_TIERS[self.level])
                moves.resolve_style_move(move_s, self)
            # no need to refresh full atts here since they are refreshed when upgrading atts and
            # learning techs

    def log(self, text):
        """Empty method for convenience."""
        pass

    def maneuver(self):
        m = self.action
        n = self.current_fight.get_f_name_string(self)
        s = f'{n}: {m.name}'
        self.current_fight.display(s)
        self.current_fight.display('=' * len(s))
        if m.dist_change:
            self.change_distance(m.dist_change, self.target)
            self.check_move_failed()
        self.do_move_functions(m)
        self.change_stamina(-m.stam_cost)
        self.change_qp(-m.qi_cost)

    def msg(self, *args, **kwargs):
        pass

    def pak(self):
        pass

    def prepare_for_fight(self):
        self.hp = self.hp_max
        self.qp = round(self.qp_max * self.qp_start)
        self.stamina = self.stamina_max
        self.previous_actions = ['', '', '']
        self.is_auto_fighting = True
        self.distances = d = {}
        # todo optimize not to walk over the same pair of fighters twice
        for f2 in self.current_fight.all_fighters:
            if self is f2:
                d[f2] = 0
            else:
                dist = random.choice(VALID_DISTANCES)
                d[f2] = dist
                f2.distances[self] = dist
        self.status = {}
        self.exp_yield = self.get_exp_worth()
        self.took_damage = False
        self.kos_this_fight = 0

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

    def say_prefight_quote(self):
        pool = quotes.PREFIGHT_QUOTES.get(self.quotes, None)
        if pool is not None:
            q = random.choice(pool)
            self.current_fight.show(f'{self.name}: "{q}"')
            return True
        else:
            return False

    def say_win_quote(self):
        pool = quotes.WIN_QUOTES.get(self.quotes, None)
        if pool is not None:
            q = random.choice(pool)
            self.current_fight.show(f'{self.name}: "{q}"')

    def see_fight_info(self, *args, **kwargs):
        pass

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

    def set_rand_techs(self):
        n = len([lv for lv in LVS_GET_NEW_TECH if lv <= self.level])
        if self.style.is_tech_style:
            techs = []
            for lv, t in self.style.techs.items():
                if self.level >= lv:
                    techs.append(t.name)
            if n:
                techs += random.sample(techniques.get_upgradable_techs(), n)
            self.techs = set(techs)
            if self.check_lv(self.adv_tech_at_lv):
                t = random.choice(techniques.get_upgradable_techs(self))
                self.techs.remove(t)
                self.techs.add(techniques.reg_to_adv(t))

    def set_style(self, style_name):
        if style_name is not None:
            style_obj = styles.get_style_obj(style_name)
        else:
            style_obj = styles.FLOWER_KUNGFU
        self.style = style_obj

    def set_target(self, target):
        self.target = target
        target.target = self

    def set_techs(self, tech_names):
        if not tech_names:
            self.set_rand_techs()
        else:
            self.techs = set(tech_names)
        self.apply_tech(*self.techs)

    def show(self, text, align=False):
        pass

    def show_ascii(self):
        if self in self.current_fight.side_a:
            a = self.ascii_l
            b = self.target.ascii_r
        else:
            b = self.ascii_r
            a = self.target.ascii_l
        pic = ascii_art.concat(a, b)
        self.current_fight.show(pic, align=False)
        # prev = self.current_fight.cartoon[-1]
        # if pic != prev:
        self.current_fight.cartoon.append(pic)

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

    def start_fight_turn(self):
        cur_fight = self.current_fight
        self.act_targets = (
            cur_fight.active_side_b if self in cur_fight.active_side_a else cur_fight.active_side_a
        )
        self.act_allies = (
            cur_fight.active_side_b if self in cur_fight.active_side_b else cur_fight.active_side_a
        )
        self.action = None
        self.dfs_bonus = 1.0
        self.dfs_penalty_mult = 1.0
        self.target = None
        # breathing techs and other automatic actions
        self.change_hp(self.hp_gain)
        self.change_qp(self.qp_gain)
        self.change_stamina(self.stamina_gain)
        self.try_in_fight_impro_wp()  # before get_av_atk_actions! or won't get weapon moves
        self.calc_stamina_factor()

    def take_damage(self, dam):
        self.change_hp(-dam)
        self.took_damage = True

    def try_block_disarm(self):
        atkr = self.target
        if atkr.weapon and self.block_disarm and rnd() <= self.block_disarm:
            atkr.disarm()
            self.current_fight.display(f'{self.name} disarms {atkr.name} while blocking')

    def try_counter(self):
        if self.defended and self.hp > 0 and rnd() <= self.counter_chance:
            self.do_counter()

    def try_critical(self):
        if rnd() <= self.critical_chance:
            self.atk_pwr *= self.critical_mult
            self.current_fight.display('CRITICAL!')

    def try_environment(self, mode):
        if (
            self.environment_chance
            and self.current_fight.environment_allowed
            and rnd() <= self.environment_chance
        ):
            if mode == 'attack':
                self.atk_pwr *= self.current_fight.environment_bonus
                self.to_hit *= self.current_fight.environment_bonus
            elif mode == 'defense':
                self.dfs_pwr *= self.current_fight.environment_bonus
                self.to_block *= self.current_fight.environment_bonus
                self.to_dodge *= self.current_fight.environment_bonus
            self.current_fight.display(f'{self.name} uses the environment!')

    def try_hit_disarm(self):
        tgt = self.target
        if tgt.weapon and self.hit_disarm and rnd() <= self.hit_disarm:
            tgt.disarm()
            self.current_fight.display(f'{self.name} disarms {tgt.name} while attacking')

    def try_in_fight_impro_wp(self):
        if (
            self.in_fight_impro_wp_chance
            and not self.weapon
            and self.current_fight.environment_allowed
            and rnd() <= self.in_fight_impro_wp_chance
        ):
            self.arm_improv()
            s = self.current_fight.get_f_name_string(self)
            self.current_fight.display(f'{s} grabs an improvised weapon!')
            self.current_fight.pak()

    def try_insta_ko(self):
        targ = self.target
        if rnd() <= INSTA_KO_CHANCE:
            dam = targ.hp
            self.current_fight.display('INSTANT KNOCK-OUT!!!')
            targ.take_damage(dam)

    def try_knockback(self):
        targ = self.target
        kb = 0
        if not targ.check_status('lying'):
            dam_ratio = self.dam / targ.hp_max
            for thresh in KNOCKBACK_HP_THRESHOLDS:
                if dam_ratio > thresh:
                    kb += 1
        if kb > 0:
            targ.cause_knockback(kb)

    def try_knockdown(self):
        targ = self.target
        if not targ.check_status('lying'):
            if self.dam >= targ.hp_max / KNOCKDOWN_HP_DIVISOR:
                targ.cause_fall()
            elif self.dam >= targ.hp_max / OFF_BALANCE_HP_DIVISOR:
                targ.cause_off_balance()

    def try_ko(self):
        tgt = self.target
        if not tgt.hp:
            if tgt.resist_ko and rnd() <= tgt.resist_ko:
                tgt.hp = 1
                self.log(f'{tgt.name} resists being knocked out.')
                tgt.log('Resists being knocked out.')
                self.current_fight.display(f'{tgt.name} resists being knocked out!')
            else:
                self.kos_this_fight += 1
                self.log(f'Knocks out {tgt.name}.')
                tgt.log(f'Knocked out by {self.name}.')
                if not tgt.ascii_name.startswith('lying'):
                    tgt.set_ascii('Falling')
                self.current_fight.display(' KNOCK-OUT!'.format(tgt.name), align=False)

    def try_shock_move(self):
        targ = self.target
        if rnd() <= SHOCK_CHANCE:
            targ.cause_shock()

    def try_strike(self):
        if not self.check_move_failed():
            self.do_strike()

    def try_stun(self):
        targ = self.target
        if (self.dam >= targ.hp_max / STUN_HP_DIVISOR) or (
            self.stun_chance and rnd() <= self.stun_chance
        ):
            targ.cause_stun()

    def try_unblockable(self):
        if self.unblock_chance and rnd() <= self.unblock_chance:
            self.target.to_block = 0
            self.current_fight.display('UNBLOCKABLE!')

    def unboost(self, **kwargs):
        """'Unboost' fighter's attributes."""
        kwargs_copy = {}
        for k, v in kwargs.items():
            kwargs_copy[k] = -v
        self.boost(**kwargs_copy)
        self.refresh_full_atts()

    def unlearn_tech(self, tech):
        self.techs.remove(tech)
        techniques.undo(tech, self)

    def upgrade_tech(self, tech):
        self.unlearn_tech(tech)
        new_tech = techniques.reg_to_adv(tech)
        self.learn_tech(new_tech)

    def visualize_fight_state(self):
        try:
            ft = self.current_fight
            side_a, side_b = ft.active_side_a, ft.active_side_b
            n_a, n_b = len(side_a), len(side_b)
            hp_a, hp_b = sum((f.hp for f in side_a)), sum((f.hp for f in side_b))
            bar = get_bar(hp_a, hp_a + hp_b, '/', '\\', 20)
            s = f'\n{n_a} {bar} {n_b}\n'
            return s
        except ZeroDivisionError:
            from pprint import pprint
            import traceback
            traceback.print_exc()
            pprint(vars())
            pprint(vars(self))
            pprint(self.current_fight.timeline)
            pak()

    def write(self, *args, **kwargs):
        pass


class Challenger(Fighter):
    quotes = 'challenger'


class Master(Fighter):
    quotes = 'master'


class Thug(Fighter):
    quotes = 'thug'