"""Chocolate: a scripted seven-scene campaign, a homage to the Thai film (2008).

The hero, Zen, has a fixed level and never gains exp; she grows only through
the techniques and moves each scene teaches her. A lost fight costs nothing
but is counted, and the fight is replayed against a freshly built gang (so
weapons knocked away last time are back).
"""
from kf_lib.actors import fighter_factory as ff
from kf_lib.actors.human_controlled_fighter import HumanControlledFighter
from kf_lib.i18n import _, ngettext
from kf_lib.kung_fu import boosts as b
from kf_lib.kung_fu import styles, techniques
from kf_lib.kung_fu.techniques import Tech
from kf_lib.ui import cls, pak, rprint


ZEN_LEVEL = 12
ZEN_ATTS = (5, 10, 7, 5)  # strength, agility, speed, health

# mini-game-only techs (plain Techs: never offered on level-up in the main game)
MIGHTY_ELBOWS = Tech('Mighty Elbows', elbow_strike_mult=b.STRIKE_MULT2)
MIGHTY_KNEES = Tech('Mighty Knees', knee_strike_mult=b.STRIKE_MULT2)


class Zen(HumanControlledFighter):
    """Starts with the basic moves only and no techs; never levels up."""

    def set_rand_moves(self):
        pass

    def set_rand_techs(self, forced=False):
        pass


def _gang(name, style, lv, n=1, weapon=None):
    f = ff.new_f(name, style, lv, weapon=weapon, n=n)
    return f if isinstance(f, list) else [f]


class Scene:
    def __init__(self, title, techs, moves, fights):
        """fights: list of (make_opponents, zen_weapon) pairs fought in order;
        make_opponents() returns a fresh list, the first one being the leader."""
        self.title = title
        self.techs = techs
        self.moves = moves
        self.fights = fights


def _tech(name):
    return techniques.get_tech_obj(name)


def get_scenes():
    df = styles.DIRTY_FIGHTING.name
    return [
        Scene(
            _('Scene 1 - Teen Gang'),
            [_tech('Shadow of a Shadow'), _tech('Strong as an Ox')],
            ['Flying Kick'],
            [(lambda: _gang('Teen Thug', df, 1, n=4), None)],
        ),
        Scene(
            _('Scene 2 - Ice'),
            [_tech('Hurricane Legs'), _tech('Explosive Strikes')],
            ['Acrobatic Kick', 'Onslaught Kick'],
            [(lambda: _gang('Boss', df, 3, weapon='axe') + _gang('Worker', df, 1, n=5), None)],
        ),
        Scene(
            _('Scene 3 - Warehouse'),
            [_tech('Behind You All'), _tech('Environment Domination')],
            [],
            [
                (
                    lambda: _gang('Boss', df, 3)
                    + _gang('Worker', df, 1, n=3)
                    + _gang('Armed Worker', df, 1, n=4, weapon='stick'),
                    None,
                )
            ],
        ),
        Scene(
            _('Scene 4 - Meat'),
            [_tech('Flying Monkey and Golden Fox'), _tech('Anything Is a Weapon')],
            ['Energy Kick'],
            [
                (
                    lambda: _gang('Boss', df, 4, weapon='knife')
                    + _gang('Butcher', df, 1, n=5)
                    + _gang('Armed Butcher', df, 1, n=4, weapon='knife'),
                    None,
                )
            ],
        ),
        Scene(
            _('Scene 5 - Tension'),
            [MIGHTY_ELBOWS, MIGHTY_KNEES],
            ['Energy Elbow', 'Flying Knee', 'Shocking Knee'],
            [(lambda: _gang('Tough Thug', 'Muai Thai', 10, n=3), None)],
        ),
        Scene(
            _('Scene 6 - Katana'),
            [_tech('Flying Strikes'), _tech('Lightning-Fast Strikes')],
            ['Flying Elbow', 'Acrobatic Knee'],
            [
                (lambda: _gang('Twitching Fighter', styles.DRUNKARD_STYLE.name, 18), None),
                (
                    lambda: _gang('Boss', df, 12, weapon='sword')
                    + _gang('Swordsman', df, 8, n=3, weapon='sword'),
                    'sword',
                ),
            ],
        ),
        Scene(
            _('Scene 7 - Anger'),
            [_tech('Fist of Fury II'), _tech("Hero's Resilience")],
            ['Shocking Kick', 'Shocking Elbow'],
            [
                (
                    lambda: _gang('Gang Leader', df, 14, weapon='sword')
                    + _gang('Tough Thug', 'Muai Thai', 10, n=2)
                    + _gang('Thug', df, 3, n=4),
                    None,
                )
            ],
        ),
    ]


def new_zen():
    zen = Zen(name='Zen', style=styles.ZENS_STYLE, level=ZEN_LEVEL, atts_tuple=ZEN_ATTS)
    zen.gender = 'f'
    return zen


def play_scene(zen, scene):
    """Teach the scene's techs and moves, then fight until every fight is won.
    Return the number of lost fights."""
    zen.cls()
    zen.show(f'[bold]{scene.title}[/bold]\n')
    zen.learn_tech(*scene.techs)
    for m in scene.moves:
        zen.learn_move(m)
    zen.pak()
    defeats = 0
    for make_opponents, zen_weapon in scene.fights:
        if zen_weapon:
            zen.arm(zen_weapon)
            zen.cls()
            zen.show(_('Zen picks up a {weapon}.').format(weapon=zen.weapon.display_name))
            zen.pak()
        while True:
            opps = make_opponents()
            if zen_weapon:
                zen.arm(zen_weapon)
            else:
                zen.disarm()
            if zen.fight(opps[0], en_allies=opps[1:], hide_stats=False):
                break
            defeats += 1
    zen.disarm()
    return defeats


def play_chocolate():
    cls()
    rprint(_(' ***Welcome to [bold]Chocolate[/bold]***'))
    pak()
    zen = new_zen()
    defeats = 0
    for scene in get_scenes():
        defeats += play_scene(zen, scene)
    cls()
    rprint(_(' ***The End***'))
    if defeats:
        print(
            ngettext(
                ' Zen fought her way through, losing {n} fight on the way.',
                ' Zen fought her way through, losing {n} fights on the way.',
                defeats,
            ).format(n=defeats)
        )
    else:
        print(_(' Zen fought her way through without a single defeat!'))
    pak()
