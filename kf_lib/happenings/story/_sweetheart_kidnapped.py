import random

from kf_lib.actors import fighter_factory
from kf_lib.actors.names import ROBBER_NICKNAMES
from kf_lib.i18n import _, tr_fighter_name
from ._base_story import BaseStory


class KidnappedSweetheartStory(BaseStory):
    min_level = 3
    max_level = 20

    reputation_reward = 25
    progress_reward = 5

    def test(self, player):
        return BaseStory.test(self, player) and player.sweetheart is not None

    def intro(self):
        g = self.game
        g.cls()
        b = self.boss = fighter_factory.new_convict()
        b.name = g.get_new_name(random.choice(ROBBER_NICKNAMES))
        g.register_fighter(b)
        p = self.player
        sw = p.sweetheart
        t = (
            _(
                '{p_name} returns home to find the door open and signs of a struggle. '
                'A note is pinned to the wall with a knife:'
                '\n"{p_name}! Your beloved {sw_name} is our guest now. If you ever want '
                'to see {sw_name} again, come to the old fish market and bring money. '
                'And no police!"\n— {b_name}'
            ).format(
                p_name=tr_fighter_name(p.name),
                sw_name=tr_fighter_name(sw.name),
                b_name=tr_fighter_name(b.name),
            )
        )
        g.show(t)
        g.pak()

    def reward(self):
        p = self.player
        p.gain_rep(self.reputation_reward)
        p.add_accompl('Rescued Sweetheart')
        p.romance_progress += self.progress_reward

    def check_sweetheart_gone(self):
        """The romance may have ended while the story was in progress."""
        if self.player.sweetheart is None:
            p = self.player
            p.msg(
                _(
                    '{p_name} never finds out what happened — the trail has gone cold.'
                ).format(p_name=tr_fighter_name(p.name))
            )
            self.end()
            return True
        return False

    def scene1(self):
        if self.check_sweetheart_gone():
            return
        p, b = self.player, self.boss
        sw = p.sweetheart
        t = (
            _(
                '{p_name} spends days asking around the docks and the market. Finally, an '
                'old fisherman whispers that {b_name}\'s gang has a hideout by the old '
                'fish market.'
                '\n{p_name}: "Hold on, {sw_name}. I am coming."'
            ).format(
                p_name=tr_fighter_name(p.name),
                b_name=tr_fighter_name(b.name),
                sw_name=tr_fighter_name(sw.name),
            )
        )
        p.msg(t)

    def scene2(self):
        if self.check_sweetheart_gone():
            return
        p, b = self.player, self.boss
        sw = p.sweetheart
        thugs = fighter_factory.new_thug(n=2)
        t = (
            _(
                'The old fish market at dusk. {b_name} and his thugs are waiting.'
                '\n{b_name}: "So the lovebird came after all! Get \'em, boys!"'
                '\n{sw_name}: "{p_name}!"'
            ).format(
                b_name=tr_fighter_name(b.name),
                sw_name=tr_fighter_name(sw.name),
                p_name=tr_fighter_name(p.name),
            )
        )
        p.msg(t)
        p.check_help()
        if p.fight(b, p.allies, thugs):
            p.show(
                _('{sw_name}: "I knew you would come for me!"').format(
                    sw_name=tr_fighter_name(sw.name)
                )
            )
            p.pak()
            self.reward()
        else:
            p.show(
                _(
                    'Beaten and barely conscious, {p_name} suddenly hears the guards '
                    'screaming... {sw_name} has broken free and driven the bandits off '
                    '— {sw_name} is a martial artist, after all.'
                    '\n{sw_name}: "You came for me, and that is what matters. But you '
                    'should practice more, my love."'
                ).format(
                    p_name=tr_fighter_name(p.name),
                    sw_name=tr_fighter_name(sw.name),
                )
            )
            p.log(
                _('{sw_name} frees herself from {b_name}\'s gang.').format(
                    sw_name=tr_fighter_name(sw.name), b_name=tr_fighter_name(b.name)
                )
            )
            p.pak()
        self.end()
