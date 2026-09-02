"""Content characterization: encounters, stories, tournament, events."""
import random

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib.actors.player import SmartAIP
from kf_lib.fighting.fight import get_prefight_info
from kf_lib.happenings import encounters, events, story
from kf_lib.happenings.encounters._base_encounter import BaseEncounter
from kf_lib.happenings.story._base_story import BaseStory
from kf_lib.happenings.tournament import Tournament


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


class TestEncounterData:
    def test_random_encounter_classes_registered(self):
        assert len(encounters.all_random_encounter_classes) > 0
        for cls in encounters.all_random_encounter_classes:
            assert issubclass(cls, BaseEncounter)
            assert not cls.guaranteed

    def test_guaranteed_encounters_not_in_random_pool(self):
        pool = set(encounters.all_random_encounter_classes)
        for name in ('GBeggar', 'GChallenger', 'GDrunkard', 'GGambler', 'GMerchant', 'GRobbers'):
            cls = getattr(encounters, name)
            assert cls.guaranteed
            assert cls not in pool

    def test_encounter_chance_constants_are_probabilities(self):
        for name in dir(encounters):
            if name.startswith('ENC_CH_'):
                value = getattr(encounters, name)
                assert 0 < value <= 1, name

    def test_extra_encounter_lists_are_well_formed(self):
        for list_name in (
            'BUY_ITEMS_ENCS',
            'FIGHT_CRIME_ENCS',
            'HELP_POOR_ENCS',
            'PICK_FIGHTS_ENCS',
            'PRACTICE_SCHOOL_ENCS',
            'SEEDY_PLACES_ENCS',
            'WALK_ENCS',
        ):
            enc_list = getattr(encounters, list_name)
            assert enc_list, list_name
            for cls in enc_list:
                assert issubclass(cls, BaseEncounter), f'{list_name}: {cls}'

    def test_every_random_encounter_implements_abstract_methods(self):
        for cls in encounters.all_random_encounter_classes:
            assert cls.check_if_happens is not BaseEncounter.check_if_happens
            assert cls.run is not BaseEncounter.run


class TestStories:
    def test_all_stories_registered(self):
        all_stories = story.get_all_stories()
        assert len(all_stories) >= 6
        for cls in all_stories:
            assert issubclass(cls, BaseStory)

    def test_new_game_instantiates_all_stories(self):
        g = make_game()
        assert len(g.stories) == len(story.get_all_stories())
        for key, s in g.stories.items():
            assert key == s.__class__.__name__
            assert s.state is None
            assert s.check_hasnt_started()
            assert s.player is None and s.boss is None

    def test_story_instantiation_defaults(self):
        for cls in story.get_all_stories():
            s = cls(None)
            assert s.name == cls.__name__
            assert s.state is None


class TestTournament:
    def test_tournament_runs_headless(self):
        g = make_game(seed=2)
        t = Tournament(g, num_participants=8, min_lv=1, max_lv=5, fee=50)
        assert t.winner is not None
        assert t.winner in t.participants
        assert t.current_round == 3  # 8 participants -> 3 rounds

    def test_tournament_participants_within_level_range(self):
        g = make_game(seed=3)
        t = Tournament(g, num_participants=8, min_lv=1, max_lv=5, fee=50)
        assert len(t.participants) <= 8
        for f in t.participants:
            assert 1 <= f.level <= 5

    def test_tournament_deterministic_with_seed(self):
        g1 = make_game(seed=7)
        t1 = Tournament(g1, num_participants=8, min_lv=1, max_lv=5, fee=50)
        g2 = make_game(seed=7)
        t2 = Tournament(g2, num_participants=8, min_lv=1, max_lv=5, fee=50)
        assert t1.winner.name == t2.winner.name

    def test_prize_calculation(self):
        g = make_game()
        t = Tournament(g, num_participants=8, min_lv=1, max_lv=5, fee=100)
        # auto prize = fee * num_participants / 2, rounded to tens
        assert t.prize == 400

    def test_player_winner_gets_prize_and_stat(self):
        # force an all-player tournament so the winner must be a player
        g = make_game(seed=5, num_players=4)
        for p in g.players:
            p.money = 1000
        t = Tournament(g, num_participants=4, min_lv=1, max_lv=5, fee=50)
        assert t.winner.is_player
        assert t.winner.get_stat('tourn_won') == 1


