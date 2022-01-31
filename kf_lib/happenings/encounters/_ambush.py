import random

from ...actors import fighter_factory
from .. import events
from ._base_encounter import BaseEncounter
from ._utils import get_escape_chance, check_scary_fight, try_escape
from ...utils.utilities import rnd, rndint


CH_ENEMY_REPENTS = 0.5
LINES_ENEMY = (
    "Does it hurt? I'll KILL you next time!",
    "That'll teach ya!",
    "What's wrong? Can't get up, huh?",
    "This is what happens if you mess with me!",
    "You are much weaker than I thought!",
)
NUM_AMBUSH_THUGS = (2, 4)
REP_REFORM_ENEMY = 10


class Ambush(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.e = None
        self.thugs = []
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return self.p.enemies and rnd() <= len(self.p.enemies) * 0.02

    def run(self):
        p = self.player
        self.e = random.choice(p.enemies)
        num_thugs = rndint(NUM_AMBUSH_THUGS[0], NUM_AMBUSH_THUGS[1])
        self.thugs = fighter_factory.new_thug(weak=True, n=num_thugs)
        p.show(
            f"{p.name} is ambushed by his enemy {self.e.name} with {num_thugs} thugs!!"
        )
        p.log(f"Is ambushed by {self.e.name} with {num_thugs} thugs.")
        opp = [self.e] + self.thugs
        opp_strength = p.get_rel_strength(*opp)
        esc_chance = get_escape_chance(p)
        if p.fight_or_run(opp_strength, esc_chance) and not check_scary_fight(p, opp_strength[0]):
            self.do_fight()
        else:
            try_escape(p, esc_chance)

    def do_fight(self):
        p = self.player
        p.check_help()
        if p.fight(self.e, p.allies, self.thugs):
            events.crime_down(p.game)
            if rnd() <= CH_ENEMY_REPENTS:
                p.msg(
                    '{}: "Please forgive me! I swear you\'ll never see me again!"'.format(
                        self.e.name
                    )
                )
                p.remove_enemy(self.e)
                p.gain_rep(REP_REFORM_ENEMY)
                p.add_accompl("Enemy Reformed")
        else:
            p.msg(f'{self.e.name}: "{random.choice(LINES_ENEMY)}"')
