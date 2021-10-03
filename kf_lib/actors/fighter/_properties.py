class FighterProperties:
    # the following attribute values can be modified by Techs and Styles
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
    off_balance_atk_mult = 0.75
    off_balance_dfs_mult = 0.75
    speed_mult = 1.0
    stamina_gain_mult = 1.0
    stamina_max_mult = 1.0
    strength_mult = 1.0
    stun_chance = 0.0
    qp_gain_mult = 1.0
    qp_max_mult = 1.0
    resist_ko = 0.0
    unblock_chance = 0.0

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
