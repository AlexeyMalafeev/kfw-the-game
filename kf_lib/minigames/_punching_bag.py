"""Punching Bag: one minute of fight time to hit a bag as hard as you can.

The bag never fights back, dodges or blocks, so the round is about choosing
strong, affordable moves, managing stamina and qi, and staying in range (heavy
pushes swing the bag away). The fighter has a fixed level, so records compare
like with like; the best damage is kept as a record. The bag and its round
are shared with the main game's practice: kf_lib/actors/punching_bag.py,
kf_lib/fighting/fight/_bag_fights.py.
"""
from kf_lib.actors import fighter_factory
from kf_lib.fighting.fight import TimedBagRound, play_timed_bag_round
from kf_lib.i18n import _, tr_style_name
from kf_lib.ui import MUSIC, cls, pak, play_music, rprint, style, yn
from . import _records


FIGHTER_LEVEL = 10
ROUND_SECONDS = TimedBagRound.ROUND_SECONDS
RECORDS = 'bag'


def play_round(fighter):
    """One round; return the damage dealt."""
    return play_timed_bag_round(fighter)


def _record_text(record):
    return _('{dam} damage ({name}, {style})').format(
        dam=_records.get_score(record, 'damage'),
        name=record.get('name', '?'),
        style=tr_style_name(str(record.get('style', '?'))),
    )


def update_record(fighter, damage):
    old = _records.get_records(RECORDS).get('best')
    if damage > _records.get_score(old, 'damage'):
        _records.save_record(
            RECORDS,
            'best',
            {
                'damage': damage,
                'name': fighter.name,
                'style': fighter.style.public_name,
            },
        )
        rprint(style(_(' New record!'), 'bold green'))
    elif old:
        rprint(_(' Record: {record}').format(record=_record_text(old)))


def play_punching_bag():
    play_music(MUSIC['practice'])
    cls()
    rprint(_(' ***Welcome to the [bold]Punching Bag[/bold]***'))
    rprint(
        _(' Hit the bag as hard as you can in {sec} seconds of fight time.').format(
            sec=ROUND_SECONDS
        )
    )
    rprint(
        _(' The bag never fights back. Your fighter is level {lv}.').format(
            lv=FIGHTER_LEVEL
        )
    )
    old = _records.get_records(RECORDS).get('best')
    if old:
        rprint(_(' Record: {record}').format(record=_record_text(old)))
    pak()
    fighter = fighter_factory.new_custom_hcf(level=FIGHTER_LEVEL)
    while True:
        damage = play_round(fighter)
        update_record(fighter, damage)
        if not yn(_('Another round?')):
            break
