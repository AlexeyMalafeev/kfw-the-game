import random
from typing import List, Type

from kf_lib.kung_fu import styles
from kf_lib.utils import rnd, rndint


_all_stories = []


class BaseStory:
    min_level = None
    max_level = None

    def __init__(self, g, state=None, player=None, boss=None):
        self.game = g
        self.name = self.__class__.__name__
        self.state = state
        self.player = player
        self.boss = boss

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _all_stories.append(cls)

    def __repr__(self):
        return self.get_init_string()

    def advance(self):
        self.state += 1
        g = self.game
        p = self.player
        g.cls()
        g.show(p.get_p_info(), align=False)
        exec(f'self.scene{self.state}()')

    def check_hasnt_started(self):
        return self.state is None

    def delete_boss(self):
        self.game.unregister_fighter(self.boss)
        self.boss = None

    def end(self):
        self.state = -1
        if self.boss:
            self.delete_boss()
        self.player.current_story = None

    def get_init_string(self):
        if self.player:
            p_ref = self.game.get_fighter_ref(self.player)
        else:
            p_ref = None
        if self.boss:
            b_ref = self.game.get_fighter_ref(self.boss)
        else:
            b_ref = None
        return 'story.{}(g, state={!r}, player={}, boss={})'.format(
            self.__class__.__name__, self.state, p_ref, b_ref
        )

    def intro(self):
        pass

    def start(self, player):
        p = self.player = player
        p.current_story = self
        p.change_stat('num_stories', 1)
        self.state = 0
        self.intro()

    def test(self, player):
        p = player
        return self.min_level <= p.level <= self.max_level


def get_all_stories() -> List[Type[BaseStory]]:
    return _all_stories


# exp
DREAM1_EXP = 50
DREAM2_EXP = 100
DREAM3_EXP = 200

# money
BRIBE = 100

# numbers
OFFICIALS_BODYGUARDS = (3, 5)

# reputation
BEAT_FOREIGNER = 30
BRIBERY_REP_PENALTY = -5
RECOVER_TREASURES = 30


class NinjaTurtlesBaseStory(BaseStory):
    min_level = 12
    max_level = 15

    def intro(self):
        g = self.game
        g.cls()
        t = (
            'A sudden flash pierces the deep darkness of the night... Four figures appear, muscular and not quite '
            'human. They are wielding traditional Japanese weapons. Looking around in confusion, they speak in hushed '
            'tones, clearly deciding what to do next...'
        )
        g.show(t)
        g.pak()

    def reward(self):
        p = self.player
        p.add_accompl('TMNT')
        p.learn_tech(*list(styles.TURTLE_NUNJUTSU.techs.values()))

    def scene1(self):
        p = self.player
        p.write(
            f'{p.name} encounters the four teenage mutant ninja turtles travelling in time.'
        )
        p.pak()
        # p.choose_best_norm_wp()
        ens = fighter_factory.new_ninja_turtles()
        if p.fight(ens[0], en_allies=ens[1:], items_allowed=False):
            self.reward()

        # end of the story
        self.end()


class RenownedMaster(BaseStory):
    min_level = 14
    max_level = 16

    def intro(self):
        g, p = self.game, self.player
        g.cls()
        name = g.get_new_name(prefix='Master')
        b = self.boss = fighter_factory.new_master_challenger(p.level, name)
        g.register_fighter(b)
        t = (
            '{}, a renowned master of {} kung-fu from a remote province, comes to {} and stays at a local '
            'tavern.'.format(b.name, b.style.name, g.town_name)
        )
        g.msg(t)

    def reward(self):
        p = self.player
        p.add_accompl('Renowned Master')
        t = (
            'Having defeated such a strong opponent, {} gained an important insight into his own fighting '
            'technique.'.format(p.name)
        )
        p.write(t)
        p.choose_tech_to_upgrade()

    def scene1(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            '{p} meets {b}. {b}: "I feel that I have reached perfection in my kung-fu, {bs}. I have been looking for '
            'a worthy opponent for a very, very long time. I will be honored to test your famous {ps} '
            'kung-fu."'.format(p=p.name, b=b.name, bs=b.style.name, ps=p.style.name)
        )
        g.show(t)
        p.log(f'Challenged by {b.name}.')
        g.pak()
        if p.fight(b, environment_allowed=False, items_allowed=False):
            t = (
                '{}: "Indeed remarkable! What excellent skill. I thank you for showing me that I '
                'still have something to learn."'.format(b.name, p.name)
            )
            g.show(t)
            self.reward()
        else:
            g.show(f'{b.name}: "I am disappointed - yet again."')
        self.end()
        g.pak()


