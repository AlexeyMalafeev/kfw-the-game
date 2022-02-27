from ._basic_attributes import BasicAttributes


# COUNTER_CHANCE_BASE = 0.0
# COUNTER_CHANCE_INCR_PER_LV = 0.02
# CRITICAL_CHANCE_BASE = 0.0
# CRITICAL_CHANCE_INCR_PER_LV = 0.01
COUNTER_AGILITY_ADJUST = 3  # this will get subtracted from agility_full
COUNTER_PER_AGILITY_POINT = 0.05
CRITICAL_AGILITY_ADJUST = 3
CRITICAL_PER_AGILITY_POINT = 0.05
EPIC_CHANCE_BASE = 0.0
EPIC_CHANCE_INCR_PER_LV = 0.005
HP_PER_HEALTH_LV = 50
MAX_RESIST_KO = 0.5
QP_BASE = 0
QP_INCR_PER_LV = 5
QP_PORTION_RESTORED_PER_TURN = 0.2
STAMINA_BASE = 50  # for all fighter levels
STAMINA_INCR_PER_LV = 10
STAMINA_PORTION_RESTORED_PER_TURN = 0.1


class FightAttributes(BasicAttributes):
    def __init__(self):
        super().__init__()
        self.act_allies = []
        self.act_targets = []
        self.action = None
        self.ascii_buffer = 0
        self.ascii_l = ''
        self.ascii_r = ''
        self.ascii_name = ''
        self.atk_bonus = 0
        self.atk_pwr = 0
        self.av_moves = []
        self.current_fight = None  # ...Fight object
        self.dam = 0
        self.defended = False
        self.dfs_pwr = 0
        self.distances = {}  # fighter_obj: int
        self.is_auto_fighting = True
        self.kos_this_fight = 0
        self.momentum = 0  # (-3, 3)
        self.previous_actions = ['', '', '']
        self.qp_start = 0.0  # portion of total
        self.status = {}  # {'status_name': status_dur}
        self.target = None  # used both for attacker and defender
        self.to_block = 0
        self.to_dodge = 0
        self.to_hit = 0

        # modified by level, techs and styles:
        self.agility_mult = 1.0
        self.atk_mult = 1.0
        self.atk_wp_bonus = 0
        self.block_disarm = 0.005
        self.block_mult = 1.0  # tech-based
        self.block_default_power = 1.0  # this is common between all fighters; non-tech-based
        self.counter_chance = 0.0  # NB! level-dependent
        self.counter_chance_mult = 1.0  # tech-dependent
        self.critical_chance = 0.05  # NB! level-dependent
        self.critical_chance_mult = 1.0  # tech-dependent
        self.critical_dam_mult = 1.5
        self.dam_reduc = 0  # todo adjust this and hp_gain in boosts.py
        self.dfs_bonus = 1.0  # for moves like Guard
        self.dfs_mult = 1.0
        self.dfs_penalty_mult = 1.0
        self.dfs_penalty_step = 0.2
        self.dodge_mult = 1.0
        self.environment_chance = 0.0  # todo get rid of this as it is just another critical?
        self.epic_chance = 0.0  # NB! level-dependent
        self.epic_chance_mult = 1.0  # tech-dependent, todo not used yet, secret tech?
        self.epic_dam_mult = 2.0
        self.fury_to_all_mult = 1.6
        self.fury_chance = 0.0  # this gets multiplied by ratio of hp to max hp
        self.grab_chance = 0.0  # todo not used yet
        self.guard_dfs_bonus = 1.0  # this is the tech-dependent bonus to Guard
        self.guard_dfs_mult = 1.3  # this is the default effect of Guard
        self.guard_while_attacking = 0.0
        self.health_mult = 1.0
        self.hit_disarm = 0.005
        self.hp = 0
        self.hp_max = 0
        self.hp_gain = 0
        self.in_fight_impro_wp_chance = 0.0
        self.lying_dfs_mult = 0.5
        self.maneuver_time_cost_mult = 1.0  # lower is better
        self.num_moves_choose = 3
        self.off_balance_atk_mult = 0.75
        self.off_balance_dfs_mult = 0.75
        self.preemptive_chance = 0.0  # tech-dependent
        self.qp = 0
        self.qp_gain = 0  # NB! level-dependent
        self.qp_gain_mult = 1.0
        self.qp_max = 0  # NB! level-dependent
        self.qp_max_mult = 1.0
        self.speed_mult = 1.0
        self.stamina = 0
        self.stamina_factor = 1.0
        self.stamina_gain = 0  # NB! level-dependent
        self.stamina_gain_mult = 1.0
        self.stamina_max = 0  # NB! level-dependent
        self.stamina_max_mult = 1.0
        self.strength_mult = 1.0
        self.strike_time_cost_mult = 1.0  # lower is better
        self.stun_chance = 0.0
        self._resist_ko = 0.0
        self.unblock_chance = 0.0

        # weapon-related
        self.weapon = None  # weapon obj
        # tech-based permanent {<weapon name OR type>: [atk_bonus, dfs_bonus]}
        self.weapon_bonus = {}
        self.wp_dfs_bonus = 1.0  # for current fight only

        # strike multipliers
        # todo reimplement strike multipliers as a default dict? a data class?
        self.claw_strike_mult = 1.0
        self.dist1_bonus = 1.0
        self.dist2_bonus = 1.0
        self.dist3_bonus = 1.0
        self.elbow_strike_mult = 1.0
        self.exotic_strike_mult = 1.0
        self.flying_strike_mult = 1.0
        self.grappling_strike_mult = 1.0
        self.head_strike_mult = 1.0
        self.kick_strike_mult = 1.0
        self.knee_strike_mult = 1.0
        self.palm_strike_mult = 1.0
        self.punch_strike_mult = 1.0
        self.weapon_strike_mult = 1.0

    @property
    def resist_ko(self):
        return self._resist_ko

    @resist_ko.setter
    def resist_ko(self, value):
        self._resist_ko = value
        self._resist_ko = min(self._resist_ko, MAX_RESIST_KO)

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
        self.refresh_level_dependent_atts()

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

    def check_stamina(self, amount):
        return self.stamina >= amount

    def check_status(self, status):
        return self.status.get(status, False)

    def get_status_marks(self, right=False):
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
        padding = ' ' if lying or inact else ''
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
        return f'{padding}{fury}{slowed_down}{off_bal}{lying}{inact}{mom_s}'

    def refresh_level_dependent_atts(self):
        self.hp_max = self.health_full * HP_PER_HEALTH_LV
        self.stamina_max = round(
            (STAMINA_BASE + STAMINA_INCR_PER_LV * self.level) * self.stamina_max_mult
        )
        self.stamina_gain = round(self.stamina_max * STAMINA_PORTION_RESTORED_PER_TURN *
                                  self.stamina_gain_mult)
        self.qp_max = round(
            (QP_BASE + QP_INCR_PER_LV * self.level) * self.qp_max_mult
        )
        self.qp_gain = round(self.qp_max * QP_PORTION_RESTORED_PER_TURN * self.qp_gain_mult)
        self.counter_chance = (
            (self.agility_full - COUNTER_AGILITY_ADJUST) * COUNTER_PER_AGILITY_POINT
            * self.counter_chance_mult
        )
        self.critical_chance = (
            (self.agility_full - CRITICAL_AGILITY_ADJUST) * CRITICAL_PER_AGILITY_POINT
            * self.critical_chance_mult
        )
        self.epic_chance = (
            (EPIC_CHANCE_BASE + EPIC_CHANCE_INCR_PER_LV * self.level) * self.epic_chance_mult
        )

    def unboost(self, **kwargs):
        """'Unboost' fighter's attributes."""
        kwargs_copy = {}
        for k, v in kwargs.items():
            kwargs_copy[k] = -v
        self.boost(**kwargs_copy)
        self.refresh_full_atts()
        self.refresh_level_dependent_atts()
