BOOK_EXP = (10, 50)
FIGHT_EXP_BASE = 20

DRAW_EXP_DIVISOR = 2
LOSER_EXP_DIVISOR = 4


def calc_fight_exp(winners, losers):
    """Uses .exp_worth that is established at the beginning of a fight"""
    win_exp_total = sum([f.exp_worth for f in winners])  # can be 0 because there might be a draw
    lose_exp_total = sum([f.exp_worth for f in losers])  # can't be 0 because there are always losers
    win_exp_relative = round(win_exp_total / lose_exp_total * FIGHT_EXP_BASE)
    lose_exp_relative = round(lose_exp_total / win_exp_total * FIGHT_EXP_BASE / LOSER_EXP_DIVISOR)


def fighter_to_exp(f):
    exp = (10 + (f.strength * f.agility * f.speed * f.health) * 0.01 * 3 + len(f.techs) * 3)
    if f.weapon:
        w = f.weapon
        w_mult = w.get_exp_mult()
        exp *= w_mult
    exp = round(exp)
    return exp


def fighters_to_exp(fs):
    exp = 0
    for f in fs:
        exp += fighter_to_exp(f)
    return exp