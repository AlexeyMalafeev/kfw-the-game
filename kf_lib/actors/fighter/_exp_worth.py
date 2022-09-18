from abc import ABC
from typing import Iterable, Optional, Tuple

from kf_lib.actors.fighter._abc import FighterAPI


class ExpMethods(FighterAPI, ABC):
    RATIO_NO_RISK = 0.0
    RATIO_VERY_LOW_RISK = 0.5
    RATIO_LOW_RISK = 0.8
    RATIO_FAIR_FIGHT = 0.95
    RATIO_RISKY = 1.1
    RATIO_VERY_RISKY = 1.5
    RATIO_EXTREMELY_RISKY = 2.0
    RISK_DESCR_TABLE = (  # must be sorted high to low
        (RATIO_EXTREMELY_RISKY, 'impossible'),
        (RATIO_VERY_RISKY, 'very risky'),
        (RATIO_RISKY, 'risky'),
        (RATIO_FAIR_FIGHT, 'fair fight'),
        (RATIO_LOW_RISK, 'low risk'),
        (RATIO_VERY_LOW_RISK, 'very low risk'),
        (RATIO_NO_RISK, 'no risk'),
    )

    # todo use get_allies_power for AI, high-prio
    def get_allies_power(self) -> int:
        return sum([f.get_exp_worth() for f in self.act_allies])

    # todo check that get_exp_worth still makes sense
    def get_exp_worth(self) -> int:
        """Return how many experience points the fighter is 'worth'."""
        exp = (10 + (self.strength * self.agility * self.speed * self.health) * 0.01 * 3 +
               len(self.techs) * 3)
        if self.weapon:
            w = self.weapon
            w_mult = w.get_exp_mult()
            exp *= w_mult
        exp = round(exp)
        return exp

    # todo: use get_opponents_power for AI, high-prio
    def get_opponents_power(self) -> int:
        return sum([f.get_exp_worth() for f in self.act_targets])

    def get_rel_strength(
        self,
        *opp: FighterAPI,
        allies: Optional[Iterable[FighterAPI]] = None,
    ) -> Tuple[float, str]:
        """
        Return opp_to_self_pwr_ratio (number, the lower the weaker) and legend
        (string, e.g. 'very risky')
        """
        pwr = sum([op.get_exp_worth() for op in opp])
        own_pwr = self.get_exp_worth()
        if allies is not None:
            own_pwr += sum([al.get_exp_worth() for al in allies])
        opp_to_self_pwr_ratio = round(pwr / own_pwr, 2)
        for threshold, legend in self.RISK_DESCR_TABLE:
            if opp_to_self_pwr_ratio >= threshold:
                return opp_to_self_pwr_ratio, legend
