"""Own-school late-game mechanics: teaching, best student, students in
tournaments, the all-schools tournament and the schools-unification victory."""
import random
from types import SimpleNamespace

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
import kf_lib.actors.player._base_player as _bp
from kf_lib.actors.player import SmartAIP
from kf_lib.actors.player._base_player import TAUGHT_STUDENT_LV_GAP, UNITED_SCHOOL_REP
from kf_lib.fighting import fight
from kf_lib.game._playing import check_united_schools
from kf_lib.happenings import events
from kf_lib.happenings.events import (
    ALL_SCHOOLS_TEAM_SIZE,
    ALL_SCHOOLS_PRIZE,
    ALL_SCHOOLS_WIN_REP,
)
from kf_lib.happenings.tournament import (
    STUDENT_TOURN_WIN_REP,
    STUDENT_TOURN_WINS_ACCOMPL,
    Tournament,
)


def make_game_and_player(seed=0, level=1):
    random.seed(seed)
    g = game.Game()
    g.new_game(
        num_players=2,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=True,
        silent_ending=True,
        forced_aip_class=SmartAIP,
    )
    p = g.players[0]
    if level > 1:
        p.level_up(level - 1)
    return g, p


def make_master(p, num_students=4):
    """Replicate what MasterTrial does when a player founds a school."""
    old_school = p.get_school()
    if p in old_school:
        old_school.remove(p)
    p.is_master = True
    school_name = f"{p.name}'s school"
    p.game.schools[school_name] = []
    p.game.masters[school_name] = p
    p.new_school_name = school_name
    if num_students:
        p.add_students(num_students)
    return p


class TestTeaching:
    def test_teaching_levels_up_students(self):
        g, p = make_game_and_player(seed=0, level=14)
        make_master(p, num_students=6)
        school = g.schools[p.new_school_name]
        start_levels = [s.level for s in school]
        money_before = p.money
        for _ in range(20):
            assert p.teach_students() is True
        assert p.money > money_before  # tuition income is kept
        end_levels = [s.level for s in school]
        assert end_levels != start_levels  # someone improved over 20 lessons
        # nobody is taught beyond the master's reach
        assert all(lv <= p.level - TAUGHT_STUDENT_LV_GAP for lv in end_levels)

    def test_teaching_without_students(self):
        g, p = make_game_and_player(seed=1, level=12)
        make_master(p, num_students=0)
        assert p.teach_students() is None  # turn not consumed

    def test_best_student_is_strongest(self):
        g, p = make_game_and_player(seed=2, level=14)
        make_master(p, num_students=5)
        school = g.schools[p.new_school_name]
        assert p.best_student is max(school, key=lambda s: s.get_exp_worth())
        for _ in range(10):
            p.teach_students()
        assert p.best_student is max(school, key=lambda s: s.get_exp_worth())

    def test_monthly_refreshes_best_student(self):
        g, p = make_game_and_player(seed=3, level=14)
        make_master(p, num_students=5)
        for _ in range(3):
            g.do_monthly()
        school = g.schools[p.new_school_name]
        assert p.best_student is max(school, key=lambda s: s.get_exp_worth())

    def test_best_student_save_round_trip(self):
        g, p = make_game_and_player(seed=4, level=14)
        make_master(p, num_students=3)
        data = g._player_to_data(p)
        assert data['best_student'] is not None
        assert data['best_student']['args'][0] == p.best_student.name


class TestStudentsInTournaments:
    @staticmethod
    def run_rigged_tournament(g, forced_winner):
        """Run a headless all-comers tournament with a forced winner."""
        orig = Tournament._do_rounds
        Tournament._do_rounds = lambda self: setattr(self, 'winner', forced_winner)
        try:
            # huge num_participants => every master/student gets in
            return Tournament(g, num_participants=200, min_lv=1, max_lv=20, fee=0)
        finally:
            Tournament._do_rounds = orig

    def test_student_participation_is_logged(self):
        g, p = make_game_and_player(seed=5, level=14)
        make_master(p, num_students=3)
        self.run_rigged_tournament(g, forced_winner=None)
        school = g.schools[p.new_school_name]
        assert any(
            f'{s.name} represents the school' in line for s in school for line in p.plog
        )

    def test_student_win_rewards_master(self):
        g, p = make_game_and_player(seed=6, level=14)
        make_master(p, num_students=3)
        student = p.best_student
        rep_before = p.reputation
        self.run_rigged_tournament(g, forced_winner=student)
        assert p.reputation == rep_before + STUDENT_TOURN_WIN_REP
        assert p.get_stat('students_tourn_won') == 1

    def test_master_of_champions_accomplishment(self):
        g, p = make_game_and_player(seed=7, level=14)
        make_master(p, num_students=3)
        student = p.best_student
        for _ in range(STUDENT_TOURN_WINS_ACCOMPL):
            self.run_rigged_tournament(g, forced_winner=student)
        assert 'Master of Champions' in p.accompl


