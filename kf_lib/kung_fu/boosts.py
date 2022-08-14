from kf_lib.utils import add_pcnt, add_sign, hund


ACROBATIC_STRIKE_MULT1 = 0.1
ACROBATIC_STRIKE_MULT2 = 0.2
AGILITY1 = 0.2
AGILITY2 = 0.4
ATTACK1 = 0.15
ATTACK2 = 0.3
ATTACK_HALF = round(ATTACK1 / 2, 2)
BLEEDING_CH1 = 0.3
BLEEDING_CH2 = 0.6
BLOCK1 = 0.5
BLOCK2 = 1.0
BLOCK_DISARM1 = 0.5
BLOCK_DISARM2 = 1.0
COUNTER_CH_MULT1 = 0.5
COUNTER_CH_MULT2 = 1.0
CRIT_CH1 = 0.15
CRIT_CH2 = 0.3
CRIT_M1 = 0.5
CRIT_M2 = 1
DAM_REDUC1 = 0.15
DAM_REDUC2 = 0.3
DEFENSE1 = 0.5
DEFENSE2 = 1.0
DEFENSE_HALF = round(DEFENSE1 / 2, 2)
DFS_PEN1 = -0.1
DFS_PEN2 = -0.2  # this effectively reduces defense penalty down to zero
DIST1_MULT1 = 0.4
DIST1_MULT2 = 0.8
DIST2_MULT1 = 0.25
DIST2_MULT2 = 0.5
DIST3_MULT1 = 0.2
DIST3_MULT2 = 0.4
DRUNKEN_STRIKE_MULT1 = 0.1
DRUNKEN_STRIKE_MULT2 = 0.2
ENVIRONMENT_CH1 = 0.15
ENVIRONMENT_CH2 = 0.3
EVADE1 = 0.4
EVADE2 = 0.8
FALL_DAMAGE_MULT1 = -0.5
FALL_DAMAGE_MULT2 = -1.0
FURY_CH1 = 0.3
FURY_CH2 = 0.5
GRAB_CH1 = 0.2  # todo this is not used!
GRAB_CH2 = 0.4
GUARD_DFS1 = 0.5
GUARD_DFS2 = 1.0
GUARD_WHILE_ATTACKING1 = 0.5
GUARD_WHILE_ATTACKING2 = 1.0
HEALTH1 = 0.2
HEALTH2 = 0.4
HIT_DISARM1 = 0.5
HIT_DISARM2 = 1.0
HP_GAIN1 = 0.05
HP_GAIN2 = 0.1
HP_MULT = 1.5  # todo this is not used?
IN_FIGHT_IMPRO_WP_CH1 = 0.25
IN_FIGHT_IMPRO_WP_CH2 = 0.5
MANEUVER_TIME_COST_MULT1 = -0.4
MANEUVER_TIME_COST_MULT2 = -0.8
MOVE_COMPLEXITY_MULT1 = -0.5
MOVE_COMPLEXITY_MULT2 = -1.0
OFF_BAL_MULT1 = 0.25
OFF_BAL_MULT2 = 0.5
PREEMPTIVE_CH1 = 0.10
PREEMPTIVE_CH2 = 0.20
QI_WHEN_ATK = 0.5  # todo this is not used
QP_GAIN1 = 0.1
QP_GAIN2 = 0.2
QP_MAX1 = 0.1
QP_MAX2 = 0.2
QP_START1 = 0.5
QP_START2 = 1.0
RARE_STRIKE_MULT1 = 0.4  # todo get rid of this?
RARE_STRIKE_MULT2 = 0.8
RESIST_KO1 = 0.3
RESIST_KO2 = 0.6
SPEED1 = 0.15
SPEED2 = 0.3
STAM_MAX1 = 0.3
STAM_MAX2 = 0.6
STAM_RESTORE1 = 0.2
STAM_RESTORE2 = 0.4
STRENGTH1 = 0.2
STRENGTH2 = 0.4
STRIKE_MULT1 = 0.25
STRIKE_MULT2 = 0.5
STRIKE_MULT_HALF = 0.125
STRIKE_TIME_COST_MULT1 = -0.3
STRIKE_TIME_COST_MULT2 = -0.6
STUN_CH1 = 0.2
STUN_CH2 = 0.4
UNBLOCK_CHANCE1 = 0.5
UNBLOCK_CHANCE2 = 1.0
WP_STRIKE_MULT1 = 0.25
WP_STRIKE_MULT2 = 0.5


