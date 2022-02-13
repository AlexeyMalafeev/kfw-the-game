from ._base_fighter import BaseFighter


RATIO_NO_RISK = 0
RATIO_VERY_LOW_RISK = 0.5
RATIO_LOW_RISK = 0.8
RATIO_FAIR_FIGHT = 0.95
RATIO_RISKY = 1.1
RATIO_VERY_RISKY = 1.5
RATIO_EXTREMELY_RISKY = 2

RISK_DESCR_TABLE = (  # must be sorted high to low
    (RATIO_EXTREMELY_RISKY, 'impossible'),
    (RATIO_VERY_RISKY, 'very risky'),
    (RATIO_RISKY, 'risky'),
    (RATIO_FAIR_FIGHT, 'fair fight'),
    (RATIO_LOW_RISK, 'low risk'),
    (RATIO_VERY_LOW_RISK, 'very low risk'),
    (RATIO_NO_RISK, 'no risk'),
)


class ExpMethods(BaseFighter):
    def get_allies_power(self):  # todo: use get_allies_power for AI, high-prio
        return sum([f.get_exp_worth() for f in self.act_allies])

    def get_exp_worth(self):  # todo check that get_exp_worth still makes sense
        """Return how many experience points the fighter is 'worth'."""
        exp = (10 + (self.strength * self.agility * self.speed * self.health) * 0.01 * 3 +
               len(self.techs) * 3)
        if self.weapon:
            w = self.weapon
            w_mult = w.get_exp_mult()
            exp *= w_mult
        exp = round(exp)
        return exp

    def get_opponents_power(self):  # todo: use get_opponents_power for AI, high-prio
        return sum([f.get_exp_worth() for f in self.act_targets])

    def get_rel_strength(self, *opp, allies=None):
        """Return ratio (number, the lower the weaker) and legend (string, e.g. 'very risky')"""
        pwr = sum([op.get_exp_worth() for op in opp])
        own_pwr = self.get_exp_worth()
        if allies:
            own_pwr += sum([al.get_exp_worth() for al in allies])
        ratio = round(pwr / own_pwr, 2)
        for threshold, legend in RISK_DESCR_TABLE:
            if ratio >= threshold:
                return ratio, legend