class TestAllSchoolsTournament:
    @staticmethod
    def run_rigged(g, winners):
        """Run the event with the group FFA replaced by a stub."""
        orig = fight.group_free_for_all
        fight.group_free_for_all = lambda groups, **kw: SimpleNamespace(winners=winners)
        try:
            events.all_schools_tournament(g)
        finally:
            fight.group_free_for_all = orig

    def test_teams_are_master_plus_top_students(self):
        g, p = make_game_and_player(seed=8, level=14)
        make_master(p, num_students=4)
        captured = {}
        orig = fight.group_free_for_all

        def fake_gffa(groups, **kw):
            captured['groups'] = groups
            return SimpleNamespace(winners=[])

        fight.group_free_for_all = fake_gffa
        try:
            events.all_schools_tournament(g)
        finally:
            fight.group_free_for_all = orig
        teams = captured['groups']
        assert len(teams) >= 2
        for team in teams:
            assert 2 <= len(team) <= ALL_SCHOOLS_TEAM_SIZE
        # the player's school fields the player-master + its top 2 students
        p_team = next(t for t in teams if p in t)
        school = g.schools[p.new_school_name]
        top2 = sorted(school, key=lambda f: -f.get_exp_worth())[:2]
        assert p_team == [p] + top2

    def test_draw_gives_no_rewards(self):
        g, p = make_game_and_player(seed=9, level=14)
        make_master(p, num_students=3)
        exp_before, rep_before, money_before = p.exp, p.reputation, p.money
        self.run_rigged(g, winners=[])
        assert (p.exp, p.reputation, p.money) == (exp_before, rep_before, money_before)
        assert 'All-Schools Champion' not in p.accompl

    def test_player_win_rewards(self):
        g, p = make_game_and_player(seed=10, level=14)
        make_master(p, num_students=3)
        rep_before, money_before = p.reputation, p.money
        self.run_rigged(g, winners=[p])  # the player's team wins
        assert p.reputation == rep_before + ALL_SCHOOLS_WIN_REP
        assert p.money == money_before + ALL_SCHOOLS_PRIZE
        assert 'All-Schools Champion' in p.accompl

    def test_runs_headless_for_real(self):
        for seed in range(3):
            g, p = make_game_and_player(seed=20 + seed, level=14)
            make_master(p, num_students=3)
            events.all_schools_tournament(g)  # must not crash


class TestUniteSchools:
    def test_day_action_is_master_only(self):
        g, p = make_game_and_player(seed=11, level=14)
        labels = [a[0] for a in p.get_day_actions()]
        assert 'Visit other masters' not in labels
        make_master(p)
        labels = [a[0] for a in p.get_day_actions()]
        assert 'Visit other masters' in labels

    def test_ally_school_and_victory(self):
        g, p = make_game_and_player(seed=12, level=14)
        make_master(p)
        assert not check_united_schools(p)
        assert 'Uniter of Schools' not in g.check_victory_conditions(p)
        rep_before = p.reputation
        npc_schools = [(sn, m) for sn, m in g.masters.items() if not m.is_player]
        for sn, m in npc_schools:
            p.ally_school(sn, m)
        assert len(p.schools_allied) == len(npc_schools)
        assert p.reputation == rep_before + UNITED_SCHOOL_REP * len(npc_schools)
        assert 'Founder of the Federation' in p.accompl
        assert check_united_schools(p)
        assert 'Uniter of Schools' in g.check_victory_conditions(p)

    def test_visit_masters_persuasion(self):
        g, p = make_game_and_player(seed=13, level=14)
        make_master(p)
        p.reputation = 1000  # persuasion chance at its cap
        p.fight_or_not = lambda opp_info: False  # AI chooses persuasion
        orig_rnd = _bp.rnd
        _bp.rnd = lambda: 0.0  # force the persuasion roll to succeed
        try:
            assert p.visit_masters() is True
        finally:
            _bp.rnd = orig_rnd
        assert len(p.schools_allied) == 1

    def test_visit_masters_challenge(self):
        g, p = make_game_and_player(seed=14, level=14)
        make_master(p)
        p.fight_or_not = lambda opp_info: True  # AI chooses the spar
        p.spar = lambda opp, **kw: True
        assert p.visit_masters() is True
        assert len(p.schools_allied) == 1
        # losing the spar: no alliance, but the turn is still consumed
        p2 = g.players[1]
        make_master(p2)
        p2.fight_or_not = lambda opp_info: True
        p2.spar = lambda opp, **kw: False
        assert p2.visit_masters() is True
        assert not p2.schools_allied

    def test_no_unallied_masters_doesnt_consume_turn(self):
        g, p = make_game_and_player(seed=15, level=14)
        make_master(p)
        for sn, m in [(sn, m) for sn, m in g.masters.items() if not m.is_player]:
            p.ally_school(sn, m)
        assert p.visit_masters() is None

    def test_schools_allied_save_round_trip(self):
        g, p = make_game_and_player(seed=16, level=14)
        make_master(p)
        sn, m = p.get_unallied_masters()[0]
        p.ally_school(sn, m)
        data = g._player_to_data(p)
        assert data['atts']['schools_allied'] == [sn]
