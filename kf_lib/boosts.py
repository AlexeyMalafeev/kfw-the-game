#! python3


from .utilities import *


AGILITY1 = 0.3
AGILITY2 = 0.6
ATTACK1 = 0.1
ATTACK2 = 0.2
ATTACK_HALF = round(ATTACK1 / 2, 2)
BLOCK_DISARM1 = 0.5
BLOCK_DISARM2 = 1.0
BLOCK1 = 0.4
BLOCK2 = 0.8
COUNTER_CH1 = 0.2
COUNTER_CH2 = 0.4
CRIT_CH1 = 0.15
CRIT_CH2 = 0.3
CRIT_M1 = 0.5
CRIT_M2 = 1
DAM_REDUC1 = 5
DAM_REDUC2 = 10
DEFENSE1 = 0.3
DEFENSE2 = 0.6
DEFENSE_HALF = round(DEFENSE1 / 2, 2)
DFS_PEN1 = -0.1
DFS_PEN2 = -0.2  # this effectively reduces defense penalty down to zero
ENVIRONMENT_CH1 = 0.15
ENVIRONMENT_CH2 = 0.3
EVADE1 = 0.5
EVADE2 = 1
GRAB_CH1 = 0.2  # todo this is not used
GRAB_CH2 = 0.4
GUARD_DFS1 = 0.5
GUARD_DFS2 = 1.0
GUARD_WHILE_ATTACKING1 = 0.5
GUARD_WHILE_ATTACKING2 = 1.0
HEALTH1 = 0.3
HEALTH2 = 0.6
HIT_DISARM1 = 0.5
HIT_DISARM2 = 1.0
HOME_TRAIN_BONUS = 0.5
HP_GAIN1 = 5
HP_GAIN2 = 10
HP_MULT = 1.5  # todo this is not used
IN_FIGHT_IMPRO_WP_CH1 = 0.25
IN_FIGHT_IMPRO_WP_CH2 = 0.5
QI_WHEN_ATK = 0.5  # todo this is not used
QP_GAIN1 = 5
QP_GAIN2 = 10
QP_MAX1 = 50
QP_MAX2 = 100
QP_START1 = 0.5
QP_START2 = 1.0
RARE_STRIKE_MULT1 = 0.4
RARE_STRIKE_MULT2 = 0.8
RESIST_KO1 = 0.25
RESIST_KO2 = 0.5
SPEED1 = 0.3
SPEED2 = 0.6
STAM_MAX1 = 20
STAM_MAX2 = 40
STAM_RESTORE1 = 5
STAM_RESTORE2 = 10
STRENGTH1 = 0.3
STRENGTH2 = 0.6
STRIKE_MULT1 = 0.25
STRIKE_MULT2 = 0.5
STRIKE_MULT_HALF = 0.125
STUN_CH1 = 0.15
STUN_CH2 = 0.3
UNBLOCK_CHANCE1 = 0.3
UNBLOCK_CHANCE2 = 0.6
WP_STRIKE_MULT1 = 0.25
WP_STRIKE_MULT2 = 0.5


