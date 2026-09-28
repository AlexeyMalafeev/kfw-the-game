from ._base_story import BaseStory
from kf_lib.actors import fighter_factory
from kf_lib.i18n import _, ngettext, tr_fighter_name
from kf_lib.utils import rnd, rndint


class StolenTreasuresStory(BaseStory):
    min_level = 8
    max_level = 10

    bribe_amount = 100
    bribery_reputation_penalty = -5
    num_bodyguards = (3, 5)
    reputation_reward = 30

    def intro(self):
        g = self.game
        g.cls()
        t = (
            _('Everybody in {town} talks about national treasures being stolen and '
              'sold to foreign buyers. Who could be responsible for such horrible '
              'crimes?')
        ).format(town=g.town_name)
        g.show(t)
        g.pak()
        self.boss = b = fighter_factory.new_official(g.get_new_name('Official'))
        g.register_fighter(b)

    def reward(self):
        p = self.player
        p.gain_rep(self.reputation_reward)
        p.add_accompl('National Treasures')

    def scene1(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            _('{name} sees a pompous official surrounded by his bodyguards. As they '
              'walk down {town}\'s main street, they push walkers-by around and '
              'otherwise behave rudely.\n'
              'Some old man: "Fear not officials, except those who officiate over '
              'you! This is {boss}. Too bad he\'s so corrupt and arrogant... He\'s a '
              'shame to our town!"')
        ).format(
            name=tr_fighter_name(p.name), town=g.town_name, boss=tr_fighter_name(b.name)
        )
        p.msg(t)

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            ngettext(
                '{name} accidentally bumps into {boss}. Although {name} apologizes, '
                '{boss} is enraged. "Teach this fool a good lesson!" he orders his '
                'bodyguards. "Unless..." he looks at {name}, "...you want to pay a '
                'fine of {bribe} coin for insulting an official?"',
                '{name} accidentally bumps into {boss}. Although {name} apologizes, '
                '{boss} is enraged. "Teach this fool a good lesson!" he orders his '
                'bodyguards. "Unless..." he looks at {name}, "...you want to pay a '
                'fine of {bribe} coins for insulting an official?"',
                self.bribe_amount,
            )
        ).format(
            name=tr_fighter_name(p.name),
            boss=tr_fighter_name(b.name),
            bribe=self.bribe_amount,
        )
        p.show(t)
        if (not p.is_human or g.yn(_('Pay the bribe?'))) and p.check_money(
            self.bribe_amount
        ):
            if rnd() <= p.feel_too_greedy:
                p.show(
                    _('{name} feels too greedy to pay this ridiculous "fine": "You are '
                      'no better than a robber!"').format(
                        name=tr_fighter_name(p.name)
                    )
                )
                p.show(_('{boss}: You...').format(boss=tr_fighter_name(b.name)))
                p.log(_('Feels too greedy to pay the bribe.'))
                p.pak()
            else:
                p.pay(self.bribe_amount)
                g.show(
                    _('{boss}: "Good. Now get out of my sight!"').format(
                        boss=tr_fighter_name(b.name)
                    )
                )
                p.log(
                    _('Pays a bribe to {boss}.').format(boss=tr_fighter_name(b.name))
                )
                p.gain_rep(self.bribery_reputation_penalty)
                p.pak()
                return
        num_en = rndint(*self.num_bodyguards)
        enemies = [fighter_factory.new_bodyguard(weak=True) for _ in range(num_en)]
        p.check_help(allies=False, master=False, school=False)
        if p.fight(enemies[0], en_allies=enemies[1:], af_option=True):
            t = (
                _('{boss}: "I should hire better bodyguards... What idiots! You are '
                  'lucky I don\'t have time to beat you up myself!" \n{name}: "..."')
            ).format(boss=tr_fighter_name(b.name), name=tr_fighter_name(p.name))
            p.show(t)
        else:
            p.show(
                _('{boss}: "That will teach you! Next time just pay.').format(
                    boss=tr_fighter_name(b.name)
                )
            )
        p.pak()

    def scene3(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            _('{name} accidentally overhears a conversation between {boss} and some '
              'foreigner. {name} could swear he heard the words \'treasures\', '
              '\'foreign partners\' and \'good money\'. Could it be that {boss} is '
              'somehow connected with national treasures being stolen? Too bad {name} '
              'lacks solid proof...')
        ).format(name=tr_fighter_name(p.name), boss=tr_fighter_name(b.name))
        p.show(t)
        p.pak()

    def scene4(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            _('{name} sees some suspicious-looking men carrying crates. {name}\'s '
              'intuition tells him something is fishy. He secretly follows them to '
              'find that they are taking the crates to a guarded warehouse. As {name} '
              'sneaks in, he sees that the crates are full of ancient treasures that '
              'have recently been stolen all over the country. '
              '\nSuddenly, {boss} appears with his two elite bodyguards. '
              '\nSo it was him all along!.. {boss} is behind all this!.. {name} '
              'barely has time to figure this out before {boss}\'s thugs jump at '
              'him...')
        ).format(name=tr_fighter_name(p.name), boss=tr_fighter_name(b.name))
        p.show(t)
        p.pak()
        # first fight
        enemies = fighter_factory.new_bodyguard(n=2)
        if p.fight(enemies[0], en_allies=enemies[1:], af_option=True):
            p.show(
                _('{boss}: "This can\'t be... They were supposed to..."').format(
                    boss=tr_fighter_name(b.name)
                )
            )
            p.pak()
            if p.fight(b):
                t = (
                    _('The police arrested {boss}... The people of {town} are proud '
                      'of {name}!')
                ).format(
                    boss=tr_fighter_name(b.name),
                    town=g.town_name,
                    name=tr_fighter_name(p.name),
                )
                p.show(t)
                p.pak()
                self.reward()
            else:
                t = (
                    _('{boss}: "I always knew you are no match for my heavenly '
                      'kung-fu!"'
                      '\nDid {name} really lose to {boss}?..'
                      '\nNeedless to say, the crook disappears with all the '
                      'treasures... Too bad even {name} couldn\'t stop him.')
                ).format(boss=tr_fighter_name(b.name), name=tr_fighter_name(p.name))
                p.show(t)
        else:
            t = (
                _('As {name} comes to, he realizes that {boss} and his men have '
                  'disappeared. They took all the treasures, too. {name} is lucky to '
                  'be alive...')
            ).format(name=tr_fighter_name(p.name), boss=tr_fighter_name(b.name))
            p.show(t)
        p.pak()

        # end of the story
        self.end()
