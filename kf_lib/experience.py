from .utilities import *


BOOK_EXP = (10, 50)
FIGHT_EXP_BASE = 20

DRAW_EXP_DIVISOR = 2
LOSER_EXP_DIVISOR = 4


def calc_fight_exp(winners, losers):
    """Uses .exp_worth that is established at the beginning of a fight"""
    win_exp_total = sum([f.exp_worth for f in winners])  # can be 0 because there might be a draw
    lose_exp_total = sum(
        [f.exp_worth for f in losers]
    )  # can't be 0 because there are always losers
    win_exp_relative = round(win_exp_total / lose_exp_total * FIGHT_EXP_BASE)
    lose_exp_relative = round(lose_exp_total / win_exp_total * FIGHT_EXP_BASE / LOSER_EXP_DIVISOR)


def fighter_to_exp(f):
    exp = 10 + (f.strength * f.agility * f.speed * f.health) * 0.01 * 3 + len(f.techs) * 3
    if f.weapon:
        w = f.weapon
        w_mult = w.get_exp_mult()
        exp *= w_mult
    exp = round(exp)
    return exp


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


def fighters_to_exp(fs):
    exp = 0
    for f in fs:
        exp += fighter_to_exp(f)
    return exp
