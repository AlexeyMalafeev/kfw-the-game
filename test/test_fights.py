"""Seeded, deterministic fight tests using the headless AutoFight engine."""
import random

from kf_lib.actors.fighter_factory import new_fighter
from kf_lib.fighting.fight import AutoFight


def run_fight(lv_a, lv_b, seed):
    random.seed(seed)
    fa = new_fighter(lv_a)
    fb = new_fighter(lv_b)
    return AutoFight([fa], [fb])


class TestDeterminism:
    def test_same_seed_same_winner(self):
        f1 = run_fight(5, 5, seed=42)
        f2 = run_fight(5, 5, seed=42)
        assert [f.name for f in f1.winners] == [f.name for f in f2.winners]

    def test_same_seed_same_final_hp(self):
        f1 = run_fight(5, 5, seed=42)
        f2 = run_fight(5, 5, seed=42)
        hp1 = sorted((f.name, f.hp) for f in f1.all_fighters)
        hp2 = sorted((f.name, f.hp) for f in f2.all_fighters)
        assert hp1 == hp2


class TestOutcomes:
    def test_fight_always_terminates(self):
        # several seeds, none should hang or crash
        for seed in range(10):
            f = run_fight(1, 1, seed=seed)
            assert f.winners is not None

    def test_much_stronger_fighter_wins(self):
        # a lv-20 fighter should beat a lv-1 fighter essentially every time
        wins = 0
        n = 20
        for seed in range(n):
            f = run_fight(20, 1, seed=1000 + seed)
            if f.winners and f.winners[0] in f.side_a:
                wins += 1
        assert wins >= n - 1

    def test_no_negative_hp_overkill_weirdness(self):
        f = run_fight(10, 10, seed=7)
        for fighter in f.all_fighters:
            assert fighter.hp >= -fighter.hp_max  # sanity, not a tight bound
