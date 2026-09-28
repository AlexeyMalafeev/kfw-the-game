from typing import List, Text

from kf_lib.i18n import _, ngettext, tr_name
from kf_lib.utils import enum_words


def generate_bio(player_instance) -> Text:
    p = player_instance
    g = p.game
    # gender may be None in old (pre-gender) saves; the male branch keeps the
    # legacy wording ('His kung-fu style...') for them
    female = p.gender == 'f'
    bio: List[Text] = []
    victories = g.check_victory_conditions(p)
    bio.append(
        _('\n{name} was the renowned {victories} of {town}.').format(
            name=p.name,
            victories=enum_words([tr_name(v) for v in victories]),
            town=g.town_name,
        )
    )
    style = p.get_displayed_style_name()
    if female:
        bio.append(_('Her kung-fu style was {style}.').format(style=style))
    else:
        bio.append(_('His kung-fu style was {style}.').format(style=style))
    if fav_move := p.get_favorite_move(attack_only=True):
        if female:
            bio.append(
                _('Her signature move was the {move}.').format(move=tr_name(fav_move))
            )
            if feared_move := p.get_most_feared_move(exclude=fav_move):
                bio.append(
                    _('But her most feared move was the {move}.').format(
                        move=tr_name(feared_move)
                    )
                )
        else:
            bio.append(
                _('His signature move was the {move}.').format(move=tr_name(fav_move))
            )
            if feared_move := p.get_most_feared_move(exclude=fav_move):
                bio.append(
                    _('But his most feared move was the {move}.').format(
                        move=tr_name(feared_move)
                    )
                )
    full_atts = p.get_att_values_full()
    max_att, min_att = max(full_atts), min(full_atts)
    att_diff = max_att - min_att
    if not att_diff:
        atts = enum_words([tr_name(a) for a in p.att_names])
        if female:
            bio.append(
                _('She was uniquely versatile, having equally great {atts}.').format(
                    atts=atts
                )
            )
        else:
            bio.append(
                _('He was uniquely versatile, having equally great {atts}.').format(
                    atts=atts
                )
            )
    else:
        best_atts = enum_words(
            [tr_name(p.att_names[i]) for i, val in enumerate(full_atts) if val == max_att]
        )
        if att_diff <= 2:
            if female:
                bio.append(
                    _(
                        'She was rather versatile, but especially known for her {atts}.'
                    ).format(atts=best_atts)
                )
            else:
                bio.append(
                    _(
                        'He was rather versatile, but especially known for his {atts}.'
                    ).format(atts=best_atts)
                )
        elif att_diff <= 5:
            if female:
                bio.append(
                    _('She was especially known for her outstanding {atts}.').format(
                        atts=best_atts
                    )
                )
            else:
                bio.append(
                    _('He was especially known for his outstanding {atts}.').format(
                        atts=best_atts
                    )
                )
        else:
            worst_atts = enum_words(
                [
                    tr_name(p.att_names[i])
                    for i, val in enumerate(full_atts)
                    if val == min_att
                ]
            )
            if female:
                bio.append(
                    _(
                        'She was said to possess almost inhuman {best_atts}, although, '
                        'perhaps, at the cost of {worst_atts}.'
                    ).format(best_atts=best_atts, worst_atts=worst_atts)
                )
            else:
                bio.append(
                    _(
                        'He was said to possess almost inhuman {best_atts}, although, '
                        'perhaps, at the cost of {worst_atts}.'
                    ).format(best_atts=best_atts, worst_atts=worst_atts)
                )

    if p.is_married and p.sweetheart is not None:
        n_children = len(p.children_ages)
        if n_children:
            if female:
                bio.append(
                    ngettext(
                        'She married the love of her life, {name}, and they '
                        'raised {} wonderful child, who carries on her kung-fu.',
                        'She married the love of her life, {name}, and they '
                        'raised {} wonderful children, who carry on her kung-fu.',
                        n_children,
                    ).format(n_children, name=p.sweetheart.name)
                )
            else:
                bio.append(
                    ngettext(
                        'He married the love of his life, {name}, and they '
                        'raised {} wonderful child, who carries on his kung-fu.',
                        'He married the love of his life, {name}, and they '
                        'raised {} wonderful children, who carry on his kung-fu.',
                        n_children,
                    ).format(n_children, name=p.sweetheart.name)
                )
        else:
            if female:
                bio.append(
                    _('She married the love of her life, {name}.').format(
                        name=p.sweetheart.name
                    )
                )
            else:
                bio.append(
                    _('He married the love of his life, {name}.').format(
                        name=p.sweetheart.name
                    )
                )

    # undefeated, founded school or not, spent vs earned, gambled, popular with people,
    # notable fights, unwrap accomplishments into short stories

    return ' '.join(bio)
