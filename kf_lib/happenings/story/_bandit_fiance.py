import random

from ._base_story import BaseStory
from kf_lib.actors import fighter_factory
from kf_lib.actors.names import ROBBER_NICKNAMES
from kf_lib.i18n import _, tr_fighter_name


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
        t = _(
            'A coversation in {town}\'s tavern:'
            '\n{name}: "That old man\'s daughter is really pretty..."'
            '\n{name}\'s Henchman: "If you like her that much, boss, why not marry her?"'
            '\n{name}: "Hmm..."'
        ).format(town=g.town_name, name=tr_fighter_name(b.name))
        g.show(t)
        g.pak()

    def reward(self):
        g, p, b = self.game, self.player, self.boss
        p.gain_rep(self.reputation_reward)
        p.add_accompl('Beat Bandit Fiance')

    def scene1(self):
        g, p, b = self.game, self.player, self.boss
        t = _(
            '{p_name} meets an old man in the tavern. The old man looks very sad. '
            'It turns out that the infamous bandit {b_name} wants to marry the old man\'s '
            'beautiful daughter. The old man cannot refuse as {b_name} will likely kill '
            'him and take his daughter anyway.'
            '\n{p_name}: "Don\'t worry! When I was on Mount Wutai I learned the Buddhist Laws '
            'of Logic from the abbot. Now I can talk a man around even if he\'s hard as iron. '
            'I am sure {b_name} will listen."'
            '\nOld Man: "What great good fortune that I could meet you today!"'
        ).format(p_name=tr_fighter_name(p.name), b_name=tr_fighter_name(b.name))
        p.msg(t)

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        t = _(
            '{b_name}: "Old man, are you trying to make a fool of me? Where is your daughter?"'
            '\nOld Man: "Please, sir, have mercy..."'
            '\n{p_name}: "Wait, {b_name}, let us discuss this like civil men!"'
        ).format(p_name=tr_fighter_name(p.name), b_name=tr_fighter_name(b.name))
        p.msg(t)
        if p.fight(b):
            p.show(_('{name}: "Do you see now? You are not a good match for this girl."').format(
                name=tr_fighter_name(p.name)
            ))
            p.show(_('{name}: "Forgive me, master! You won\'t see me again."').format(
                name=tr_fighter_name(b.name)
            ))
            p.pak()
            self.reward()
        else:
            p.show(
                _('{name}: "It is no good, the police are coming! The people here are not '
                  'hospitable at all. It is time for {name} to move on to the next town!"')
                .format(name=tr_fighter_name(b.name))
            )
            p.pak()

        # end of the story
        self.end()
