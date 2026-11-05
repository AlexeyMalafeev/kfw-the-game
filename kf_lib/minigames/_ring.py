"""RING: an endless arena ladder; win to level up, three lost fights end it.

The best run per difficulty (most fights won) is kept as a record."""
from kf_lib.actors import fighter_factory
from kf_lib.i18n import _, ngettext, tr_style_name
from kf_lib.ui import (
    MUSIC,
    bold,
    cls,
    cyan,
    menu,
    pak,
    play_music,
    red,
    rprint,
    style,
    yellow,
)
from . import _records


ATTEMPTS = 3
# opponents' level cap above the player's: high enough that some group always
# matches the player's exp worth (a fixed cap of 20 hung the search at lv ~40)
OPP_LV_MARGIN = 5
# record key, multiplier on opponent strength
DIFFICULTIES = (('easy', 0.9), ('normal', 1.0), ('hard', 1.1), ('extreme', 1.2))
RECORDS = 'ring'


def _difficulty_label(key):
    labels = {
        'easy': _('easy'),
        'normal': _('normal'),
        'hard': _('hard'),
        'extreme': _('extreme'),
    }
    return labels[key]


def _wins_text(n):
    return ngettext('{n} fight won', '{n} fights won', n).format(n=n)


def _record_text(record):
    return _('{wins} ({name}, {style}, lv.{start} to lv.{level})').format(
        wins=_wins_text(_records.get_score(record, 'wins')),
        name=record.get('name', '?'),
        style=tr_style_name(str(record.get('style', '?'))),
        start=record.get('start_level', '?'),
        level=record.get('level', '?'),
    )


def show_records():
    records = _records.get_records(RECORDS)
    known = [key for key, _mult in DIFFICULTIES if key in records]
    if not known:
        return
    rprint(_(' Records:'))
    width = max(len(_difficulty_label(key)) for key in known)
    for key in known:
        label = _difficulty_label(key)
        rprint(f'  {label:<{width}}  {_record_text(records[key])}')


def update_record(difficulty, p, start_level, wins):
    """Save the run if it beats the difficulty's record; tell the player."""
    old = _records.get_records(RECORDS).get(difficulty)
    if wins > _records.get_score(old, 'wins'):
        _records.save_record(
            RECORDS,
            difficulty,
            {
                'wins': wins,
                'name': p.name,
                'style': p.style.public_name,
                'start_level': start_level,
                'level': p.level,
            },
        )
        text = _(' New record for {difficulty}!').format(
            difficulty=_difficulty_label(difficulty)
        )
        rprint(style(text, 'bold green'))
    elif old:
        rprint(
            _(' Record for {difficulty}: {record}').format(
                difficulty=_difficulty_label(difficulty), record=_record_text(old)
            )
        )


def play_ring():
    play_music(MUSIC['new_game'])
    cls()
    rprint(_(' ***Welcome to [bold]RING[/bold]***'))
    show_records()
    pak()
    attempts = ATTEMPTS
    difficulty = menu(
        [(_difficulty_label(key), key) for key, _mult in DIFFICULTIES],
        _('Choose the difficulty:'),
    )
    strength = dict(DIFFICULTIES)[difficulty]
    p = fighter_factory.new_custom_hcf()
    start_level = p.level
    wins = 0
    while attempts:
        opp = fighter_factory.from_exp_worth(
            p.get_exp_worth() * strength, max_lv=p.level + OPP_LV_MARGIN
        )
        if p.fight(opp[0], en_allies=opp[1:], hide_stats=strength >= 1.0):
            wins += 1
            p.level_up()
        else:
            attempts -= 1
            n = (yellow if attempts else red)(str(attempts))
            rprint(_(' Remaining attempts: {n}').format(n=n))
            pak()
    rprint(_(' You have reached level {lv}.').format(lv=cyan(str(p.level))))
    rprint(_(' Fights won: {n}.').format(n=wins))
    update_record(difficulty, p, start_level, wins)
    rprint(bold(_(' ***Game over***')))
    pak()
