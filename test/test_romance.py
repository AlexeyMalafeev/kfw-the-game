"""Romance system tests: meeting a sweetheart, dating, marriage, spouse effects,
jealous rivals, the kidnapped-sweetheart story, and family/children."""
import random

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
import kf_lib.actors.player._base_player as base_player_mod
import kf_lib.happenings.encounters._romance as romance_mod
from kf_lib.actors import fighter_factory
from kf_lib.actors.player import SmartAIP
from kf_lib.actors.player._base_player import CHILD_EXP, ROMANCE_PROPOSE_THRESHOLD
from kf_lib.game import biographies
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


class TestJealousRival:
    def make_rival(self, g, p):
        return fighter_factory.new_love_rival(g.get_new_name(gender='m'), 'm', p.level)

    def test_fires_only_while_courting(self):
        g = make_game()
        p = g.players[0]
        enc = encounters.JealousRival.__new__(encounters.JealousRival)
        enc.p = enc.player = p
        assert enc.check_if_happens() is False  # single
        make_sweetheart(g, p)
        p.is_married = True
        assert enc.check_if_happens() is False  # married

    def test_win_raises_progress_and_can_make_enemy(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        progress_before = p.romance_progress
        rival = self.make_rival(g, p)
        monkeypatch.setattr(p, 'fight', lambda *a, **k: True)
        monkeypatch.setattr(romance_mod, 'rnd', lambda: 0.0)  # enemy roll succeeds
        enc = encounters.JealousRival.__new__(encounters.JealousRival)
        enc.p = enc.player = p
        enc.do_fight(rival)
        assert p.romance_progress == progress_before + romance_mod.RIVAL_WIN_PROGRESS
        assert rival in p.enemies
        assert g.fighters_dict[rival.name] is rival  # registered, hence saved

    def test_loss_lowers_progress_and_can_break_up(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        p.romance_progress = 1
        rival = self.make_rival(g, p)
        monkeypatch.setattr(p, 'fight', lambda *a, **k: False)
        enc = encounters.JealousRival.__new__(encounters.JealousRival)
        enc.p = enc.player = p
        enc.do_fight(rival)
        assert p.sweetheart is None  # the sweetheart leaves
        assert p.romance_progress == 0

    def test_no_breakup_while_married(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        p.is_married = True
        p.romance_progress = 0
        p.check_romance_breakup()
        assert p.sweetheart is not None


class TestKidnappedSweetheartStory:
    def make_story(self, g, p):
        s = g.stories['KidnappedSweetheartStory']
        assert s.check_hasnt_started()
        return s

    def test_requires_sweetheart(self):
        g = make_game()
        p = g.players[0]
        p.level_up(2)  # the story's min_level is 3
        s = self.make_story(g, p)
        assert s.test(p) is False
        make_sweetheart(g, p)
        assert s.test(p) is True

    def test_rescue_success(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        sw = make_sweetheart(g, p)
        progress_before = p.romance_progress
        s = self.make_story(g, p)
        s.start(p)
        assert p.current_story is s
        assert s.boss is not None
        monkeypatch.setattr(p, 'fight', lambda *a, **k: True)
        s.advance()  # scene1
        s.advance()  # scene2
        assert 'Rescued Sweetheart' in p.accompl
        assert p.romance_progress == progress_before + s.progress_reward
        assert p.current_story is None
        assert s.state == -1
        assert s.boss is None

    def test_rescue_failure_twist(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        s = self.make_story(g, p)
        s.start(p)
        monkeypatch.setattr(p, 'fight', lambda *a, **k: False)
        s.advance()
        s.advance()
        assert 'Rescued Sweetheart' not in p.accompl
        assert p.sweetheart is not None  # she frees herself; the romance survives
        assert p.current_story is None

    def test_sweetheart_gone_mid_story(self):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        s = self.make_story(g, p)
        s.start(p)
        p.sweetheart = None  # e.g. a breakup via a lost rival duel
        s.advance()
        assert p.current_story is None
        assert s.state == -1


class TestFamily:
    def test_child_birth_and_growth(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        p.check_family_monthly()
        assert p.children_ages == []  # not married yet
        p.is_married = True
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 0.0)  # birth roll succeeds
        p.check_family_monthly()
        assert p.children_ages == [0]
        assert 'Proud Parent' in p.accompl
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 1.0)  # no birth
        p.check_family_monthly()
        assert p.children_ages == [1]

    def test_child_daily_expense(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        p.is_married = True
        p.children_ages = [3]
        p.money = 10
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 0.0)  # gift and expense
        monkeypatch.setattr(base_player_mod, 'rndint', lambda a, b: a)
        p.check_spouse_daily()
        assert p.money == 10 + 5 - 1  # +5 spouse gift, -1 child expense

    def test_practice_with_grown_child(self, monkeypatch):
        g = make_game()
        p = g.players[0]
        make_sweetheart(g, p)
        p.is_married = True
        p.children_ages = [12]
        assert p.get_grown_children() == [12]
        exp_before = p.exp
        monkeypatch.setattr(base_player_mod, 'rnd', lambda: 0.0)  # practice roll
        assert p.visit_sweetheart() is True
        assert p.exp == exp_before + CHILD_EXP

    def test_bio_mentions_family(self):
        g = make_game()
        p = g.players[0]
        sw = make_sweetheart(g, p)
        p.is_married = True
        p.children_ages = [3, 15]
        bio = biographies.generate_bio(p)
        assert sw.name in bio
        assert '2 wonderful children' in bio
