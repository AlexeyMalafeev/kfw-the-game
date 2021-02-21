#! python3
"""
Traits are activated at Player creation time. If the Player is saved, the traits are saved as well (part of the
init_atts). So far, there is no way to change the Player's traits in-game. There is no way to deactivate a trait either.
Traits are represented as strings; their effects are looked up in the TRAIT_EFFECTS dictionary.
"""


import random


# Add new traits here: (neg, pos, att_dict),
# where att_dict = {att1: change1, att2: change2, ...}.
# Note that the effects are defined in terms of _positive_ traits.
# That is, positive traits should always _add to_ attributes, while negative should _subtract from_ them.
# So, if the higher an att the better, define the change as x,
# and if the lower an att the better, define the change as -x.
_TRAITS_TUP = (
    (
        'careless',
        'careful',
        {
            'escape_bonus': 0.3,
            'training_injury': -0.05,
            'thief_steals': -0.2,
            'item_is_lost': -0.009,
            'item_is_found': 0.009,
        },
    ),
    ('greedy', 'generous', {'feel_too_greedy': -0.25}),
    (
        'lazy',
        'hardworking',
        {'home_training_exp_mult': 0.5, 'wage_mult': 0.2, 'school_training_exp_mult': 0.1},
    ),
    ('cowardly', 'brave', {'feel_too_scared': -0.3}),
    (
        'narrow-minded',
        'broad-minded',
        {
            'num_techs_choose': 1,
            'num_techs_choose_upgrade': 1,
            'num_moves_choose': 1,
            'num_atts_choose': 1,
            'grab_improvised_weapon': 0.1,
        },
    ),
    # ('unscrupulous', 'honest', {}),  # ?
    # ('arrogant', 'modest', {}),  # reputation, rep_mult?
    ('unfriendly', 'friendly', {'max_num_friends': 2, 'challenger_friend_mult': 1.0}),
    # ('impatient', 'patient', {}),  # some encounters, like WiseMan? some school encounters?
    # ('impolite', 'polite', {}),  # remove?
    (
        'undisciplined',
        'disciplined',
        {'drink_with_drunkard': -0.2, 'gamble_with_gambler': -0.2, 'gamble_continue': -0.3},
    ),
    ('slow-witted', 'quick-witted', {'next_lv_exp_mult': -0.1}),
)
# also: (un)healthy?

NEG_TRAITS_TUP = tuple(t[0] for t in _TRAITS_TUP)
NEG_TRAITS_LIST = list(NEG_TRAITS_TUP)
NEG_TRAITS_SET = set(NEG_TRAITS_TUP)
POS_TRAITS_TUP = tuple(t[1] for t in _TRAITS_TUP)
POS_TRAITS_LIST = list(POS_TRAITS_TUP)
POS_TRAITS_SET = set(POS_TRAITS_TUP)
NEG_TO_POS_DICT = {t: POS_TRAITS_TUP[i] for i, t in enumerate(NEG_TRAITS_TUP)}
POS_TO_NEG_DICT = {t: NEG_TRAITS_TUP[i] for i, t in enumerate(POS_TRAITS_TUP)}

ALL_TRAITS_TUP = NEG_TRAITS_TUP + POS_TRAITS_TUP
TRAIT_EFFECTS = {t_neg: eff_dict for t_neg, t_pos, eff_dict in _TRAITS_TUP}
# negate effects for negative traits
for t, eff_dict in TRAIT_EFFECTS.items():
    rev_eff_dict = {}
    for att, change in eff_dict.items():
        rev_eff_dict[att] = -change
    TRAIT_EFFECTS[t] = rev_eff_dict
TRAIT_EFFECTS.update({t_pos: eff_dict for t_neg, t_pos, eff_dict in _TRAITS_TUP})


def get_opposite_trait(trait):
    if trait in POS_TRAITS_SET:
        return POS_TO_NEG_DICT[trait]
    else:
        return NEG_TO_POS_DICT[trait]


def get_rand_traits(n=1, player=None, negative=True, positive=True):
    """If n == 1, return the trait as a string;
    if n > 1, return a list of traits."""
    traits = []
    if negative:
        traits += NEG_TRAITS_LIST
    if positive:
        traits += POS_TRAITS_LIST
    if player is None:
        result = random.sample(traits, n)
    else:
        av_traits = set(traits) - set(player.traits)
        opp_p_traits = set([get_opposite_trait(t) for t in player.traits])
        av_traits = av_traits - opp_p_traits
        result = random.sample(list(av_traits), n)
    if len(result) == 1:
        return result[0]
    else:
        return result


def get_trait_eff_dict(trait):
    return TRAIT_EFFECTS[trait]