class StrangeDreamsBaseStory(BaseStory):
    min_level = 6
    max_level = 8

    def intro(self):
        g = self.game
        g.cls()
        g.show('Every so often one has some really unusual dreams...')
        g.pak()

    def reward(self):
        p = self.player
        p.add_accompl('Beat Self')
        p.gain_exp(DREAM3_EXP)
        p.pak()

    def scene1(self):
        p = self.player
        p.write(f'{p.name} has a strange dream...')
        p.choose_best_norm_wp()
        ens = fighter_factory.new_opponent(n=4, rand_atts_mode=0)
        for en in ens:
            en.arm('chopsticks')
        if p.spar(ens[0], en_allies=ens[1:]):
            p.gain_exp(DREAM1_EXP)
            p.pak()

    def scene2(self):
        p = self.player
        p.write(f'{p.name} has a strange dream...')
        p.pak()
        en = fighter_factory.new_monster(lv=p.level)
        en.name = 'Weird ' + en.name
        if p.spar(en):
            p.gain_exp(DREAM2_EXP)
            p.pak()

    def scene3(self):
        p = self.player
        p.write(f'{p.name} has a strange dream...')
        p.pak()
        en = fighter_factory.copy_fighter(p)
        en.__class__ = fighter_factory.Fighter
        if p.spar(en):
            self.reward()

        # end of the story
        self.end()


class TreasuresBaseStory(BaseStory):
    min_level = 8
    max_level = 10

    def intro(self):
        g = self.game
        g.cls()
        t = (
            'Everybody in {} talks about national treasures being stolen and sold to foreign buyers. Who could be '
            'responsible for such horrible crimes?'.format(g.town_name)
        )
        g.msg(t)
        self.boss = b = fighter_factory.new_official(g.get_new_name('Official'))
        g.register_fighter(b)

    def reward(self):
        p = self.player
        p.gain_rep(RECOVER_TREASURES)
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
            '{0} accidentally bumps into {1}. Although {0} apologizes, {1} is enraged. "Teach this fool a good '
            'lesson!" he orders his bodyguards. "Unless..." he looks at {0}, "...you want to pay a fine of {2} coins '
            'for insulting an official?"'.format(p.name, b.name, BRIBE)
        )
        g.show(t)
        if (not p.is_human or g.yn('Pay the bribe?')) and p.check_money(BRIBE):
            if rnd() <= p.feel_too_greedy:
                p.show(
                    '{} feels too greedy to pay this ridiculous "fine": "You are no better than a '
                    'robber!"'.format(p.name)
                )
                p.show(f'{b.name}: You...')
                p.log('Feels too greedy to pay the bribe.')
                p.pak()
            else:
                p.pay(BRIBE)
                g.show(f'{b.name}: "Good. Now get out of my sight!"')
                p.log(f'Pays a bribe to {b.name}.')
                p.gain_rep(BRIBERY_REP_PENALTY)
                p.pak()
                return
        num_en = rndint(*OFFICIALS_BODYGUARDS)
        enemies = [fighter_factory.new_bodyguard(weak=True) for i in range(num_en)]
        p.check_help(allies=False, master=False, school=False)
        if p.fight(enemies[0], en_allies=enemies[1:], af_option=True):
            t = (
                '{}: "I should hire better bodyguards... What idiots! You are lucky I don\'t have time to beat you '
                'up myself!" \n{}: "...Whatever..."'.format(b.name, p.name)
            )
            g.show(t)
        else:
            g.show(f'{b.name}: "That will teach you! Next time just pay.')
        g.pak()

    def scene3(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            '{p} accidentally overhears a conversation between {b} and some foreigner. {p} could swear he heard the '
            'words \'treasures\', \'foreign partners\' and \'good money\'. Could it be that {b} is somehow connected '
            'with national treasures being stolen? Too bad {p} lacks solid proof...'.format(
                p=p.name, b=b.name
            )
        )
        g.msg(t)

    def scene4(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            '{p} sees some suspicious-looking men carrying crates. {p}\'s intuition tells him something is fishy. He '
            'secretly follows them to find that they are taking the crates to a guarded warehouse. As {p} sneaks in, '
            'he sees that the crates are full of ancient treasures that have recently been stolen all over the '
            'country. \nSuddenly, {b} appears with his two elite bodyguards. \nSo it was him!.. He is behind all '
            'this!.. {p} barely has time to figure this out before {b}\'s thugs jump at him...'.format(
                p=p.name, b=b.name
            )
        )
        g.msg(t)
        # first fight
        enemies = fighter_factory.new_bodyguard(n=2)
        if p.fight(enemies[0], en_allies=enemies[1:], af_option=True):
            g.show('{}: "This can\'t be... They were supposed to..."'.format(b.name))
            g.pak()
            if p.fight(b):
                t = 'The police arrested {}... The people of {} are proud of {}!'.format(
                    b.name, g.town_name, p.name
                )
                g.show(t)
                self.reward()
            else:
                t = '''{b}: "What just happened?.."
Did {p} really lose to {b}?..
Of course, the crook disappears with all the treasures... Too bad {p} couldn\'t stop him.'''.format(
                    b=b.name, p=p.name
                )
                g.show(t)
        else:
            t = (
                'As {p} comes to, he realizes that {b} and his men have disappeared. They took all the treasures, '
                'too. But frankly, {p} is lucky to be alive...'.format(p=p.name, b=b.name)
            )
            g.show(t)
        g.pak()
        # end of the story
        self.end()
