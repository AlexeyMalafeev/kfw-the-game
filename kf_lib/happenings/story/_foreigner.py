import random

from ._base_story import BaseStory
from kf_lib.actors import fighter_factory
from kf_lib.constants import experience
from kf_lib.i18n import _, tr_fighter_name, tr_style_name


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
            _(
                'Rumor has it that {b_name}, a renowned martial artist from {country}, has '
                'arrived in {town} to defeat local masters and prove the superiority of '
                'his own fighting style, {style}.'
            ).format(
                b_name=tr_fighter_name(b.name),
                country=b.country,
                town=g.town_name,
                style=tr_style_name(b.style.public_name),
            )
        )
        g.show(t)
        g.pak()

    def reward(self):
        g, p, b = self.game, self.player, self.boss
        p.gain_rep(self.reputation_reward)
        p.add_accompl('Foreign Challenger')

    def scene1(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            _(
                'The people of {town} keep talking about the foreigner, {b_name}. He has '
                'already defeated some good fighters.'
            ).format(town=g.town_name, b_name=tr_fighter_name(b.name))
        )
        p.show(t)
        p.pak()

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        f = fighter_factory.new_fighter(5)
        p.spectate([b], [f])
        t = (
            _(
                '{b_name} has challenged some martial artists in {town}, yet again. Today '
                '{p_name} watched him fight, in a few of his \'friendly matches\', which '
                'didn\'t seem all that friendly. In the last fight, {b_name} defeated three '
                'opponents at once, injuring them badly. He is a formidable adversary... '
                '\nBy watching {b_name} fight {p_name} gained some valuable insights into '
                'the foreigner\'s technique.'
            ).format(
                b_name=tr_fighter_name(b.name),
                town=g.town_name,
                p_name=tr_fighter_name(p.name),
            )
        )
        p.show(t)
        p.gain_exp(random.randint(*experience.SPECTATE_FOREIGNER_EXP))
        p.pak()

    def scene3(self):
        g, p, b = self.game, self.player, self.boss
        av_friends = [f for f in p.friends if f not in g.players]
        if p.best_student:
            f = p.best_student
            f_st = _('{p_name}\'s best student {f_name}').format(
                p_name=tr_fighter_name(p.name), f_name=tr_fighter_name(f.name)
            )
        elif av_friends:
            f = random.choice(av_friends)
            f_st = _('{p_name}\'s friend {f_name}').format(
                p_name=tr_fighter_name(p.name), f_name=tr_fighter_name(f.name)
            )
        else:
            f = random.choice(list(g.masters.values()))
            f_st = _('{f_name} of {style}').format(
                f_name=tr_fighter_name(f.name), style=tr_style_name(f.style.public_name)
            )
        t = (
            _(
                '{p_name} finds out that {b_name} beat {f_st}! Can no one stop this '
                'arrogant foreigner?'
            ).format(
                p_name=tr_fighter_name(p.name),
                b_name=tr_fighter_name(b.name),
                f_st=f_st,
            )
        )
        p.show(t)
        if not p.is_human or g.yn(
            _('Challenge {b_name}?').format(b_name=tr_fighter_name(b.name))
        ):
            if p.fight(b, hide_stats=False, environment_allowed=False, items_allowed=False):
                p.show(
                    _(
                        '{p_name}: "It\'s not about styles. True strength is in the '
                        'fighter\'s heart."'
                    ).format(p_name=tr_fighter_name(p.name))
                )
                p.show(
                    _('The people of {town} are amazed at {p_name}\'s victory!').format(
                        town=g.town_name, p_name=tr_fighter_name(p.name)
                    )
                )
                p.pak()
                self.reward()
            else:
                p.msg(
                    _(
                        'Having proved his superiority, {b_name} leaves {town}.'
                    ).format(b_name=tr_fighter_name(b.name), town=g.town_name)
                )
                # todo get depressed after losing to the foreigner?
        # end of the story
        self.end()
