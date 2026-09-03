import random

from kf_lib.actors import fighter_factory, traits
from kf_lib.utils import enum_words, rnd
from ._base_encounter import BaseEncounter, Guaranteed
from ._utils import check_feeling_greedy, check_scary_fight, get_escape_chance, try_escape


# constants
# encounter chances
ENC_CH_BRAWLER = 0.03
ENC_CH_DRUNKARD = 0.05
ENC_CH_FAT_GIRL = 0.02
ENC_CH_GOSSIP = 0.03
ENC_CH_OVERHEAR_CONVERSATION = 0.03
ENC_CH_PLAYER_MATCH = 0.01
ENC_CH_WISE_MAN = 0.02

# misc chances
CH_BRAWLER_ATTACKS = 0.2
CH_CHANGE_TRAIT = 0.15
CH_DRUNKARD_FIGHT_STRONG = 0.1
CH_DRUNKARD_FIGHT_WEAK = 0.1

# levels
REQ_LV_DRUNKARD_FIGHT_STRONG = (5, 10)
REQ_LV_DRUNKARD_FIGHT_WEAK = (1, 5)

# money
MONEY_GOSSIP_COST = (15, 20, 25, 30, 35)
MONEY_WISE_MAN = 10

# moves
DRUNKARD_LOSE_MOVE_TIERS = (2, 4)
# DRUNKARD_WIN_MOVE_TIERS = (4, 6)  # decided not to implement

# reputation
REP_PEN_BRAWL = -3
REP_PEN_DRINK = -3
REP_NOT_BRAWL = 1


class Brawler(BaseEncounter):
    def check_if_happens(self):
        return not self.player.is_master and rnd() <= ENC_CH_BRAWLER

    def run(self):
        p = self.player
        t = f'''A man bumps into {p.name} in the street.
Man: "Hey you! Apologize or I'll beat you up!\"'''
        p.show(t)
        p.log("Encounters a brawler.")
        b = fighter_factory.new_brawler()
        opp_info = p.get_rel_strength(b)
        if p.brawl_or_not(opp_info):
            p.log("Is provoked.")
            p.gain_rep(REP_PEN_BRAWL)
            p.fight(b)
            p.show('{}: "I shouldn\'t have been provoked so easily..."'.format(p.name))
            p.pak()
        else:
            p.log("Apologizes.")
            p.gain_rep(REP_NOT_BRAWL)
            if rnd() <= CH_BRAWLER_ATTACKS:
                p.log("The brawler won't let go.")
                p.show('Brawler: "That\'s not good enough!"')
                p.pak()
                p.fight(b)



