import random

from ._base_story import BaseStory
from kf_lib.actors import fighter_factory
from kf_lib.actors.names import ROBBER_NICKNAMES


class BanditFianceStory(BaseStory):
    min_level = 6
    max_level = 9

    reputation_reward = 25

    def intro(self):
        g = self.game
        g.cls()
        b = self.boss = fighter_factory.new_convict()
        b.name = g.get_new_name(random.choice(ROBBER_NICKNAMES))
        g.register_fighter(b)
        t = (
            f'A coversation in {g.town_name}\'s tavern:'
            f'\n{b.name}: "That old man\'s daughter is really pretty..."'
            f'\n{b.name}\'s Henchman: "If you like her that much, boss, why not marry her?"'
            f'\n{b.name}: "Hmm..."'
        )
        g.show(t)
        g.pak()

    def reward(self):
        g, p, b = self.game, self.player, self.boss
        p.gain_rep(self.reputation_reward)
        p.add_accompl('Beat Bandit Fiance')

    def scene1(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            f'{p.name} meets an old man in the tavern. The old man looks very sad. '
            f'It turns out that the infamous bandit {b.name} wants to marry the old man\'s '
            f'beautiful daughter. The old man cannot refuse as {b.name} will likely kill '
            'him and take his daughter anyway.'
            f'\n{p.name}: "Don\'t worry! When I was on Mount Wutai I learned the Buddhist Laws '
            'of Logic from the abbot. Now I can talk a man around even if he\'s hard as iron. '
            f'I am sure {b.name} will listen."'
            f'\nOld Man: "What great good fortune that I could meet you today!"'
        )
        p.msg(t)

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            f'{b.name}: "Old man, are you trying to make a fool of me? Where is your daughter?"'
            f'\nOld Man: "Please, sir, have mercy..."'
            f'\n{p.name}: "Wait, {b.name}, let us discuss this like civil men!"'
        )
        p.msg(t)
        if p.fight(b):
            p.show(f'{p.name}: "Do you see now? You are not a good match for this girl."')
            p.show(f'{b.name}: "Forgive me, master! You won\'t see me again."')
            p.pak()
            self.reward()
        else:
            p.show(
                f'{b.name}: "It is no good, the police are coming! The people here are not '
                f'hospitable at all. It is time for {b.name} to move on to the next town!"'
            )
            p.pak()

        # end of the story
        self.end()
