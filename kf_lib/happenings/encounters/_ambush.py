import random

from kf_lib.actors import fighter_factory
from kf_lib.i18n import _, ngettext, tr_fighter_name
from kf_lib.utils import rnd, rndint
from ._base_encounter import BaseEncounter
from ._utils import get_escape_chance, check_scary_fight, try_escape


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
        t = ngettext(
            '{name} is ambushed by his enemy {enemy} with {n} thug!!\n'
            '{enemy}: "Seize this fellow and give him a good beating!"',
            '{name} is ambushed by his enemy {enemy} with {n} thugs!!\n'
            '{enemy}: "Seize this fellow and give him a good beating!"',
            num_thugs,
        ).format(name=tr_fighter_name(p.name), enemy=tr_fighter_name(e.name), n=num_thugs)
        p.show(t)
        p.log(
            ngettext(
                'Is ambushed by {enemy} with {n} thug.',
                'Is ambushed by {enemy} with {n} thugs.',
                num_thugs,
            ).format(enemy=tr_fighter_name(self.e.name), n=num_thugs)
        )
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
                p.msg(
                    _('{name}: "Please forgive me! I swear you\'ll never see me again!"').format(
                        name=tr_fighter_name(e.name)
                    )
                )
                p.remove_enemy(e)
                p.gain_rep(REP_REFORM_ENEMY)
                p.add_accompl("Enemy Reformed")
