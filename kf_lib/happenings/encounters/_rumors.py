"""Free rumors the gossipmonger tells about the other players.

Each rumor is built from what townsfolk could plausibly know (style, school,
favorite move, family, money troubles, tournament wins...), never the exact
career numbers of the full stats table — that one still costs money.
"""

import random

from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name, tr_style_name
from kf_lib.kung_fu.moves import ALL_MOVES_DICT

# thresholds
MIN_ACCOMPL_LEGEND = 5
MIN_FEARED_MOVE_TIER = 1  # basic moves (tier 0) scare nobody
MIN_FRIENDS_MANY = 3
MIN_GAMBLING_SUM = 50
MIN_KOS_MANY = 10
MIN_MONEY_RICHEST = 100
MIN_TIMES_DRUNK = 3
MIN_TIMES_KOED = 3


def collect_rumors(listener):
    """Every rumor the gossipmonger could tell `listener` right now. Rumors are
    about the other players; in a game with no other players, about the
    listener (the gossipmonger doesn't recognize them). Never empty: everybody
    has a style."""
    players = listener.game.players
    subjects = [pp for pp in players if pp is not listener] or [listener]
    rumors = []
    for s in subjects:
        rumors.extend(_personal_rumors(s))
    rumors.extend(_comparative_rumors(players, subjects))
    return rumors


def get_rumor(listener):
    return random.choice(collect_rumors(listener))


def _public_style_name(s):
    # never the secret true name, even if the subject has learned it
    return s.custom_style_name or tr_style_name(s.style.public_name)


def _personal_rumors(s):
    name = tr_fighter_name(s.name)
    r = []

    # school
    if s.is_master:
        r.append(
            ngettext(
                '{name} now runs the {school} school, with {n} student already!',
                '{name} now runs the {school} school, with {n} students already!',
                s.students,
            ).format(
                name=name, school=s.custom_style_name or s.new_school_name, n=s.students
            )
        )
    else:
        r.append(
            _('{name} trains under {master} at the {style} school, I hear.').format(
                name=name,
                master=tr_fighter_name(s.get_master().name),
                style=_public_style_name(s),
            )
        )
    if s.banned_from_school:
        r.append(
            _('{name} has been thrown out of the school! Disgraceful.').format(
                name=name
            )
        )

    # moves
    fav_move = s.get_favorite_move(attack_only=True)
    if fav_move:
        r.append(
            _('Folks say {name} loves the {move}. Watch out for it!').format(
                name=name, move=tr_name(fav_move)
            )
        )
    feared_move = s.get_most_feared_move(exclude=fav_move)
    if feared_move and ALL_MOVES_DICT[feared_move].tier >= MIN_FEARED_MOVE_TIER:
        r.append(
            _("Nobody wants to be on the receiving end of {name}'s {move}.").format(
                name=name, move=tr_name(feared_move)
            )
        )

    # family and friends
    if s.sweetheart is not None:
        partner = tr_fighter_name(s.sweetheart.name)
        if s.is_married:
            n_children = len(s.children_ages)
            if n_children:
                r.append(
                    ngettext(
                        '{name} and {partner} are married, with {n} child at home. '
                        'How time flies!',
                        '{name} and {partner} are married, with {n} children at home. '
                        'How time flies!',
                        n_children,
                    ).format(name=name, partner=partner, n=n_children)
                )
            else:
                r.append(
                    _('{name} and {partner} got married. Such a lovely couple!').format(
                        name=name, partner=partner
                    )
                )
        else:
            r.append(
                _(
                    '{name} has been seen strolling by the river with {partner}. '
                    'Wedding soon?'
                ).format(name=name, partner=partner)
            )
    if s.enemies:
        enemy = random.choice(s.enemies)
        r.append(
            _(
                '{name} and {enemy} are sworn enemies. Mark my words, there will be '
                'blood.'
            ).format(name=name, enemy=tr_fighter_name(enemy.name))
        )
    if len(s.friends) >= MIN_FRIENDS_MANY:
        r.append(
            _(
                "{name} has lots of friends — {n} at my last count. Don't pick a fight "
                "with that one."
            ).format(name=name, n=len(s.friends))
        )

    # fame and fighting record
    tourn_won = s.get_stat('tourn_won')
    if tourn_won:
        r.append(
            ngettext(
                '{name} has won {n} tournament. A real champion!',
                '{name} has won {n} tournaments. A real champion!',
                tourn_won,
            ).format(name=name, n=tourn_won)
        )
    if len(s.accompl) >= MIN_ACCOMPL_LEGEND:
        r.append(
            _('People are already telling legends about {name}.').format(name=name)
        )
    if s.get_stat('num_kos') >= MIN_KOS_MANY:
        r.append(
            _('{name} has knocked out more people than I can count.').format(name=name)
        )
    if s.get_stat('times_koed') >= MIN_TIMES_KOED:
        r.append(
            _(
                '{name} has been knocked out cold more than once. Not the hardest head '
                'in town.'
            ).format(name=name)
        )
    if s.inactive and s.inact_status == 'injured':
        r.append(
            _('{name} is nursing an injury. A good time to get ahead!').format(
                name=name
            )
        )
    elif s.inactive and s.inact_status == 'sick':
        r.append(_('{name} is sick in bed, poor thing.').format(name=name))

    # money and vices
    if s.money < 0:
        r.append(_('{name} owes money all over town.').format(name=name))
    if s.get_stat('money_robbed') or s.get_stat('stolen_from'):
        r.append(
            _('{name} got robbed in broad daylight! Can you imagine?').format(name=name)
        )
    if s.get_stat('donated'):
        r.append(_('{name} gives money to the poor. A kind soul.').format(name=name))
    if s.get_stat('got_drunk') >= MIN_TIMES_DRUNK:
        r.append(
            _('{name} is a regular at the tavern. Too regular, if you ask me.').format(
                name=name
            )
        )
    gamb_won, gamb_lost = s.get_stat('gamb_won'), s.get_stat('gamb_lost')
    if gamb_lost >= MIN_GAMBLING_SUM and gamb_lost > gamb_won:
        r.append(_('{name} keeps losing money at dice.').format(name=name))
    elif gamb_won >= MIN_GAMBLING_SUM and gamb_won > gamb_lost:
        r.append(_("{name} has the devil's own luck at dice.").format(name=name))
    return r


def _comparative_rumors(players, subjects):
    r = []
    strongest = _unique_max(players, lambda pp: pp.level)
    if strongest in subjects and len(players) > 1:
        r.append(
            _('They say no young fighter in town is stronger than {name}.').format(
                name=tr_fighter_name(strongest.name)
            )
        )
    richest = _unique_max(players, lambda pp: pp.money)
    if richest in subjects and len(players) > 1 and richest.money >= MIN_MONEY_RICHEST:
        r.append(
            _('No young fighter in town is richer than {name}. Must be nice!').format(
                name=tr_fighter_name(richest.name)
            )
        )
    return r


def _unique_max(players, key):
    """The player with the highest key, or None on a tie."""
    if not players:
        return None
    best = max(players, key=key)
    if sum(1 for pp in players if key(pp) == key(best)) > 1:
        return None
    return best
