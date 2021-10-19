from ._base_fighter import BaseFighter


class FightAIMethods(BaseFighter):

    def set_fight_ai(self, ai_class, write_log=False):
        self.fight_ai = ai_class(self, write_log)
