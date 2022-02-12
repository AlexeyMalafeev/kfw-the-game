import random

from ...actors import names
from ...utils._random import rnd

CH_ESCAPE_CHANCES = (0.3, 0.4, 0.5, 0.6, 0.7)


def beating(p):
    p.show(f"{p.name} fails to escape and gets a beating.")
    p.log("Fails to escape.")
    p.injure()
    p.pak()


def check_feeling_greedy(p):
    if rnd() <= p.feel_too_greedy:
        p.show(f"{p.name} feels too greedy!")
        p.log("Feels too greedy.")
        p.pak()
        return True


def check_scary_fight(p, ratio):
    if rnd() <= p.feel_too_scared * ratio:
        p.show(f"{p.name} feels too scared to fight!")
        p.log("Feels too scared to fight.")
        p.pak()
        return True


def escape(p):
    p.show(f"{p.name} manages to get away.")
    p.log("Gets away.")
    p.pak()


def get_escape_chance(p):
    return random.choice(CH_ESCAPE_CHANCES) + p.escape_bonus


def set_up_weapon_fight(p, c):
    p.show('{}: "A fist fight carries no weight. Let\'s duel with blades."'.format(c.name))
    p.pak()
    c.choose_best_norm_wp()
    p.choose_best_norm_wp()


def try_enemy(p, en, chance):
    if rnd() <= chance:
        old_name = en.name.split()[0]
        en.name = p.game.get_new_name(random.choice(names.ROBBER_NICKNAMES))
        t = (
            f"{old_name}: \"You'll regret messing with {en.name}! "
            "From now on, you'd better watch your back!\""
        )
        p.show(t)
        p.add_enemy(en)
        p.pak()


def try_escape(p, esc_chance):
    p.log("Attempts to escape.")
    if rnd() <= esc_chance:
        escape(p)
    else:
        beating(p)