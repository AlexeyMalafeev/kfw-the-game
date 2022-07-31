from . import BaseStory
from kf_lib.actors import fighter_factory
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
            f'Everybody in {g.town_name} talks about national treasures being stolen and sold to '
            f'foreign buyers. Who could be responsible for such horrible crimes?'
        )
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
            f'{p.name} sees a pompous official surrounded by his bodyguards. As they walk down '
            f'{g.town_name}\'s main street, they push walkers-by around and otherwise behave '
            'rudely.\n'
            'Some old man: "Fear not officials, except those who officiate over you! This is '
            f'{b.name}. Too bad he\'s so corrupt and arrogant... He\'s a shame to our town!"'
        )
        g.msg(t)

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            f'{p.name} accidentally bumps into {b.name}. Although {p.name} apologizes, '
            f'{b.name} is enraged. "Teach this fool a good lesson!" he orders his bodyguards. '
            f'"Unless..." he looks at {p.name}, "...you want to pay a fine of {self.bribe_amount} '
            f'coins for insulting an official?"'
        )
        g.show(t)
        if (not p.is_human or g.yn('Pay the bribe?')) and p.check_money(self.bribe_amount):
            if rnd() <= p.feel_too_greedy:
                p.show(
                    f'{p.name} feels too greedy to pay this ridiculous "fine": "You are no better '
                    f'than a robber!"'
                )
                p.show(f'{b.name}: You...')
                p.log('Feels too greedy to pay the bribe.')
                p.pak()
            else:
                p.pay(self.bribe_amount)
                g.show(f'{b.name}: "Good. Now get out of my sight!"')
                p.log(f'Pays a bribe to {b.name}.')
                p.gain_rep(self.bribery_reputation_penalty)
                p.pak()
                return
        num_en = rndint(*self.num_bodyguards)
        enemies = [fighter_factory.new_bodyguard(weak=True) for _ in range(num_en)]
        p.check_help(allies=False, master=False, school=False)
        if p.fight(enemies[0], en_allies=enemies[1:], af_option=True):
            t = (
                f'{b.name}: "I should hire better bodyguards... What idiots! You are lucky I '
                f'don\'t have time to beat you up myself!" \n{p.name}: "..."'
            )
            g.show(t)
        else:
            g.show(f'{b.name}: "That will teach you! Next time just pay.')
        g.pak()

    def scene3(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            f'{p.name} accidentally overhears a conversation between {b.name} and some foreigner. '
            f'{p.name} could swear he heard the words \'treasures\', \'foreign partners\' and '
            f'\'good money\'. Could it be that {b.name} is somehow connected with national '
            f'treasures being stolen? Too bad {p.name} lacks solid proof...'
        )
        g.show(t)
        g.pak()

    def scene4(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            f'{p.name} sees some suspicious-looking men carrying crates. {p.name}\'s intuition '
            f'tells him something is fishy. He secretly follows them to find that they are taking '
            f'the crates to a guarded warehouse. As {p.name} sneaks in, he sees that the crates '
            f'are full of ancient treasures that have recently been stolen all over the country. '
            f'\nSuddenly, {b.name} appears with his two elite bodyguards. '
            f'\nSo it was him all along!.. {b.name} is behind all this!.. {p.name} barely has '
            f'time to figure this out before {b.name}\'s thugs jump at him...'
        )
        g.show(t)
        g.pak()
        # first fight
        enemies = fighter_factory.new_bodyguard(n=2)
        if p.fight(enemies[0], en_allies=enemies[1:], af_option=True):
            g.show(f'{b.name}: "This can\'t be... They were supposed to..."')
            g.pak()
            if p.fight(b):
                t = (
                    f'The police arrested {b.name}... The people of {g.town_name} are proud of '
                    f'{p.name}!'
                )
                g.show(t)
                g.pak()
                self.reward()
            else:
                t = (
                    f'{b.name}: "I always knew you are no match for my heavenly kung-fu!"'
                    f'\nDid {p.name} really lose to {b.name}?..'
                    f'\nNeedless to say, the crook disappears with all the treasures... '
                    f'Too bad even {p.name} couldn\'t stop him.'
                )
                g.show(t)
        else:
            t = (
                f'As {p.name} comes to, he realizes that {b.name} and his men have disappeared. '
                f'They took all the treasures, too. {p.name} is lucky to be alive...'
            )
            g.show(t)
        g.pak()

        # end of the story
        self.end()
