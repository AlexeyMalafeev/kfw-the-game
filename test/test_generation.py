"""Invariants for generated content: styles, moves, fighters."""
import random

from kf_lib.actors.fighter_factory import new_fighter
from kf_lib.kung_fu import moves, style_gen, styles


class TestStyleGeneration:
    def test_generate_styles(self):
        random.seed(0)
        gs = style_gen.generate_new_styles(10)
        assert len(gs) == 10
        for s in gs:
            assert s.name
            assert s.descr_short

    def test_generated_style_names_unique(self):
        random.seed(0)
        gs = style_gen.generate_new_styles(50)
        names = [s.name for s in gs]
        assert len(set(names)) == len(names)

    def test_style_roundtrip_from_words(self):
        random.seed(0)
        s = style_gen.get_new_randomly_generated_style()
        s2 = style_gen.get_style_from_str(s.name)
        assert s2.name == s.name


class TestMoves:
    def test_move_pool_nonempty(self):
        assert len(moves.ALL_MOVES_LIST) > 0

    def test_get_rand_moves_count(self):
        random.seed(0)
        f = new_fighter(5)
        ms = moves.get_rand_moves(f, 5, tier=1)
        assert len(ms) == 5

    def test_all_moves_have_valid_tier(self):
        # tier 0 = basic/weapon moves, 1..10 = randomly learnable, 11+ = special
        for m in moves.ALL_MOVES_LIST:
            assert isinstance(m.tier, int) and m.tier >= 0

    def test_random_tiers_are_nonempty(self):
        # get_rand_moves picks from MOVES_BY_TIERS[tier]; an empty tier would crash it
        for tier in range(moves.TIER_MIN, moves.TIER_MAX + 1):
            assert moves.MOVES_BY_TIERS.get(tier), f'no moves at tier {tier}'


class TestFighterFactory:
    def test_new_fighter_level(self):
        random.seed(0)
        f = new_fighter(7)
        assert f.level == 7

    def test_new_fighter_group(self):
        random.seed(0)
        fs = new_fighter(3, n=4)
        assert len(fs) == 4
        # group members get numbered, unique names
        assert len({f.name for f in fs}) == 4

    def test_fighter_has_moves(self):
        random.seed(0)
        f = new_fighter(10)
        assert len(f.moves) > 0


class TestStdStyles:
    def test_known_styles_resolve(self):
        for sname in ('Drunken Boxing', 'Long Fist', 'Praying Mantis'):
            s = styles.get_style_obj(sname)
            assert s.name == sname
