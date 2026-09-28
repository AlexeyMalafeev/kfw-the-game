from kf_lib.actors.fighter_factory import new_craftsman
from kf_lib.i18n import _, tr_fighter_name, tr_name
from kf_lib.things import items
from kf_lib.utils import rnd
from ._base_encounter import BaseEncounter
from ._utils import check_feeling_greedy


ENC_CH_CRAFTSMAN = 0.01
MONEY_MANNEQUIN = 500


class Craftsman(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_CRAFTSMAN and not self.p.check_item(items.MANNEQUIN)

    def run(self):
        p = self.player
        item = items.MANNEQUIN
        descr = items.get_item_descr(item)
        price = MONEY_MANNEQUIN
        t = _(
            '{name} meets a craftsman.\n'
            'Craftsman: "Ah, a martial artist! You\'re in luck! I\'m selling this excellent '
            '{item} ({descr}). It\'s only {price} coins! Don\'t worry, if you don\'t have enough '
            'money right now, you can pay the rest later. Will you buy it?"'
        ).format(
            name=tr_fighter_name(p.name), item=tr_name(item), descr=descr, price=price
        )
        p.show(t)
        p.log(_("Meets a craftsman."))
        if p.buy_item_or_not() and not check_feeling_greedy(p):
            luck = p.check_luck()
            if luck == 1:
                t = _(
                    'Craftsman: "A spark from the soul is worth more than a thousand pieces of '
                    'gold. I see that you are fated to become one of the greats. Let us spar and '
                    'then you can have my {item} for free!"'
                ).format(item=tr_name(item))
                p.show(t)
                p.pak()
                c = new_craftsman()
                p.spar(c)
                p.show(_('Craftsman: "What a good sparring session!"'))
                p.buy_item(item, 0)
                p.pak()
                return
            p.buy_item(item, price)
            if luck == -1:
                p.show(
                    _(
                        'However, the {item} turns out to be of very shoddy quality. '
                        'It breaks immediately as {name} tries a few of his moves on it. '
                        'Too bad the craftsman has vanished in thin air!'
                    ).format(item=tr_name(item), name=tr_fighter_name(p.name))
                )
                p.lose_item(item)
                p.pak()
