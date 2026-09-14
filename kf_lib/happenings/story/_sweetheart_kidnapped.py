import random

from kf_lib.actors import fighter_factory
from kf_lib.actors.names import ROBBER_NICKNAMES
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
            f'{p.name} returns home to find the door open and signs of a struggle. '
            f'A note is pinned to the wall with a knife:'
            f'\n"{p.name}! Your beloved {sw.name} is our guest now. If you ever want '
            f'to see {sw.name} again, come to the old fish market and bring money. '
            f'And no police!"\n— {b.name}'
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
            p.msg(f'{p.name} never finds out what happened — the trail has gone cold.')
            self.end()
            return True
        return False

    def scene1(self):
        if self.check_sweetheart_gone():
            return
        p, b = self.player, self.boss
        sw = p.sweetheart
        t = (
            f'{p.name} spends days asking around the docks and the market. Finally, an '
            f'old fisherman whispers that {b.name}\'s gang has a hideout by the old '
            f'fish market.'
            f'\n{p.name}: "Hold on, {sw.name}. I am coming."'
        )
        p.msg(t)

    def scene2(self):
        if self.check_sweetheart_gone():
            return
        p, b = self.player, self.boss
        sw = p.sweetheart
        thugs = fighter_factory.new_thug(n=2)
        t = (
            f'The old fish market at dusk. {b.name} and his thugs are waiting.'
            f'\n{b.name}: "So the lovebird came after all! Get \'em, boys!"'
            f'\n{sw.name}: "{p.name}!"'
        )
        p.msg(t)
        p.check_help()
        if p.fight(b, p.allies, thugs):
            p.show(f'{sw.name}: "I knew you would come for me!"')
            p.pak()
            self.reward()
        else:
            p.show(
                f'Beaten and barely conscious, {p.name} suddenly hears the guards '
                f'screaming... {sw.name} has broken free and driven the bandits off '
                f'— {sw.name} is a martial artist, after all.'
                f'\n{sw.name}: "You came for me, and that is what matters. But you '
                f'should practice more, my love."'
            )
            p.log(f'{sw.name} frees herself from {b.name}\'s gang.')
            p.pak()
        self.end()
