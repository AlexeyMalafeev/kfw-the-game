#! python3


import random


from . import moves
from .utilities import *


all_weapons = {}


class Weapon(object):
    wp_type = 'n/a'

    def __init__(self, name, dfs_bonus, wp_moves):
        self.name = name
        self.dfs_bonus = 1.0 + dfs_bonus
        self.moves = [moves.get_move_obj(m) for m in wp_moves]
        dfs = float_to_pcnt(dfs_bonus)
        pwr_min = min(m.power for m in self.moves)
        pwr_max = max(m.power for m in self.moves)
        pwr = mean([m.power for m in self.moves])
        acc_min = min(m.accuracy for m in self.moves)
        acc_max = max(m.accuracy for m in self.moves)
        acc = mean([m.accuracy for m in self.moves])
        self.atk_mean = mean((pwr, acc)) / 100
        atk = float_to_pcnt(self.atk_mean)
        rng_min = min(m.distance for m in self.moves)
        rng_max = max(m.distance for m in self.moves)
        self.descr = '(Pwr:{}-{}  Acc:{}-{}  Rng:{}-{}  Dfs:{})'.format(
            pwr_min, pwr_max, acc_min, acc_max, rng_min, rng_max, dfs
        )
        self.descr_short = '({}|{})'.format(atk, dfs)
        all_weapons[self.name] = self

    def __repr__(self):
        return '{}({!r}, {}, ({},))'.format(
            self.__class__.__name__,
            self.name,
            self.dfs_bonus,
            ', '.join((repr(m.name) for m in self.moves)),
        )

    def __str__(self):
        return '{} {}'.format(self.name, self.descr)

    def get_exp_mult(self):
        return 1.0 + mean((self.dfs_bonus, self.atk_mean))


class NormalWeapon(Weapon):
    wp_type = 'normal'


class ImprovisedWeapon(Weapon):
    wp_type = 'improvised'


class RobberWeapon(Weapon):
    wp_type = 'robber'


class PoliceWeapon(Weapon):
    wp_type = 'police'


_NW = NormalWeapon
NORMAL_WEAPONS = (
    _NW('pair of swords', 0.5, ('Pair of Swords Slash', 'Pair of Swords Stab')),
    _NW('saber', 0.35, ('Saber Slash', 'Saber Thrust')),
    _NW('spear', 0.3, ('Long Spear Thrust', 'Spear Thrust')),
    _NW('staff', 0.45, ('Staff Strike',)),
    _NW('sword', 0.4, ('Sword Slash', 'Sword Thrust')),
)

_IW = ImprovisedWeapon
IMPROVISED_WEAPONS = (
    _IW('fan', 0.25, ('Fan Strike',)),
    _IW('chopsticks', 0.2, ('Chopsticks Thrust',)),
    _IW(
        'broom',
        0.4,
        (
            'Broom Strike',
            'Broom Thrust',
        ),
    ),
    _IW(
        'stick',
        0.35,
        (
            'Stick Strike',
            'Stick Thrust',
        ),
    ),
    _IW(
        'pole',
        0.25,
        (
            'Pole Strike',
            'Pole Thrust',
        ),
    ),
    _IW(
        'umbrella',
        0.35,
        (
            'Pole Strike',
            'Pole Thrust',
        ),
    ),
    _IW('bench', 0.25, ('Bench Smash',)),
    _IW('chair', 0.3, ('Chair Smash',)),
    _IW('guqin', 0.25, ('Guqin Smash',)),
    _IW('hammer', 0.2, ('Hammer Smash', 'Hammer Strike')),
    _IW('cloth', 0.2, ('Cloth Whip',)),
    _IW('rope', 0.25, ('Rope Whip',)),
    _IW('chain', 0.25, ('Chain Whip',)),
)

_RW = RobberWeapon
ROBBER_WEAPONS = (
    _RW('axe', 0.3, ('Axe Chop', 'Axe Slash')),
    _RW('bludgeon', 0.35, ('Bludgeon Smash', 'Bludgeon Strike')),
    _RW('knife', 0.4, ('Knife Stab', 'Knife Slash')),
)

POLICE_WEAPONS = (PoliceWeapon('baton', 0.4, ('Baton Smash', 'Baton Strike')),)

ALL_WEAPONS_LIST = list(all_weapons.values())
ALL_WEAPONS_SET = set(all_weapons.values())

WEAPON_TYPES = {}
for w in ALL_WEAPONS_LIST:
    if w.wp_type in WEAPON_TYPES:
        WEAPON_TYPES[w.wp_type].append(w)
    else:
        WEAPON_TYPES[w.wp_type] = [w]


def get_rnd_wp_by_type(wp_type):
    """Return random weapon name by type."""
    return random.choice(WEAPON_TYPES[wp_type])


def get_wp(weapon_name):
    """Return Weapon instance."""
    return all_weapons[weapon_name]
