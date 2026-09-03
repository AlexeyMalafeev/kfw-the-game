import random

from kf_lib.actors import fighter_factory
from kf_lib.things import items
from kf_lib.utils import rnd, rndint
from ._base_encounter import BaseEncounter
from ._utils import check_feeling_greedy, check_scary_fight, set_up_weapon_fight


# constants
# encounter chances
ENC_CH_STREET_PERFORMER = 0.03

# misc chances
CH_PERFORMER_SELLS_GOOD_ITEM = 0.5
CH_STREET_PERFORMER_ARMED = 0.3

# money
MONEY_PERFORMER = (40, 50, 60)

# moves
PERFORMER_LOSE_MOVE_TIERS = (2, 4)
# PERFORMER_WIN_MOVE_TIERS = (4, 6)  # decided not to implement

# numbers
NUM_PERFORMER_THUGS = (2, 5)

# misc
PERFORMER_EXP_REWARD = 50


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
            and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0])
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
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
            p.gain_rep(n - 1)
            if p.fight(thugs[0], allies=[c], en_allies=thugs[1:]):
                self.reward()



