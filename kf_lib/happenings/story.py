import random

from kf_lib.actors import fighter_factory
from kf_lib.actors.names import ROBBER_NICKNAMES
from kf_lib.kung_fu import styles
from kf_lib.utils import rnd, rndint


# todo refactor story into a package
# constants
# required levels
# the last element in range is not included; todo refactor REQ_LV
# todo this is bad design, factor REQ_LV with story classes
REQ_LV = {
    'BanditFianceStory': range(6, 10),
    'ForeignerStory': range(10, 13),
    'NinjaTurtlesStory': range(13, 16),
    'RenownedMaster': range(14, 17),
    'StrangeDreamsStory': range(6, 9),
    'TreasuresStory': range(8, 11),
}

# exp
DREAM1_EXP = 50
DREAM2_EXP = 100
DREAM3_EXP = 200

# money
BRIBE = 100

# numbers
OFFICIALS_BODYGUARDS = (3, 5)

# reputation
BEAT_BANDIT_FIANCE = 25
BEAT_FOREIGNER = 30
BRIBERY_REP_PENALTY = -5
RECOVER_TREASURES = 30


class Story(object):
    def __init__(self, g, state=None, player=None, boss=None):
        self.game = g
        self.name = self.__class__.__name__
        self.state = state
        self.player = player
        self.boss = boss
        self.required_lv = REQ_LV[self.name]

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
        return p.level in self.required_lv


class BanditFianceStory(Story):
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
        p.gain_rep(BEAT_BANDIT_FIANCE)
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
        g.msg(t)

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            f'{b.name}: "Old man, are you trying to make a fool of me? Where is your daughter?"'
            f'\nOld Man: "Please, sir, have mercy..."'
            f'\n{p.name}: "Wait, {b.name}, let us discuss this like civil men!"'
        )
        g.msg(t)
        if p.fight(b):
            g.show(f'{p.name}: "Do you see now? You are not a good match for this girl."')
            g.show(f'{b.name}: "Forgive me, master! You won\'t see me again."')
            g.pak()
            self.reward()
        else:
            g.msg(f'{b.name}: "It is no good, the police are coming! The people here are not'
                  f'hospitable at all. It is time for {b.name} to move on to the next town!"')
        # end of the story
        self.end()


class ForeignerStory(Story):
    def intro(self):
        g = self.game
        g.cls()
        b = self.boss = fighter_factory.new_foreigner()
        g.register_fighter(b)
        t = 'Rumor has it that {}, a renowned martial artist from {}, has arrived in {} to defeat local masters and \
             prove the superiority of his own fighting style, {}.'.format(
            b.name, b.country, g.town_name, b.style.name
        )
        g.msg(t)

    def reward(self):
        g, p, b = self.game, self.player, self.boss
        p.gain_rep(BEAT_FOREIGNER)
        p.add_accompl('Foreign Challenger')

    def scene1(self):
        g, b = self.game, self.boss
        t = (
            'The people of {} keep talking about the foreigner, {}. He has already defeated some good '
            'fighters.'.format(g.town_name, b.name)
        )
        g.msg(t)

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        f = fighter_factory.new_fighter(5)
        p.spectate([b], [f])
        t = "{b} has challenged some martial artists in {f}, yet again. Today {p} watched him fight, in a few of \
        his \'friendly matches\', which didn\'t seem all that friendly. In the last fight, {b} defeated three \
        opponents at once, injuring them badly. He is a formidable adversary... \nBy watching {b} fight {p} gained \
        some valuable insights into the foreigner\'s technique.".format(
            b=b.name, f=g.town_name, p=p.name
        )
        g.show(t)
        base_exp = 10
        p.gain_exp(rndint(base_exp, base_exp * 3))
        g.pak()

    def scene3(self):
        g, p, b = self.game, self.player, self.boss
        av_friends = [f for f in p.friends if f not in g.players]
        if p.best_student:
            f = p.best_student
            f_st = '{}\'s best student {}'.format(p.name, f.name)
        elif av_friends:
            f = random.choice(av_friends)
            f_st = '{}\'s friend {}'.format(p.name, f.name)
        else:
            f = random.choice(list(g.masters.values()))
            f_st = f'{f.name} of {f.style.name}'
        t = '{} finds out that {} beat {}! Can no one stop this arrogant foreigner?'.format(
            p.name, b.name, f_st
        )
        g.show(t)
        if not p.is_human or g.yn(f'Challenge {b.name}?'):
            if p.fight(b, hide_stats=False, environment_allowed=False, items_allowed=False):
                g.show(
                    '{}: "It\'s not about styles. True strength is in the fighter\'s heart."'.format(
                        p.name
                    )
                )
                g.msg('The people of {} are amazed at {}\'s victory!'.format(g.town_name, p.name))
                self.reward()
            else:
                g.msg(f'Having proved his superiority, {b.name} leaves {g.town_name}.')
                # get depressed?
        # end of the story
        self.end()


class NinjaTurtlesStory(Story):
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


class RenownedMaster(Story):
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


class StrangeDreamsStory(Story):
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


class TreasuresStory(Story):
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


# in the order added, though the order doesn't matter
all_stories = (
    BanditFianceStory,
    ForeignerStory,
    TreasuresStory,
    StrangeDreamsStory,
    RenownedMaster,
    NinjaTurtlesStory,
)
