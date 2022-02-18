import random

from kf_lib.ui import get_bar
from kf_lib.utils import choose_adverb, rnd, rndint_2d
from ._distances import DistanceMethods
from ._exp_worth import ExpMethods
from ._strike_mechanics import StrikeMechanics
from ._weapons import WeaponMethods

DUR_FURY_MIN = 500
DUR_FURY_MAX = 1000


class FighterWithActions(
    DistanceMethods,
    ExpMethods,
    StrikeMechanics,
    WeaponMethods,
):
    def apply_dfs_penalty(self):
        self.dfs_penalty_mult -= self.dfs_penalty_step
        if self.dfs_penalty_mult < 0:
            self.dfs_penalty_mult = 0

    def attack(self):
        n1 = self.current_fight.get_f_name_string(self)
        fury = ' *FURY*' if self.check_status('fury') else ''
        n2 = self.current_fight.get_f_name_string(self.target)
        s = f'{n1}{fury}: {self.action.name} @ {n2}'
        self.current_fight.display(s)
        if self.guard_while_attacking:
            self.current_fight.display(f' (guarding while attacking)')
            self.dfs_bonus += self.guard_dfs_bonus * self.guard_while_attacking
        self.current_fight.display('=' * len(s))
        if self.target.check_preemptive():
            self.target.do_preemptive()
        else:
            self.try_strike()
            self.target.try_counter()

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

    def check_preemptive(self):
        return self.preemptive_chance and rnd() <= self.preemptive_chance

    def choose_move(self):
        self.av_moves = self.get_av_moves()  # this depends on target
        self.action = self.fight_ai.choose_move()

    def choose_target(self):
        if len(self.act_targets) == 1:
            self.set_target(self.act_targets[0])
        else:
            self.set_target(self.fight_ai.choose_target())

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
                '{} {}dodges!'.format(self.name, choose_adverb(dodge_chance, 'barely', 'easily'))
            )
            self.set_ascii(prefix + 'Dodge')
            self.defended = True
        elif roll <= block_chance:
            atkr.dam = max(atkr.dam - self.dfs_pwr, 0)
            self.change_qp(self.qp_gain // 2)
            self.current_fight.display(
                '{} {}blocks!'.format(self.name, choose_adverb(block_chance, 'barely', 'easily'))
            )
            self.set_ascii(prefix + 'Block')
            self.try_block_disarm()
            self.defended = True
        else:
            self.try_critical()
            self.set_ascii(prefix + 'Hit')
        # todo handle the no defense case
        atkr.dam = round(atkr.dam)

    def do_counter(self):
        cand_moves = self.get_av_moves(attack_moves_only=True)
        if cand_moves:
            self.current_fight.display('+COUNTER!+')
            new_action = random.choice(cand_moves)
            self.action = new_action
            s = f'{self.name}: {self.action.name} @ {self.target.name}'
            self.current_fight.display(s)
            self.do_strike()

    def do_preemptive(self):
        cand_moves = self.get_av_moves(attack_moves_only=True)
        if cand_moves:
            self.current_fight.display('<-PREEMPTIVE!-<')
            new_action = random.choice(cand_moves)
            self.action = new_action
            self.refresh_ascii()
            s = f'{self.name}: {self.action.name} @ {self.target.name}'
            self.current_fight.display(s)
            self.do_strike()

    def do_strike(self):
        m = self.action
        self.calc_atk(m)
        self.try_environment('attack')
        # self.try_critical()
        self.try_epic()
        self.target.calc_dfs()
        self.try_unblockable()
        self.target.try_environment('defense')
        self.target.defend()
        self.hit_or_miss()
        self.target.apply_dfs_penalty()
        if m.dist_change:
            self.change_distance(m.dist_change, self.target)
        else:
            self.momentum = 0
        self.previous_actions = self.previous_actions[1:] + [m.name]
        self.change_stamina(-m.stam_cost)
        self.change_qp(-m.qi_cost)

    def exec_move(self):
        m = self.action
        self.current_fight.cls()
        if m.power:
            self.attack()  # changing distance is included
        else:
            self.maneuver()
        self.current_fight.show(self.visualize_fight_state())
        self.show_ascii()

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
                        anti_ground = ('antiground only' in m.features
                                       or 'also antiground' in m.features) and lying_op
                        anti_standing = 'antiground only' not in m.features and not lying_op
                        if anti_ground or anti_standing:
                            av_moves.append(m)
                else:
                    av_moves.append(m)
        if attack_moves_only:
            av_moves = [m for m in av_moves if m.power]
        return av_moves

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
            if tgt.momentum > 0:
                tgt.momentum = 0
            self.current_fight.display(f'hit: -{self.dam} HP ({tgt.hp})')
            self.try_hit_disarm()
            self.do_move_functions(self.action)
            self.try_stun()
            self.try_knockback()
            self.try_knockdown()
            self.try_ko()

    def maneuver(self):
        m = self.action
        n = self.current_fight.get_f_name_string(self)
        s = f'{n}: {m.name}'
        self.current_fight.display(s)
        self.current_fight.display('=' * len(s))
        if m.dist_change:
            self.change_distance(m.dist_change, self.target)
            self.check_move_failed()
        else:
            self.momentum = 0
        self.do_move_functions(m)
        self.change_stamina(-m.stam_cost)
        self.change_qp(-m.qi_cost)

    def prepare_for_fight(self):
        self.hp = self.hp_max
        self.qp = round(self.qp_max * self.qp_start)
        self.stamina = self.stamina_max
        self.previous_actions = ['', '', '']
        self.is_auto_fighting = True
        self.set_distances_before_fight()
        self.status = {}
        self.exp_yield = self.get_exp_worth()
        self.took_damage = False
        self.kos_this_fight = 0
        self.momentum = 0

    def set_target(self, target):
        self.target = target
        target.target = self

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
        self.try_fury()
        self.calc_stamina_factor()

    def try_strike(self):
        if not self.check_move_failed():
            self.do_strike()

    def try_block_disarm(self):
        atkr = self.target
        if atkr.weapon and self.block_disarm and rnd() <= self.block_disarm:
            atkr.disarm()
            self.current_fight.display(f'{self.name} disarms {atkr.name} while blocking')

    def try_counter(self):
        if self.defended and self.hp > 0 and rnd() <= self.counter_chance:
            self.do_counter()

    def try_fury(self):
        if (
            not self.check_status('fury')
            # todo possibly change how fury prob is computed
            and rnd() <= ((1 - self.hp / self.hp_max) * self.fury_chance)
        ):
            fury_dur = rndint_2d(DUR_FURY_MIN, DUR_FURY_MAX) // self.speed_full
            self.add_status('fury', fury_dur)
            s = self.current_fight.get_f_name_string(self)
            self.current_fight.display(f'{s} is in FURY!')
            self.pak()

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
            self.pak()

    def try_ko(self):
        tgt = self.target
        if not tgt.hp:
            if tgt.resist_ko and rnd() <= tgt.resist_ko:
                tgt.hp = 1
                # self.log(f'{tgt.name} resists being knocked out.')
                # tgt.log('Resists being knocked out.')
                self.current_fight.display(f'{tgt.name} resists being knocked out!')
            else:
                self.kos_this_fight += 1
                self.log(f'Knocks out {tgt.name}.')
                tgt.log(f'Knocked out by {self.name}.')
                if not tgt.ascii_name.startswith('lying'):
                    tgt.set_ascii('Falling')
                self.current_fight.display(' KNOCK-OUT!'.format(tgt.name), align=False)

    def visualize_fight_state(self):
        ft = self.current_fight
        side_a, side_b = ft.active_side_a, ft.active_side_b
        n_a, n_b = len(side_a), len(side_b)
        hp_a, hp_b = sum((f.hp for f in side_a)), sum((f.hp for f in side_b))
        bar = get_bar(hp_a, hp_a + hp_b, '/', '\\', 20)
        s = f'\n{n_a} {bar} {n_b}\n'
        return s
