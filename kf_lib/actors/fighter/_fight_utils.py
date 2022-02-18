from kf_lib.fighting.fight import fight, spar
from ._base_fighter import BaseFighter


class FightUtils(BaseFighter):
    def fight(self, en, allies=None, en_allies=None, *args, **kwargs):
        return fight(self, en, allies, en_allies, *args, **kwargs)

    def spar(
        self,
        en,
        allies=None,
        en_allies=None,
        auto_fight=False,
        af_option=True,
        hide_stats=False,
        environment_allowed=True,
    ):
        return spar(
            self, en, allies, en_allies, auto_fight, af_option, hide_stats, environment_allowed
        )