# att_name, short_descr, long_descr, funcs
PMAP = (
    ('agility_full', 'agility', 'agility', [add_sign]),
    ('agility_mult', 'agility', 'agility', [hund, add_sign, add_pcnt]),
    ('atk_mult', 'attack', 'attack', [hund, add_sign, add_pcnt]),
    ('block_disarm', 'disarm', 'disarm chance when defending', [hund, add_sign, add_pcnt]),
    ('block_mult', 'blocks', 'block efficiency', [hund, add_sign, add_pcnt]),
    ('counter_chance', 'counters', 'counterattack chance', [hund, add_sign, add_pcnt]),
    ('critical_chance', 'criticals', 'critical attack chance', [hund, add_sign, add_pcnt]),
    ('critical_mult', 'criticals', 'critical attack power', [hund, add_sign, add_pcnt]),
    ('dam_reduc', 'dam.reduc.', 'damage reduction', [add_sign]),
    ('dfs_mult', 'defense', 'defense', [hund, add_sign, add_pcnt]),
    (
        'dfs_penalty_step',
        'vs crowd',
        'defense penalty (20% by default)',
        [hund, add_sign, add_pcnt],
    ),
    ('environment_chance', 'environment', 'chance to use environment', [hund, add_sign, add_pcnt]),
    ('dodge_mult', 'dodge', 'dodge efficiency', [hund, add_sign, add_pcnt]),
    (
        'grab_chance',
        'grabs',
        'grab chance',
        [hund, add_sign, add_pcnt],
    ),  # todo use grab_chance boost
    ('guard_dfs_bonus', 'guard', 'guard efficiency', [hund, add_sign, add_pcnt]),
    (
        'guard_while_attacking',
        'guard while atk',
        'guard while attacking',
        [hund, add_sign, add_pcnt],
    ),
    ('health_full', 'health', 'health', [add_sign]),
    ('health_mult', 'health', 'health', [hund, add_sign, add_pcnt]),
    ('hit_disarm', 'disarm', 'disarm chance when attacking', [hund, add_sign, add_pcnt]),
    ('home_training_exp_mult', 'home train.', 'home training', [hund, add_sign, add_pcnt]),
    ('hp_gain', 'HP gain', 'HP/turn', [add_sign]),
    ('hp_per_health_lv', 'HP/lv.', 'HP/health level', [add_sign]),
    (
        'in_fight_impro_wp_chance',
        'weapons',
        'in-fight improvised weapon chance',
        [hund, add_sign, add_pcnt],
    ),
    ('qi_when_atk', 'qi/atk', 'qi when attacking', [hund, add_sign, add_pcnt]),
    ('qp_gain', 'qi', 'QP/turn', [add_sign]),
    ('qp_max', 'qi', 'max QP', [add_sign]),
    ('qp_start', 'qi', 'QP to start with', [hund, add_sign, add_pcnt]),
    ('resist_ko', 'resist KO', 'chance to resist KO', [hund, add_sign, add_pcnt]),
    ('speed_full', 'speed', 'speed', [add_sign]),
    ('speed_mult', 'speed', 'speed', [hund, add_sign, add_pcnt]),
    ('stamina_max', 'stamina', 'max stamina', [add_sign]),
    ('stamina_gain', 'stamina', 'restore stamina', [add_sign]),
    ('strength_full', 'strength', 'strength', [add_sign]),
    ('strength_mult', 'strength', 'strength', [hund, add_sign, add_pcnt]),
    ('stun_chance', 'stun', 'stun chance', [hund, add_sign, add_pcnt]),
    ('unblock_chance', 'unblock.', 'unblockable attack', [hund, add_sign, add_pcnt]),
    # strike multipliers  # todo add more strike multipliers
    ('dist1_bonus', 'close-range', 'close-range strike efficiency', [hund, add_sign, add_pcnt]),
    ('dist2_bonus', 'mid-range', 'mid-range strike efficiency', [hund, add_sign, add_pcnt]),
    ('dist3_bonus', 'long-range', 'long-range strike efficiency', [hund, add_sign, add_pcnt]),
    ('elbow_strike_mult', 'elbows', 'elbow strike efficiency', [hund, add_sign, add_pcnt]),
    ('exotic_strike_mult', 'exot.str.', 'exotic strike efficiency', [hund, add_sign, add_pcnt]),
    ('flying_strike_mult', 'jumps', 'jumping strike efficiency', [hund, add_sign, add_pcnt]),
    ('grappling_strike_mult', 'grappling', 'grappling efficiency', [hund, add_sign, add_pcnt]),
    ('kick_strike_mult', 'kicks', 'kick efficiency', [hund, add_sign, add_pcnt]),
    ('knee_strike_mult', 'knees', 'knee strike efficiency', [hund, add_sign, add_pcnt]),
    ('palm_strike_mult', 'palm str.', 'palm strike efficiency', [hund, add_sign, add_pcnt]),
    ('punch_strike_mult', 'punches', 'punch efficiency', [hund, add_sign, add_pcnt]),
    ('weapon_strike_mult', 'weapons', 'weapon efficiency', [hund, add_sign, add_pcnt]),
)


def set_descr(obj):
    descr_list = []
    descr_short_set = set()
    for param, short, long, funcs in PMAP:
        if param in obj.params:
            v = obj.params[param]
            for f in funcs:
                v = f(v)
            descr_list.append('{} {}'.format(v, long))
            descr_short_set.add(short)
    obj.descr = '; '.join(descr_list)
    obj.descr_short = ', '.join(sorted(descr_short_set))
