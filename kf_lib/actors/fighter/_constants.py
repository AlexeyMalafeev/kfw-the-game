BLOCK_DIVISOR = 2
DAM_DIVISOR = 2
DODGE_DIVISOR = 3
DUR_LYING_MIN = 100
DUR_LYING_MAX = 200
DUR_OFF_BAL_MIN = 30
DUR_OFF_BAL_MAX = 60
DUR_SHOCK_MIN = 50
DUR_SHOCK_MAX = 100
DUR_SLOW_MIN = 300
DUR_SLOW_MAX = 600
DUR_STUN_MIN = 50
DUR_STUN_MAX = 150
FALL_DAMAGE = (25, 50)
INSTA_KO_CHANCE = 0.25
KNOCKBACK_DIST_FORCED = (1, 1, 1, 2, 2, 3)
KNOCKBACK_HP_THRESHOLDS = (0.3, 0.35, 0.4)  # correspond to levels of knockback: 1, 2, 3
KNOCKDOWN_HP_DIVISOR = 2     # todo make 0.5 like above thresholds
LEVEL_BASED_DAM_UPPER_MULT = 10  # * self.level in damage; upper bound
NEW_MOVE_TIERS = {
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 4,
    8: 4,
    9: 5,
    10: 5,
    11: 6,
    12: 6,
    13: 7,
    14: 7,
    15: 8,
    16: 8,
    17: 9,
    18: 9,
    19: 10,
    20: 10,
}
MOB_DAM_PENALTY = 0.3
OFF_BALANCE_HP_DIVISOR = 4  # todo make 0.25 like above thresholds
QI_BASED_DAM_UPPER_MULT = 3
SHOCK_CHANCE = 0.5  # for moves
STAMINA_DAMAGE = 0.2  # for moves
STAMINA_FACTOR_BIAS = 0.5
STAT_BASED_DAM_UPPER_MULT = 5
STUN_HP_DIVISOR = 2.8
TIME_UNIT_MULTIPLIER = 20

INDENT = 0
ALIGN = 60
