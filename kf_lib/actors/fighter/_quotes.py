import random

from ...actors import quotes


class QuoteUser:
    quotes = 'fighter'

    # override by child class:
    current_fight = None
    name = ''

    def say_prefight_quote(self):
        pool = quotes.PREFIGHT_QUOTES.get(self.quotes, None)
        if pool is not None:
            q = random.choice(pool)
            self.current_fight.show(f'{self.name}: "{q}"')
            return True
        else:
            return False

    def say_win_quote(self):
        pool = quotes.WIN_QUOTES.get(self.quotes, None)
        if pool is not None:
            q = random.choice(pool)
            self.current_fight.show(f'{self.name}: "{q}"')