import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.i18n import _, tr_fighter_name
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
        t = _(
            'Word of {name}\'s battle royale triumph reaches a reclusive master living '
            'in the mountains near {town}. A letter arrives, written in elegant '
            'script: "You have proven you can stand alone against many. But can you pass '
            'the Trial of Eight Gates? Come."'
        ).format(name=tr_fighter_name(p.name), town=g.town_name)
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
                _('{name}: "Few have passed the Trial. You have earned this."').format(
                    name=tr_fighter_name(self.boss.name)
                )
            )
            p.learn_tech(tech)
        else:
            p.gain_exp(100)

    def scene1(self):
        p, b = self.player, self.boss
        t = _(
            'A mountain courtyard. {name} sits motionless as eight disciples of eight '
            'different styles step into a circle drawn in the dust. '
            '{name}: "No weapons. No tricks. The Eight Gates do not open for the '
            'faint-hearted. BEGIN!"'
        ).format(name=tr_fighter_name(b.name))
        p.show(t)
        p.log(_('Takes part in the Trial of Eight Gates.'))
        p.pak()
        disciples = [
            fighter_factory.new_fighter(rndint(max(p.level - 2, 1), p.level))
            for _ in range(self.num_gates)
        ]
        if fight.free_for_all([p] + disciples, environment_allowed=False, items_allowed=False):
            p.show(
                _('One by one, the eight disciples fall. Finally, only {p_name} is left '
                  'standing in the circle. {b_name} slowly rises and bows.')
                .format(p_name=tr_fighter_name(p.name), b_name=tr_fighter_name(b.name))
            )
            p.log(_('Passes the Trial of Eight Gates!'))
            self.reward()
        else:
            p.show(
                _('{p_name} wakes up at the mountain gate, every bone aching. '
                  '{b_name}: "The Gates are still closed to you. Come back stronger... '
                  'in your next life."')
                .format(p_name=tr_fighter_name(p.name), b_name=tr_fighter_name(b.name))
            )
            p.log(_('Fails the Trial of Eight Gates.'))
        p.pak()
        self.end()
