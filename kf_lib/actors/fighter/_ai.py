from ...ai.fight_ai import DefaultFightAI
from ._base_fighter import BaseFighter


class FightAIMethods(BaseFighter):
    def set_fight_ai(self, ai_class=None, write_log=False):
        if ai_class is None:
            ai_class = DefaultFightAI
        self.fight_ai = ai_class(self, write_log)
