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
from kf_lib.utils import enum_words


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


class TestBookSeller:
    def _run(self, monkeypatch, money):
        g = make_game()
        p = g.players[0]
        p.money = money
        p.feel_too_greedy = 0.0
        asked = []
        monkeypatch.setattr(p, 'buy_item_or_not', lambda: asked.append(True) or True)
        encounters.BookSeller(p, check_if_happens=False)
        return p, asked

    def test_broke_player_is_refused_without_being_asked(self, monkeypatch):
        p, asked = self._run(monkeypatch, money=99)
        assert asked == []
        assert p.money == 99

    def test_player_who_can_pay_is_asked_and_pays(self, monkeypatch):
        p, asked = self._run(monkeypatch, money=150)
        assert asked == [True]
        assert p.money == 50


class TestStoryDispatch:
    def test_missing_scene_ends_story_with_a_warning(self, caplog):
        g = make_game()
        p = g.players[0]
        s = g.stories['ForeignerStory']
        s.start(p)
        assert p.current_story is s
        s.state = 99  # past the last scene
        s.advance()
        assert s.state == -1
        assert p.current_story is None
        assert s.boss is None
        assert 'ForeignerStory has no scene100' in caplog.text


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
        for token in (
            'First Fighter',
            '5',
            fa.style.public_name,
            'Second Fighter',
            '7',
            fb.style.public_name,
        ):
            assert token in info
        assert '-vs-' in info

    def test_prefight_info_never_reveals_true_style_names_of_npcs(self):
        from kf_lib.actors.fighter import Fighter
        from kf_lib.kung_fu import style_gen

        style = style_gen.get_style_from_str('Light-Footed Avalanche Leopard')
        fa = Fighter('First Fighter', style=style, level=5)
        assert style.public_name != style.name
        info = get_prefight_info([fa], basic_info_only=True)
        assert style.name not in info
        assert style.public_name in info


