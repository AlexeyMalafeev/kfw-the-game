from ._ascii import FighterWithASCII
from ...utils.utilities import rnd, rndint, rndint_2d


import random


BLOCK_DIVISOR = 2
DAM_DIVISOR = 2
DODGE_DIVISOR = 3
DUR_LYING_MIN = 100
DUR_LYING_MAX = 200
DUR_OFF_BAL_MIN = 30
DUR_OFF_BAL_MAX = 60
DUR_SHOCK_MIN = 50
DUR_SHOCK_MAX = 100
DUR_SLOW_MIN = 300
DUR_SLOW_MAX = 600
DUR_STUN_MIN = 50
DUR_STUN_MAX = 150
FALL_DAMAGE = (25, 50)
INSTA_KO_CHANCE = 0.25
KNOCKBACK_DIST_FORCED = (1, 1, 1, 2, 2, 3)
KNOCKBACK_FULL_HP_DAM = 5  # knockback distance when damage = full hp
KNOCKDOWN_HP_THRESHOLD = 0.5
LEVEL_BASED_DAM_UPPER_MULT = 10  # * self.level in damage; upper bound
MOB_DAM_PENALTY = 0.3
MOMENTUM_EFFECT_SIZE = 0.1
OFF_BALANCE_HP_THRESHOLD = 0.25
QI_BASED_DAM_UPPER_MULT = 3
SHOCK_CHANCE = 0.5  # for moves
STAMINA_DAMAGE = 0.2  # for moves
STAMINA_FACTOR_BIAS = 0.5
STAT_BASED_DAM_UPPER_MULT = 5
STUN_HP_DIVISOR = 2.8  # todo make STUN_HP_DIVISOR into threshold
TIME_UNIT_MULTIPLIER = 20


class StrikeMechanics(FighterWithASCII):
    took_damage = False

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
        # take into account momentum
        momentum_effect = 1.0 + MOMENTUM_EFFECT_SIZE * self.momentum
        self.atk_pwr *= momentum_effect
        self.to_hit *= momentum_effect

    # todo how is calc_dfs used? why not relative to attacker?
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
        self.momentum = 0

    def cause_knockback(self, dist):
        opp = self.target
        self.change_distance(dist, opp)
        s = 's' if dist > 1 else ''
        self.set_ascii('Knockback')
        self.ascii_buffer += dist
        self.current_fight.display(f' knocked back {dist} step{s}!', align=False)

    def cause_off_balance(self):
        ob_dur = rndint_2d(DUR_OFF_BAL_MIN, DUR_OFF_BAL_MAX) // self.speed_full
        self.add_status('off-balance', ob_dur)
        self.current_fight.display(' off-balance!', align=False)

    def cause_shock(self):
        """Shock is worse than stun."""
        shock_dur = rndint_2d(DUR_SHOCK_MIN, DUR_SHOCK_MAX) // self.speed_full
        self.add_status('shocked', shock_dur)
        self.add_status('skip', shock_dur)
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        self.current_fight.display(' shocked!', align=False)

    def cause_slow_down(self):
        slow_dur = rndint_2d(DUR_SLOW_MIN, DUR_SLOW_MAX) // self.speed_full
        self.add_status('slowed down', slow_dur)
        # todo do not repeat this line in all functions, use helper
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        self.current_fight.display(' slowed down!', align=False)

    def cause_stun(self):
        """Stun is not as bad as shock."""
        stun_dur = rndint_2d(DUR_STUN_MIN, DUR_STUN_MAX) // self.speed_full
        self.add_status('stunned', stun_dur)
        self.add_status('skip', stun_dur)
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        self.current_fight.display(' stunned!', align=False)

    def do_agility_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.agility_full * STAT_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' agility-based -{dam} HP ({targ.hp})', align=False)

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

    def do_takedown(self):
        targ = self.target
        targ.cause_fall()

    def get_move_fail_chance(self, move_obj):
        return move_obj.complexity ** 2 / self.agility_full ** 2

    def get_move_time_cost(self, move_obj):
        if self.check_status('slowed down'):
            mob_mod = 1 - MOB_DAM_PENALTY
        else:
            mob_mod = 1
        cost = move_obj.time_cost / (self.speed_full * mob_mod)
        if move_obj.power:
            cost *= self.strike_time_cost_mult
        elif move_obj.dist_change:
            cost *= self.maneuver_time_cost_mult
        return round(cost)

    def get_rep_actions_factor(self, move):
        n = self.previous_actions.count(move.name)  # 0-3
        return 1.0 + n * 0.33  # up to 1.99

    def take_damage(self, dam):
        self.change_hp(-dam)
        self.took_damage = True

    def try_epic(self):
        if self.epic_chance and rnd() <= self.epic_chance:
            self.to_hit *= self.epic_to_hit_mult
            self.atk_pwr *= self.epic_atk_pwr_mult
            self.current_fight.display('~*~*~EPIC!!!~*~*~')
            # print('epic')

    def try_critical(self):
        if rnd() <= self.critical_chance:
            self.dam *= self.critical_mult
            self.current_fight.display('CRITICAL!')
            # print('critical')

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
            kb = int(dam_ratio * KNOCKBACK_FULL_HP_DAM) - targ.momentum
        if kb > 0:
            targ.cause_knockback(kb)

    def try_knockdown(self):
        targ = self.target
        if not targ.check_status('lying'):
            hp_before_dam = targ.hp + self.dam
            if self.dam >= hp_before_dam * KNOCKDOWN_HP_THRESHOLD:
                targ.cause_fall()
            elif self.dam >= hp_before_dam * OFF_BALANCE_HP_THRESHOLD:
                targ.cause_off_balance()

    def try_shock_move(self):
        targ = self.target
        if rnd() <= SHOCK_CHANCE:
            targ.cause_shock()

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
