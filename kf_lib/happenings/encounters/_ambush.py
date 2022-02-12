import random

from ...actors import fighter_factory
from ._base_encounter import BaseEncounter
from ._utils import get_escape_chance, check_scary_fight, try_escape
from ...utils._random import rnd, rndint

CH_ENEMY_REPENTS = 0.5
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
        e = self.e = random.choice(p.enemies)
        num_thugs = rndint(NUM_AMBUSH_THUGS[0], NUM_AMBUSH_THUGS[1])
        self.thugs = fighter_factory.new_thug(weak=True, n=num_thugs)
        p.show(
            f"{p.name} is ambushed by his enemy {self.e.name} with {num_thugs} thugs!!\n"
            f'{e.name}: "Seize this fellow and give him a good beating!"'
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
        e = self.e
        p.check_help()
        if p.fight(e, p.allies, self.thugs):
            p.game.crime_down()
            if rnd() <= CH_ENEMY_REPENTS:
                p.msg(f'{e.name}: "Please forgive me! I swear you\'ll never see me again!"')
                p.remove_enemy(e)
                p.gain_rep(REP_REFORM_ENEMY)
                p.add_accompl("Enemy Reformed")
