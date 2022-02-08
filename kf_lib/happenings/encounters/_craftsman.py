from ._base_encounter import BaseEncounter
from ._utils import check_feeling_greedy
from ...actors.fighter_factory import new_craftsman
from ...things import items
from ...utils.utilities import rnd


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
        t = (
            f'{p.name} meets a craftsman.\n'
            'Craftsman: "Ah, a martial artist! You\'re in luck! I\'m selling this excellent' 
            f'{item} ({descr}). It\'s only {price} coins! Don\'t worry, if you don\'t have enough' 
            'money right now, you can pay the rest later. Will you buy it?"'
        )
        p.show(t)
        p.log("Meets a craftsman.")
        is_fake_mannequin = False
        luck = p.check_luck()
        if luck == 1:
            t = (
                'Craftsman: "A spark from the soul is worth more than a thousand pieces of gold. '
                'I see that you are fated to become one of the greats. Let us spar and then you '
                f'can have my {item} for free!"'
            )
            p.show(t)
            p.pak()
            c = new_craftsman()
            p.spar(c)
            p.show('Craftsman: "What a good sparring session!"')
            price = 0
            p.buy_item(item, price)
            items.use_item(item, p)
            p.pak()
            return
        elif luck == -1:
            is_fake_mannequin = True
        if p.buy_item_or_not() and not check_feeling_greedy(p):
            p.buy_item(item, price)
            if is_fake_mannequin:
                p.show(f'However, the {item} turns out to be of very shoddy quality. '
                       f'It breaks immediately as {p.name} tries a few of his moves on it. '
                       'Too bad the craftsman has vanished in thin air!')
                p.pak()
                p.lose_item(item)
            else:
                items.use_item(item, p)