# att_name, short_descr, long_descr, funcs
PMAP = (
    ('agility_mult', 'agility', 'agility'),
    ('atk_mult', 'attack', 'attack'),
    ('chance_cause_bleeding', 'bleeding', 'cause bleeding'),
    ('block_disarm', 'disarm', 'disarm chance when defending'),
    ('block_mult', 'blocks', 'block efficiency'),
    ('counter_chance_mult', 'counters', 'counterattack chance'),
    ('critical_chance_mult', 'criticals', 'critical attack chance'),
    ('critical_dam_mult', 'criticals', 'critical attack power'),
    ('dam_reduc', 'dam.reduc.', 'damage reduction'),
    ('dfs_mult', 'defense', 'defense'),
    (
        'dfs_penalty_step',
        'vs crowd',
        'defense penalty (20% by default)',
    ),
    ('dodge_mult', 'dodge', 'dodge efficiency'),
    ('environment_chance', 'environment', 'chance to use environment'),
    ('fall_damage_mult', 'low fall dam', 'fall damage'),
    ('fury_chance', 'fury', 'fury chance'),
    (
        'grab_chance',
        'grabs',
        'grab chance',
    ),  # todo use grab_chance boost
    ('guard_dfs_bonus', 'guard', 'guard efficiency'),
    (
        'guard_while_attacking',
        'guard while atk',
        'guard while attacking',
    ),
    ('health_mult', 'health', 'health'),
    ('hit_disarm', 'disarm', 'disarm chance when attacking'),
    ('hp_gain_mult', 'HP gain', 'HP gain per turn'),
    (
        'in_fight_impro_wp_chance',
        'improv.weapons',
        'in-fight improvised weapon chance',
    ),
    ('maneuver_time_cost_mult', 'maneuv.time', 'maneuver time cost'),
    (
        'preemptive_chance',
        'preemptive',
        'preemptive strike chance',
    ),
    ('move_complexity_mult', 'move cplx.', 'move complexity'),
    ('off_balance_atk_mult', 'off-bal.atk', 'off-balance attack'),
    ('off_balance_dfs_mult', 'off-bal.dfs', 'off-balance defense'),
    ('qi_when_atk', 'qi/atk', 'qi when attacking'),
    ('qp_gain_mult', 'qi', 'QP/turn'),
    ('qp_max_mult', 'qi', 'max QP'),
    ('qp_start', 'qi', 'QP to start with'),
    ('resist_ko', 'resist KO', 'chance to resist KO'),
    ('speed_mult', 'speed', 'speed'),
    ('stamina_max_mult', 'stamina', 'max stamina'),
    ('stamina_gain_mult', 'stamina', 'restore stamina'),
    ('strength_mult', 'strength', 'strength'),
    ('strike_time_cost_mult', 'strike time', 'strike time cost'),
    ('stun_chance', 'stun', 'stun chance'),
    ('unblock_chance', 'unblock.', 'unblockable attack'),

    # strike multipliers  # todo add more strike multipliers
    ('acrobatic_strike_mult', 'acrob.str', 'acrobatic strike efficiency'),
    ('dist1_strike_mult', 'close-range', 'close-range strike efficiency'),
    ('dist2_strike_mult', 'mid-range', 'mid-range strike efficiency'),
    ('dist3_strike_mult', 'long-range', 'long-range strike efficiency'),
    ('drunken_strike_mult', 'drun.str.', 'drunken strike efficiency'),
    ('elbow_strike_mult', 'elbows', 'elbow strike efficiency'),
    ('flying_strike_mult', 'jumps', 'jumping strike efficiency'),
    ('grappling_strike_mult', 'grappling', 'grappling efficiency'),
    ('kick_strike_mult', 'kicks', 'kick efficiency'),
    ('knee_strike_mult', 'knees', 'knee strike efficiency'),
    ('palm_strike_mult', 'palm str.', 'palm strike efficiency'),
    ('punch_strike_mult', 'punches', 'punch efficiency'),
    ('weapon_strike_mult', 'weapons', 'weapon efficiency'),
)


def set_descr(obj):
    descr_list = []
    descr_short_set = set()
    for param, short, long in PMAP:
        if param in obj.params:
            v = obj.params[param]
            for f in (hund, add_sign, add_pcnt):
                v = f(v)
            descr_list.append(f'{v} {long}')
            descr_short_set.add(short)
    obj.descr = '; '.join(descr_list)
    obj.descr_short = ', '.join(sorted(descr_short_set))
