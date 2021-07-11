from ...mechanics import experience


RATIO_NO_RISK = 0
RATIO_VERY_LOW_RISK = 0.5
RATIO_LOW_RISK = 0.8
RATIO_FAIR_FIGHT = 0.95
RATIO_RISKY = 1.1
RATIO_VERY_RISKY = 1.5
RATIO_EXTREMELY_RISKY = 2


class ExpWorthUser:
    exp_yield = 0

    # override by child class:
    act_allies = None
    act_targets = None
    level = 0

    def get_allies_power(self):  # todo: use this for AI, high-prio
        return sum([f.get_exp_worth() for f in self.act_allies])

    def get_exp_worth(self):
        """Return how many experience points the fighter is 'worth'."""
        return experience.fighter_to_exp(self)

    def get_opponents_power(self):  # todo: use this for AI, high-prio
        return sum([f.get_exp_worth() for f in self.act_targets])

    def get_rel_strength(self, *opp, allies=None):
        """Return ratio (number, the lower the weaker) and legend (string, e.g. 'very risky')"""
        pwr = sum([op.get_exp_worth() for op in opp])
        own_pwr = self.get_exp_worth()
        if allies:
            own_pwr += sum([al.get_exp_worth() for al in allies])
        ratio = round(pwr / own_pwr, 2)
        table = (
            (RATIO_EXTREMELY_RISKY, 'impossible'),
            (RATIO_VERY_RISKY, 'very risky'),
            (RATIO_RISKY, 'risky'),
            (RATIO_FAIR_FIGHT, 'fair fight'),
            (RATIO_LOW_RISK, 'low risk'),
            (RATIO_VERY_LOW_RISK, 'very low risk'),
            (RATIO_NO_RISK, 'no risk'),
        )
        for threshold, legend in table:
            if ratio >= threshold:
                return ratio, legend
