import random

from kf_lib.actors import fighter_factory
from kf_lib.things import items
from kf_lib.utils import add_article, rnd, rndint
from ._base_encounter import BaseEncounter, Guaranteed
from ._utils import check_feeling_greedy, check_scary_fight, get_escape_chance, \
    try_enemy, try_escape


# constants
# encounter chances
ENC_CH_CRIMINAL = 0.03

# misc chances
CH_CONVICT_ARMED = 0.35
CH_ROBBER_ARMED = 0.35
CH_ROBBER_ENEMY = 0.1
CH_THIEF_ARMED = 0.3
CH_THIEF_ESCAPES = 0.3
CH_THIEF_TOUGH = 0.1
CH_THUG_ENEMY = 0.1

# lines
LINES_ROBBER = (
    "Hey, I really need {} coins. Do you think you can help me out?",
    "If you don't give me {} coins, you'll need a doctor, and a good one!",
    "Hey you! This is my territory. Entering is free, but leaving in one piece costs {} coins.",
    "You know, I need {} coins to buy medicine for my sick grandma. Wanna share?",
    "It is important to share what you have with others. Pay {} coins and you are free to go.",
)

# money
MONEY_CONVICT_REWARD_MULT = (10, 15, 20, 25, 30, 40)
MONEY_GIVE_ROBBERS = (40, 50, 60, 80, 100, 120, 130, 150, 180)
MONEY_SHOP_BREAKAGES = (30, 50, 70)
MONEY_THIEF_STEALS = (25, 50, 75, 100, 200)

# numbers
NUM_EXTORTERS = (2, 6)
NUM_POLICE_VS_THUGS = (2, 4)
NUM_THUGS_VS_POLICE = (+1, +4)  # always more than the police
NUM_ROBBERS_CROWD = (5, 8)
NUM_ROBBERS_GROUP = (2, 4)

# reputation
REP_PEN_BREAK_NOT_PAY = -1


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
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
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
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
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
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
            p.gain_rep(num_en - num_al)
            p.check_help(allies=False, master=False, school=False)
            if p.fight(en[0], al, en[1:]):
                p.show('Police Officer: "Thank you very much for your help!"')
                p.pak()
        else:
            p.log("Does not help the police.")



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
            self.p.show(f"He is armed with {add_article(self.r.weapon.name)}.")
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
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
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



class GRobbers(Guaranteed, Robbers):
    pass