class TestQuotes:
    def test_quotes_loaded_at_import(self):
        from kf_lib.actors import quotes

        for attr in (
            'CHALLENGER_PREFIGHT',
            'CHALLENGER_WIN',
            'FIGHTER_PREFIGHT',
            'FIGHTER_WIN',
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

        for quotes_key in ('challenger', 'fighter', 'hero', 'master', 'thug'):
            assert quotes_key in quotes.PREFIGHT_QUOTES
            assert quotes_key in quotes.WIN_QUOTES


class TestWeaponsData:
    def test_weapons_registered(self):
        from kf_lib.things import weapons

        assert len(weapons.ALL_WEAPONS_LIST) > 0
        for w in weapons.ALL_WEAPONS_LIST:
            assert w.name
            assert w.get_exp_mult() >= 1.0

    def test_exp_mult_uses_the_defense_bonus_not_the_multiplier(self):
        # dfs_bonus is stored as 1 + bonus; until 2026-10 get_exp_mult averaged the
        # whole multiplier in, so every weapon was worth x1.8-1.9, while in A/B
        # mirror matches a weapon is worth about x1.2-1.4
        from kf_lib.things import weapons

        for w in weapons.ALL_WEAPONS_LIST:
            assert 1.2 < w.get_exp_mult() < 1.5, w.name

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

    def test_new_foreigner_skips_used_names(self):
        from kf_lib.actors import fighter_factory, names

        pool = names.FOREIGN_NAMES['Brazil']
        f = fighter_factory.new_foreigner(country='Brazil', used_names=set(pool[1:]))
        assert f.name == pool[0]
        with pytest.raises(ValueError, match='already in use'):
            fighter_factory.new_foreigner(country='Brazil', used_names=set(pool))


class TestAsciiArt:
    def test_duplicate_art_name_raises(self, tmp_path, monkeypatch):
        from kf_lib.kung_fu import ascii_art

        (tmp_path / 'ascii_mapping.txt').write_text(
            '# Stance, Kick\n (}\n/|\\\n# Kick\n (}\n/|_\n'
        )
        monkeypatch.setattr(ascii_art, 'MOVES_FOLDER', str(tmp_path))
        monkeypatch.setattr(ascii_art, 'FIGHTER_ART_L', {})
        monkeypatch.setattr(ascii_art, 'FIGHTER_ART_R', {})
        with pytest.raises(ValueError, match="'Kick' has more than one ASCII art"):
            ascii_art.set_ascii_art()


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

    def test_no_shadow_kick_rename_and_legacy_alias(self):
        # the move was 'No-Shadow_Kick' (a one-off underscore typo) before
        # 2026-09; old saves may still reference the old spelling
        from kf_lib.kung_fu import moves

        m = moves.get_move_obj('No-Shadow Kick')
        assert 'No-Shadow_Kick' not in moves.ALL_MOVES_DICT
        assert moves.get_move_obj('No-Shadow_Kick') is m

    def test_hung_ga_learns_signature_move(self):
        # regression: styles.py said 'No-Shadow Kick' but the move was named
        # 'No-Shadow_Kick', so Hung Ga lv-8 silently granted a random move
        from kf_lib.actors.fighter import Fighter

        random.seed(42)
        f = Fighter('Test', 'Hung Ga', 8)
        assert 'No-Shadow Kick' in [mv.name for mv in f.moves]

    def test_wing_chun_learns_short_fast_punch(self):
        # the style string always said 'Short Fast Punch'; the move itself was
        # only added to the data in 2026-09 (perks of Short Punch + Fast Punch)
        from kf_lib.actors.fighter import Fighter
        from kf_lib.kung_fu import moves

        m = moves.get_move_obj('Short Fast Punch')
        assert {'fast', 'punch', 'short'} <= m.features
        random.seed(1)
        f = Fighter('Test', 'Wing Chun', 8)
        assert 'Short Fast Punch' in [mv.name for mv in f.moves]

    def test_all_default_style_move_strings_are_valid(self):
        # content integrity: every default-style move string must reference
        # existing move names and existing feature tokens (features bias the
        # random pick; unknown ones silently do nothing)
        from kf_lib.kung_fu import styles
        from kf_lib.kung_fu.moves import ALL_MOVES_DICT

        valid_features = set()
        for m in ALL_MOVES_DICT.values():
            valid_features |= set(m.features)
        for s in styles.default_styles:
            for lv, ms in s.move_strings.items():
                entries = ms if isinstance(ms, tuple) else (ms,)
                for e in entries:
                    parts = [p.strip() for p in e.split(',')]
                    if len(parts) == 1 and not parts[0].isdigit():
                        assert parts[0] in ALL_MOVES_DICT, f'{s.name} lv{lv}: {parts[0]!r}'
                    else:
                        feats = parts[1:] if parts[0].isdigit() else parts
                        for feat in feats:
                            assert feat in valid_features, f'{s.name} lv{lv}: {feat!r} in {e!r}'

    def test_default_style_move_string_pools_non_empty(self):
        # an empty pool crashes on random.choice before the fallback
        from kf_lib.actors.fighter import Fighter
        from kf_lib.kung_fu import styles
        from kf_lib.kung_fu.moves import get_rand_moves

        random.seed(0)
        probe = Fighter('Probe', 'Xing Yi', 20)
        for s in styles.default_styles:
            for lv, ms in s.move_strings.items():
                entries = ms if isinstance(ms, tuple) else (ms,)
                for e in entries:
                    parts = [p.strip() for p in e.split(',')]
                    if len(parts) > 1:
                        tier = int(parts[0]) if parts[0].isdigit() else 10
                        feats = parts[1:] if parts[0].isdigit() else parts
                        assert get_rand_moves(probe, 3, tier, feats), f'{s.name} lv{lv}: {e!r}'


class TestGossipOpponentGrouping:
    def test_all_same_type_condensed(self):
        from kf_lib.happenings.encounters._people import group_same_fighters

        opps = [f'Thug {i}, lv.{i} Dirty Fighting' for i in (1, 2, 3, 4, 5)]
        assert enum_words(group_same_fighters(opps)) == '5 Thugs'

    def test_mixed_groups_and_singles(self):
        from kf_lib.happenings.encounters._people import group_same_fighters

        opps = [f'Thug {i}, lv.{i} Dirty Fighting' for i in (1, 2, 3)]
        opps += ['Zhao Liao, lv.5 Water Viper']
        opps += [f'Robber {i}, lv.{i + 1} Drunken Boxing' for i in (1, 2)]
        assert enum_words(group_same_fighters(opps)) == (
            '3 Thugs, Zhao Liao, lv.5 Water Viper and 2 Robbers'
        )

    def test_single_opponent_unchanged(self):
        from kf_lib.happenings.encounters._people import group_same_fighters

        opps = ['Qiu Cao, lv.3 Monkey Fist']
        assert group_same_fighters(opps) == opps

    def test_unnumbered_names_not_grouped(self):
        from kf_lib.happenings.encounters._people import group_same_fighters

        opps = ['Qiu Cao, lv.3 Monkey Fist', 'Qiu Cao, lv.4 Monkey Fist']
        assert group_same_fighters(opps) == opps


class TestGossipRumors:
    def test_fresh_game_always_has_a_rumor_about_someone_else(self):
        from kf_lib.happenings.encounters._rumors import collect_rumors

        g = make_game(seed=3, num_players=3)
        listener, *others = g.players
        rumors = collect_rumors(listener)
        assert rumors
        assert all(listener.name not in r for r in rumors)
        assert any(o.name in r for o in others for r in rumors)

    def test_lone_player_hears_about_themself(self):
        from kf_lib.happenings.encounters._rumors import collect_rumors

        g = make_game(seed=3, num_players=1)
        (p,) = g.players
        rumors = collect_rumors(p)
        assert rumors and all(p.name in r for r in rumors)

    def test_rumors_never_reveal_true_style_names(self):
        from kf_lib.happenings.encounters._rumors import collect_rumors

        g = make_game(seed=5, num_players=2)
        listener, other = g.players
        assert other.style.name != other.style.public_name
        other.knows_style_secret = lambda: True  # even if they learned it
        text = ' '.join(collect_rumors(listener))
        assert other.style.name not in text
        assert other.style.public_name in text

    def test_life_events_become_rumors(self):
        from kf_lib.happenings.encounters._rumors import collect_rumors

        g = make_game(seed=3, num_players=2)
        listener, other = g.players
        before = len(collect_rumors(listener))
        other.money = -10
        other.stats_dict['tourn_won'] = 2
        other.stats_dict['got_drunk'] = 5
        rumors = collect_rumors(listener)
        assert len(rumors) == before + 3
        assert any('owes money' in r for r in rumors)
        assert any('won 2 tournaments' in r for r in rumors)

    def test_basic_strikes_are_neither_favorite_nor_feared(self):
        from kf_lib.happenings.encounters._rumors import collect_rumors

        g = make_game(seed=3, num_players=2)
        listener, other = g.players
        basic = [m.name for m in other.moves if m.is_basic and m.power]
        other.move_usage = {name: 100 for name in basic}
        text = ' '.join(collect_rumors(listener))
        assert 'loves the' not in text
        assert 'receiving end' not in text  # a fresh fighter knows only basics
        other.level_up(6)  # learns style strikes
        style_move = next(m for m in other.moves if m.power and not m.is_basic)
        other.move_usage[style_move.name] = 1
        text = ' '.join(collect_rumors(listener))
        assert f'loves the {style_move.name}' in text

    @pytest.mark.parametrize('pays', [True, False])
    def test_gossip_tells_a_free_rumor_then_sells_the_table(self, monkeypatch, pays):
        from kf_lib.happenings.encounters import _people

        g = make_game(seed=3, num_players=2)
        p = g.players[0]
        p.money = 100
        shown = []
        monkeypatch.setattr(p, 'show', lambda t, *a, **kw: shown.append(t))
        monkeypatch.setattr(p, 'hear_rumors_or_not', lambda: pays)
        tables = []
        monkeypatch.setattr(g, 'show_stats', lambda *a, **kw: tables.append(1))
        _people.Gossip(p, check_if_happens=False)
        assert shown[1].startswith('Gossipmonger: "')
        spent = 100 - p.money
        if pays:
            assert spent in _people.MONEY_GOSSIP_COST and tables == [1]
        else:
            assert spent == 0 and tables == []
