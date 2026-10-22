"""Rule experiments of the 2026-10 balance pass, as runtime monkeypatches.

Not game code: each function below patches `Fighter` to try a rule change
without editing the engine. Use them with
    run_test_fb.py --variants rule_variants.py:Gc+Hb25     (100k harness)
    run_test_tech_ab.py "Advanced Guard" --variants rule_variants.py:Gs
apply('A+B') applies several. Measured 2026-10-22 on top of commit 9b7bb7f
(dodge buff dodge-only, qi regen 10%), 100k harness each; the full tables are
in `tests/balance experiments 2026-10-22.txt`. Diff% = the harness's
winner-vs-loser correlation; a tech that does nothing scores about -9 to -13.

Guard (baseline: guard buff -11.8, Advanced Guard -8.5, fights 62.7 s):
  Ga   Guard doubles counter chance until the next turn       -> no effect
  Gb   Guard x1.5 -> x2.0                                     -> no effect
  Gc   Guard also recovers 10 stamina + 10 qi (x guard bonus) -> fights 53.9 s,
       Guard 29% -> 21% of actions; guard techs unchanged
  Gs   stored guard: the bonus waits for the next incoming strike instead of
       expiring at the fighter's next turn                    -> guard -8.2
       (Gs+Gc: guard -9.4, fights 56.8 s)
  (why a/b fail: the default AI guards only when it can't attack, and 92% of
  Guard turns receive no strike at all)
Counters (baseline: counters buff -12.5, Retaliative Blows -5.5, 0.59/fight):
  Ca   counter with the best move (max atk_pwr * to_hit)       -> no effect
  Cb   counter-tech fighters also counter after a partial block -> no effect
  Cx3, Cx5  counter techs' counter_chance_mult x3 / x5          -> -10.9 / -11.3
  Cfree        counters cost nothing                            -> -11.9
  Cfree+Cx3, Chalf+Cx3                                          -> -8.5 / -10.5
  (why: a counter needs a full dodge/block (28% of incoming strikes) and a ~15%
  roll — ~0.3 counters per fighter per fight, so per-counter changes barely show)
Qi, qi techs only (baseline: qi buff -3.6, Lotus Stance +2.6):
  Qb   qi shield: a partial block spends qi (1 QP per 2 HP)      -> qi -1.1
  Qc   qi-charged strikes, atk x (1 + 0.3 * qp / qp_max)        -> qi +16.9 (too strong)
  Qc10 the same at 0.1                                           -> qi +3.0
  Qb+Qc10                                                        -> qi +7.2
Health (baseline: health -2.0, strength +2.1, agility +1.8, speed -1.9):
  Ha   block power from (strength + health) / 2                  -> health -1.7
  Hb   toughness and stamina from health, not level              -> health +5.8 (too strong)
  Hb25 / Hb50  25% / 50% of them from health                     -> health +0.2 / +2.2
  HbT / HbS    only toughness / only stamina from health         -> +3.3 (fights 79 s) / +1.9
  Hc   max qi scaled by health relative to the level average     -> no added effect
  (Hb25 side effects: 'health' techs +3.4 -> +11.8; speed -1.9 -> -2.7)
"""
import math

from kf_lib.actors.fighter import Fighter as F
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.ui import yellow
from kf_lib.utils import rnd

H0, H_PER_LV = 3.449, 0.267  # health_full ~ H0 + H_PER_LV * level (generated fighters)


def is_qi(f):
    return f.qp_gain_mult > 1.0 or f.qp_max_mult > 1.0


def Ga():
    og, os_, ot = F.guard, F.start_fight_turn, F.try_counter
    def guard(self):
        og(self)
        self._guarding = True
    def start_fight_turn(self):
        self._guarding = False
        os_(self)
    def try_counter(self):
        if getattr(self, '_guarding', False):
            c = self.counter_chance
            self.counter_chance = c * 2
            try:
                ot(self)
            finally:
                self.counter_chance = c
        else:
            ot(self)
    F.guard, F.start_fight_turn, F.try_counter = guard, start_fight_turn, try_counter


def Gb():
    F.GUARD_POWER = 2.0


def Ca():
    def do_counter(self):
        cand_moves = self.get_av_moves(attack_moves_only=True)
        if cand_moves:
            if self.fight_stats is not None:
                self.fight_stats['counters'] += 1
            self.current_fight.display(yellow(_('+COUNTER!+')))
            def score(m):
                self.calc_atk(m)
                return self.atk_pwr * self.to_hit
            self.action = max(cand_moves, key=score)
            self.current_fight.display(f'{tr_fighter_name(self.name)}: {self.action.display_name}')
            self.try_strike()
            self.apply_move_cost()
    F.do_counter = do_counter


def Cb():
    ot = F.try_counter
    def try_counter(self):
        atkr = self.target
        partial_block = self.defended and atkr.dam > 0
        if (partial_block and self.counter_chance_mult > 1.0 and self.hp > 0
                and rnd() <= self.counter_chance):
            self.do_counter()
        else:
            ot(self)
    F.try_counter = try_counter


def Ha():
    oc = F.calc_dfs
    def calc_dfs(self):
        oc(self)
        if not self.check_status('shocked') and self.strength_full:
            self.dfs_pwr *= (self.strength_full + self.health_full) / 2 / self.strength_full
    F.calc_dfs = calc_dfs


