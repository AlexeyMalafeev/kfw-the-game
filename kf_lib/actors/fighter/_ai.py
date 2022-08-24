from typing import Optional, Type


from kf_lib.ai.fight_ai import BaseAI, DefaultFightAI
from kf_lib.actors.fighter._abc import FighterABC


class FightAIMethods(FighterABC):
    def set_fight_ai(self,
                     ai_class: Optional[Type[BaseAI]] = None,
                     write_log: bool = False,
                     ):
        if ai_class is None:
            ai_class = DefaultFightAI
        self.fight_ai = ai_class(self, write_log)
