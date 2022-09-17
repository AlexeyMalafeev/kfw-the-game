from abc import ABC
from collections import deque
from typing import Dict, Final, Union

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.utils import Float, Integer


class FightAttributes(FighterAPI, ABC):
    # common for all fighters, not modified
    COUNTER_AGILITY_ADJUST: Final = 3  # this will get subtracted from agility_full
    COUNTER_PER_AGILITY_POINT: Final = 0.05
    CRITICAL_AGILITY_ADJUST: Final = 3
    CRITICAL_PER_AGILITY_POINT: Final = 0.05
    EPIC_CHANCE_BASE: Final = 0.0
    EPIC_CHANCE_INCR_PER_LV: Final = 0.005
    HP_PER_HEALTH_LV: Final = 50
    MAX_RESIST_KO: Final = 0.5
    QP_BASE: Final = 0
    QP_INCR_PER_LV: Final = 5
    QP_PORTION_RESTORED_PER_TURN: Final = 0.2
    STAMINA_BASE: Final = 50  # for all fighter levels
    STAMINA_INCR_PER_LV: Final = 10
    STAMINA_PORTION_RESTORED_PER_TURN: Final = 0.1
    TOUGHNESS_PER_LV: Final = 3

    # strike multipliers
    STRIKE_MULTIPLIERS: Final = (
        'acrobatic_strike_mult',
        'claw_strike_mult',
        'dist1_strike_mult',
        'dist2_strike_mult',
        'dist3_strike_mult',
        'drunken_strike_mult',
        'elbow_strike_mult',
        'flying_strike_mult',
        'grappling_strike_mult',
        'head_strike_mult',
        'kick_strike_mult',
        'knee_strike_mult',
        'palm_strike_mult',
        'punch_strike_mult',
        'weapon_strike_mult',
    )

    # tech-dependent, with validation. NB! double declaration! add initial values below
    fall_damage_mult = Float(minvalue=0.0)  # also wine-dependent?
    move_complexity_mult = Float(minvalue=0.0)  # wine-dependent?
    maneuver_time_cost_mult = Float(minvalue=0.0)
    qp_start = Float(minvalue=0.0, maxvalue=1.0)  # portion of total
    resist_ko = Float(maxvalue=MAX_RESIST_KO)
    strike_time_cost_mult = Float(minvalue=0.0)

    stamina = Integer()

    def init_fight_attributes(self) -> None:
        self.act_allies = []
        self.act_targets = []
        self.action = None
        self.ascii_buffer = 0
        self.ascii_l = ''
        self.ascii_r = ''
        self.ascii_name = ''
        self.atk_bonus = 0.0
        self.atk_pwr = 0.0
        self.av_moves = []
        self.bleeding = 0  # refreshed every fight
        self.current_fight = None  # ...Fight object
        self.dam = 0
        self.defended = False
        self.dfs_pwr = 0.0
        self.distances = {}  # fighter_obj: int
        self.is_auto_fighting = True
        self.kos_this_fight = 0
        self.momentum = 0  # (-3, 3)
        self.previous_actions = deque(maxlen=3)
        self.status = {}  # {'status_name': status_dur}
        self.target = None  # used both for attacker and defender
        self.to_block = 0.0
        self.to_dodge = 0.0
        self.to_hit = 0.0

        # modified by level, techs and styles:
        self.agility_mult = 1.0
        self.atk_mult = 1.0
        self.block_disarm = 0.005
        self.block_mult = 1.0  # tech-based
        self.chance_cause_bleeding = 0.03  # tech-dependent
        self.counter_chance = 0.0  # NB! level-dependent
        self.counter_chance_mult = 1.0  # tech-dependent
        self.critical_chance = 0.05  # NB! level-dependent
        self.critical_chance_mult = 1.0  # tech-dependent
        self.critical_dam_mult = 1.5
        self.dam_reduc = 0.0  # portion of damage to be 'absorbed'
        self.dfs_bonus = 1.0  # for moves like Guard
        self.dfs_mult = 1.0
        self.dfs_penalty_mult = 1.0
        self.dfs_penalty_step = 0.2
        self.dodge_mult = 1.0
        self.environment_chance = 0.0  # todo get rid of this as it is just another critical?
        self.epic_chance = 0.0  # NB! level-dependent
        self.epic_chance_mult = 1.0  # tech-dependent, todo not used yet, secret tech?
        self.epic_dam_mult = 2.0
        self.fall_damage_mult = 1.0  # with descriptor
        self.fury_to_all_mult = 1.6
        self.fury_chance = 0.0  # this gets multiplied by ratio of hp to max hp
        self.guard_dfs_bonus = 1.0  # the tech-dependent bonus to Guard
        self.guard_while_attacking = 0.0
        self.health_mult = 1.0
        self.hit_disarm = 0.005
        self.hp = 0
        self.hp_max = 0
        self.hp_gain = 0  # actual amount of hp restored per turn, derived
        self.hp_gain_mult = 0.0  # tech-dependent
        self.in_fight_impro_wp_chance = 0.0
        self.lying_dfs_mult = 0.5
        self.maneuver_time_cost_mult = 1.0  # with descriptor
        self.move_complexity_mult = 1.0  # with descriptor
        self.num_moves_choose = 3
        self.off_balance_atk_mult = 0.75
        self.off_balance_dfs_mult = 0.75
        self.preemptive_chance = 0.0  # tech-dependent
        self.qp = 0
        self.qp_gain = 0  # level-dependent
        self.qp_gain_mult = 1.0  # tech-dependent
        self.qp_max = 0  # level-dependent
        self.qp_max_mult = 1.0
        self.qp_start = 0.0  # with descriptor
        self.resist_ko = 0.0  # with descriptor
        self.speed_mult = 1.0
        self.stamina = 0  # with descriptor
        self.stamina_factor = 1.0  # todo comment for stamina_factor
        self.stamina_gain = 0  # NB! level-dependent
        self.stamina_gain_mult = 1.0
        self.stamina_max = 0  # NB! level-dependent
        self.stamina_max_mult = 1.0
        self.strength_mult = 1.0
        self.strike_time_cost_mult = 1.0  # with descriptor
        self.stun_chance = 0.0
        self.toughness = 0  # level-dependent
        self.unblock_chance = 0.0

        # weapon-related
        self.weapon = None  # weapon obj
        # tech-based permanent {<weapon name OR type>: [atk_bonus, dfs_bonus]}
        self.weapon_bonus = {}
        self.wp_dfs_bonus = 1.0  # for current fight only

        # strike multipliers
        for att in self.STRIKE_MULTIPLIERS:
            setattr(self, att, 1.0)

    def add_status(self, status: str, dur: int) -> None:
        self.status[status] = self.status.get(status, 0) + dur

    def boost(self, **kwargs: Union[int, float]) -> None:
        """Boost fighter's attribute(s); k = att_name, v = quantity"""
        for k, v in kwargs.items():
            curr_v = getattr(self, k)
            setattr(self, k, curr_v + v)
        self.refresh_full_atts()
        self.refresh_dependent_atts()

    # todo remove change_hp and other similar methods? but it's dynamic
    def change_hp(self, amount: int) -> None:
        self.hp += amount
        if self.hp > self.hp_max:
            self.hp = self.hp_max
        elif self.hp < 0:
            self.hp = 0
            # set qp to zero too
            self.qp = 0

    def change_qp(self, amount: int) -> None:
        self.qp += amount
        if self.qp > self.qp_max:
            self.qp = self.qp_max
        elif self.qp < 0:
            self.qp = 0

    def change_stamina(self, amount: int) -> None:
        self.stamina += amount
        if self.stamina > self.stamina_max:
            self.stamina = self.stamina_max
        elif self.stamina < 0:
            self.stamina = 0

    def check_stamina(self, amount: int) -> bool:
        return self.stamina >= amount

    def check_status(self, status: str) -> bool:
        return bool(self.status.get(status, 0))

    def get_status_marks(self, right: bool = False) -> str:
        bleeding = ';' if self.bleeding else ''
        fury = '#' if self.check_status('fury') else ''
        slowed_down = ',' if self.check_status('slowed down') else ''
        off_bal = '\'' if self.check_status('off-balance') else ''
        lying = '...' if self.check_status('lying') else ''
        excl = 0
        if self.check_status('shocked'):
            excl = 2
        elif self.check_status('stunned'):
            excl = 1
        inact = '!' * excl
        if self.momentum:
            if right:
                if self.momentum > 0:
                    mom_s = '<'
                else:
                    mom_s = '>'
            else:
                if self.momentum > 0:
                    mom_s = '>'
                else:
                    mom_s = '<'
            mom_s *= abs(self.momentum)
            mom_s = f' {mom_s}'
        else:
            mom_s = ''
        return f'{fury}{bleeding}{slowed_down}{off_bal}{lying}{inact}{mom_s}'

    def refresh_dependent_atts(self) -> None:
        self.hp_max = self.health_full * self.HP_PER_HEALTH_LV
        self.hp_gain = round(self.hp_max * self.hp_gain_mult)
        self.stamina_max = round(
            (self.STAMINA_BASE + self.STAMINA_INCR_PER_LV * self.level) * self.stamina_max_mult
        )
        self.stamina_gain = round(self.stamina_max * self.STAMINA_PORTION_RESTORED_PER_TURN *
                                  self.stamina_gain_mult)
        self.qp_max = round(
            (self.QP_BASE + self.QP_INCR_PER_LV * self.level) * self.qp_max_mult
        )
        self.qp_gain = round(self.qp_max * self.QP_PORTION_RESTORED_PER_TURN * self.qp_gain_mult)
        self.counter_chance = (
            (self.agility_full - self.COUNTER_AGILITY_ADJUST) * self.COUNTER_PER_AGILITY_POINT
            * self.counter_chance_mult
        )
        self.critical_chance = (
            (self.agility_full - self.CRITICAL_AGILITY_ADJUST) * self.CRITICAL_PER_AGILITY_POINT
            * self.critical_chance_mult
        )
        self.epic_chance = (
            (self.EPIC_CHANCE_BASE + self.EPIC_CHANCE_INCR_PER_LV * self.level)
            * self.epic_chance_mult
        )
        self.toughness = (self.level - 1) * self.TOUGHNESS_PER_LV

    def unboost(self, **kwargs: Union[int, float]) -> None:
        """'Unboost' fighter's attributes: k = att_name, v = quantity."""
        kwargs_copy = {}
        for k, v in kwargs.items():
            kwargs_copy[k] = -v
        self.boost(**kwargs_copy)
        self.refresh_full_atts()
        self.refresh_dependent_atts()
