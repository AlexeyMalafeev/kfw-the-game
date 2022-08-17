import random

from kf_lib.happenings.encounters._base_encounter import BaseEncounter
from kf_lib.happenings.encounters._utils import check_feeling_greedy
from kf_lib.kung_fu import moves
from kf_lib.constants import experience
from kf_lib.utils import rnd


BOOK_MOVE_TIER_PENALTY = 1
BOOK_MOVE_TIER_BONUS = 1
CH_BOOK_RUBBISH = 0.3
CH_BOOK_MOVE = 0.5  # given book is not rubbish, so (1 - p(not_rubbish)) * p(move)
ENC_CH_BOOK_SELLER = 0.02  # todo move to constants module
MONEY_BOOK = 100


class BookSeller(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_BOOK_SELLER

    def run(self):
        p = self.player
        price = MONEY_BOOK
        t = (
            f'{p.name} meets a traveling book seller.'
            '\nBook Seller: "Ah, a martial artist! I\'m selling this wonderful kung-fu book for '
            f'only {price} coins! Its secret and powerful techniques will make you a legendary '
            'fighter! What say you?" Buy it?'
        )
        p.show(t)
        p.log("Meets a book seller.")
        if p.buy_item_or_not() and not check_feeling_greedy(p):
            if not p.check_money(price):
                p.show(f"{p.name} doesn't have enough money.")
            else:
                p.pay(price)
                if rnd() < CH_BOOK_RUBBISH:  # todo BAD LUCK only
                    t = "The book turns out to be complete rubbish!"
                    p.write(t)
                else:  # todo weak/pathetic
                    if rnd() < CH_BOOK_MOVE:
                        tier = max(1, p.get_move_tier_for_lv - BOOK_MOVE_TIER_PENALTY)
                        features = p.fav_move_features.copy()
                        features.add(random.choice(['weak', 'pathetic']))
                        move = moves.get_rand_move(f=p, tier=tier, features=features)
                        p.learn_move(move)
                    else:
                        exp = random.randint(*experience.BOOK_EXP)
                        p.gain_exp(exp)
                    # todo LUCKY case
            p.pak()
