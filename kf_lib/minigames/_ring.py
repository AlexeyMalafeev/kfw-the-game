"""RING: an endless arena ladder; win to level up, three lost fights end it."""
from kf_lib.actors import fighter_factory
from kf_lib.i18n import _
from kf_lib.ui import cls, menu, pak, rprint


ATTEMPTS = 3


def play_ring():
    cls()
    rprint(_(' ***Welcome to [bold]RING[/bold]***'))
    pak()
    attempts = ATTEMPTS
    difficulty = menu(
        [(_('easy'), 0.9), (_('normal'), 1.0), (_('hard'), 1.1), (_('extreme'), 1.2)],
        _('Choose the difficulty:'),
    )
    p = fighter_factory.new_custom_hcf()
    while attempts:
        opp = fighter_factory.from_exp_worth(p.get_exp_worth() * difficulty)
        if p.fight(opp[0], en_allies=opp[1:], hide_stats=difficulty >= 1.0):
            p.level_up()
        else:
            attempts -= 1
            print(_(' Remaining attempts: {n}').format(n=attempts))
            pak()
    print(_(' You have reached level {lv}.').format(lv=p.level))
    print(_(' ***Game over***'))
    pak()
