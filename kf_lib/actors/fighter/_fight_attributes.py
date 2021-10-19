class FightAttributes:
    act_allies = []
    act_targets = []
    action = None
    atk_bonus = 0
    atk_pwr = 0
    av_moves = []
    current_fight = None  # ...Fight object
    dam = 0
    defended = False
    dfs_pwr = 0
    distances = {}  # fighter_obj: int
    is_auto_fighting = True
    kos_this_fight = 0
    previous_actions = ['', '', '']
    qp_start = 0.0  # portion of total
    status = {}  # {'status_name': status_dur}
    target = None  # used both for attacker and defender
    to_block = 0
    to_dodge = 0
    to_hit = 0

    # modified by level, techs and styles:
    agility_mult = 1.0
    atk_mult = 1.0
    atk_wp_bonus = 0
    block_disarm = 0.005
    block_mult = 1.0
    block_power = 1.0  # todo give boost to block_power
    critical_chance = 0.05
    critical_mult = 1.5
    dam_reduc = 0  # todo adjust this and hp_gain in boosts.py
    dfs_bonus = 1.0  # for moves like Guard
    dfs_mult = 1.0
    dfs_penalty_mult = 1.0
    dfs_penalty_step = 0.2
    dodge_mult = 1.0
    environment_chance = 0.0  # todo get rid of this as it is just another critical?
    grab_chance = 0.0  # todo not used yet
    guard_dfs_bonus = 1.0
    guard_while_attacking = False
    health_mult = 1.0
    hit_disarm = 0.005
    in_fight_impro_wp_chance = 0.0
    lying_dfs_mult = 0.5
    num_moves_choose = 3
    off_balance_atk_mult = 0.75
    off_balance_dfs_mult = 0.75
    speed_mult = 1.0
    stamina_factor = 1.0
    strength_mult = 1.0
    stun_chance = 0.0
    resist_ko = 0.0
    unblock_chance = 0.0

    # weapon-related
    weapon = None  # weapon obj
    weapon_bonus = {}  # tech-based permanent {<weapon name OR type>: [atk_bonus, dfs_bonus]}
    wp_dfs_bonus = 1.0  # for current fight only

    # strike multipliers
    # todo reimplement strike multipliers as a default dict? a data class?
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
