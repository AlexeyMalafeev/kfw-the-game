"""RING: an endless arena ladder; win to level up, three lost fights end it."""
from kf_lib.actors import fighter_factory
from kf_lib.i18n import _
from kf_lib.ui import MUSIC, bold, cls, cyan, menu, pak, play_music, red, rprint, yellow


ATTEMPTS = 3
# opponents' level cap above the player's: high enough that some group always
# matches the player's exp worth (a fixed cap of 20 hung the search at lv ~40)
OPP_LV_MARGIN = 5


def play_ring():
    play_music(MUSIC['new_game'])
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
        opp = fighter_factory.from_exp_worth(
            p.get_exp_worth() * difficulty, max_lv=p.level + OPP_LV_MARGIN
        )
        if p.fight(opp[0], en_allies=opp[1:], hide_stats=difficulty >= 1.0):
            p.level_up()
        else:
            attempts -= 1
            n = (yellow if attempts else red)(str(attempts))
            rprint(_(' Remaining attempts: {n}').format(n=n))
            pak()
    rprint(_(' You have reached level {lv}.').format(lv=cyan(str(p.level))))
    rprint(bold(_(' ***Game over***')))
    pak()
