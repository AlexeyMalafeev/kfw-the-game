from __future__ import annotations
from abc import ABC
import random
from typing import Final, List, TYPE_CHECKING

if TYPE_CHECKING:
    # todo refactor - use base classes in separate files
    from kf_lib.kung_fu.moves import Move

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.ui import get_bar
from kf_lib.utils import rnd, rndint_2d


DEBUG = False


class FighterWithActions(FighterAPI, ABC):
    BASE_DFS_BONUS_FROM_GUARDING = 1.5
    DUR_FURY_MIN: Final = 500
    DUR_FURY_MAX: Final = 1000

    def apply_bleeding(self) -> None:
        if self.bleeding:
            self.change_hp(-self.bleeding)
            if self.hp <= 0:
                self.display_bleed_pass_out()

    def apply_dfs_penalty(self) -> None:
        self.dfs_penalty_mult -= self.dfs_penalty_step
        self.dfs_penalty_mult = max(self.dfs_penalty_mult, 0)

    def apply_move_cost(self) -> None:
        m = self.action
        self.change_stamina(-m.stam_cost)
        self.change_qp(-m.qi_cost)

    def attack(self) -> None:
        self.display_start_of_attack()
        if self.guard_while_attacking:
            self.dfs_bonus_from_guarding *= self.BASE_DFS_BONUS_FROM_GUARDING * (1.0 + self.guard_while_attacking)
        if self.target.check_preemptive():
            self.target.do_preemptive()
        else:
            self.try_strike()
            self.target.try_counter()

    def can_use_move_now(self, m: Move) -> bool:
        lying_op = self.target.check_status('lying')
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
                        return True
            else:
                return True
        return False

    def check_move_failed(self) -> bool:
        compl = self.calc_move_complexity(self.action)
        f_ch = self.get_move_fail_chance(self.action)
        if rnd() > f_ch:
            return False
        if self.action.power:
            self.to_hit = 0
            if compl >= 1:
                self.display_miss()
                self.cause_off_balance()
        if self.action.dist_change:
            self.display_fail()
            if compl >= 3:
                self.cause_fall()
            else:
                self.cause_off_balance()
        return True

    def check_preemptive(self) -> bool:
        return self.preemptive_chance and rnd() <= self.preemptive_chance

    def choose_move(self) -> None:
        self.av_moves = self.get_av_moves()  # this depends on target
        self.action = self.fight_ai.choose_move()

    def choose_target(self) -> None:
        if len(self.act_targets) == 1:
            self.set_target(self.act_targets[0])
        else:
            self.set_target(self.fight_ai.choose_target())

    def do_block(self) -> None:
        self._calc_block_pwr()
        self.block_pwr = round(self.block_pwr)
        self.target.dam = max(self.target.dam - self.block_pwr, 0)
        self.change_qp(self.qp_gain // 2)
        self.display_block()
        prefix = 'Lying ' if self.check_status('lying') else ''
        self.set_ascii(f'{prefix}Block')
        self.try_block_disarm()
        self.defended = True

    def do_counter(self) -> None:
        if cand_moves := self.get_av_moves(attack_moves_only=True):
            new_action = random.choice(cand_moves)
            self.action = new_action
            self.display_counter()
            self.try_strike()

    def do_dodge(self) -> None:
        self.target.dam = 0
        self.change_qp(self.qp_gain)
        self.display_dodge()
        prefix = 'Lying ' if self.check_status('lying') else ''
        self.set_ascii(f'{prefix}Dodge')
        self.defended = True

    def do_on_strike_end(self) -> None:
        if self.action.dist_change:
            self.change_distance(self.action.dist_change, self.target)
        else:
            self.momentum = 0
        self.previous_actions.append(self.action)

    def do_per_turn_actions(self) -> None:
        if self.hp_gain:
            self.change_hp(self.hp_gain)
        self.change_qp(self.qp_gain)
        self.change_stamina(self.stamina_gain)
        self.try_in_fight_impro_wp()  # before get_av_atk_actions! or won't get weapon moves
        self.try_fury()
        self.calc_stamina_factor()

    def do_preemptive(self) -> None:
        if cand_moves := self.get_av_moves(attack_moves_only=True):
            new_action = random.choice(cand_moves)
            self.action = new_action
            self.refresh_ascii()
            self.display_preemptive()
            self.try_strike()
            # this is by design separate from actually performing the strike
            self.apply_move_cost()

    def do_strike(self) -> None:
        self.calc_atk(self.action)
        self.try_environment('attack')
        self.target.calc_dfs()
        self.try_unblockable()
        self.target.try_environment('defense')
        self.target.try_defend()
        self.try_hit()
        self.target.apply_dfs_penalty()
        self.do_on_strike_end()

    def exec_move(self) -> None:
        m = self.action
        self.current_fight.cls()
        if m.power:
            self.attack()  # changing distance is included
        else:
            self.maneuver()
        self.apply_move_cost()
        self.current_fight.show(self.visualize_fight_state())
        self.show_ascii()

    def get_av_moves(self, attack_moves_only: bool = False) -> List[Move]:
        av_moves: List[Move] = [
            m
            for m in self.moves + (self.weapon.moves if self.weapon else [])
            if self.can_use_move_now(m)
        ]
        if attack_moves_only:
            av_moves = [m for m in av_moves if m.power]
        return av_moves

    def guard(self) -> None:
        """This is called with eval as a function of the Guard move."""
        # print('giving guard dfs bonus:', self.dfs_bonus, '+', self.guard_dfs_bonus)
        self.dfs_bonus_from_guarding *= self.guard_dfs_bonus * self.BASE_DFS_BONUS_FROM_GUARDING

    def maneuver(self) -> None:
        m = self.action
        self.display_start_of_maneuver()
        if m.dist_change:
            self.change_distance(m.dist_change, self.target)
            self.check_move_failed()
        else:
            self.momentum = 0
        self.do_move_functions(m)

    def prepare_for_fight(self) -> None:
        # this is done to clean up after possible previous fights
        self.hp = self.hp_max
        self.qp = round(self.qp_max * self.qp_start)
        self.stamina = self.stamina_max
        self.bleeding = 0
        self.previous_actions.clear()
        self.is_auto_fighting = True
        self.set_distances_before_fight()
        self.status = {}
        self.exp_yield = self.get_exp_worth()
        self.took_damage = False
        self.kos_this_fight = 0
        self.momentum = 0

        # attack- and defense-related
        self.stamina_factor = 1.0
        self.dfs_penalty_mult = 1.0
        self.dfs_bonus_from_guarding = 1.0

    def _print_defender_debug_info(self, roll: float) -> None:
        # todo separate module for fighter debug
        print(
            '\n---DEBUG---'
            f'\n{self.target.name} '
            f'to_hit: {round(self.target.to_hit, 2)} '
            f'potential_dam: {round(self.target.potential_dam, 2)}'
            f'\n{self.name} '
            f'curr_dfs_mult: {round(self.curr_dfs_mult, 2)} '
            f'\nto_dodge: {round(self.to_dodge, 2)} '
            f'dodge_chance: {round(self.dodge_chance, 2)} '
            f'\nto_block: {round(self.to_block, 2)} '
            f'block_chance: {round(self.block_chance, 2)} '
            f'\nroll: {round(roll, 2)}'
        )
        if not self.curr_dfs_mult:
            print(
                f'---EXTRA-DEBUG---'
                f'\n{self.BASE_DFS_MULT=}'
                f'\n{self.dfs_penalty_mult=}'
                f'\n{self.agility_full=}'
                f'\n{self.stamina_factor=}'
                f'\n{self.dfs_bonus_from_guarding=}'
            )
        print('---END-OF-DEBUG---\n')

    def refresh_per_turn_attributes(self) -> None:
        cur_fight = self.current_fight
        self.act_targets = (
            cur_fight.active_side_b if self in cur_fight.active_side_a else cur_fight.active_side_a
        )
        self.act_allies = (
            cur_fight.active_side_b if self in cur_fight.active_side_b else cur_fight.active_side_a
        )
        self.action = None
        self.dfs_bonus_from_guarding = 1.0  # needs to be refreshed because guarding can happen during both atk and dfs
        self.dfs_penalty_mult = 1.0
        self.target = None

    def set_target(self, target: FighterAPI) -> None:
        self.target = target
        target.target = self

    def start_fight_turn(self) -> None:
        self.refresh_per_turn_attributes()
        self.do_per_turn_actions()

    def try_block_disarm(self) -> None:
        if self.target.weapon and self.block_disarm and rnd() <= self.block_disarm:
            self.target.disarm()
            self.display_block_disarm()

    def try_counter(self) -> None:
        if self.target.dam or self.hp <= 0:
            return
        roll = rnd()
        # todo wrap in a method
        if DEBUG:
            print('\n---COUNTER-DEBUG---')
            print(
                f'{self.name}: '
                f'\ncounter_chance={round(self.counter_chance, 2)} '
                f'roll={round(roll, 2)}'
            )
            print('---END-OF-COUNTER-DEBUG---\n')
        if roll <= self.counter_chance:
            self.do_counter()

    def try_defend(self) -> None:
        atkr = self.target
        atkr.dam = atkr.potential_dam
        self.dodge_chance = self.to_dodge / atkr.to_hit
        self.block_chance = self.to_block / atkr.to_hit
        roll = rnd()
        if DEBUG:
            self._print_defender_debug_info(roll)
        self.defended = False
        if roll <= self.dodge_chance:
            self.do_dodge()
        elif roll <= self.block_chance:
            self.do_block()
        else:
            prefix = 'Lying ' if self.check_status('lying') else ''
            self.set_ascii(f'{prefix}Hit')
        # this is necessary here, do not remove, otherwise dam will be a float on hit / block
        atkr.dam = round(atkr.dam)
        # todo handle the no defense case

    def try_fury(self) -> None:
        if (
            not self.check_status('fury')
            # todo possibly change how fury prob is computed
            and rnd() <= ((1 - self.hp / self.hp_max) * self.fury_chance)
        ):
            fury_dur = rndint_2d(self.DUR_FURY_MIN, self.DUR_FURY_MAX) // self.speed_full
            self.add_status('fury', fury_dur)
            self.display_fury()

    def try_hit(self) -> None:
        if self.dam > 0:
            self.try_critical()
            self.try_epic()
            # todo use skip list here for functions not to be applied twice
            # todo let try_* functions return True or False to determine skip
            self.dam = max(self.dam - self.target.toughness, 0)
            if self.target.dam_reduc:
                self.dam *= (1 - self.target.dam_reduc)
                self.dam = round(self.dam)
            self.target.take_damage(self.dam)
            self.display_hit()
            self.try_cause_bleeding()
            self.try_hit_disarm()
            self.do_move_functions(self.action)
            self.try_stun()
            self.try_knockback()
            self.try_knockdown()
            self.try_ko()

    def try_in_fight_impro_wp(self) -> None:
        if (
            self.in_fight_impro_wp_chance
            and not self.weapon
            and self.current_fight.environment_allowed
            and rnd() <= self.in_fight_impro_wp_chance
        ):
            self.arm_improv()
            self.display_grab_impro_wp()

    def try_ko(self) -> None:
        tgt = self.target
        if not tgt.hp:
            if tgt.resist_ko and rnd() <= tgt.resist_ko:
                tgt.hp = 1
                self.display_resist_ko()
            else:
                self.kos_this_fight += 1
                self.log(f'Knocks out {tgt.name}.')
                tgt.log(f'Knocked out by {self.name}.')
                if not tgt.ascii_name.startswith('lying'):
                    tgt.set_ascii('Falling')
                self.display_ko()

    def try_strike(self) -> None:
        if not self.check_move_failed():
            self.do_strike()

    def visualize_fight_state(self) -> str:
        ft = self.current_fight
        side_a, side_b = ft.active_side_a, ft.active_side_b
        n_a, n_b = len(side_a), len(side_b)
        hp_a, hp_b = sum((f.hp for f in side_a)), sum((f.hp for f in side_b))
        bar = get_bar(hp_a, hp_a + hp_b, '/', '\\', 20)
        return f'\n{n_a} {bar} {n_b}\n'
