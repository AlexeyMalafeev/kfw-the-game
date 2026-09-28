import random

from kf_lib.i18n import _, tr_fighter_name, tr_name
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
        p.show(
            _('{name} accidentally finds an item: {item}.').format(
                name=tr_fighter_name(p.name), item=tr_name(it)
            )
        )
        p.log(_('Accidentally finds an item: {item}.').format(item=tr_name(it)))
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
        p.show(
            _('{name} accidentally loses his {item}.').format(
                name=tr_fighter_name(p.name), item=tr_name(it)
            )
        )
        p.log(_('Accidentally loses his {item}.').format(item=tr_name(it)))
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
        t = (
            _('{name} meets a street merchant.\n'
              'Merchant: "Please buy this {item}{descr_s}!"\n'
              'Buy it for {price} coins?').format(
                name=tr_fighter_name(p.name),
                item=tr_name(item),
                descr_s=descr_s,
                price=price,
            )
        )
        p.show(t)
        p.log(_('Meets a street merchant.'))
        if not p.check_money(price):
            p.show(
                _("{name} doesn't have enough money.").format(
                    name=tr_fighter_name(p.name)
                )
            )
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
        t = (
            _('A very strange-looking man bumps into {name}.\n'
              'Weirdo: "Quick! I need a {item}!"').format(
                name=tr_fighter_name(p.name), item=tr_name(item)
            )
        )
        p.show(t)
        p.log(
            _('Meets a strange-looking man asking for {item}.').format(
                item=tr_name(item)
            )
        )
        if p.check_item(item):
            t = (
                _('{name}: "Here, I happen to have one."\n'
                  'Weirdo: "THANKS! I\'ll give you this in return."\n'
                  'With these words, the strange man rushes off. {name} is left with a {reward} '
                  'in his hands, and a strong feeling of confusion.').format(
                    name=tr_fighter_name(p.name), reward=tr_name(reward)
                )
            )
            p.show(t)
            p.log(
                _('Trades {item} for a {reward}.').format(
                    item=tr_name(item), reward=tr_name(reward)
                )
            )
            p.lose_item(item)
            p.obtain_item(reward)
            p.add_accompl("Weird Item")
            p.change_stat("super_herbs_obtained", 1)
        else:
            t = _('{name}: "Sorry, I can\'t help you.').format(
                name=tr_fighter_name(p.name)
            )
            p.show(t)
        p.pak()



class GMerchant(Guaranteed, Merchant):
    pass



