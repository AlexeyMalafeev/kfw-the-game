import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.kung_fu import techniques
from kf_lib.utils import rndint
from ._base_story import BaseStory


class EightGatesStory(BaseStory):
    """A reclusive master offers a secret technique to whoever survives the Trial
    of Eight Gates: eight disciples of eight styles, one circle, no weapons, no
    items. Only a proven battle-royale champion is invited."""

    min_level = 11
    max_level = 14

    num_gates = 8

    def test(self, player):
        return super().test(player) and 'Battle Royale Champion' in player.accompl

    def intro(self):
        g = self.game
        g.cls()
        p = self.player
        t = (
            f'Word of {p.name}\'s battle royale triumph reaches a reclusive master living '
            f'in the mountains near {g.town_name}. A letter arrives, written in elegant '
            f'script: "You have proven you can stand alone against many. But can you pass '
            f'the Trial of Eight Gates? Come."'
        )
        g.show(t)
        g.pak()
        name = g.get_new_name('Master')
        self.boss = b = fighter_factory.new_master_challenger(p.level + 2, name)
        g.register_fighter(b)

    def reward(self):
        p = self.player
        p.add_accompl('Eight Gates')
        learnable = [t for t in techniques.get_learnable_techs(p) if t not in p.techs]
        if learnable:
            tech = random.choice(learnable)
            self.player.show(
                f'{self.boss.name}: "Few have passed the Trial. You have earned this."'
            )
            p.learn_tech(tech)
        else:
            p.gain_exp(100)

    def scene1(self):
        p, b = self.player, self.boss
        t = (
            f'A mountain courtyard. {b.name} sits motionless as eight disciples of eight '
            f'different styles step into a circle drawn in the dust. '
            f'{b.name}: "No weapons. No tricks. The Eight Gates do not open for the '
            f'faint-hearted. BEGIN!"'
        )
        p.show(t)
        p.log('Takes part in the Trial of Eight Gates.')
        p.pak()
        disciples = [
            fighter_factory.new_fighter(rndint(max(p.level - 2, 1), p.level))
            for _ in range(self.num_gates)
        ]
        if fight.free_for_all([p] + disciples, environment_allowed=False, items_allowed=False):
            p.show(
                f'One by one, the eight disciples fall. Finally, only {p.name} is left '
                f'standing in the circle. {b.name} slowly rises and bows.'
            )
            p.log('Passes the Trial of Eight Gates!')
            self.reward()
        else:
            p.show(
                f'{p.name} wakes up at the mountain gate, every bone aching. '
                f'{b.name}: "The Gates are still closed to you. Come back stronger... '
                f'in your next life."'
            )
            p.log('Fails the Trial of Eight Gates.')
        p.pak()
        self.end()
