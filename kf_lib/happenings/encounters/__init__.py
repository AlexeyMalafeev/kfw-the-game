from ._ambush import Ambush
from ._beggar import Beggar, GBeggar
from ._challenger import Challenger, GChallenger
from ._craftsman import Craftsman
from ._utils import check_feeling_greedy, check_scary_fight, get_escape_chance, try_enemy, try_escape
from ._base_encounter import BaseEncounter, Guaranteed
# todo refactor imports in encounters
from ._utils import check_feeling_greedy, check_scary_fight, get_escape_chance, set_up_weapon_fight, \
    try_enemy, try_escape
from ...actors import fighter_factory, traits, quotes
from ...mechanics import experience
from ...utils import lang_tools
from ...kung_fu import moves
from ...things import items
from ...utils.utilities import *

# todo f-strings in encounters

# constants
# encounter chances
ENC_CH_BOOK_SELLER = 0.02
ENC_CH_BRAWLER = 0.03
ENC_CH_CRIMINAL = 0.03
ENC_CH_DRUNKARD = 0.05
ENC_CH_FAT_GIRL = 0.02
ENC_CH_GAMBLER = 0.05
ENC_CH_GOSSIP = 0.03
ENC_CH_MASTER_TRIAL = 0.05
ENC_CH_MERCHANT = 0.04
ENC_CH_OVERHEAR_CONVERSATION = 0.03
ENC_CH_PLAYER_MATCH = 0.01
# ENC_CH_SCHOOL_CHALL = 0.05
ENC_CH_PRIZE_FIGHTING = 0.02
ENC_CH_SCHOOL_BULLYING = 0.03
ENC_CH_STREET_PERFORMER = 0.03
ENC_CH_STUDENT = 0.07
ENC_CH_WEIRDO = 0.02
ENC_CH_WISE_MAN = 0.02

# misc chances
CH_BOOK_RUBBISH = 0.3
CH_BOOK_MOVE = 0.3  # given book is not rubbish, so (1 - p(not_rubbish)) * p(move)
CH_BRAWLER_ATTACKS = 0.2
CH_CHANGE_TRAIT = 0.15
CH_CONVICT_ARMED = 0.35
CH_DRUNKARD_FIGHT_STRONG = 0.1
CH_DRUNKARD_FIGHT_WEAK = 0.1
CH_GAMBLER_ARMED = 0.3
CH_GAMBLER_ENEMY = 0.5
CH_GAMBLER_FIGHT = 0.25
CH_PERFORMER_SELLS_GOOD_ITEM = 0.5
CH_ROBBER_ARMED = 0.35
CH_ROBBER_ENEMY = 0.1
CH_SCHOOL_CHALLENGER_ARMED = 0.3
CH_STORY_DEVELOPS = 0.07
CH_STREET_PERFORMER_ARMED = 0.3
CH_STUDENT_CHALLENGE = 0.25
CH_THIEF_ARMED = 0.3
CH_THIEF_ESCAPES = 0.3
CH_THIEF_TOUGH = 0.1
CH_THUG_ENEMY = 0.1

# levels
LV_STUD_CHALLENGERS = (1, 3)
LV_PRIZE_FIGHTERS = (2, 4, 7, 10, 15)
REQ_LV_DRUNKARD_FIGHT_STRONG = (5, 10)
REQ_LV_DRUNKARD_FIGHT_WEAK = (1, 5)
REQ_LV_MASTER_TRIAL = fighter_factory.MASTER_LV[0]

# lines
LINES_ROBBER = (
    "Hey, I really need {} coins. Do you think you can help me out?",
    "If you don't give me {} coins, you'll need a doctor, and a good one!",
    "Hey you! This is my territory. Entering is free, but leaving in one piece costs {} coins.",
    "You know, I need {} coins to buy medicine for my sick grandma. Wanna share?",
    "It is important to share what you have with others. Pay {} coins and you are free to go.",
)

# money
MONEY_BOOK = 100
MONEY_CONVICT_REWARD_MULT = (10, 15, 20, 25, 30, 40)
MONEY_GAMBLING_BETS = (20, 25, 30, 40, 50)
MONEY_GOSSIP_COST = (15, 20, 25, 30, 35)
MONEY_GIVE_ROBBERS = (40, 50, 60, 80, 100, 120, 130, 150, 180)
MONEY_OPEN_SCHOOL = 1000
MONEY_PERFORMER = (40, 50, 60)
MONEY_PRIZE_FIGHTING_FEE = 50
MONEY_PRIZE_FIGHTING_WIN = (25, 50, 100, 150, 250)
MONEY_SHOP_BREAKAGES = (30, 50, 70)
MONEY_THIEF_STEALS = (25, 50, 75, 100, 200)
MONEY_WISE_MAN = 10

