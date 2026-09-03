import random

from kf_lib.things import items
from kf_lib.utils import rnd
from ._base_encounter import BaseEncounter, Guaranteed
from ._utils import check_feeling_greedy


# constants
# encounter chances
ENC_CH_MERCHANT = 0.04
ENC_CH_WEIRDO = 0.02


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



class GMerchant(Guaranteed, Merchant):
    pass



