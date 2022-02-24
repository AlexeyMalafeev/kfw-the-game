from kf_lib.utils import add_pcnt, add_sign, hund


AGILITY1 = 0.2
AGILITY2 = 0.4
ATTACK1 = 0.15
ATTACK2 = 0.3
ATTACK_HALF = round(ATTACK1 / 2, 2)
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
DAM_REDUC1 = 5
DAM_REDUC2 = 10
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
ENVIRONMENT_CH1 = 0.15
ENVIRONMENT_CH2 = 0.3
EVADE1 = 0.4
EVADE2 = 0.8
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
HOME_TRAIN_BONUS = 0.5
HP_GAIN1 = 10
HP_GAIN2 = 20
HP_MULT = 1.5  # todo this is not used?
IN_FIGHT_IMPRO_WP_CH1 = 0.25
IN_FIGHT_IMPRO_WP_CH2 = 0.5
MANEUVER_TIME_COST_MULT1 = -0.4
MANEUVER_TIME_COST_MULT2 = -0.8
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


HUND_ADD_SIGN_ADD_PCNT = (hund, add_sign, add_pcnt)


# att_name, short_descr, long_descr, funcs
PMAP = (
    ('agility_mult', 'agility', 'agility', HUND_ADD_SIGN_ADD_PCNT),
    ('atk_mult', 'attack', 'attack', HUND_ADD_SIGN_ADD_PCNT),
    ('block_disarm', 'disarm', 'disarm chance when defending', HUND_ADD_SIGN_ADD_PCNT),
    ('block_mult', 'blocks', 'block efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('counter_chance_mult', 'counters', 'counterattack chance', HUND_ADD_SIGN_ADD_PCNT),
    ('critical_chance_mult', 'criticals', 'critical attack chance', HUND_ADD_SIGN_ADD_PCNT),
    ('critical_dam_mult', 'criticals', 'critical attack power', HUND_ADD_SIGN_ADD_PCNT),
    ('dam_reduc', 'dam.reduc.', 'damage reduction', (add_sign, )),
    ('dfs_mult', 'defense', 'defense', HUND_ADD_SIGN_ADD_PCNT),
    (
        'dfs_penalty_step',
        'vs crowd',
        'defense penalty (20% by default)',
        HUND_ADD_SIGN_ADD_PCNT,
    ),
    ('environment_chance', 'environment', 'chance to use environment', HUND_ADD_SIGN_ADD_PCNT),
    ('dodge_mult', 'dodge', 'dodge efficiency', HUND_ADD_SIGN_ADD_PCNT),
    (
        'grab_chance',
        'grabs',
        'grab chance',
        HUND_ADD_SIGN_ADD_PCNT,
    ),  # todo use grab_chance boost
    ('fury_chance', 'fury', 'fury chance', HUND_ADD_SIGN_ADD_PCNT),
    ('guard_dfs_bonus', 'guard', 'guard efficiency', HUND_ADD_SIGN_ADD_PCNT),
    (
        'guard_while_attacking',
        'guard while atk',
        'guard while attacking',
        HUND_ADD_SIGN_ADD_PCNT,
    ),
    ('health_mult', 'health', 'health', HUND_ADD_SIGN_ADD_PCNT),
    ('hit_disarm', 'disarm', 'disarm chance when attacking', HUND_ADD_SIGN_ADD_PCNT),
    ('home_training_exp_mult', 'home train.', 'home training', HUND_ADD_SIGN_ADD_PCNT),
    ('hp_gain', 'HP gain', 'HP/turn', [add_sign]),
    (
        'in_fight_impro_wp_chance',
        'weapons',
        'in-fight improvised weapon chance',
        HUND_ADD_SIGN_ADD_PCNT,
    ),
    ('maneuver_time_cost_mult', 'maneuv.time', 'maneuver time cost', HUND_ADD_SIGN_ADD_PCNT),
    (
        'preemptive_chance',
        'preemptive',
        'preemptive strike chance',
        HUND_ADD_SIGN_ADD_PCNT,
    ),
    ('qi_when_atk', 'qi/atk', 'qi when attacking', HUND_ADD_SIGN_ADD_PCNT),
    ('qp_gain_mult', 'qi', 'QP/turn', HUND_ADD_SIGN_ADD_PCNT),
    ('qp_max_mult', 'qi', 'max QP', HUND_ADD_SIGN_ADD_PCNT),
    ('qp_start', 'qi', 'QP to start with', HUND_ADD_SIGN_ADD_PCNT),
    ('resist_ko', 'resist KO', 'chance to resist KO', HUND_ADD_SIGN_ADD_PCNT),
    ('speed_mult', 'speed', 'speed', HUND_ADD_SIGN_ADD_PCNT),
    ('stamina_max_mult', 'stamina', 'max stamina', HUND_ADD_SIGN_ADD_PCNT),
    ('stamina_gain_mult', 'stamina', 'restore stamina', HUND_ADD_SIGN_ADD_PCNT),
    ('strength_mult', 'strength', 'strength', HUND_ADD_SIGN_ADD_PCNT),
    ('strike_time_cost_mult', 'strike time', 'strike time cost', HUND_ADD_SIGN_ADD_PCNT),
    ('stun_chance', 'stun', 'stun chance', HUND_ADD_SIGN_ADD_PCNT),
    ('unblock_chance', 'unblock.', 'unblockable attack', HUND_ADD_SIGN_ADD_PCNT),
    # strike multipliers  # todo add more strike multipliers
    ('dist1_bonus', 'close-range', 'close-range strike efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('dist2_bonus', 'mid-range', 'mid-range strike efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('dist3_bonus', 'long-range', 'long-range strike efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('elbow_strike_mult', 'elbows', 'elbow strike efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('exotic_strike_mult', 'exot.str.', 'exotic strike efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('flying_strike_mult', 'jumps', 'jumping strike efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('grappling_strike_mult', 'grappling', 'grappling efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('kick_strike_mult', 'kicks', 'kick efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('knee_strike_mult', 'knees', 'knee strike efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('palm_strike_mult', 'palm str.', 'palm strike efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('punch_strike_mult', 'punches', 'punch efficiency', HUND_ADD_SIGN_ADD_PCNT),
    ('weapon_strike_mult', 'weapons', 'weapon efficiency', HUND_ADD_SIGN_ADD_PCNT),
)


def set_descr(obj):
    descr_list = []
    descr_short_set = set()
    for param, short, long, funcs in PMAP:
        if param in obj.params:
            v = obj.params[param]
            for f in funcs:
                v = f(v)
            descr_list.append(f'{v} {long}')
            descr_short_set.add(short)
    obj.descr = '; '.join(descr_list)
    obj.descr_short = ', '.join(sorted(descr_short_set))