class Drunkard(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_DRUNKARD

    def run(self):
        p = self.player
        t = f"""{p.name} meets a drunkard. "Hey, pal, come drink with me!" he slurs."""
        p.show(t)
        p.log("Meets a drunkard.")
        if rnd() < p.drink_with_drunkard:
            p.show(f"{p.name} can't resist the temptation.")
            p.drink()
            p.gain_rep(REP_PEN_DRINK)
        else:
            p.show(f"{p.name} refuses to drink.")
            p.log("Refuses to drink.")
            roll = rnd()
            if (
                p.check_lv(*REQ_LV_DRUNKARD_FIGHT_STRONG)
                and roll <= CH_DRUNKARD_FIGHT_STRONG
                and p.game.drunkard is not None
            ):
                self.do_fight(strong=True)
            elif not p.is_master and roll <= CH_DRUNKARD_FIGHT_WEAK:
                self.do_fight()
        p.pak()

    def do_fight(self, strong=False):
        p = self.player
        if strong:
            d = p.game.drunkard
            t = '''Drunkard: "What? Just ignoring Legendary {}? \
            Let me teach you some manners!"'''.format(
                d.name.replace("Drunkard ", "")
            )
        else:
            t = '''Drunkard: "You think you're too good for drinkin' with me?"'''
            d = fighter_factory.new_drunkard(strong=False)
        p.show(t)
        p.log(f"The drunkard attacks {p.name}.")
        p.pak()
        if p.fight(d, items_allowed=False):
            if strong:
                t = '''{}: "Whoa, you are good! I was just as good and just as arrogant in my day... \
                I\'m sure we\'ll meet again."'''.format(
                    d.name
                )
                p.show(t)
                p.add_friend(d)
                p.add_accompl("Drunkard's Friend")
                p.show(f'{p.name}: "What amazing kung-fu! I feel that my technique has improved"')
                p.pak()
                p.learn_move_from(d)
                p.game.drunkard = None
        else:
            p.show(f'{d.name}: "When I\'m one-tenth drunk I can use only one-tenth of my skill, '
                   f'but when I\'m ten-tenths drunk I\'m at the top of my form."')
            p.pak()
            if strong:
                p.show(f'{p.name}: "What amazing kung-fu! Even though I lost, I feel that my '
                       'technique has improved"')
                p.pak()
                p.learn_move_from(d)



class FatGirl(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.g = player.game.fat_girl
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        p = self.p
        return p.game.fat_girl is not None and not p.is_master and rnd() <= ENC_CH_FAT_GIRL

    def run(self):
        p = self.player
        p.show(f"{p.name} is ambushed by a strange fat girl.")
        p.log("Is ambushed by a fat girl.")
        self.g = p.game.fat_girl
        opp_strength = p.get_rel_strength(self.g)
        esc_chance = get_escape_chance(p)
        p.show(
            'Fat Girl: "You look like a martial artist! '
            "Surely you'll make a fine husband. MARRY ME NOW OR I'LL BEAT THE CRAP OUT OF YOU!"
        )
        if p.fight_or_run(opp_strength, esc_chance) and not check_scary_fight(p, opp_strength[0]):
            self.do_fight()
        else:
            try_escape(p, esc_chance)

    def do_fight(self):
        p = self.player
        if p.fight(self.g):
            p.msg(f"{self.p.name} runs away in fear.")
            p.game.fat_girl = None
            p.add_accompl("Fat Girl Defeated")
        else:
            p.msg('Fat Girl: "Now that I think about it, you are too weak to be my husband '
                  'anyway!"')



class FriendMatch(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.av_fr = []
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        self.av_fr = self.player.get_nonhuman_friends()
        return rnd() <= len(self.av_fr) * 0.01

    def run(self):
        p = self.player
        opp = random.choice(self.av_fr)
        t1 = f'''{opp.name}: "{p.name}, I've learned some new moves. Let's practice!\"'''
        t2 = f"{p.name}'s friend {opp.name} challenges him to a friendly match."
        p.show(t1)
        p.log(t2)
        p.show("Accept?")
        if p.p_match_or_not():
            p.spar(opp)
            p.show('{}: "That was a good match! Let\'s do it again some time."'.format(opp.name))
            p.pak()
        else:
            p.log("Refuses.")



class Gossip(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_GOSSIP

    def run(self):
        p = self.player
        cost = random.choice(MONEY_GOSSIP_COST)
        t = "{} meets a local gossipmonger. Pay {} coins to hear the latest rumors?".format(
            p.name, cost
        )
        p.show(t)
        p.log("Meets a gossipmonger.")
        if p.hear_rumors_or_not() and p.check_money(cost):
            p.pay(cost)
            p.log("Hears the rumors.")
            p.game.show_stats()




class OverhearConversation(BaseEncounter):
    """Hear interesting facts about players."""

    def __init__(self, player, check_if_happens=True):
        self.facts = []
        BaseEncounter.__init__(self, player, check_if_happens)

    def collect_facts(self):
        g = self.player.game
        for p in g.players:
            for stat in ("aston_victory", "humil_defeat"):
                result = p.get_stat(stat)  # tuple: (date, p.level, [enemies strings], big opp_to_self_pwr_ratio)
                if result is not None:
                    self.facts.append((p, stat, result))

    def check_if_happens(self):
        return rnd() <= ENC_CH_OVERHEAR_CONVERSATION

    def run(self):
        p = self.player
        t = "{} accidentally overhears a conversation of two young kung-fu practitioners.".format(
            p.name
        )
        p.log("Overhears a conversation.")
        p.show(t)
        self.collect_facts()
        if not self.facts:
            p.show(
                '"They talk about such silly things instead of practicing!" - {} thinks.'.format(
                    p.name
                )
            )
            p.log("Nothing interesting.")
        else:
            random.shuffle(self.facts)
            person, fact, result = self.facts[0]
            date, lv, opps, ratio = result
            n_opp = len(opps)
            if n_opp == 1:
                opp_str = opps[0]
            else:
                opp_str = enum_words(opps)
            if fact == "humil_defeat":
                t = '''One of them says: "Haven't you heard? {} at lv.{} shamefully lost to {}. What a disgrace to \
kung-fu!"'''.format(
                    person.name, lv, opp_str
                )
                p.show(t)
                p.log(f"Something about {person.name}'s astonishing victory.")
            elif fact == "aston_victory":
                t = '''One of them says: "Haven't you heard? {} at lv.{} beat {}. What an astonishing \
victory!"'''.format(
                    person.name, lv, opp_str
                )
                p.show(t)
                p.log(f"Something about {person.name}'s humiliating defeat.")
        p.pak()



class PlayerMatch(BaseEncounter):
    """Works with computer players as opponents only (for both human and computer players)."""

    def __init__(self, player, check_if_happens=True):
        self.av_p = []
        BaseEncounter.__init__(self, player, check_if_happens)

    def set_available_players(self):
        p, g = self.player, self.player.game
        self.av_p = [pp for pp in g.get_act_players() if not pp.is_human and not pp == p]

    def check_if_happens(self):
        self.set_available_players()
        return self.av_p and rnd() <= ENC_CH_PLAYER_MATCH

    def run(self):
        p = self.player
        opp = random.choice(self.av_p)
        t = '''{0} meets {1} (lv.{2}).
{1}: "Let\'s have a friendly match!"'''.format(
            p.name, opp.name, opp.level
        )
        p.show(t)
        p.log(f"Meets {opp.name}")
        if p.p_match_or_not():
            p.spar(opp)
            p.show('{}: "That was a good match! Let\'s do it again some time."'.format(opp.name))
            p.pak()
        else:
            p.log("Refuses.")



class WiseMan(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_WISE_MAN

    def run(self):
        p = self.player
        t = f"{p.name} meets a wise man."
        p.show(t)
        p.log("Meets a wise man.")
        if p.check_money(MONEY_WISE_MAN):
            if p.talk_wise_or_not() and not check_feeling_greedy(p):
                p.pay(MONEY_WISE_MAN)
                trait = traits.get_rand_traits(negative=False)
                p.show(
                    "{} and the wise man have a long conversation in a nearby tavern. The wise man talks about "
                    "the importance of being {}.".format(p.name, trait)
                )
                p.log(f"The wise man talks about the importance of being {trait}.")
                if rnd() <= CH_CHANGE_TRAIT and trait not in p.traits:
                    p.show(f"This conversation changes {p.name}'s life.")
                    opp_trait = traits.get_opposite_trait(trait)
                    if opp_trait in p.traits:
                        p.remove_trait(opp_trait)
                    else:
                        p.add_trait(trait)
                    p.add_accompl("Personality Change")
            else:
                return
        else:
            p.show(
                "Too bad {} doesn't have enough money to treat the wise man to lunch and talk to him.".format(
                    p.name
                )
            )
        p.pak()



class GDrunkard(Guaranteed, Drunkard):
    pass



