"""Utils characterization: numbers, language helpers, random helpers, validators."""
import random

import pytest

from kf_lib.utils import (
    Float,
    Integer,
    add_article,
    add_pcnt,
    add_sign,
    add_to_dict,
    choose_adverb,
    enum_words,
    float_to_pcnt,
    hund,
    mean,
    median,
    multiply,
    pcnt,
    percentage,
    remove_article,
    rnd,
    rndint,
    rndint_2d,
    roman,
    sg_or_pl,
    sigmoid,
)
from kf_lib.utils._validators import ValidationError


class TestRandomHelpers:
    def test_rnd_bounds(self):
        random.seed(0)
        for _ in range(100):
            assert 0.0 <= rnd() <= 1.0

    def test_rndint_bounds(self):
        random.seed(0)
        for _ in range(100):
            assert 1 <= rndint(1, 6) <= 6

    def test_rndint_2d_bounds(self):
        random.seed(0)
        for a, b in ((1, 2), (2, 12), (5, 7), (3, 4), (2, 3)):
            for _ in range(200):
                assert a <= rndint_2d(a, b) <= b

    def test_rndint_2d_is_bell_shaped(self):
        # two-dice distribution clusters around the middle
        random.seed(0)
        samples = [rndint_2d(2, 12) for _ in range(2000)]
        avg = sum(samples) / len(samples)
        assert 6.5 <= avg <= 7.5
        # extremes are rarer than the middle
        from collections import Counter

        c = Counter(samples)
        assert c[7] > c[2] and c[7] > c[12]

    def test_rndint_2d_deterministic_with_seed(self):
        random.seed(42)
        first = [rndint_2d(1, 10) for _ in range(10)]
        random.seed(42)
        assert [rndint_2d(1, 10) for _ in range(10)] == first


class TestNumberHelpers:
    def test_mean(self):
        assert mean([1, 2, 3]) == 2
        assert mean([1, 2]) == 1.5

    def test_median_odd_and_even(self):
        assert median([3, 1, 2]) == 2
        assert median([4, 1, 3, 2]) == 2.5

    def test_multiply(self):
        assert multiply([2, 3, 4]) == 24
        assert multiply([5]) == 5

    def test_add_sign(self):
        assert add_sign(5) == '+5'
        assert add_sign(-5) == '-5'
        assert add_sign(0) == '0'

    def test_add_pcnt(self):
        assert add_pcnt(50) == '50%'

    def test_float_to_pcnt(self):
        assert float_to_pcnt(0.4) == '40%'
        assert float_to_pcnt(0.426) == '43%'

    def test_hund(self):
        assert hund(0.4) == 40

    def test_pcnt(self):
        assert pcnt(20, 40) == 50
        assert pcnt(1, 3) == 33.33
        assert pcnt(1, 4, n=0) == 25
        assert pcnt(20, 40, as_string=True) == '50.0%'

    def test_percentage(self):
        assert percentage(20, 40) == '20/40 (50.0%)'

    def test_roman(self):
        assert roman(1) == 'I'
        assert roman(4) == 'IV'
        assert roman(9) == 'IX'
        assert roman(10) == 'X'
        assert roman(25) == 'XXV'

    def test_sigmoid(self):
        assert sigmoid(0) == 0.5
        assert sigmoid(100) > 0.99
        assert sigmoid(-100) < 0.01
        assert abs(sigmoid(2) + sigmoid(-2) - 1) < 1e-9


class TestLangTools:
    def test_enum_words(self):
        assert enum_words(()) == ''
        assert enum_words(('a',)) == 'a'
        assert enum_words(('a', 'b')) == 'a and b'
        assert enum_words(('a', 'b', 'c')) == 'a, b and c'

    def test_add_article(self):
        assert add_article('knife') == 'a knife'
        assert add_article('apple') == 'an apple'

    def test_remove_article(self):
        assert remove_article('a knife') == 'knife'
        assert remove_article('an apple') == 'apple'
        assert remove_article('knife') == 'knife'

    def test_sg_or_pl(self):
        assert sg_or_pl(1) == ''
        assert sg_or_pl(2) == 's'

    def test_choose_adverb(self):
        assert choose_adverb(0.1, 'low', 'high') == 'low '
        assert choose_adverb(0.5, 'low', 'high') == ''
        assert choose_adverb(0.9, 'low', 'high') == 'high '

    def test_add_to_dict(self):
        d = {}
        add_to_dict(d, 'a', 5)
        add_to_dict(d, 'a', 3)
        add_to_dict(d, 'b', 1, start_val=10)
        assert d == {'a': 8, 'b': 11}


class TestValidators:
    class Model:
        int_att = Integer(minvalue=0, maxvalue=10)
        int_strict = Integer(minvalue=0, action='raise')
        float_att = Float(minvalue=0.0)

    def test_integer_normal_set(self):
        m = self.Model()
        m.int_att = 5
        assert m.int_att == 5

    def test_integer_clamps_out_of_range_by_default(self):
        # default action='ignore': out-of-range values are silently clamped
        m = self.Model()
        m.int_att = 99
        assert m.int_att == 10
        m.int_att = -5
        assert m.int_att == 0

    def test_integer_coerces_wrong_type_by_default(self):
        m = self.Model()
        m.int_att = '7'
        assert m.int_att == 7

    def test_integer_raise_action(self):
        m = self.Model()
        with pytest.raises(ValidationError):
            m.int_strict = -1
        with pytest.raises(ValidationError):
            m.int_strict = 1.5

    def test_float(self):
        m = self.Model()
        m.float_att = 1.5
        assert m.float_att == 1.5
        m.float_att = -1.0
        assert m.float_att == 0.0


class TestNameGeneration:
    def test_generated_names_are_unique(self):
        from kf_lib import game

        random.seed(0)
        g = game.Game()
        names = {g.get_new_name() for _ in range(100)}
        assert len(names) == 100

    def test_prefixed_names(self):
        from kf_lib import game

        random.seed(0)
        g = game.Game()
        for _ in range(20):
            name = g.get_new_name(prefix='Master')
            assert name.startswith('Master ')
            assert name == name.title()

    def test_registering_duplicate_fighter_raises(self):
        from kf_lib import game
        from kf_lib.actors import fighter_factory

        random.seed(0)
        g = game.Game()
        f1 = fighter_factory.new_fighter(1)
        f1.name = 'Dup Name'
        g.register_fighter(f1)
        f2 = fighter_factory.new_fighter(1)
        f2.name = 'Dup Name'
        with pytest.raises(Exception):
            g.register_fighter(f2)
