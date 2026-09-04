"""Player AI decision logic characterization (headless, seeded)."""
import random

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib.actors.player import AIPlayer, BaselineAIP, LazyAIP, SmartAIP, VanillaAIP


def make_player(cls=SmartAIP, seed=0):
    random.seed(seed)
    return cls(name='Test Player', style='Drunken Boxing')


class TestChooseDayAction:
    def test_poor_non_master_goes_to_work(self):
        p = make_player()
        p.money = p.min_non_master_money - 1
        assert p.choose_day_action() == p.go_work

    def test_rich_non_master_practices_or_walks(self):
        p = make_player()
        p.money = p.min_non_master_money
        seen = set()
        for seed in range(20):
            random.seed(seed)
            seen.add(p.choose_day_action())
        assert seen <= {p.practice_school, p.go_walk}
        assert seen == {p.practice_school, p.go_walk}  # both outcomes happen

    def test_poor_master_with_few_students_works(self):
        p = make_player()
        p.is_master = True
        p.students = p.min_students_to_teach - 1
        p.money = p.min_master_money - 1
        assert p.choose_day_action() == p.go_work

    def test_poor_master_with_many_students_teaches(self):
        p = make_player()
        p.is_master = True
        p.students = p.min_students_to_teach
        p.money = p.min_master_money - 1
        assert p.choose_day_action() == p.teach_students

    def test_rich_master_practices_or_walks(self):
        p = make_player()
        p.is_master = True
        p.money = p.min_master_money
        seen = set()
        for seed in range(20):
            random.seed(seed)
            seen.add(p.choose_day_action())
        assert seen == {p.practice_master, p.go_walk}

    def test_baseline_ai_picks_any_day_action(self):
        p = make_player(cls=BaselineAIP)
        allowed = {a[1] for a in p.get_day_actions()}
        for seed in range(20):
            random.seed(seed)
            assert p.choose_day_action() in allowed

    def test_choose_day_action_returns_bound_method(self):
        p = make_player()
        action = p.choose_day_action()
        assert callable(action)
        assert action.__self__ is p


class TestFightDecisions:
    def test_fight_or_not_threshold(self):
        p = make_player(cls=VanillaAIP)
        assert p.acceptable_fight_threshold == 1.2
        assert p.fight_or_not((1.2,)) is True
        assert p.fight_or_not((1.21,)) is False
        assert p.fight_or_not((0.5,)) is True

    def test_smart_ai_has_stricter_threshold(self):
        p = make_player(cls=SmartAIP)
        assert p.acceptable_fight_threshold == 1.1
        assert p.fight_or_not((1.15,)) is False
        assert p.fight_or_not((1.1,)) is True

    def test_fight_or_run(self):
        p = make_player(cls=VanillaAIP)
        # winnable fight -> fight regardless of escape chance
        assert p.fight_or_run((1.0,), esc_chance=0.9) is True
        # unwinnable, good escape chance -> run
        assert p.fight_or_run((2.0,), esc_chance=0.9) is False
        # unwinnable, poor escape chance -> fight
        assert p.fight_or_run((2.0,), esc_chance=0.1) is True

    def test_run_or_not(self):
        p = make_player(cls=VanillaAIP)
        assert p.acceptable_escape_risk == 0.6
        assert p.run_or_not(0.6) is True
        assert p.run_or_not(0.59) is False

    def test_fight_run_or_pay_matrix(self):
        p = make_player(cls=VanillaAIP)
        # not enough money -> fight or run only
        p.money = 0
        assert p.fight_run_or_pay((1.0,), esc_chance=0.9, money=50) == 'f'
        assert p.fight_run_or_pay((2.0,), esc_chance=0.9, money=50) == 'r'
        assert p.fight_run_or_pay((2.0,), esc_chance=0.1, money=50) == 'f'
        # enough money: prefers fight, then run, then pay
        p.money = 100
        assert p.fight_run_or_pay((1.0,), esc_chance=0.9, money=50) == 'f'
        assert p.fight_run_or_pay((2.0,), esc_chance=0.9, money=50) == 'r'
        assert p.fight_run_or_pay((2.0,), esc_chance=0.1, money=50) == 'p'

    def test_brawl_or_not(self):
        p = make_player(cls=VanillaAIP)  # brawl_chance = 0.25
        seen = set()
        for seed in range(50):
            random.seed(seed)
            seen.add(p.brawl_or_not((1.0,)))
        assert seen == {True, False}
        # too strong opponent -> never brawl
        for seed in range(50):
            random.seed(seed)
            assert p.brawl_or_not((1.3,)) is False

    def test_smart_ai_never_brawls(self):
        p = make_player(cls=SmartAIP)  # brawl_chance = 0
        for seed in range(10):
            random.seed(seed)
            assert p.brawl_or_not((0.5,)) is False

    def test_use_med_or_not(self):
        p = make_player(cls=SmartAIP)  # min_days_use_med = 3
        p.inactive = 2
        assert p.use_med_or_not() is False
        p.inactive = 3
        assert p.use_med_or_not() is True

    def test_static_preferences(self):
        assert AIPlayer.hear_rumors_or_not() is False
        assert AIPlayer.talk_wise_or_not() is True
        assert AIPlayer.tourn_or_not() is True
        assert AIPlayer.p_match_or_not() is True


