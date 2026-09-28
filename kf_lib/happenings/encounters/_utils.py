import random

from kf_lib.actors import names
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.utils import rnd


CH_ESCAPE_CHANCES = (0.3, 0.4, 0.5, 0.6, 0.7)
FAILED_ESCAPE_BEATING = (3, 5)


def beating(p):
    p.show(_('{} fails to escape and gets a beating.').format(tr_fighter_name(p.name)))
    p.log(_("Fails to escape."))
    p.injure()
    p.pak()


def check_feeling_greedy(p):
    if rnd() <= p.feel_too_greedy:
        p.show(_('{} feels too greedy!').format(tr_fighter_name(p.name)))
        p.log(_("Feels too greedy."))
        p.pak()
        return True
    return False


def check_scary_fight(p, opp_to_self_pwr_ratio):
    if opp_to_self_pwr_ratio < 1.0 and 'cowardly' not in p.traits:
        return False
    if rnd() <= p.feel_too_scared * opp_to_self_pwr_ratio:
        p.show(_('{} feels too scared to fight!').format(tr_fighter_name(p.name)))
        p.log(_("Feels too scared to fight."))
        p.pak()
        return True
    return False


def escape(p):
    p.show(_('{} manages to get away.').format(tr_fighter_name(p.name)))
    p.log(_("Gets away."))
    p.pak()


def get_escape_chance(p):
    return random.choice(CH_ESCAPE_CHANCES) + p.escape_bonus


def set_up_weapon_fight(p, c):
    p.show(
        _('{}: "A fist fight carries no weight. Let\'s duel with blades."').format(
            tr_fighter_name(c.name)
        )
    )
    p.pak()
    c.choose_best_norm_wp()
    p.choose_best_norm_wp()


def try_enemy(p, en, chance):
    if rnd() <= chance:
        old_name = en.name.split()[0]
        en.name = p.game.get_new_name(random.choice(names.ROBBER_NICKNAMES))
        t = _(
            '{old}: "You\'ll regret messing with {new}! '
            'From now on, you\'d better watch your back!"'
        ).format(old=tr_fighter_name(old_name), new=tr_fighter_name(en.name))
        p.show(t)
        p.add_enemy(en)
        p.pak()


def try_escape(p, esc_chance):
    p.log(_("Attempts to escape."))
    if rnd() <= esc_chance:
        escape(p)
    else:
        beating(p)