def Hb():
    orf = F.refresh_dependent_atts
    def refresh(self):
        orf(self)
        h = self.health_full
        # level-based: toughness 3 * (lv - 1), stamina (50 + 10 * lv) * mult
        self.toughness = max(0, round(3 / H_PER_LV * (h - H0 - H_PER_LV)))
        self.stamina_max = max(30, round((50 + 10 / H_PER_LV * (h - H0)) * self.stamina_max_mult))
        self.stamina_gain = round(self.stamina_max * self.STAMINA_PORTION_RESTORED_PER_TURN
                                  * self.stamina_gain_mult)
        self.stamina = min(self.stamina, self.stamina_max)
    F.refresh_dependent_atts = refresh


def Hc():
    orf = F.refresh_dependent_atts
    def refresh(self):
        orf(self)
        rel = self.health_full / (H0 + H_PER_LV * self.level)
        self.qp_max = round(self.qp_max * rel)
        self.qp_gain = round(self.qp_max * self.QP_PORTION_RESTORED_PER_TURN * self.qp_gain_mult)
        self.qp = min(self.qp, self.qp_max)
    F.refresh_dependent_atts = refresh


QI_SHIELD_HP_PER_QP = 2


def Qb():
    od = F.defend
    def defend(self):
        od(self)
        atkr = self.target
        if self.defended and atkr.dam > 0 and self.qp > 0 and is_qi(self):
            absorb = min(atkr.dam, self.qp * QI_SHIELD_HP_PER_QP)
            self.qp -= math.ceil(absorb / QI_SHIELD_HP_PER_QP)
            atkr.dam = round(atkr.dam - absorb)
            if not atkr.dam:  # the shield completed the block
                if self.fight_stats is not None:
                    self.fight_stats['full_blocks'] += 1
                atkr.cause_off_balance(brief=True)
    F.defend = defend


QI_CHARGE = 0.3


def Qc():
    oa = F.calc_atk
    def calc_atk(self, action):
        oa(self, action)
        if is_qi(self) and self.qp_max:
            self.atk_pwr *= 1 + QI_CHARGE * self.qp / self.qp_max
    F.calc_atk = calc_atk


def apply(names):
    for name in filter(None, names.split('+')):
        globals()[name]()


#   Gc     Guard also recovers 10 stamina and 10 qi, times guard_dfs_bonus
#   Cx3/5  counter techs' counter_chance_mult params x3 / x5 (+50% -> +150% / +250%)
#   Qc10   qi-charged strikes at 0.1 instead of 0.3
#   Hb25/50  toughness and stamina 25% / 50% from health, the rest from level
#   HbT/HbS  only toughness / only stamina from health


def Gc():
    og = F.guard
    def guard(self):
        og(self)
        self.change_stamina(round(10 * self.guard_dfs_bonus))
        self.change_qp(round(10 * self.guard_dfs_bonus))
    F.guard = guard


def _scale_param(param, factor):
    from kf_lib.actors import fighter_factory  # noqa: F401  (style_gen techs exist now)
    from kf_lib.kung_fu import techniques
    for t in techniques.get_all_techs_dict().values():
        if param in getattr(t, 'params', {}):
            t.params[param] *= factor


def Cx3():
    _scale_param('counter_chance_mult', 3)


def Cx5():
    _scale_param('counter_chance_mult', 5)


def Qc10():
    global QI_CHARGE
    QI_CHARGE = 0.1
    Qc()


def _hb(weight, toughness=True, stamina=True):
    orf = F.refresh_dependent_atts
    def refresh(self):
        orf(self)  # level-based values
        h = self.health_full
        if toughness:
            from_health = max(0, 3 / H_PER_LV * (h - H0 - H_PER_LV))
            self.toughness = round((1 - weight) * self.toughness + weight * from_health)
        if stamina:
            from_health = max(30, (50 + 10 / H_PER_LV * (h - H0)) * self.stamina_max_mult)
            self.stamina_max = round((1 - weight) * self.stamina_max + weight * from_health)
            self.stamina_gain = round(self.stamina_max * self.STAMINA_PORTION_RESTORED_PER_TURN
                                      * self.stamina_gain_mult)
            self.stamina = min(self.stamina, self.stamina_max)
    F.refresh_dependent_atts = refresh


def Hb25():
    _hb(0.25)


def Hb50():
    _hb(0.5)


def HbT():
    _hb(1.0, stamina=False)


def HbS():
    _hb(1.0, toughness=False)


#   Gs     stored guard: Guard's bonus waits for the next incoming strike instead
#          of expiring at the fighter's next turn (consumed by that strike)
#   Cfree  counters cost nothing; Chalf: half the move's stamina/qi


def Gs():
    og, os_, oc, od = F.guard, F.start_fight_turn, F.calc_dfs, F.defend
    def guard(self):
        mult = self.guard_dfs_bonus * self.GUARD_POWER
        og(self)
        self.dfs_bonus /= mult  # don't double-apply this turn; store it instead
        self._stored_guard = mult
    def calc_dfs(self):
        g = getattr(self, '_stored_guard', 1.0)
        self.dfs_bonus *= g
        try:
            oc(self)
        finally:
            self.dfs_bonus /= g
    def defend(self):
        od(self)
        self._stored_guard = 1.0  # consumed by this strike
    F.guard, F.calc_dfs, F.defend = guard, calc_dfs, defend


def _counter_refund(share):
    odc = F.do_counter
    def do_counter(self):
        st, qp = self.stamina, self.qp
        odc(self)
        self.change_stamina(round((st - self.stamina) * share))
        self.change_qp(round((qp - self.qp) * share))
    F.do_counter = do_counter


def Cfree():
    _counter_refund(1.0)


def Chalf():
    _counter_refund(0.5)
