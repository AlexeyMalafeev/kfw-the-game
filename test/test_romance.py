"""Romance system tests: meeting a sweetheart, dating, marriage, spouse effects."""
import random

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
import kf_lib.actors.player._base_player as base_player_mod
from kf_lib.actors import fighter_factory
from kf_lib.actors.player import SmartAIP
from kf_lib.actors.player._base_player import ROMANCE_PROPOSE_THRESHOLD
from kf_lib.happenings import encounters


def make_game(seed=0, num_players=2):
    random.seed(seed)
    g = game.Game()
    g.new_game(
        num_players=num_players,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=True,
        silent_ending=True,
        forced_aip_class=SmartAIP,
    )
    return g


def make_sweetheart(g, p, gender='f', level=3):
    sw = fighter_factory.new_sweetheart(g.get_new_name(gender=gender), gender, level)
    g.register_fighter(sw)
    p.sweetheart = sw
    p.romance_progress = 1
    return sw


class TestNewRomance:
    def test_pursued_romance_creates_sweetheart(self):
        g = make_game()
        p = g.players[0]
        p.romance_pursuit_chance = 1.0
        encounters.NewRomance(p, check_if_happens=False)
        sw = p.sweetheart
        assert sw is not None
        assert g.fighters_dict[sw.name] is sw  # registered, hence saved
        assert sw.gender in ('f', 'm')
        assert p.romance_progress == 1
        assert 1 <= sw.level <= p.level + 2

    def test_declined_romance_leaves_no_sweetheart(self):
        g = make_game()
        p = g.players[0]
        p.romance_pursuit_chance = 0.0
        encounters.NewRomance(p, check_if_happens=False)
        assert p.sweetheart is None
        assert p.romance_progress == 0

    def test_no_new_romance_while_courting(self):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        enc = encounters.NewRomance.__new__(encounters.NewRomance)
        enc.p = enc.player = p
        assert enc.check_if_happens() is False


class TestDating:
    def test_romantic_date_raises_progress(self):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        encounters.RomanticDate(p, check_if_happens=False)
        assert p.romance_progress >= 2

    def test_no_dates_after_marriage(self):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        p.is_married = True
        enc = encounters.RomanticDate.__new__(encounters.RomanticDate)
        enc.p = enc.player = p
        assert enc.check_if_happens() is False

    def test_visit_sweetheart_consumes_turn_and_raises_progress(self):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        progress_before = p.romance_progress
        assert p.visit_sweetheart() is True
        assert p.romance_progress > progress_before

    def test_day_actions_include_visit_sweetheart(self):
        g = make_game()
        p = g.players[0]
        assert 'Visit sweetheart' not in [label for label, _ in p.get_day_actions()]
        make_sweetheart(g, p)
        actions = dict(p.get_day_actions())
        assert 'Visit sweetheart' in actions
        p.is_married = True
        actions = dict(p.get_day_actions())
        assert 'Visit spouse' in actions


class TestMarriage:
    def test_accepted_proposal(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        sw = make_sweetheart(g, p)
        p.romance_progress = ROMANCE_PROPOSE_THRESHOLD
        p.romance_pursuit_chance = 1.0
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 0.0)
        p.propose_marriage()
        assert p.is_married
        assert p.sweetheart is sw
        assert 'Got Married' in p.accompl

    def test_rejected_proposal(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        p.romance_progress = ROMANCE_PROPOSE_THRESHOLD
        p.romance_pursuit_chance = 1.0
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 1.0)
        p.propose_marriage()
        assert not p.is_married
        assert p.romance_progress < ROMANCE_PROPOSE_THRESHOLD

    def test_spouse_joins_fight_via_check_help(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        sw = make_sweetheart(g, p)
        p.is_married = True
        monkeypatch.setattr(base_player_mod.random, 'choice', lambda seq: 'sp')
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 0.0)
        p.check_help()
        assert p.allies == [sw]

    def test_no_spouse_channel_when_single(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        monkeypatch.setattr(base_player_mod.random, 'choice', lambda seq: 'sp')
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 0.0)
        p.check_help()
        assert p.sweetheart not in p.allies

    def test_spouse_daily_gift(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        p.is_married = True
        money_before = p.money
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 0.0)
        p.check_spouse_daily()
        assert p.money > money_before


class TestSweetheartFactory:
    def test_gendered_names_use_female_pool(self):
        from kf_lib.actors import names

        random.seed(0)
        g = make_game()
        for _ in range(20):
            name = g.get_new_name(gender='f')
            first = name.split(' ', 1)[1].lower()
            parts = names.FEMALE_FIRST_NAME_PARTS
            assert any(
                first == a + b for a in parts for b in parts
            ) or first in parts

    def test_new_sweetheart_level_and_gender(self):
        random.seed(0)
        sw = fighter_factory.new_sweetheart('Test Love', 'f', 5)
        assert sw.level == 5
        assert sw.gender == 'f'
        assert sw.occupation == 'fighter'
