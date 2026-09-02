"""Game-state mechanics: calendar, victory conditions, schools, ranks."""
import random

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib.actors.player import SmartAIP
from kf_lib.game._playing import (
    FOLK_HERO_REP,
    GRANDMASTER_LV,
    GT_FIGHTER_FIGHTS,
    KFLEGEND_ACCOMPL,
    Playing,
)


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


def make_player(seed=0):
    random.seed(seed)
    return SmartAIP(name='Test Player', style='Drunken Boxing')


class TestCalendar:
    def test_starting_date(self):
        g = make_game()
        assert (g.day, g.month, g.year) == (1, 1, 1)
        assert g.get_date() == '1/1/1'

    def test_next_day_increments(self):
        g = make_game()
        g.next_day()
        assert g.get_date() == '2/1/1'

    def test_month_rollover_at_30_days(self):
        g = make_game()
        g.day = 30
        g.next_day()
        assert (g.day, g.month) == (1, 2)

    def test_year_rollover_at_12_months(self):
        g = make_game()
        g.day, g.month = 30, 12
        g.next_day()
        assert (g.day, g.month, g.year) == (1, 1, 2)

    def test_next_day_resets_ended_turn(self):
        g = make_game()
        for p in g.players:
            p.ended_turn = True
        g.next_day()
        assert all(not p.ended_turn for p in g.players)

    def test_monthly_adds_a_convict(self):
        g = make_game()
        n_before = len(g.criminals)
        g.day = 30
        g.next_day()
        assert len(g.criminals) == n_before + 1


class TestVictoryConditions:
    def test_no_victory_for_new_player(self):
        p = make_player()
        assert Playing.check_victory_conditions(p) == []

    def test_grandmaster_at_level_20(self):
        assert GRANDMASTER_LV == 20
        p = make_player()
        p.level = GRANDMASTER_LV
        assert 'Grandmaster' in Playing.check_victory_conditions(p)
        p.level = GRANDMASTER_LV - 1
        assert 'Grandmaster' not in Playing.check_victory_conditions(p)

    def test_folk_hero_at_100_rep(self):
        p = make_player()
        p.reputation = FOLK_HERO_REP
        assert 'Folk Hero' in Playing.check_victory_conditions(p)
        p.reputation = FOLK_HERO_REP - 1
        assert 'Folk Hero' not in Playing.check_victory_conditions(p)

    def test_kung_fu_legend_at_8_accomplishments(self):
        p = make_player()
        p.accompl = ['x'] * (KFLEGEND_ACCOMPL - 1)
        assert 'Kung-fu Legend' not in Playing.check_victory_conditions(p)
        p.accompl.append('x')
        assert 'Kung-fu Legend' in Playing.check_victory_conditions(p)

    def test_greatest_fighter_needs_wins_and_kos(self):
        p = make_player()
        p.set_stat('fights_won', GT_FIGHTER_FIGHTS[0])
        p.set_stat('num_kos', GT_FIGHTER_FIGHTS[1] - 1)
        assert 'Greatest Fighter' not in Playing.check_victory_conditions(p)
        p.set_stat('num_kos', GT_FIGHTER_FIGHTS[1])
        assert 'Greatest Fighter' in Playing.check_victory_conditions(p)

    def test_check_victory_sets_n_days_to_win(self):
        g = make_game()
        g.day, g.month, g.year = 15, 2, 1
        g.players[0].level = GRANDMASTER_LV
        assert g.check_victory()
        # n_days = (year-1)*360 + (month-1)*30 + day
        assert g.n_days_to_win == 30 + 15

    def test_play_indefinitely_disables_victory(self):
        g = make_game()
        g.play_indefinitely = True
        g.players[0].level = GRANDMASTER_LV
        assert g.check_victory() is False


class TestSchoolsAndRanks:
    def test_schools_exist_for_all_styles(self):
        g = make_game()
        assert set(g.schools) == {s.name for s in g.style_list}
        assert set(g.masters) == set(g.schools)

    def test_players_are_in_their_style_school(self):
        g = make_game()
        for p in g.players:
            assert p in g.schools[p.style.name]

    def test_school_rank_is_valid(self):
        g = make_game()
        for p in g.players:
            school = g.schools[p.style.name]
            assert 1 <= p.school_rank <= len(school)
            assert school[p.school_rank - 1] is p

    def test_schools_sorted_by_exp_worth_desc(self):
        g = make_game()
        for school in g.schools.values():
            worths = [s.get_exp_worth() for s in school]
            assert worths == sorted(worths, reverse=True)

    def test_get_act_players_excludes_inactive(self):
        g = make_game()
        assert len(g.get_act_players()) == len(g.players)
        g.players[0].inactive = 2
        assert g.get_act_players() == g.players[1:]


class TestGameSetup:
    def test_special_npcs_exist(self):
        g = make_game()
        assert g.beggar is not None
        assert g.drunkard is not None
        assert g.thief is not None
        assert g.fat_girl is not None
        assert len(g.criminals) == 5

    def test_fighters_registered_consistently(self):
        g = make_game()
        for f in g.fighters_list:
            assert g.fighters_dict[f.name] is f
        assert len(g.fighters_list) == len(g.fighters_dict)

    def test_encounter_counters_initialized(self):
        g = make_game()
        from kf_lib.happenings import encounters

        for cls in encounters.all_random_encounter_classes:
            assert g.enc_count_dict[cls.__name__] == 0

    def test_town_stats_in_range(self):
        for seed in range(10):
            g = make_game(seed=seed)
            for stat in (g.poverty, g.crime, g.kung_fu):
                assert stat in (0.05, 0.1, 0.15, 0.2)
