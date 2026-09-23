"""Own-school late-game mechanics: teaching, best student, students in
tournaments, the all-schools tournament and the schools-unification victory."""
import random
from types import SimpleNamespace

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
import kf_lib.actors.player._base_player as _bp
from kf_lib.actors.player import SmartAIP
from kf_lib.actors.player._base_player import (
    NUM_SCHOOL_TECHS,
    TAUGHT_STUDENT_LV_GAP,
    UNITED_SCHOOL_REP,
)
from kf_lib.fighting import fight
from kf_lib.game._playing import check_united_schools
from kf_lib.happenings import events
from kf_lib.happenings.encounters import _school as school_mod
from kf_lib.happenings.encounters._school import RANK1_EXP, RANK1_REP, SchoolChallenge, Students
from kf_lib.happenings.story import _student_rivalry as sr_mod
from kf_lib.happenings.story._school_attack import (
    SCHOOL_DEFENSE_LOSE_REP,
    SCHOOL_DEFENSE_WIN_REP,
)
from kf_lib.kung_fu import techniques
import kf_lib.happenings.all_schools as as_mod
from kf_lib.happenings.all_schools import (
    ALL_SCHOOLS_MASTER_REP,
    ALL_SCHOOLS_PART_EXP,
    AllSchoolsTournament,
)
import kf_lib.happenings.tournament as tourn_mod
from kf_lib.happenings.tournament import (
    BET_REPUTATION_PENALTY,
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
    """Scheduled monthly tournament: a fighter-centric bracket — each round
    every school fields one fighter (the previous survivor or, after a KO,
    the next higher-ranking student); KO'd fighters are out for good."""

    @staticmethod
    def make_tournament(g):
        """An AllSchoolsTournament instance without running anything."""
        t = AllSchoolsTournament.__new__(AllSchoolsTournament)
        t.g = t.game = g
        t.rosters = {}
        t.final_fighter = None
        t.champion = None
        return t

    @staticmethod
    def school_of(g, f):
        for name, roster in g.schools.items():
            if f in roster:
                return name

    @classmethod
    def run_rigged(cls, g, champion_school=None, mutual_ko=False):
        """Run the whole tournament with fight.fight/free_for_all stubbed.
        champion_school's representative always stays up; with mutual_ko every
        bout ends with everybody down."""

        def resolve(fighters):
            if mutual_ko:
                for f in fighters:
                    f.hp = 0
                return
            champion_reps = [
                f for f in fighters
                if champion_school is not None
                and cls.school_of(g, f) == champion_school
            ]
            if champion_reps:
                for f in fighters:
                    if f not in champion_reps:
                        f.hp = 0
            else:
                for f in fighters[1:]:
                    f.hp = 0

        def fake_fight(a, b, **kw):
            resolve([a, b])

        def fake_ffa(fighters, **kw):
            resolve(list(fighters))

        orig_fight, orig_ffa = fight.fight, fight.free_for_all
        fight.fight, fight.free_for_all = fake_fight, fake_ffa
        try:
            return AllSchoolsTournament(g)
        finally:
            fight.fight, fight.free_for_all = orig_fight, orig_ffa

    def test_rosters_are_students_only_weakest_first(self):
        g, p = make_game_and_player(seed=8, level=14)
        make_master(p, num_students=4)
        t = self.make_tournament(g)
        t._gather_rosters()
        assert len(t.rosters) == len(g.schools)  # no school is empty here
        for name, roster in t.rosters.items():
            assert g.masters.get(name) not in roster  # masters don't fight
            assert roster == sorted(roster, key=lambda f: f.get_exp_worth())
        assert p not in t.rosters[p.new_school_name]  # the player-master doesn't fight

    def test_inactive_players_are_excluded(self):
        g, p = make_game_and_player(seed=8, level=14)
        p.inactive = 3  # injured
        t = self.make_tournament(g)
        t._gather_rosters()
        assert all(p not in roster for roster in t.rosters.values())

    def test_odd_fighter_count_yields_one_three_way_per_round(self):
        g, p = make_game_and_player(seed=8, level=14)
        make_master(p, num_students=3)
        t = self.make_tournament(g)
        t._gather_rosters()
        captured = []

        def fake_bout(self_, fighters):
            captured.append(len(fighters))
            for f in fighters:  # everyone down — full replacement next round
                f.hp = 0

        orig = AllSchoolsTournament._do_bout
        AllSchoolsTournament._do_bout = fake_bout
        try:
            t._do_rounds()
        finally:
            AllSchoolsTournament._do_bout = orig
        # every school loses exactly one student per round, so a school is
        # still active in round r iff it has at least r students
        roster_sizes = sorted(len(roster) for roster in t.rosters.values())
        expected = []
        r = 1
        while True:
            n_active = sum(1 for s in roster_sizes if s >= r)
            if n_active <= 1:
                break
            if n_active % 2:
                expected.append(3)
                expected += [2] * ((n_active - 3) // 2)
            else:
                expected += [2] * (n_active // 2)
            r += 1
        assert captured == expected  # one 3-way per odd round, pairs otherwise

    def test_kod_fighter_replaced_survivor_heals(self):
        g, p = make_game_and_player(seed=9, level=1)
        t = self.make_tournament(g)
        names = [n for n in g.schools if len(g.schools[n]) >= 2][:2]
        assert len(names) == 2
        t.rosters = {
            n: sorted(g.schools[n], key=lambda f: f.get_exp_worth()) for n in names
        }
        win_school, lose_school = names
        calls = []

        def school_of(f):
            return next(n for n in names if f in t.rosters[n])

        def fake_fight(a, b, **kw):
            win_f, lose_f = (a, b) if school_of(b) == lose_school else (b, a)
            calls.append((win_f, lose_f, win_f.hp))
            lose_f.hp = 0  # knocked out
            win_f.hp = 1  # the winner is left battered

        orig = fight.fight
        fight.fight = fake_fight
        try:
            t._do_rounds()
        finally:
            fight.fight = orig
        assert t.champion == win_school
        # the weakest student of the winning school survives every round
        winner = t.rosters[win_school][0]
        assert t.final_fighter is winner
        assert [w for w, l, hp in calls] == [winner] * len(calls)
        # the losing school fields its students weakest-first, and a KO'd
        # fighter never comes back
        assert [l for w, l, hp in calls] == t.rosters[lose_school]
        # nobody fights twice in a round: the survivor starts every bout healed
        assert all(hp == winner.hp_max for w, l, hp in calls)

    def test_drawn_final_with_no_reserves_is_a_draw(self):
        g, p = make_game_and_player(seed=9, level=1)
        t = self.make_tournament(g)
        names = list(g.schools)[:2]
        t.rosters = {n: g.schools[n][:1] for n in names}

        def fake_fight(a, b, **kw):
            a.hp = b.hp = 0

        orig = fight.fight
        fight.fight = fake_fight
        try:
            t._do_rounds()
        finally:
            fight.fight = orig
        assert t.champion is None and t.final_fighter is None

    def test_final_winner_player_gets_accomplishment(self):
        g, p = make_game_and_player(seed=10, level=5)
        school_name = p.style.name
        assert p in g.schools[school_name]
        g.schools[school_name] = [p]  # p is the school's only student
        t = self.run_rigged(g, champion_school=school_name)
        assert t.champion == school_name
        assert 'All-Schools Champion' in p.accompl

    def test_non_final_roster_player_gets_part_exp(self):
        g, p = make_game_and_player(seed=11, level=8)
        school_name = p.style.name
        others = [f for f in g.schools[school_name] if f is not p]
        weakest = min(others, key=lambda f: f.get_exp_worth())
        assert weakest.get_exp_worth() < p.get_exp_worth()  # sanity: p fights last
        g.schools[school_name] = [weakest, p]
        exp_before = p.exp
        t = self.run_rigged(g, champion_school=school_name)
        assert t.champion == school_name
        assert t.final_fighter is weakest  # p never had to fight
        assert 'All-Schools Champion' not in p.accompl
        assert p.exp == exp_before + ALL_SCHOOLS_PART_EXP

    def test_master_of_champion_school_gets_rep(self):
        g, p = make_game_and_player(seed=12, level=14)
        make_master(p, num_students=3)
        rep_before, exp_before, money_before = p.reputation, p.exp, p.money
        t = self.run_rigged(g, champion_school=p.new_school_name)
        assert t.champion == p.new_school_name
        assert p.reputation == rep_before + ALL_SCHOOLS_MASTER_REP
        assert p.get_stat('all_schools_tourn_won') == 1
        # prestige only: no exp (masters don't fight) and no money prize
        assert p.exp == exp_before
        assert p.money == money_before
        assert 'All-Schools Champion' not in p.accompl

    def test_drawn_tournament_gives_no_rewards(self):
        g, p = make_game_and_player(seed=13, level=5)
        for name, roster in g.schools.items():
            g.schools[name] = [p] if p in roster else roster[:1]
        exp_before, rep_before = p.exp, p.reputation
        t = self.run_rigged(g, mutual_ko=True)
        assert t.champion is None
        assert (p.exp, p.reputation) == (exp_before, rep_before)
        assert 'All-Schools Champion' not in p.accompl

    def test_scheduled_monthly(self):
        g, p = make_game_and_player(seed=30, level=5)
        calls = []
        orig = events.all_schools_tournament
        events.all_schools_tournament = calls.append
        try:
            g.do_monthly()
        finally:
            events.all_schools_tournament = orig
        assert calls == [g]

    def test_runs_headless_for_real(self):
        for seed in range(3):
            g, p = make_game_and_player(seed=20 + seed, level=10)
            make_master(p, num_students=3)
            AllSchoolsTournament(g)  # must not crash

    def test_auto_fight_all_asked_and_reset(self):
        g, p = make_game_and_player(seed=14, level=5)
        p.is_human = True  # fake hot-seat human
        g.schools[p.style.name] = [p]  # make sure p fights in every match
        asked = []
        orig_yn = as_mod.yn
        as_mod.yn = lambda text: asked.append(text) or True
        flags = []
        orig_fight, orig_ffa = fight.fight, fight.free_for_all

        def fake_fight(a, b, **kw):
            if p in (a, b):
                flags.append(p.auto_fight_all)
            b.hp = 0

        def fake_ffa(fighters, **kw):
            if p in fighters:
                flags.append(p.auto_fight_all)
            for f in fighters[1:]:
                f.hp = 0

        fight.fight, fight.free_for_all = fake_fight, fake_ffa
        try:
            AllSchoolsTournament(g)
        finally:
            as_mod.yn = orig_yn
            fight.fight, fight.free_for_all = orig_fight, orig_ffa
        assert len(asked) == 1  # only p is human
        assert flags and all(flags)  # the flag was on during p's bouts
        assert p.auto_fight_all is False  # reset after the tournament


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


class TestSchoolTechs:
    def test_ai_master_picks_known_techs(self):
        g, p = make_game_and_player(seed=17, level=14)
        p.learn_tech(techniques.get_learnable_techs(p)[0])
        p.choose_school_techs()
        assert 1 <= len(p.school_techs) <= NUM_SCHOOL_TECHS
        known = [t.name for t in p.techs]
        assert all(name in known for name in p.school_techs)

    def test_weapon_techs_are_not_taught(self):
        g, p = make_game_and_player(seed=18, level=14)
        weapon_tech = techniques.get_weapon_techs()[0]
        p.techs = [weapon_tech]  # knows nothing but a weapon tech
        p.choose_school_techs()
        assert p.school_techs == []

    def test_teaching_passes_school_techs(self):
        g, p = make_game_and_player(seed=19, level=14)
        make_master(p, num_students=4)
        tech = techniques.get_learnable_techs(p)[0]
        p.learn_tech(tech)
        p.school_techs = [tech.name]
        school = g.schools[p.new_school_name]
        orig_rnd = _bp.rnd
        _bp.rnd = lambda: 0.0  # every roll succeeds
        try:
            p.teach_students()
        finally:
            _bp.rnd = orig_rnd
        assert all(tech in s.techs for s in school)

    def test_students_dont_learn_unrelated_techs(self):
        g, p = make_game_and_player(seed=20, level=14)
        make_master(p, num_students=3)
        school = g.schools[p.new_school_name]
        # level the students to the cap first, so no level-up style techs
        # interfere with the count
        for s in school:
            while s.level < p.level - TAUGHT_STUDENT_LV_GAP:
                s.level_up()
        tech_counts_before = [len(s.techs) for s in school]
        p.school_techs = []  # school teaches nothing
        orig_rnd = _bp.rnd
        _bp.rnd = lambda: 0.0
        try:
            p.teach_students()
        finally:
            _bp.rnd = orig_rnd
        assert [len(s.techs) for s in school] == tech_counts_before

    def test_school_techs_save_round_trip(self):
        g, p = make_game_and_player(seed=21, level=14)
        make_master(p)
        p.learn_tech(techniques.get_learnable_techs(p)[0])
        p.choose_school_techs()
        data = g._player_to_data(p)
        assert data['atts']['school_techs'] == p.school_techs


def run_story(g, p, story_name, max_advances=4):
    """Force-start a story and advance it to the end."""
    s = g.stories[story_name]
    assert s.test(p), f'{story_name} should be available to {p.name}'
    s.start(p)
    for _ in range(max_advances):
        if p.current_story is None:
            break
        p.hp = p.hp_max
        p.inactive = 0
        s.advance()
    assert p.current_story is None, f'{story_name} stuck at state {s.state}'
    return s


class TestSchoolAttackStory:
    def test_gating(self):
        g, p = make_game_and_player(seed=30, level=14)
        s = g.stories['SchoolAttackStory']
        assert not s.test(p)  # not a master
        make_master(p, num_students=1)
        assert not s.test(p)  # not enough students
        p.add_students(1)
        assert s.test(p)

    def test_win_branch(self):
        g, p = make_game_and_player(seed=31, level=14)
        make_master(p, num_students=3)
        p.fight = lambda *a, **kw: True
        rep_before = p.reputation
        run_story(g, p, 'SchoolAttackStory')
        assert p.reputation == rep_before + SCHOOL_DEFENSE_WIN_REP
        assert 'School Defender' in p.accompl

    def test_lose_branch(self):
        g, p = make_game_and_player(seed=32, level=14)
        make_master(p, num_students=3)
        p.fight = lambda *a, **kw: False
        p.money = 500
        rep_before = p.reputation
        run_story(g, p, 'SchoolAttackStory')
        assert p.reputation == rep_before + SCHOOL_DEFENSE_LOSE_REP
        assert p.money < 500  # the school is ransacked
        assert 'School Defender' not in p.accompl

    def test_completes_for_real(self):
        for seed in range(3):
            g, p = make_game_and_player(seed=40 + seed, level=16)
            make_master(p, num_students=4)
            run_story(g, p, 'SchoolAttackStory')


class TestStudentRivalryStory:
    @staticmethod
    def force_choice(choice, duel_anyway=False):
        """Patch the story module's RNG so the AI player picks `choice`."""
        orig_random, orig_rnd = sr_mod.random, sr_mod.rnd
        sr_mod.random = SimpleNamespace(sample=random.sample, choice=lambda seq: choice)
        sr_mod.rnd = lambda: 0.0 if duel_anyway else 1.0
        return orig_random, orig_rnd

    @staticmethod
    def restore(orig_random, orig_rnd):
        sr_mod.random, sr_mod.rnd = orig_random, orig_rnd

    def make_master_with_students(self, seed):
        g, p = make_game_and_player(seed=seed, level=14)
        make_master(p, num_students=3)
        return g, p

    def test_gating(self):
        g, p = make_game_and_player(seed=50, level=14)
        s = g.stories['StudentRivalryStory']
        assert not s.test(p)
        make_master(p, num_students=2)
        assert s.test(p)

    def test_duel_branch(self):
        g, p = self.make_master_with_students(51)
        state = self.force_choice(sr_mod.DUEL)
        rep_before = p.reputation
        try:
            run_story(g, p, 'StudentRivalryStory')
        finally:
            self.restore(*state)
        assert p.reputation == rep_before + sr_mod.DUEL_REP
        assert any('duel' in line for line in p.plog)

    def test_spar_branches(self):
        for spar_wins, expected_rep in (
            (True, sr_mod.SPAR_WIN_REP),
            (False, sr_mod.SPAR_LOSS_REP),
        ):
            g, p = self.make_master_with_students(52)
            p.spar = lambda *a, **kw: spar_wins
            state = self.force_choice(sr_mod.SPAR)
            rep_before = p.reputation
            try:
                run_story(g, p, 'StudentRivalryStory')
            finally:
                self.restore(*state)
            assert p.reputation == rep_before + expected_rep

    def test_forbid_branches(self):
        # obeyed: nothing happens
        g, p = self.make_master_with_students(53)
        state = self.force_choice(sr_mod.FORBID, duel_anyway=False)
        rep_before = p.reputation
        try:
            run_story(g, p, 'StudentRivalryStory')
        finally:
            self.restore(*state)
        assert p.reputation == rep_before
        # disobeyed: they duel anyway, the master loses face
        g, p = self.make_master_with_students(54)
        state = self.force_choice(sr_mod.FORBID, duel_anyway=True)
        rep_before = p.reputation
        try:
            run_story(g, p, 'StudentRivalryStory')
        finally:
            self.restore(*state)
        assert p.reputation == rep_before + sr_mod.DISOBEYED_REP

    def test_completes_for_real(self):
        for seed in range(5):
            g, p = self.make_master_with_students(60 + seed)
            run_story(g, p, 'StudentRivalryStory')


class TestMastersHelp:
    @staticmethod
    def force_rnd_zero():
        orig_rnd = _bp.rnd
        _bp.rnd = lambda: 0.0  # every chance roll succeeds
        return orig_rnd

    def test_get_school_for_masters_and_students(self):
        g, p = make_game_and_player(seed=70, level=14)
        style_school = g.schools[p.style.name]
        assert p.get_school() is style_school
        make_master(p, num_students=2)
        assert p.get_school() is g.schools[p.new_school_name]

    def test_master_helped_by_best_student(self):
        g, p = make_game_and_player(seed=71, level=14)
        make_master(p, num_students=3)
        orig_rnd = self.force_rnd_zero()
        try:
            p.check_help(allies=False, master=True, impr_wp=False, school=False)
        finally:
            _bp.rnd = orig_rnd
        school = g.schools[p.new_school_name]
        assert p.allies == [max(school, key=lambda f: f.get_exp_worth())]

    def test_non_master_helped_by_master(self):
        g, p = make_game_and_player(seed=72, level=5)
        orig_rnd = self.force_rnd_zero()
        try:
            p.check_help(allies=False, master=True, impr_wp=False, school=False)
        finally:
            _bp.rnd = orig_rnd
        assert p.allies == [p.get_master()]

    def test_school_help_with_a_single_student(self):
        g, p = make_game_and_player(seed=73, level=14)
        make_master(p, num_students=1)
        orig_rnd = self.force_rnd_zero()
        try:
            # must not crash on random.sample with fewer mates than requested
            p.check_help(allies=False, master=False, impr_wp=False, school=True)
        finally:
            _bp.rnd = orig_rnd
        school = g.schools[p.new_school_name]
        assert p.allies == school


class TestTournamentEdgeCases:
    def test_zero_participants_cancels(self):
        g, p = make_game_and_player(seed=80)
        t = Tournament(g, num_participants=8, min_lv=100, max_lv=200, fee=0)
        assert t.winner is None  # canceled, no crash

    def test_drawn_final_gives_no_winner(self):
        g, p = make_game_and_player(seed=81)
        orig = tourn_mod.fight.fight
        orig_gather = Tournament._gather_participants
        tourn_mod.fight.fight = lambda *a, **kw: SimpleNamespace(winners=[])
        # force a two-man bracket: no byes, so a drawn final means no winner
        Tournament._gather_participants = lambda self: setattr(
            self, 'participants', g.fighters_list[:2]
        )
        try:
            t = Tournament(g, num_participants=200, min_lv=1, max_lv=20, fee=0)
        finally:
            tourn_mod.fight.fight = orig
            Tournament._gather_participants = orig_gather
        assert t.winner is None  # drawn final, no NotImplementedError

    def test_bet_rep_penalty_on_placement(self):
        g, p = make_game_and_player(seed=82)
        g.players[1].bet_on_tourn_or_not = lambda: False
        p.bet_on_tourn_or_not = lambda: True
        p.place_bet_on_tourn = lambda t: (t.participants[0], 10)
        rep_before = p.reputation
        Tournament(g, num_participants=4, min_lv=1, max_lv=20, fee=0)
        assert p.reputation == rep_before + BET_REPUTATION_PENALTY


class TestStudentIntake:
    def test_fresh_master_has_base_chance(self):
        g, p = make_game_and_player(seed=90, level=14)
        make_master(p, num_students=0)
        assert p.get_fame() == 0
        enc = Students.__new__(Students)
        enc.p = enc.player = p
        orig_rnd = school_mod.rnd
        try:
            school_mod.rnd = lambda: 0.005  # below the 0.01 base chance
            assert enc.check_if_happens()
            school_mod.rnd = lambda: 0.02  # above it
            assert not enc.check_if_happens()
        finally:
            school_mod.rnd = orig_rnd

    def test_best_student_in_verbose_info(self):
        g, p = make_game_and_player(seed=91, level=14)
        make_master(p, num_students=2)
        assert f'best: {p.best_student.name}' in p.get_p_info_verbose()


class TestRank1Reward:
    def test_reaching_rank1_rewards(self):
        g, p = make_game_and_player(seed=95, level=10)
        school = g.schools[p.style.name]
        school.remove(p)
        school.insert(1, p)  # rank 2, one win away from the top
        p.refresh_school_rank()
        assert p.school_rank == 2
        p.spar = lambda opp, **kw: True
        p.fight_or_not = lambda *a, **kw: True
        exp_gains = []
        p.gain_exp = lambda n, **kw: exp_gains.append(n)
        rep_before = p.reputation
        SchoolChallenge(p, check_if_happens=False)
        assert p.school_rank == 1
        assert exp_gains == [RANK1_EXP]
        assert p.reputation == rep_before + RANK1_REP


class TestSchoolChallenge:
    """A school-rank challenge must skip inactive (KO'd) schoolmates: the
    challenger fights the next active one above, leapfrogging the skipped
    ones in the ranking on a win."""

    def _setup_same_school(self, seed=97, level=8):
        """Two players in one school (like a hot-seat game sharing a style),
        ranked [npc1, npc2, p2, p]."""
        g, p = make_game_and_player(seed=seed, level=level)
        p2 = g.players[1]
        own = g.schools[p2.style.name]
        if p2 in own:
            own.remove(p2)
        p2.style = p.style
        school = g.schools[p.style.name]
        npcs = [f for f in school if f is not p][:2]
        school[:] = [npcs[0], npcs[1], p2, p]
        for pl in g.players:
            pl.refresh_school_rank()
        return g, p, p2, npcs

    def test_challenge_skips_inactive_and_leapfrogs_ranks(self):
        g, p, p2, npcs = self._setup_same_school()
        assert (p.school_rank, p2.school_rank) == (4, 3)
        p2.inactive = 3  # KO'd: cannot be challenged
        sparred = []
        p.spar = lambda opp, **kw: sparred.append(opp) or True
        p.fight_or_not = lambda *a, **kw: True
        orig_rnd = school_mod.rnd
        try:
            school_mod.rnd = lambda: 0.99  # no arming
            SchoolChallenge(p, check_if_happens=False)
        finally:
            school_mod.rnd = orig_rnd
        # the challenge goes past the KO'd p2 to the next active one above
        assert sparred == [npcs[1]]
        # the winner takes the defeated's slot; everyone passed drops a rank
        p.refresh_school_rank()
        p2.refresh_school_rank()
        assert p.school_rank == 2  # +2
        assert p2.school_rank == 4  # skipped while KO'd: -1 (was 3)
        school = g.schools[p.style.name]
        assert school.index(npcs[1]) == 2  # defeated: rank 3
        assert school.index(npcs[0]) == 0  # rank 1 untouched

    def test_no_challenge_when_everyone_above_is_inactive(self):
        g, p, p2, npcs = self._setup_same_school()
        school = g.schools[p.style.name]
        school.remove(npcs[0])
        school.remove(npcs[1])  # only the KO'd p2 is above p
        p.refresh_school_rank()
        assert p.school_rank == 2
        p2.inactive = 3
        # check the gate without running the encounter
        enc = SchoolChallenge.__new__(SchoolChallenge)
        enc.p = p
        orig_rnd = school_mod.rnd
        try:
            school_mod.rnd = lambda: 0.0  # chance is not the blocker here
            assert not enc.check_if_happens()
        finally:
            school_mod.rnd = orig_rnd
