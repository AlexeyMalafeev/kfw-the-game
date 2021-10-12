from ._base_fighter import BaseFighter
from ...fighting.fight import fight
from ...utils.utilities import mean


class FightUtils(BaseFighter):
    def fight(self, en, allies=None, en_allies=None, *args, **kwargs):
        return fight(self, en, allies, en_allies, *args, **kwargs)

    # todo get_wellness is not used
    def get_wellness(self):
        """This can be used as a simple metric for how 'well' the fighter is."""
        # todo make this metric weighted, as hp is more important than stamina / qp
        return mean((self.hp / self.hp_max, self.stamina / self.stamina_max, self.qp / self.qp_max))

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
        from kf_lib.fighting.fight import spar as f_spar

        return f_spar(
            self, en, allies, en_allies, auto_fight, af_option, hide_stats, environment_allowed
        )