class TestEvents:
    def test_tournament_definitions_are_well_formed(self):
        assert events.TOURN_TYPES == ('beginner', 'intermediate', 'advanced', 'master')
        for t in events.TOURNAMENTS:
            assert t['min_lv'] < t['max_lv']
            assert t['tourn_type'] in events.TOURN_TYPES

    def test_chance_constants_are_probabilities(self):
        for name in dir(events):
            if name.startswith('CH_'):
                value = getattr(events, name)
                assert 0 < value <= 1, name


class TestPrefightInfo:
    def test_prefight_info_mentions_names_levels_styles(self):
        from kf_lib.actors import fighter_factory

        random.seed(0)
        fa = fighter_factory.new_fighter(5)
        fb = fighter_factory.new_fighter(7)
        fa.name, fb.name = 'First Fighter', 'Second Fighter'
        info = get_prefight_info([fa], [fb], basic_info_only=True)
        for token in ('First Fighter', '5', fa.style.name, 'Second Fighter', '7', fb.style.name):
            assert token in info
        assert '-vs-' in info


class TestQuotes:
    def test_quotes_loaded_at_import(self):
        from kf_lib.actors import quotes

        for attr in (
            'CHALLENGER_PREFIGHT',
            'CHALLENGER_WIN',
            'HERO_PREFIGHT',
            'HERO_WIN',
            'THUG_PREFIGHT',
            'THUG_WIN',
            'WISDOM',
            'MASTER_CRITICISM',
            'TRAINING_INJURY',
        ):
            assert len(getattr(quotes, attr)) > 0, attr

    def test_prefight_and_win_quote_maps_cover_fighter_classes(self):
        from kf_lib.actors import quotes

        for quotes_key in ('challenger', 'hero', 'master', 'thug'):
            assert quotes_key in quotes.PREFIGHT_QUOTES
            assert quotes_key in quotes.WIN_QUOTES


class TestWeaponsData:
    def test_weapons_registered(self):
        from kf_lib.things import weapons

        assert len(weapons.ALL_WEAPONS_LIST) > 0
        for w in weapons.ALL_WEAPONS_LIST:
            assert w.name
            assert w.get_exp_mult() >= 1.0

    def test_get_wp_by_name(self):
        from kf_lib.things import weapons

        w = weapons.get_wp('knife')
        assert w.name == 'knife'

    def test_arm_and_disarm_by_name(self):
        from kf_lib.actors import fighter_factory

        random.seed(0)
        f = fighter_factory.new_fighter(5)
        assert f.weapon is None
        f.arm('knife')
        assert f.weapon.name == 'knife'
        f.disarm()
        assert f.weapon is None


class TestForeignStyles:
    def test_every_foreign_style_country_has_names(self):
        # names.py warns: "when adding new foreign style, add names to names.py"
        from kf_lib.actors import names
        from kf_lib.kung_fu import styles

        assert set(names.FOREIGN_COUNTRIES) == set(styles.FOREIGN_STYLES)
        assert set(names.FOREIGN_NAMES) == set(styles.FOREIGN_STYLES)
        for country, name_list in names.FOREIGN_NAMES.items():
            assert len(name_list) > 0, country

    def test_new_foreigner_matches_country(self):
        from kf_lib.actors import fighter_factory

        random.seed(0)
        f = fighter_factory.new_foreigner(country='Japan')
        assert f.country == 'Japan'
        assert f.style.name == 'Karate'


class TestMoveLookup:
    def test_get_move_obj(self):
        from kf_lib.kung_fu import moves

        m = moves.get_move_obj('Punch')
        assert m.name == 'Punch'

    def test_unknown_move_raises(self):
        from kf_lib.kung_fu import moves

        with pytest.raises(moves.MoveNotFoundError):
            moves.get_move_obj('No Such Move')

    def test_resolve_move_string_by_tier(self):
        from kf_lib.actors import fighter_factory
        from kf_lib.kung_fu import moves

        random.seed(0)
        f = fighter_factory.new_fighter(1)
        n_moves = len(f.moves)
        moves.resolve_move_string('1', f)  # '1' = one random tier-1 move
        assert len(f.moves) == n_moves + 1
        assert f.moves[-1].tier == 1
