import random

from ._base_story import BaseStory
from kf_lib.actors import fighter_factory
from kf_lib.utils import rndint_2d


class ForeignerStory(BaseStory):
    min_level = 9
    max_level = 12

    reputation_reward = 30

    def intro(self):
        g = self.game
        g.cls()
        b = self.boss = fighter_factory.new_foreigner()
        g.register_fighter(b)
        t = (
            f'Rumor has it that {b.name}, a renowned martial artist from {b.country}, has arrived '
            f'in {g.town_name} to defeat local masters and prove the superiority of his own '
            f'fighting style, {b.style.name}.'
        )
        g.show(t)
        g.pak()

    def reward(self):
        g, p, b = self.game, self.player, self.boss
        p.gain_rep(self.reputation_reward)
        p.add_accompl('Foreign Challenger')

    def scene1(self):
        g, b = self.game, self.boss
        t = (
            f'The people of {g.town_name} keep talking about the foreigner, {b.name}. He has '
            f'already defeated some good fighters.'
        )
        g.show(t)
        g.pak()

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        f = fighter_factory.new_fighter(5)
        p.spectate([b], [f])
        t = (
            f'{b.name} has challenged some martial artists in {g.town_name}, yet again. Today '
            f'{p.name} watched him fight, in a few of his \'friendly matches\', which didn\'t '
            f'seem all that friendly. In the last fight, {b.name} defeated three opponents at '
            f'once, injuring them badly. He is a formidable adversary... '
            f'\nBy watching {b.name} fight {p.name} gained some valuable insights into the '
            f'foreigner\'s technique.'
        )
        g.show(t)
        base_exp = 10
        p.gain_exp(rndint_2d(base_exp, base_exp * 3))
        g.pak()

    def scene3(self):
        g, p, b = self.game, self.player, self.boss
        av_friends = [f for f in p.friends if f not in g.players]
        if p.best_student:
            f = p.best_student
            f_st = f'{p.name}\'s best student {f.name}'
        elif av_friends:
            f = random.choice(av_friends)
            f_st = f'{p.name}\'s friend {f.name}'
        else:
            f = random.choice(list(g.masters.values()))
            f_st = f'{f.name} of {f.style.name}'
        t = (
            f'{p.name} finds out that {b.name} beat {f_st}! Can no one stop this arrogant '
            f'foreigner?'
        )
        g.show(t)
        if not p.is_human or g.yn(f'Challenge {b.name}?'):
            if p.fight(b, hide_stats=False, environment_allowed=False, items_allowed=False):
                g.show(
                    f'{p.name}: "It\'s not about styles. True strength is in the fighter\'s heart."'
                )
                g.show(f'The people of {g.town_name} are amazed at {p.name}\'s victory!')
                g.pak()
                self.reward()
            else:
                g.msg(f'Having proved his superiority, {b.name} leaves {g.town_name}.')
                # todo get depressed after losing to the foreigner?
        # end of the story
        self.end()
