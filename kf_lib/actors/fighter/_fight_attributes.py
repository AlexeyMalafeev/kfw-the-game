class FightAttributes:
    def __init__(self):
        self.act_allies = []
        self.act_targets = []
        self.action = None
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
        self.block_mult = 1.0
        self.block_power = 1.0  # todo give boost to block_power
        self.critical_chance = 0.05
        self.critical_mult = 1.5
        self.dam_reduc = 0  # todo adjust this and hp_gain in boosts.py
        self.dfs_bonus = 1.0  # for moves like Guard
        self.dfs_mult = 1.0
        self.dfs_penalty_mult = 1.0
        self.dfs_penalty_step = 0.2
        self.dodge_mult = 1.0
        self.environment_chance = 0.0  # todo get rid of this as it is just another critical?
        self.grab_chance = 0.0  # todo not used yet
        self.guard_dfs_bonus = 1.0
        self.guard_while_attacking = False
        self.health_mult = 1.0
        self.hit_disarm = 0.005
        self.in_fight_impro_wp_chance = 0.0
        self.lying_dfs_mult = 0.5
        self.num_moves_choose = 3
        self.off_balance_atk_mult = 0.75
        self.off_balance_dfs_mult = 0.75
        self.speed_mult = 1.0
        self.stamina_factor = 1.0
        self.strength_mult = 1.0
        self.stun_chance = 0.0
        self.resist_ko = 0.0
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

    def add_status(self, status, dur):
        if status not in self.status:
            self.status[status] = 0
        self.status[status] += dur

    def check_status(self, status):
        return self.status.get(status, False)

    def get_status_marks(self):
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
        return f'{padding}{slowed_down}{off_bal}{lying}{inact}'