# moves
BOOK_MOVE_TIERS = (1, 5)
BEGGAR_LOSE_MOVE_TIERS = (2, 4)
# BEGGAR_WIN_MOVE_TIERS = (4, 6)  # decided not to implement
DRUNKARD_LOSE_MOVE_TIERS = (2, 4)
# DRUNKARD_WIN_MOVE_TIERS = (4, 6)  # decided not to implement
PERFORMER_LOSE_MOVE_TIERS = (2, 4)
# PERFORMER_WIN_MOVE_TIERS = (4, 6)  # decided not to implement

# numbers
NUM_EXTORTERS = (2, 6)
NUM_PERFORMER_THUGS = (2, 5)
NUM_POLICE_VS_THUGS = (2, 4)
NUM_THUGS_VS_POLICE = (+1, +4)  # always more than the police
NUM_ROBBERS_CROWD = (5, 8)
NUM_ROBBERS_GROUP = (2, 4)
NUM_STUD_CHALLENGERS = (2, 5)

# reputation
REP_PEN_BRAWL = -3
REP_PEN_BREAK_NOT_PAY = -1
REP_PEN_DRINK = -3
REP_PEN_GAMBLE = -3
REP_PEN_PRIZE_FIGHTING = -5
REP_NOT_BRAWL = 1

# misc
FAILED_ESCAPE_BEATING = (3, 5)
PERFORMER_EXP_REWARD = 50