class TestDayActionList:
    def test_get_day_actions_structure(self):
        p = make_player()
        actions = p.get_day_actions()
        labels = [a[0] for a in actions]
        assert 'Practice at school' in labels
        assert 'Go to work' in labels
        assert 'Pick fights' in labels
        for label, func in actions:
            assert isinstance(label, str)
            assert callable(func)

    def test_master_day_actions_differ(self):
        p = make_player()
        p.is_master = True
        labels = [a[0] for a in p.get_day_actions()]
        assert 'Practice' in labels
        assert 'Teach students' in labels
        assert 'Practice at school' not in labels
        assert 'Pick fights' not in labels

    def test_lazy_ai_differs_from_vanilla(self):
        # class-level characterization of the AI variants
        assert LazyAIP.non_master_practice_chance < VanillaAIP.non_master_practice_chance
        assert LazyAIP.gamble_chance > VanillaAIP.gamble_chance
        assert SmartAIP.brawl_chance == 0


class TestSmartAIPKnobs:
    """SmartAIP used to set dead attribute names (drink_chance,
    continue_gambling_chance, buy_med_chance) that nothing ever read; the real
    knobs are instance attributes set in BasePlayer.__init__, so they must be
    overridden post-init, not as class attributes."""

    def make_sober_player(self, cls):
        # traits_list=[]: random traits (e.g. 'undisciplined') modify these
        # very knobs, so a traited player makes the test flaky
        random.seed(0)
        return cls(name='Test Player', style='Drunken Boxing', traits_list=[])

    def test_smart_ai_never_drinks_or_chases_losses(self):
        p = self.make_sober_player(SmartAIP)
        assert p.drink_with_drunkard == 0.0
        assert p.gamble_continue == 0.0

    def test_smart_ai_knobs_override_traits(self):
        # even an 'undisciplined' SmartAIP (trait bumps drinking/gambling)
        # keeps the post-init override
        p = SmartAIP(name='Test Player', style='Drunken Boxing', traits_list=['undisciplined'])
        assert p.drink_with_drunkard == 0.0
        assert p.gamble_continue == 0.0

    def test_base_ai_keeps_default_knobs(self):
        p = self.make_sober_player(VanillaAIP)
        assert p.drink_with_drunkard == 0.25
        assert p.gamble_continue == 0.4

    def test_dead_attribute_names_are_gone(self):
        for dead in ('drink_chance', 'continue_gambling_chance', 'buy_med_chance'):
            assert not hasattr(SmartAIP, dead)
