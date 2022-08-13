from kf_lib.utils import mean, multiply

BOOK_EXP = (10, 50)
FIGHT_EXP_BASE = 20

DRAW_EXP_DIVISOR = 2
LOSER_EXP_DIVISOR = 4


# todo refactor extract_features
def extract_features(side_a, side_b):
    # side_a.average_lv, side_b.average_lv, lv_relation
    # side_a.average_atts, side_b.average_atts, att_relation
    # side_a.average_techs, side_b.average_techs, tech_relation
    # side_a.n, side_b.n, n_relative
    # weapons_a, weapons_b, weapons_rel
    features = []

    # level-related
    val1 = mean([f.level for f in side_a])
    features.append(val1)
    val2 = mean([f.level for f in side_b])
    features.append(val2)
    val3 = round(val1 / val2, 2)
    features.append(val3)

    # att-related
    val1 = mean([multiply(f.get_att_values_full()) for f in side_a])
    features.append(val1)
    val2 = mean([multiply(f.get_att_values_full()) for f in side_b])
    features.append(val2)
    val3 = round(val1 / val2, 2)
    features.append(val3)

    # tech-related
    val1 = 1 + mean([len(f.techs) for f in side_a])
    features.append(val1)
    val2 = 1 + mean([len(f.techs) for f in side_b])
    features.append(val2)
    val3 = round(val1 / val2, 2)
    features.append(val3)

    # crowd
    val1 = len(side_a)
    features.append(val1)
    val2 = len(side_b)
    features.append(val2)
    val3 = round(val1 / val2, 2)
    features.append(val3)

    # weapon
    val1 = 1 + mean([0.0] + [f.weapon.dfs_bonus + f.weapon.atk_mean for f in side_a if f.weapon])
    features.append(val1)
    val2 = 1 + mean([0.0] + [f.weapon.dfs_bonus + f.weapon.atk_mean for f in side_b if f.weapon])
    features.append(val2)
    val3 = round(val1 / val2, 2)
    features.append(val3)

    return features
