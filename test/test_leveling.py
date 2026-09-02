"""Leveling and experience characterization."""
import random

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib.actors import fighter_factory
from kf_lib.actors.fighter import Fighter
from kf_lib.actors.player import SmartAIP
from kf_lib.constants.experience import EXP_PER_LEVEL
from kf_lib.fighting.fight._base_fight import BaseFight
from kf_lib.utils._validators import ValidationError


def bare_fighter(style_name, level=1):
    """Fighter with no pre-learned techs/moves beyond the basics."""
    random.seed(0)
    return Fighter('Test', style_name, level=level, tech_names=[], move_names=[])


class TestLevelUp:
    def test_level_up_increments_level(self):
        f = bare_fighter('Drunken Boxing')
        f.level_up()
        assert f.level == 2
        f.level_up(3)
        assert f.level == 5

    def test_level_up_increases_hp_max(self):
        f = bare_fighter('Drunken Boxing')
        hp_before = f.hp_max
        f.level_up(5)
        assert f.hp_max > hp_before

    def test_style_techs_learned_at_levels_3_5_7(self):
        f = bare_fighter('Drunken Boxing')
        tech_names = lambda: {t.name for t in f.techs}
        assert tech_names() == set()
        f.level_up(2)  # level 3
        assert tech_names() == {'Drunken Boxing I'}
        f.level_up(2)  # level 5
        assert tech_names() == {'Drunken Boxing I', 'Drunken Boxing II'}
        f.level_up(2)  # level 7
        assert tech_names() == {
            'Drunken Boxing I',
            'Drunken Boxing II',
            'Drunken Boxing III',
        }
        f.level_up(1)  # level 8: no more style techs
        assert len(f.techs) == 3

    def test_general_techs_learned_at_levels_13_15_17(self):
        # Fighter.LVS_GET_GENERAL_TECH = {13, 15, 17}
        f = bare_fighter('Drunken Boxing', level=12)
        n_techs = len(f.techs)
        for lv, step in ((13, 1), (15, 2), (17, 2)):
            random.seed(lv)
            f.level_up(step)
            assert f.level == lv
            assert len(f.techs) == n_techs + 1
            n_techs += 1

    def test_named_style_moves_learned_at_style_levels(self):
        # Long Fist has explicit move names at levels 1, 2
        f = bare_fighter('Long Fist')
        move_names = [m.name for m in f.moves]
        assert 'Leap Back' in move_names  # level 1 style move
        assert 'Long Punch' not in move_names
        f.level_up()  # level 2
        assert 'Long Punch' in [m.name for m in f.moves]

    def test_default_style_move_at_even_levels(self):
        # styles without explicit move names use DEFAULT_STYLE_MOVE_DICT:
        # one extra move at levels 2, 4, 6, 8, 10
        f = bare_fighter('Drunken Boxing')
        n_moves = len(f.moves)
        f.level_up()  # level 2
        assert len(f.moves) == n_moves + 1

    def test_all_fighters_know_basic_moves(self):
        f = bare_fighter('Long Fist')
        names = {m.name for m in f.moves}
        for basic in ('Punch', 'Kick', 'Guard', 'Do Nothing'):
            assert basic in names


class TestGainExp:
    def make_player(self, **kwargs):
        # empty traits: random traits can change next_lv_exp_mult etc.
        random.seed(0)
        return SmartAIP(name='Test Player', style='Drunken Boxing', traits_list=[], **kwargs)

    def test_next_level_scales_with_level(self):
        p = self.make_player()
        assert p.level == 1
        assert p.next_level == EXP_PER_LEVEL  # 100 * level
        p.level_up()
        assert p.next_level == 2 * EXP_PER_LEVEL

    def test_gain_exp_below_threshold(self):
        p = self.make_player()
        p.gain_exp(50, silent=True)
        assert p.exp == 50
        assert p.level == 1

    def test_gain_exp_exact_boundary_levels_up(self):
        p = self.make_player()
        p.gain_exp(100, silent=True)
        assert p.level == 2

    def test_gain_exp_cascades_multiple_levels(self):
        p = self.make_player()
        p.gain_exp(250, silent=True)
        # 250 >= 100 (lv2) and >= 200 (lv3), but < 300
        assert p.level == 3
        assert p.exp == 250
        assert p.next_level == 300

    def test_negative_exp_raises(self):
        p = self.make_player()
        with pytest.raises(ValidationError):
            p.exp = -1

    def test_exp_is_coerced_to_int(self):
        # exp is an Integer(minvalue=0, action='raise') descriptor; assigning a
        # non-int with action='raise'... still coerces after raising only for
        # range violations: wrong TYPE is also 'raise'
        p = self.make_player()
        with pytest.raises(ValidationError):
            p.exp = 1.5


class TestTraits:
    def test_slow_witted_raises_exp_requirements(self):
        # negative traits negate the effect dict: 'slow-witted' -> next_lv_exp_mult +0.1
        random.seed(0)
        p = SmartAIP(
            name='Test Player', style='Drunken Boxing', traits_list=['slow-witted']
        )
        assert p.next_lv_exp_mult == pytest.approx(1.1)
        assert p.next_level == 110

    def test_quick_witted_lowers_exp_requirements(self):
        random.seed(0)
        p = SmartAIP(
            name='Test Player', style='Drunken Boxing', traits_list=['quick-witted']
        )
        assert p.next_lv_exp_mult == pytest.approx(0.9)
        assert p.next_level == 90

    def test_random_traits_one_negative_one_positive(self):
        random.seed(0)
        p = SmartAIP(name='Test Player', style='Drunken Boxing')
        assert len(p.traits) == 2


class TestExpWorth:
    def test_exp_yield_is_zero_until_fight(self):
        # characterization: exp_yield attr is only set in prepare_for_fight()
        random.seed(0)
        f = fighter_factory.new_fighter(10)
        assert f.exp_yield == 0
        assert f.get_exp_worth() > 0

    def test_exp_worth_grows_with_level(self):
        random.seed(0)
        f1 = fighter_factory.new_fighter(1)
        random.seed(0)
        f10 = fighter_factory.new_fighter(10)
        random.seed(0)
        f20 = fighter_factory.new_fighter(20)
        assert f1.get_exp_worth() < f10.get_exp_worth() < f20.get_exp_worth()

    def test_prepare_for_fight_sets_exp_yield(self):
        random.seed(0)
        f = fighter_factory.new_fighter(5)
        other = fighter_factory.new_fighter(5)
        f.current_fight = BaseFight([f], [other])
        f.prepare_for_fight()
        assert f.exp_yield == f.get_exp_worth() > 0
