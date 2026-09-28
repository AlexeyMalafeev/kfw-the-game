import random

from kf_lib.actors import fighter_factory
from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name
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
            _('{name} sees a travelling kung-fu master demonstrating his skills in the '
              'street.').format(name=tr_fighter_name(p.name))
        )
        p.log(_('Sees a kung-fu master demonstrating his skills in the street.'))
        # challenge, protect from thugs, buy items
        func = random.choice((self.challenge, self.challenge, self.sell, self.sell, self.thugs))
        func()

    def challenge(self):
        p = self.player
        c = self.performer
        cost = random.choice(MONEY_PERFORMER)
        p.show(
            _('{name}: "Now, who dares to challenge me? It costs {cost} coins - if you win, '
              'you\'ll get twice as much!"').format(
                name=tr_fighter_name(c.name), cost=cost
            )
        )
        p.log(_('The master offers a challenge.'))
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
                p.show(
                    _('{name}: "I didn\'t think I could lose..."').format(
                        name=tr_fighter_name(c.name)
                    )
                )
            else:
                p.show(
                    _('{name}: "Hmph! No one can beat me."').format(
                        name=tr_fighter_name(c.name)
                    )
                )
                # todo only if lucky
                p.show(
                    _('{name}: "What amazing kung-fu! Even though I lost, I feel that my '
                      'technique has improved"').format(name=tr_fighter_name(p.name))
                )
                p.pak()
                p.learn_move_from(c)
            p.pak()
        else:
            # disarm player!!!
            p.disarm()
            p.log(_('Chooses to ignore the challenge.'))

    def reward(self):
        p = self.player
        c = self.performer
        rewards = "iiit"
        reward = random.choice(list(rewards))
        p.show(
            _('{name}: "I see that you are a very brave young man.').format(
                name=tr_fighter_name(c.name)
            )
        )
        if reward == "i":
            item = items.get_random_item()
            p.show(
                _('Please accept this {item} as a token of my gratitude."').format(
                    item=tr_name(item)
                )
            )
            p.obtain_item(item)
            p.pak()
        elif reward == "t":
            p.show(
                _('Your kung-fu is very good; however, I can help you improve it."\n'
                  '{master} teaches {name} some of his moves.').format(
                    master=tr_fighter_name(c.name), name=tr_fighter_name(p.name)
                )
            )
            p.pak()
            p.learn_move_from(c)

    def sell(self):
        p = self.player
        c = self.performer
        price = random.choice(MONEY_PERFORMER)
        p.show(
            _('{name}: "Now, if you want to become as strong as I am and cure all your '
              'diseases, buy this Golden Magnificent Elixir. It\'s only {price} coins".\n'
              'This seems a little fishy... Could be the real thing though. Buy it?').format(
                name=tr_fighter_name(c.name), price=price
            )
        )
        p.log(_('The master offers to buy Golden Magnificent Elixir.'))
        if not p.check_money(price):
            p.show(
                _("{name} doesn't have enough money.").format(
                    name=tr_fighter_name(p.name)
                )
            )
            p.pak()
        elif p.buy_item_or_not() and not check_feeling_greedy(p):
            if rnd() <= CH_PERFORMER_SELLS_GOOD_ITEM:
                item = items.get_random_item()
            else:
                item = items.get_random_mock_item()
                p.change_stat("mock_items_bought", 1)
            p.show(
                _('{name} collects the money from all those willing to buy his Elixir and '
                  'quickly walks away.\n'
                  'Later, the "Golden Magnificent Elixir" turns out to be a simple {item}.'
                  ).format(name=tr_fighter_name(c.name), item=tr_name(item))
            )
            p.log(
                _('The Elixir turns out to be a {item}.').format(item=tr_name(item))
            )
            p.buy_item(item, price)
            p.pak()

    def thugs(self):
        p = self.player
        c = self.performer
        n = rndint(*NUM_PERFORMER_THUGS)
        p.show(
            ngettext(
                'Suddenly, {} thug appears and attacks the master. Apparently, they are after '
                'his money. Help him?',
                'Suddenly, {} thugs appear and attack the master. Apparently, they are after '
                'his money. Help him?',
                n,
            ).format(n)
        )
        p.log(ngettext('{} thug attacks the master.', '{} thugs attack the master.', n).format(n))
        thugs = fighter_factory.new_thug(weak=True, n=n)
        opp_strength = p.get_rel_strength(*thugs, allies=[c])
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
            p.gain_rep(n - 1)
            if p.fight(thugs[0], allies=[c], en_allies=thugs[1:]):
                self.reward()



