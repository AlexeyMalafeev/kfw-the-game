import random


from ._base_fighter import BaseFighter
from kf_lib.actors import quotes


class QuoteMethods(BaseFighter):
    quotes = 'fighter'

    def say_prefight_quote(self):
        pool = quotes.PREFIGHT_QUOTES.get(self.quotes, None)
        if pool is not None:
            q = random.choice(pool)
            self.current_fight.show(f'{self.name}: "{q}"')
            return True
        else:  # this is important for correctly making pauses after quotes
            return False

    def say_win_quote(self):
        pool = quotes.WIN_QUOTES.get(self.quotes, None)
        if pool is not None:
            q = random.choice(pool)
            self.current_fight.show(f'{self.name}: "{q}"')
