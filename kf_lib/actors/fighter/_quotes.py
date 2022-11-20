import random
from abc import ABC

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.actors import quotes


class QuoteMethods(FighterAPI, ABC):
    quotes = 'fighter'

    def say_prefight_quote(self) -> bool:
        """Returning True/False is used for making pauses correctly."""
        pool = quotes.PREFIGHT_QUOTES.get(self.quotes, None)
        if pool is not None:
            q = random.choice(pool)
            self.current_fight.show(f'{self.name}: "{q}"')
            return True
        else:  # this is important for correctly making pauses after quotes
            return False

    def say_win_quote(self) -> None:
        pool = quotes.WIN_QUOTES.get(self.quotes, None)
        if pool is not None:
            q = random.choice(pool)
            self.current_fight.show(f'{self.name}: "{q}"')