class BookSeller(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_BOOK_SELLER

    def run(self):
        p = self.player
        price = MONEY_BOOK
        t = f"""{p.name} meets a traveling book seller.
Book Seller: "Ah, a martial artist! I'm selling this wonderful kung-fu book for only {price} \
coins! Its secret and powerful techniques will make you a legendary fighter! What do you say?"
Buy it?"""
        p.show(t)
        p.log("Meets a book seller.")
        if p.buy_item_or_not() and not check_feeling_greedy(p):
            if not p.check_money(price):
                p.show(f"{p.name} doesn't have enough money.")
            else:
                p.pay(price)
                if rnd() < CH_BOOK_RUBBISH:
                    t = "The book turns out to be complete rubbish!"
                    p.write(t)
                else:
                    if rnd() < CH_BOOK_MOVE:
                        tier = random.randint(*BOOK_MOVE_TIERS)
                        move = moves.get_rand_move(f=p, tier=tier, moves_to_exclude=None)
                        p.learn_move(move)
                    else:
                        exp = random.randint(*experience.BOOK_EXP)
                        p.gain_exp(exp)
            p.pak()


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


class ContinueStory(BaseEncounter):
    def check_if_happens(self):
        p = self.player
        s = p.current_story
        return s and rnd() <= CH_STORY_DEVELOPS

    def run(self):
        s = self.player.current_story
        s.advance()


class Criminal(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.c = None
        self.allies = None
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= ENC_CH_CRIMINAL and self.p.game.criminals

    def run(self):
        p = self.player
        self.c = c = random.choice(p.game.criminals)
        p.show(f"{p.name} accidentally bumps into a wanted criminal, {c.name}.")
        p.log("Encounters a wanted criminal.")
        opp_strength = p.get_rel_strength(c)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, ratio=opp_strength[0]):
            if c.check_lv(p.level + 1):
                self.allies = p.check_allies(1)
            if rnd() <= CH_CONVICT_ARMED:
                c.arm_robber()
                p.msg("The criminal pulls out a weapon!")
            win = p.fight(c, self.allies)
            if win:
                self.reward()
                p.game.criminals.remove(c)
                p.game.unregister_fighter(c)
        else:
            p.log("Doesn't try to stop the criminal.")

    def reward(self):
        p = self.player
        c = self.c
        rew_mult = random.choice(MONEY_CONVICT_REWARD_MULT)
        reward = c.level * rew_mult
        rep_gain = c.level
        p.show(f"{p.name} takes the criminal to the police.")
        # split the reward
        if self.allies:
            ally = self.allies[0]
            reward = round(reward / 2)
            rep_gain = round(rep_gain / 2)
            if ally.is_player:
                ally.gain_rep(rep_gain)
                ally.earn_reward(reward)
        p.gain_rep(c.level)
        p.earn_reward(reward)
        p.pak()


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


class Extorters(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.p.game.crime / 4

    def run(self):
        p = self.player
        num_en = rndint(*NUM_EXTORTERS)
        p.show(f"{p.name} sees {num_en} men in a shop demanding 'protection' money.")
        p.log(f"Sees {num_en} extorters in a shop.")
        en = fighter_factory.new_thug(n=num_en)
        for e in en:
            if random.choice((True, False, False)):
                e.arm_robber()
        opp_strength = p.get_rel_strength(*en)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, ratio=opp_strength[0]):
            p.check_help()
            p.gain_rep(num_en * 2)
            if p.fight(en[0], p.allies, en[1:]):
                p.game.crime_down()
                try_enemy(p, en[0], CH_THUG_ENEMY)
                if random.choice([True, True, False]):
                    item = items.get_random_item()
                    p.show('Shop owner: "Thank you, thank you young man!"')
                    for pp in [p] + (p.allies if p.allies is not None else []):
                        if pp.is_player:
                            pp.show(
                                f"{p.name} gets {item} from the grateful shop owner."
                            )
                            pp.obtain_item(item)
                else:
                    t = (
                        'Shop owner: "Oh boy... You martial artists only know how to fight and break things! '
                        "Look what you've done to my shop! Who's gonna pay for the breakages?.."
                    )
                    p.show(t)
                    cost = random.choice(MONEY_SHOP_BREAKAGES)
                    if p.check_money(cost) and not check_feeling_greedy(p):
                        p.pay(cost)
                        p.show(f"{p.name} pays {cost} c.")
                    else:
                        p.gain_rep(REP_PEN_BREAK_NOT_PAY)
            else:
                p.show('Shop owner: "Are you hurt? I\'ll find a doctor..."')
            p.pak()
        else:
            p.log("Looks the other way.")


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


class FindItem(BaseEncounter):
    def check_if_happens(self):
        p = self.player
        return rnd() <= p.item_is_found

    def run(self):
        p = self.player
        it = items.get_random_item()
        p.show(f"{p.name} accidentally finds an item: {it}.")
        p.log(f"Accidentally finds an item: {it}.")
        p.obtain_item(it)
        p.change_stat("items_found", 1)
        p.pak()


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


class Gambler(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.bet = 0
        self.won = 0
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= ENC_CH_GAMBLER

    def run(self):
        p = self.player
        self.bet = random.choice(MONEY_GAMBLING_BETS)
        t = f"""Gambler: "Hey, do you want to play? You could make some serious money!"
One bet is {self.bet} coins."""
        p.show(t)
        p.log("Meets a gambler.")
        if p.gamble_or_not() or rnd() < p.gamble_with_gambler:
            p.show(f"{p.name} can't resist the temptation.")
            p.log("Gambles.")
            p.gain_rep(REP_PEN_GAMBLE)
            money = p.money
            p.pak()
            self.play()
            self.won = p.money - money
            p.refresh_screen()
            if self.won <= 0:
                p.msg('Gambler: "Better luck next time!"')
                p.record_gamble_lost(-self.won)
            else:
                p.record_gamble_win(self.won)
                if self.won >= 100 and rnd() <= CH_GAMBLER_FIGHT:
                    self.do_fight()
        else:
            p.show(f"{p.name} refuses to gamble.")
            p.log("Refuses to gamble.")
            p.pak()

    def play(self):
        p = self.player
        skewed = random.choice((1, 0))
        if skewed:
            weights = [rndint(1, 3) for _ in range(3)]
            gambler_options = (
                ["Rock"] * weights[0] + ["Paper"] * weights[1] + ["Scissors"] * weights[2]
            )
        else:
            gambler_options = ["Rock", "Paper", "Scissors"]
        i = 0
        while True:
            i += 1
            if p.check_money(self.bet):
                if i <= 5:
                    p.pay(self.bet)
                    while True:
                        p.refresh_screen()
                        yc = p.rock_paper_or_scissors()
                        gc = random.choice(gambler_options)
                        p.show(f"{p.name}: {yc}\nGambler: {gc}")
                        if yc == gc:
                            p.show("Tie!")
                            p.pak()
                            continue
                        if (
                            (yc == "Rock" and gc == "Scissors")
                            or (yc == "Paper" and gc == "Rock")
                            or (yc == "Scissors" and gc == "Paper")
                        ):
                            p.money += self.bet * 2
                            p.show(f"{p.name} wins!")
                            p.pak()
                            break
                        else:
                            p.show("Gambler wins!")
                            p.pak()
                            break
                    p.refresh_screen()
                else:
                    if not rnd() < p.gamble_continue:
                        p.show(f"{p.name} decides to stop gambling.")
                        p.pak()
                        return
                    else:
                        i = 0
            else:
                break

    def do_fight(self):
        p = self.player
        g = fighter_factory.new_gambler()
        g.name = p.game.get_new_name("Gambler")
        if rnd() <= CH_GAMBLER_ARMED:
            g.arm_improv()
        p.show('Gambler: "You think you can get away with that?"')
        p.log(f"The gambler attacks {p.name}.")
        p.pak()
        if p.fight(g):
            if rnd() <= CH_GAMBLER_ENEMY:
                p.show('Gambler: "I\'m telling you, this is not over yet!"')
                p.add_enemy(g)
                p.pak()
            p.add_accompl("Gambler Beaten")
        else:
            p.money -= self.won
            p.show("Gambler: I'm just taking back what's mine!")
            p.pak()


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


class HelpPolice(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 4

    def run(self):
        p = self.player
        num_al = rndint(*NUM_POLICE_VS_THUGS)
        num_en = num_al + rndint(*NUM_THUGS_VS_POLICE)
        p.show(f"{p.name} sees {num_al} police officers fighting {num_en} thugs!")
        p.log(f"Sees {num_al} police officers fighting {num_en} thugs.")
        al = fighter_factory.new_police(n=num_al)
        for a in al:
            if random.choice((True, False)):
                a.arm_police()
        en = fighter_factory.new_thug(n=num_en)
        for e in en:
            if random.choice((True, False)):
                e.arm_robber()
        opp_strength = p.get_rel_strength(*en, allies=al)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, ratio=opp_strength[0]):
            p.gain_rep(num_en - num_al)
            p.check_help(allies=False, master=False, school=False)
            if p.fight(en[0], al, en[1:]):
                p.show('Police Officer: "Thank you very much for your help!"')
                p.pak()
        else:
            p.log("Does not help the police.")


class LoseItem(BaseEncounter):
    def check_if_happens(self):
        p = self.player
        return rnd() <= p.item_is_lost and p.get_items(incl_healer=True)

    def run(self):
        p = self.player
        _items = p.get_items(incl_healer=True)
        it = random.choice(_items)
        p.show(f"{p.name} accidentally loses his {it}.")
        p.log(f"Accidentally loses his {it}.")
        p.lose_item(it)
        p.change_stat("items_lost", 1)
        p.pak()


class MasterTrial(BaseEncounter):
    def check_if_happens(self):
        p = self.player
        return (
            not p.is_master
            and p.school_rank == 1
            and p.check_lv(REQ_LV_MASTER_TRIAL)
            and rnd() <= ENC_CH_MASTER_TRIAL
        )

    def run(self):
        p = self.player
        m = p.get_master()
        t = (
            '{0} meets his master. \n{1}: "{0}, you are one of my best students. '
            "You have made a lot of progress in {2}. But you might be ready to found your own "
            "kung-fu school... "
            "Let's find that out!\"".format(p.name, m.name, p.style.name)
        )
        p.show(t)
        p.log("Is offered a trial to become a master.")
        opp_strength = p.get_rel_strength(m)
        if p.fight_or_not(opp_strength):
            if p.spar(m, hide_stats=False):
                p.show(f'{m.name}: "Yes, you ARE ready!"')
                p.add_friend(m)
                outlay = MONEY_OPEN_SCHOOL
                p.show(
                    "To open a martial arts school, {} needs to make the initial outlay of {} coins.".format(
                        p.name, outlay
                    )
                )
                p.pay(outlay)
                p.is_master = True
                p.log("Becomes a master and founds his own school.")
                p.set_stat("became_master", p.game.get_date())
                p.set_stat("became_master_at_lv", p.level)
                school = p.get_school()
                school.remove(p)
                for a_player in p.game.players:
                    a_player.refresh_school_rank()  # in case there are other players in the same school
                school_name = p.choose_school_name()
                p.game.schools[school_name] = []
                p.game.masters[school_name] = p
                p.new_school_name = school_name
            else:
                p.show(f'{m.name}: "No, you are not ready yet. Practice some more."')
            p.pak()


class Merchant(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_MERCHANT

    def run(self):
        p = self.player
        med = random.choice((True, False))
        if med:
            item = items.MEDICINE
        else:
            item = random.choice(items.STD_FIGHT_ITEMS)
        price = random.choice(items.PRICES)
        descr = items.get_item_descr(item)
        descr_s = f" ({descr})" if descr else ""
        t = f"""{p.name} meets a street merchant.
Merchant: "Please buy this {item}{descr_s}!"
Buy it for {price} coins?"""
        p.show(t)
        p.log("Meets a street merchant.")
        if not p.check_money(price):
            p.show(f"{p.name} doesn't have enough money.")
            p.pak()
        elif p.buy_item_or_not() and not check_feeling_greedy(p):
            p.buy_item(item, price)


class OverhearConversation(BaseEncounter):
    """Hear interesting facts about players."""

    def __init__(self, player, check_if_happens=True):
        self.facts = []
        BaseEncounter.__init__(self, player, check_if_happens)

    def collect_facts(self):
        g = self.player.game
        for p in g.players:
            for stat in ("aston_victory", "humil_defeat"):
                result = p.get_stat(stat)  # tuple: (date, p.level, [enemies strings], big ratio)
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
                opp_str = lang_tools.enum_words(opps)
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


class PrizeFighting(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_PRIZE_FIGHTING

    def run(self):
        p = self.player
        t = (
            "{} meets a shady character who offers to participate in an underground prize fighting contest. "
            "\"It's simple. You pay {} coins to enter. There are five stages in the contest. The more opponents you "
            'beat, the more money you win. How does that sound?"'.format(
                p.name, MONEY_PRIZE_FIGHTING_FEE
            )
        )
        p.show(t)
        p.log("Offered to take part in an underground prize fighting contest.")
        if not p.check_money(MONEY_PRIZE_FIGHTING_FEE):
            p.show(f"{p.name} doesn't have enough money.")
            p.pak()
        elif p.tourn_or_not():
            p.gain_rep(REP_PEN_PRIZE_FIGHTING)
            p.pay(MONEY_PRIZE_FIGHTING_FEE)
            self.do_fight()
        else:
            p.log("Chooses to ignore the offer.")

    def do_fight(self):
        p = self.p
        prize = 0
        for i, lv in enumerate(LV_PRIZE_FIGHTERS):
            p.cls()
            p.show(f"Stage {i + 1}")
            c = fighter_factory.new_prize_fighter(lv)
            opp_strength = p.get_rel_strength(c)
            if (i and p.fight_or_not(opp_strength)) or not i:
                win = p.fight(c, items_allowed=False)
                if win:
                    prize = MONEY_PRIZE_FIGHTING_WIN[i]
                else:
                    prize = 0
                    break
            else:
                break
        if prize:
            p.earn_prize(prize)
            p.pak()


class Robbers(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.num_r = 0
        self.r = None
        self.rs = []
        self.sn = ""
        self.sv = ""
        self.escape_chance = 0
        self.money = random.choice(MONEY_GIVE_ROBBERS)
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 2

    def run(self):
        self.set_up()
        if self.num_r > 1:
            self.start_many()
        else:
            self.start_one()
        self.pre_fight()

    def set_up(self):
        self.num_r = random.choice((1, 1, rndint(*NUM_ROBBERS_GROUP), rndint(*NUM_ROBBERS_CROWD)))
        self.r = fighter_factory.new_robber()
        self.sn = "s" if self.num_r > 1 else ""
        self.sv = "" if self.num_r > 1 else "s"
        self.escape_chance = get_escape_chance(self.p)

    def start_one(self):
        self.p.show(f"{self.p.name} encounters a robber.")
        self.p.log("Encounters a robber.")
        if rnd() <= CH_ROBBER_ARMED:
            self.r.arm_robber()
            self.p.show(f"He is armed with {lang_tools.add_article(self.r.weapon.name)}.")
        self.rs = []

    def start_many(self):
        self.p.show(f"{self.p.name} encounters {self.num_r} robbers.")
        self.p.log(f"Encounters {self.num_r} robbers.")
        self.rs = fighter_factory.new_robber(n=self.num_r)
        self.r, self.rs = self.rs[0], self.rs[1:]

    def pre_fight(self):
        p = self.player
        r_words = random.choice(LINES_ROBBER)
        r_line = f'Robber: "{r_words}"'
        p.show(r_line.format(self.money))
        opp = [self.r] + self.rs
        opp_strength = p.get_rel_strength(*opp)
        choice = p.fight_run_or_pay(opp_strength, self.escape_chance, self.money)
        if choice == "f" and not check_scary_fight(p, opp_strength[0]):
            self.do_fight()
        elif choice == "p":
            if check_feeling_greedy(p):
                try_escape(p, self.escape_chance)
            else:
                self.pay()
        else:
            try_escape(p, self.escape_chance)

    def do_fight(self):
        p = self.p
        if self.num_r > 1:
            p.check_help()
            allies = p.allies
        else:
            if self.r.weapon and self.r.check_lv(p.level + 1):
                p.check_help(allies=False, master=False, school=False)
            allies = None
        if p.fight(self.r, allies, self.rs):
            if self.num_r >= NUM_ROBBERS_GROUP[0]:
                p.game.crime_down()
            p.gain_rep(self.num_r)
            try_enemy(p, self.r, CH_ROBBER_ENEMY)

    def pay(self):
        self.p.pay(self.money)
        self.p.change_stat("money_robbed", self.money)
        self.p.msg(f"The robber{self.sn} decide{self.sv} to let {self.p.name} go.")


class RobbingSomeone(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 4

    def run(self):
        p = self.player
        num_en = rndint(*NUM_EXTORTERS)
        p.show(f"{p.name} sees {num_en} men robbing someone.")
        p.log(f"Sees {num_en} men robbing someone.")
        en = fighter_factory.new_thug(n=num_en)
        opp_strength = p.get_rel_strength(*en)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, ratio=opp_strength[0]):
            p.check_help()
            p.gain_rep(num_en * 2)
            if p.fight(en[0], p.allies, en[1:]):
                p.game.crime_down()
                try_enemy(p, en[0], CH_ROBBER_ENEMY)
                victim = random.choice(("Man", "Woman"))
                p.show(f'{victim}: "Thank you very much!!!"')
                p.pak()
        else:
            p.log("Looks the other way.")


class SchoolBullying(BaseEncounter):
    def check_if_happens(self):
        p = self.p
        return not p.is_master and p.school_rank > 1 and rnd() <= ENC_CH_SCHOOL_BULLYING

    def run(self):
        p = self.player
        m = self.player.get_master()
        t = f"""{p.name} is bullied at his school while {m.name} is away."""
        p.show(t)
        p.log("Is bullied at his school.")
        school = p.get_school()
        opp = random.choice(
            school[: p.school_rank - 1]
        )  # adjusts for Python indexing and skips self
        opp_strength = p.get_rel_strength(opp)
        esc_chance = get_escape_chance(p)
        if p.fight_or_run(opp_strength, esc_chance):
            p.fight(opp, hide_stats=False)
        else:
            try_escape(p, esc_chance)


class SchoolChallenge(BaseEncounter):
    def check_if_happens(self):
        p = self.p
        return not p.is_master and p.school_rank > 1 and rnd() <= ((len(p.get_school()) - 1) / 100)

    def run(self):
        p = self.player
        m = self.player.get_master()
        t = '''{0} meets his master.
{1}: "{0}, you have been practicing hard. It is now time to test your kung-fu!"'''.format(
            p.name, m.name
        )
        p.show(t)
        p.log("Is offered a trial at his school.")
        school = p.get_school()
        opp = school[p.school_rank - 2]  # adjusts for Python indexing and skips self
        opp_strength = p.get_rel_strength(opp)
        if p.fight_or_not(opp_strength):
            if rnd() < CH_SCHOOL_CHALLENGER_ARMED:
                p.arm_normal()
                opp.arm_normal()
            if p.spar(opp, hide_stats=False):
                school.remove(p)
                school.insert(
                    p.school_rank - 2, p
                )  # adjusts for Python indexing and skips defeated fighter
                p.refresh_school_rank()
                if p.school_rank > 1:
                    t = (
                        '{}: "{}, I can see that you have mastered some aspects of {}. However, you must keep '
                        'practicing as you still have a long way to go."'.format(
                            m.name, p.name, p.style.name
                        )
                    )
                    p.show(t)
                else:
                    # t = ('{}: "Well done, {}. Now it is time you learned the secret technique of our school, '
                    #      '"{}".'.format(m.name, p.name, m.style.tech.name))
                    t = f'{m.name}: "Well done, {p.name}."'
                    p.show(t)
                    # p.learn_tech(m.style.tech.name)
            else:
                react = random.choice(quotes.MASTER_CRITICISM)
                p.show(f"{m.name}: {react}")
            p.pak()


class StreetPerformer(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.performer = None
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= ENC_CH_STREET_PERFORMER

    def run(self):
        p = self.player
        c = self.performer = fighter_factory.new_performer()
        c.name = p.game.get_new_name(prefix="Master")
        p.show(
            "{} sees a travelling kung-fu master demonstrating his skills in the street.".format(
                p.name
            )
        )
        p.log("Sees a kung-fu master demonstrating his skills in the street.")
        # challenge, protect from thugs, buy items
        func = random.choice((self.challenge, self.challenge, self.sell, self.sell, self.thugs))
        func()

    def challenge(self):
        p = self.player
        c = self.performer
        cost = random.choice(MONEY_PERFORMER)
        p.show(
            "{}: \"Now, who dares to challenge me? It costs {} coins - if you win, you'll get twice "
            'as much!"'.format(c.name, cost)
        )
        p.log("The master offers a challenge.")
        opp_strength = p.get_rel_strength(c)
        if (
            p.fight_or_not(opp_strength)
            and p.check_money(cost)
            and not check_scary_fight(p, ratio=opp_strength[0])
        ):
            p.pay(cost)
            if rnd() <= CH_STREET_PERFORMER_ARMED:
                set_up_weapon_fight(p, c)
            win = p.fight(c, items_allowed=False)
            if win:
                p.money += cost * 2
                p.show('{}: "I didn\'t think I could lose..."'.format(c.name))
            else:
                p.show(f'{c.name}: "Hmph! No one can beat me."')
                # todo only if lucky
                p.show(
                    f'{p.name}: "What amazing kung-fu! Even though I lost, I feel that my '
                    'technique has improved"'
                )
                p.pak()
                p.learn_move_from(c)
            p.pak()
        else:
            # disarm player!!!
            p.disarm()
            p.log("Chooses to ignore the challenge.")

    def reward(self):
        p = self.player
        c = self.performer
        rewards = "iiit"
        reward = random.choice(list(rewards))
        p.show(f'{c.name}: "I see that you are a very brave young man.')
        if reward == "i":
            item = items.get_random_item()
            p.show(f'Please accept this {item} as a token of my gratitude."')
            p.obtain_item(item)
            p.pak()
        elif reward == "t":
            p.show(
                'Your kung-fu is very good; however, I can help you improve it."'
                "\n{} teaches {} some of his moves.".format(c.name, p.name)
            )
            p.pak()
            p.learn_move_from(c)

    def sell(self):
        p = self.player
        c = self.performer
        price = random.choice(MONEY_PERFORMER)
        p.show(
            '{}: "Now, if you want to become as strong as I am and cure all your diseases, buy this '
            "Golden Magnificent Elixir. It's only {} coins\".\nThis seems a little fishy... "
            "Could be the real thing though. Buy it?".format(c.name, price)
        )
        p.log("The master offers to buy Golden Magnificent Elixir.")
        if not p.check_money(price):
            p.show(f"{p.name} doesn't have enough money.")
            p.pak()
        elif p.buy_item_or_not() and not check_feeling_greedy(p):
            if rnd() <= CH_PERFORMER_SELLS_GOOD_ITEM:
                item = items.get_random_item()
            else:
                item = items.get_random_mock_item()
                p.change_stat("mock_items_bought", 1)
            p.show(
                "{} collects the money from all those willing to buy his Elixir and quickly walks away."
                '\nLater, the "Golden Magnificent Elixir" turns out to be a simple {}.'.format(
                    c.name, item
                )
            )
            p.log(f"The Elixir turns out to be a {item}.")
            p.buy_item(item, price)
            p.pak()

    def thugs(self):
        p = self.player
        c = self.performer
        n = rndint(*NUM_PERFORMER_THUGS)
        p.show(
            "Suddenly, {} thugs appear and attack the master. Apparently, they are after his money. Help him?".format(
                n
            )
        )
        p.log(f"{n} thugs attack the master.")
        thugs = fighter_factory.new_thug(weak=True, n=n)
        opp_strength = p.get_rel_strength(*thugs, allies=[c])
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, ratio=opp_strength[0]):
            p.gain_rep(n - 1)
            if p.fight(thugs[0], allies=[c], en_allies=thugs[1:]):
                self.reward()


class Students(BaseEncounter):
    def check_if_happens(self):
        return (
            self.p.is_master
            and self.p.students < self.p.game.MAX_NUM_STUDENTS
            and rnd() <= min(self.p.get_fame(), ENC_CH_STUDENT)
        )

    def run(self):
        p = self.player
        n_can_join = p.game.MAX_NUM_STUDENTS - p.students
        if n_can_join >= NUM_STUD_CHALLENGERS[0] and rnd() <= CH_STUDENT_CHALLENGE:
            num_st = rndint(NUM_STUD_CHALLENGERS[0], min(NUM_STUD_CHALLENGERS[1], n_can_join))
            t = '''Young men: "Master {}! We want to learn kung-fu. Please show us your skill!"'''.format(
                p.name.split()[0]
            )
            p.show(t)
            p.log("Is approached by a group of potential students.")
            p.pak()
            students = fighter_factory.new_opponent(
                lv=rndint(*LV_STUD_CHALLENGERS), n=num_st, rand_atts_mode=0
            )
            if p.fight(students[0], en_allies=students[1:], hide_stats=False, items_allowed=False):
                t = ("Young men: \"Thank you Master, now we see that you're very strong! Please "
                     'teach us to be strong too!"')
                p.show(t)
                p.add_students(num_st)
            else:
                p.show('Young men: "Sorry, Master, we\'ll learn kung-fu elsewhere."')
            p.pak()
        else:
            p.show(
                'Young man: "Master {}! Please accept me as your student!"'.format(
                    p.name.split()[0]
                )
            )
            p.log("Is approached by a potential student.")
            if p.is_human:
                choice = yn("Accept the young man?")
            else:
                choice = True
            if choice:
                p.add_students(1)


class Thief(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.players_items = None
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 3

    def run(self):
        p = self.player
        _items = self.players_items = p.get_items(incl_healer=True)
        if p.money <= 0 and not _items:
            self.nothing_to_steal()
        else:
            if rnd() <= p.thief_steals:
                self.steal()
            else:
                self.fail()
        p.pak()

    def nothing_to_steal(self):
        p = self.p
        t = '''A thief tries to steal something from {} but fails to find anything!
Thief: "What\'s with that? Are you poor or something?"'''.format(
            p.name
        )
        p.show(t)
        p.log(f"A thief fails to find anything to steal from {p.name}.")
        p.pak()

    def steal(self):
        p = self.player
        steal_item = random.choice((1, 0))
        if (steal_item or p.money <= 0) and self.players_items:
            item = random.choice(self.players_items)
            p.lose_item(item)
            p.show(f"A thief steals {item} from {p.name}.")
            p.log(f"{item} is stolen by a thief.")
            p.change_stat("items_stolen_from", 1)
        else:
            amount = random.choice(MONEY_THIEF_STEALS)
            if amount >= p.money:
                amount = p.money
                p.show("A thief steals all {0}'s money! {0} loses {1} c.".format(p.name, amount))
                p.log(f"All {p.name}'s money ({amount}) is stolen by a thief.")
            else:
                p.write(f"A thief steals {amount} coins from {p.name}!")
                p.log(f"{amount} c. is stolen by a thief.")
            self.p.steal_from(amount)
            p.show(f"The pickpocket had escaped before {p.name} noticed anything.")

    def fail(self):
        p = self.player
        p.show(f"A thief tries to steal from {p.name}, but fails.")
        p.log(f"A thief fails to steal from {p.name}.")
        if rnd() <= CH_THIEF_ESCAPES:
            t = "{} tries to stop him, but the pickpocket quickly disappears in the crowd.".format(
                p.name
            )
            p.show(t)
            p.log("The thief escapes.")
        else:
            p.show(f"{p.name} grabs the thief by the arm, but the thief fights back.")
            p.log(f"The thief attacks {p.name}.")
            self.do_fight()

    def do_fight(self):
        p = self.p
        if rnd() <= CH_THIEF_TOUGH and p.game.thief is not None:
            tough_thief = True
            thief = p.game.thief
            p.show(f'Thief: "Can you stop the infamous {thief.name}?"')
        else:
            tough_thief = False
            thief = fighter_factory.new_thief(tough=False)
        p.pak()
        if rnd() <= CH_THIEF_ARMED:
            thief.arm("knife")
        if self.p.fight(thief):
            p.show('{}: "Now let\'s go to the police..."'.format(self.p.name))
            if tough_thief:
                p.add_accompl("Beat Tough Thief")
                p.game.thief = None
                p.game.unregister_fighter(thief)
        else:
            p.show('{}: "Can\'t stop me, can you? Ha-ha-ha!"'.format(thief.name))


class Weirdo(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_WEIRDO

    def run(self):
        p = self.player
        item = random.choice(items.MOCK_ITEMS)
        reward = items.SUPER_BOOSTER
        t = 'A very strange-looking man bumps into {}.\nWeirdo: "Quick! I need a {}!"'.format(
            p.name, item
        )
        p.show(t)
        p.log(f"Meets a strange-looking man asking for {item}.")
        if p.check_item(item):
            t = (
                '{0}: "Here, I happen to have one."\nWeirdo: "THANKS! I\'ll give you this in return."'
                "\nWith these words, the strange man rushes off. {0} is left with a {1} in his hands, and a "
                "strong feeling of confusion.".format(p.name, reward)
            )
            p.show(t)
            p.log(f"Trades {item} for a {reward}.")
            p.lose_item(item)
            p.obtain_item(reward)
            p.add_accompl("Weird Item")
            p.change_stat("super_herbs_obtained", 1)
        else:
            t = f"{p.name}: \"Sorry, I can't help you."
            p.show(t)
        p.pak()


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


class GGambler(Guaranteed, Gambler):
    pass


class GMerchant(Guaranteed, Merchant):
    pass


class GRobbers(Guaranteed, Robbers):
    pass


# all encounters; can happen regardless of the day action chosen (except 'Rest', with no encounters)
ENC_LIST = [
    Ambush,
    Beggar,
    BookSeller,
    Brawler,
    Challenger,
    ContinueStory,
    Craftsman,
    Criminal,
    Drunkard,
    Extorters,
    FatGirl,
    FindItem,
    FriendMatch,
    Gambler,
    Gossip,
    HelpPolice,
    LoseItem,
    MasterTrial,
    Merchant,
    OverhearConversation,
    PlayerMatch,
    PrizeFighting,
    Robbers,
    RobbingSomeone,
    SchoolBullying,
    SchoolChallenge,
    StreetPerformer,
    Students,
    Thief,
    Weirdo,
    WiseMan,
]

# todo reimplement enc extra chances with random.choices


# extra chance of getting these encounters when choosing the corresponding day actions
BUY_ITEMS_ENCS = (
        [Craftsman] * 2 + [BookSeller] * 2 + [GMerchant] * 3 + [Merchant] * 3 + [StreetPerformer] * 2
)
FIGHT_CRIME_ENCS = (
    [GRobbers] + [Criminal] * 4 + [Extorters] * 7 + [HelpPolice] * 7 + [RobbingSomeone] * 7
)
HELP_POOR_ENCS = [GBeggar] * 3 + [Beggar] * 10 + [WiseMan] * 5
PICK_FIGHTS_ENCS = (
        [Brawler] * 3 + [GChallenger] + [Challenger] * 3 + [FriendMatch] * 3 + [PlayerMatch] * 3
)
PRACTICE_SCHOOL_ENCS = [MasterTrial] * 3 + [SchoolChallenge] * 3 + [SchoolBullying]
SEEDY_PLACES_ENCS = (
    [GGambler] * 1
    + [GDrunkard] * 1
    + [Gambler] * 3
    + [Drunkard] * 3
    + [OverhearConversation] * 3
    + [PrizeFighting] * 3
)
WALK_ENCS = (
    [ContinueStory] * 3
    + [OverhearConversation] * 3
    + [StreetPerformer] * 3
    + [Merchant] * 3
    + [Gossip] * 3
    + [Weirdo] * 3
)
WORK_ENCS = []


def random_encounters(p, encs=None):
    if encs is None:
        encs = ENC_LIST[:]
    random.shuffle(encs)

    for e in encs:
        if p.inactive:
            return
        e(p)


class EncControl:
    def __init__(self, game):
        self.g = self.game = game

    def rand_enc(self, encs=None):
        p = self.g.current_player
        random_encounters(p, encs)

    def run_enc(self, enc_name_string, test=False):
        p = self.g.current_player
        exec(f"{enc_name_string}(p, test={test})")
