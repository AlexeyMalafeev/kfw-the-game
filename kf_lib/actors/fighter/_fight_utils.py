from abc import ABC
from typing import List

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.fighting.fight import fight, spar


class FightUtils(FighterAPI, ABC):
    def fight(
        self,
        en: FighterAPI,
        allies: List[FighterAPI] = None,
        en_allies: List[FighterAPI] = None,
        *args,
        **kwargs,
    ) -> bool:
        return fight(self, en, allies, en_allies, *args, **kwargs)

    def spar(
        self,
        en: FighterAPI,
        allies: List[FighterAPI] = None,
        en_allies: List[FighterAPI] = None,
        auto_fight: bool = False,
        af_option: bool = True,
        hide_stats: bool = False,
        environment_allowed: bool = True,
    ) -> bool:
        return spar(
            self, en, allies, en_allies, auto_fight, af_option, hide_stats, environment_allowed
        )
