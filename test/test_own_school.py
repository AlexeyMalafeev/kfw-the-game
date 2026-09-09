"""Own-school late-game mechanics: teaching, best student, students in
tournaments, the all-schools tournament and the schools-unification victory."""
import random

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib.actors.player import SmartAIP
from kf_lib.actors.player._base_player import TAUGHT_STUDENT_LV_GAP
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
