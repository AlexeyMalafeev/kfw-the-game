from typing import List, Text

from kf_lib.utils import enum_words


def generate_bio(player_instance) -> Text:
    p = player_instance
    g = p.game
    bio: List[Text] = []
    victories = g.check_victory_conditions(p)
    bio.append(f'\n{p.name} was the renowned {enum_words(victories)} of {g.town_name}.')
    bio.append(f'His kung-fu style was {p.style.name}.')
    full_atts = p.get_att_values_full()
    max_att, min_att = max(full_atts), min(full_atts)
    att_diff = max_att - min_att
    if not att_diff:
        bio.append(f'He was uniquely versatile, having equally great {enum_words(p.att_names)}.')
    else:
        best_atts = [p.att_names[i] for i, val in enumerate(full_atts) if val == max_att]
        if att_diff <= 2:
            bio.append(
                f'He was rather versatile, but especially known for his {enum_words(best_atts)}.')
        elif att_diff <= 5:
            bio.append(
                f'He was especially known for his outstanding {enum_words(best_atts)}.')
        else:
            worst_atts = [p.att_names[i] for i, val in enumerate(full_atts) if val == min_att]
            bio.append(
                f'He was said to possess almost inhuman {enum_words(best_atts)}, although, '
                f'perhaps, at the cost of {enum_words(worst_atts)}.'
            )

    # undefeated, founded school or not, spent vs earned, gambled, popular with people,
    # most favorite strike, most feared move, notable fights, unwrap accomplishments into
    # short stories

    return ' '.join(bio)
