"""Save system characterization tests.

The save format is JSON (see kf_lib/game/_save_game.py); loading auto-detects
the format — JSON saves are parsed, anything else falls back to the legacy
exec()-based loader (kf_lib/game/_load_game.py). These tests keep the user's
real save/ folder untouched by monkeypatching SAVE_FOLDER in both modules to a
pytest tmp_path.
"""
import json
import random
from pathlib import Path
from types import SimpleNamespace

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
import kf_lib.game._save_game as save_mod
import kf_lib.game._load_game as load_mod
from kf_lib.actors import fighter_factory
from kf_lib.actors.fighter import Fighter
from kf_lib.actors.player import SmartAIP
from kf_lib.happenings import story

SAVE_NAME = 'pytest save.txt'

# A small hand-written save in the legacy exec-based format (modeled on real
# output of the old writer): one player, three schools with masters, the
# special NPCs, all stories, game attributes and a per-player block.
LEGACY_SAVE = """\
g.fighters_dict = fsd = {}

fsd['Test Hero'] = SmartAIP('Test Hero', 'Drunken Boxing', 5, (4, 5, 4, 6), [], ['Precise Claw'], 2, ['unfriendly', 'brave'])

fsd['Master Lei'] = Master('Master Lei', 'Drunken Boxing', 14, (8, 6, 7, 7), [], ['Pushing Elbow'])

fsd['Master Zhao'] = Master('Master Zhao', 'Long Fist', 13, (3, 8, 9, 7), [], ['Heavy Claw'])

fsd['Master Qiu'] = Master('Master Qiu', 'Tiger', 14, (6, 5, 9, 8), [], ['Long Elbow'])

fsd['Wang Jing'] = Fighter('Wang Jing', 'Drunken Boxing', 2, (3, 3, 3, 4), [], ['Precise Kick'])

fsd['Liu Shen'] = Fighter('Liu Shen', 'Drunken Boxing', 5, (4, 4, 4, 5), [], ['Precise Kick'])

fsd['Chen Mao'] = Fighter('Chen Mao', 'Drunken Boxing', 8, (5, 5, 5, 6), [], ['Fast Punch'])

fsd['Dong Hao'] = Fighter('Dong Hao', 'Long Fist', 3, (4, 3, 4, 4), [], ['Fast Punch'])

fsd['Sun Ping'] = Fighter('Sun Ping', 'Long Fist', 12, (6, 7, 6, 6), [], ['Heavy Claw'])

fsd['Yuan Fan'] = Fighter('Yuan Fan', 'Tiger', 2, (4, 3, 3, 5), [], ['Precise Kick'])

fsd['Ho Han'] = Fighter('Ho Han', 'Tiger', 9, (5, 5, 6, 6), [], ['Long Elbow'])

fsd['Beggar Xue'] = Fighter('Beggar Xue', 'Drunken Boxing', 1, (2, 2, 2, 3), [], [])

fsd['Drunkard Tan'] = Fighter('Drunkard Tan', 'Drunken Boxing', 3, (3, 3, 4, 4), [], [])

fsd['Thief Wei'] = Thug('Thief Wei', 'Drunken Boxing', 2, (3, 4, 3, 3), [], [])

fsd['Fat Girl'] = Fighter('Fat Girl', 'Drunken Boxing', 1, (2, 2, 2, 2), [], [])

fsd['Little Gu'] = Thug('Little Gu', 'Drunken Boxing', 3, (4, 3, 3, 4), [], ['Light Claw'])


g.fighters_list = list(fsd.values())

g.masters = md = {}
md['Drunken Boxing'] = g.fighters_dict['Master Lei']
md['Long Fist'] = g.fighters_dict['Master Zhao']
md['Tiger'] = g.fighters_dict['Master Qiu']

g.schools = {}

g.schools['Drunken Boxing'] = school = []
school.append(g.fighters_dict['Wang Jing'])
school.append(g.fighters_dict['Liu Shen'])
school.append(g.fighters_dict['Chen Mao'])
school.append(g.fighters_dict['Test Hero'])

g.schools['Long Fist'] = school = []
school.append(g.fighters_dict['Dong Hao'])
school.append(g.fighters_dict['Sun Ping'])

g.schools['Tiger'] = school = []
school.append(g.fighters_dict['Yuan Fan'])
school.append(g.fighters_dict['Ho Han'])

g.beggar = g.fighters_dict['Beggar Xue']
g.drunkard = g.fighters_dict['Drunkard Tan']
g.thief = g.fighters_dict['Thief Wei']
g.criminals = []
g.criminals.append(g.fighters_dict['Little Gu'])
g.fat_girl = g.fighters_dict['Fat Girl']

g.stories = {'BanditFianceStory': story.BanditFianceStory(g, state=None, player=None, boss=None), 'ForeignerStory': story.ForeignerStory(g, state=-1, player=g.fighters_dict['Test Hero'], boss=None), 'NinjaTurtlesStory': story.NinjaTurtlesStory(g, state=None, player=None, boss=None), 'RenownedMasterStory': story.RenownedMasterStory(g, state=None, player=None, boss=None), 'StolenTreasuresStory': story.StolenTreasuresStory(g, state=None, player=None, boss=None), 'StrangeDreamsStory': story.StrangeDreamsStory(g, state=None, player=None, boss=None)}

g.town_name = 'Foshan'
g.poverty = 0.1
g.crime = 0.1
g.kung_fu = 0.15
g.day = 5
g.month = 2
g.year = 1
g.auto_save_on = False
g.play_indefinitely = False
g.fights_total = 10
g.enc_count_dict = {'Beggar': 2, 'Robbers': 3}

g.players = []

g.players.append(g.fighters_dict['Test Hero'])
p = g.players[-1]
p.exp = 100
p.is_master = False
p.new_school_name = ''
p.money = 50
p.reputation = 5
p.inactive = 0
p.inact_status = ''
p.inventory = {'Tiger Herb': 1}
p.ended_turn = True
p.accompl = []
p.accompl_dates = []
p.stats_dict = {}

p.friends = [g.fighters_dict['Wang Jing'], ]

p.enemies = []

p.students = 0

p.best_student = None
"""


@pytest.fixture
def temp_save_folder(tmp_path, monkeypatch):
    """Redirect saves to a temp folder; the real save/ dir is never touched."""
    monkeypatch.setattr(save_mod, 'SAVE_FOLDER', str(tmp_path))
    monkeypatch.setattr(load_mod, 'SAVE_FOLDER', str(tmp_path))
    return tmp_path


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


def player_snapshot(g):
    return [
        (
            p.name,
            type(p).__name__,
            p.level,
            p.exp,
            p.money,
            p.style.name,
            [m.name for m in p.moves],
            sorted(t.name for t in p.techs),
            sorted(p.traits),
        )
        for p in g.players
    ]


def game_snapshot(g):
    """Everything the save format must preserve, in a comparable shape."""

    def fighter_snapshot(f):
        return (
            f.name,
            type(f).__name__,
            f.occupation,
            f.style.name,
            f.level,
            f.get_base_atts_tup(),
            sorted(t.name for t in f.techs),
            [m.name for m in f.moves if not m.is_basic],
            sorted(getattr(f, 'traits', [])),
        )

    def full_player_snapshot(p):
        return fighter_snapshot(p) + (
            p.exp,
            p.is_master,
            p.new_school_name,
            p.money,
            p.reputation,
            p.inactive,
            p.inact_status,
            p.inventory,
            p.ended_turn,
            p.accompl,
            p.accompl_dates,
            p.stats_dict,
            [f.name for f in p.friends],
            [en.name for en in p.enemies],
            p.students,
            fighter_snapshot(p.best_student) if p.best_student else None,
            p.current_story.name if p.current_story else None,
        )

    return {
        'fighters': sorted(fighter_snapshot(f) for f in g.fighters_dict.values()),
        'fighters_order': [f.name for f in g.fighters_list],
        'masters': {sn: m.name for sn, m in g.masters.items()},
        'schools': {sn: [f.name for f in school] for sn, school in g.schools.items()},
        'special_npcs': [
            None if f is None else f.name
            for f in (g.beggar, g.drunkard, g.thief, g.fat_girl)
        ],
        'criminals': [c.name for c in g.criminals],
        'stories': {
            name: (
                type(s).__name__,
                s.state,
                s.player.name if s.player else None,
                s.boss.name if s.boss else None,
            )
            for name, s in g.stories.items()
        },
        'game_atts': {att: getattr(g, att) for att in g.savable_atts},
        'players': [full_player_snapshot(p) for p in g.players],
    }


class TestSaving:
    def test_save_creates_file_in_save_folder(self, temp_save_folder):
        g = make_game()
        g.save_game(SAVE_NAME)
        assert (temp_save_folder / SAVE_NAME).is_file()

    def test_save_file_is_json(self, temp_save_folder):
        g = make_game()
        g.save_game(SAVE_NAME)
        data = json.loads((temp_save_folder / SAVE_NAME).read_text())
        assert data['format'] == 'kfw-save'
        # every fighter is serialized with class name and constructor args
        by_name = {fd['args'][0]: fd for fd in data['fighters']}
        for p in g.players:
            assert by_name[p.name]['class'] == 'SmartAIP'
        # game attributes are serialized under game_atts
        assert data['game_atts']['day'] == g.day
        assert data['game_atts']['enc_count_dict'] == g.enc_count_dict
        # fighter references elsewhere are by name
        for sn, m in g.masters.items():
            assert data['masters'][sn] == m.name

    def test_save_dumps_player_logs_aside(self, temp_save_folder):
        g = make_game()
        for p in g.players:
            p.log('some log entry')
        g.save_game(SAVE_NAME)
        for p in g.players:
            log_path = temp_save_folder / f"{p.name}'s log.txt"
            assert log_path.is_file()
            assert 'some log entry' in log_path.read_text()
        # logs are flushed, not duplicated on the next save
        g.save_game(SAVE_NAME)
        for p in g.players:
            log_text = (temp_save_folder / f"{p.name}'s log.txt").read_text()
            assert log_text.count('some log entry') == 1


class TestInitStringRoundtrip:
    """get_init_string() must eval() back into an equal fighter — this is the
    legacy save-format contract (old saves break if it changes)."""

    EVAL_NS = dict(
        Fighter=Fighter,
        SmartAIP=SmartAIP,
    )

    def check_roundtrip(self, f):
        random.seed(0)
        f2 = eval(f.get_init_string(), self.EVAL_NS)
        assert f2.name == f.name
        assert f2.style.name == f.style.name
        assert f2.level == f.level
        assert f2.get_base_atts_tup() == f.get_base_atts_tup()
        assert sorted(t.name for t in f2.techs) == sorted(t.name for t in f.techs)
        assert [m.name for m in f2.moves] == [m.name for m in f.moves]

    def test_plain_fighter(self):
        random.seed(0)
        self.check_roundtrip(fighter_factory.new_fighter(10))

    def test_named_npc_occupations(self):
        random.seed(0)
        for f, occupation in (
            (fighter_factory.new_thug(), 'thug'),
            (fighter_factory.new_master('Test Master', 'Long Fist'), 'master'),
            (fighter_factory.new_convict(), 'thug'),
        ):
            assert type(f) is Fighter
            assert f.occupation == occupation
            self.check_roundtrip(f)

    def test_player(self):
        random.seed(0)
        p = SmartAIP(name='Test Player', style='Drunken Boxing')
        self.check_roundtrip(p)
        p2 = eval(p.get_init_string(), self.EVAL_NS)
        assert sorted(p2.traits) == sorted(p.traits)

    def test_story_init_string(self):
        g = make_game()
        s = next(iter(g.stories.values()))
        s2 = eval(s.get_init_string(), {'story': story, 'g': g})
        assert type(s2) is type(s)
        assert s2.state == s.state
        assert s2.player is None and s2.boss is None


class TestLoading:
    def test_load_roundtrip_preserves_state(self, temp_save_folder):
        g = make_game()
        for p in g.players:
            p.gain_exp(50, silent=True)
            p.earn_money(100)
        g.save_game(SAVE_NAME)
        snapshot = player_snapshot(g)
        date = (g.year, g.month, g.day)

        g2 = game.Game()
        g2.load_game(SAVE_NAME)
        assert player_snapshot(g2) == snapshot
        assert (g2.year, g2.month, g2.day) == date
        assert len(g2.fighters_dict) == len(g.fighters_dict)
        assert set(g2.stories) == set(g.stories)
        assert set(g2.masters) == set(g.masters)
        assert set(g2.schools) == set(g.schools)

    def test_load_roundtrip_preserves_full_state(self, temp_save_folder):
        g = make_game()
        p = g.players[0]
        p.gain_exp(50, silent=True)
        p.earn_money(100)
        p.inventory['Tiger Herb'] = 2
        p.accompl.append('Test Accompl')
        p.accompl_dates.append('1/1/1')
        # stats_dict values that are tuples must come back as tuples
        p.stats_dict['aston_victory'] = ('1/1/1', 2, ['Somebody, lv.1 X'], 1.5)
        # social links and a story in progress (player/boss refs are by name)
        friend = g.schools[p.style.name][0]
        assert friend is not p
        p.friends.append(friend)
        p.enemies.append(g.criminals[0])
        p.best_student = fighter_factory.new_student('Test Stud', p.style.name)
        s = g.stories['ForeignerStory']
        s.player = p
        s.state = 2
        s.boss = fighter_factory.new_fighter(10)
        s.boss.name = 'Test Boss'
        p.current_story = s
        g.fights_total = 42
        g.enc_count_dict['Beggar'] = 7
        g.save_game(SAVE_NAME)
        snapshot = game_snapshot(g)

        g2 = game.Game()
        g2.load_game(SAVE_NAME)
        assert game_snapshot(g2) == snapshot
        # references are re-linked to the loaded fighter objects, by identity
        p2 = g2.players[0]
        assert g2.stories['ForeignerStory'].player is p2
        assert g2.stories['ForeignerStory'].boss is g2.fighters_dict['Test Boss']
        assert p2.current_story is g2.stories['ForeignerStory']
        assert p2.friends[0] is g2.fighters_dict[friend.name]
        assert p2.enemies[0] is g2.criminals[0]

    def test_loaded_game_continues_playing(self, temp_save_folder):
        g = make_game()
        g.save_game(SAVE_NAME)
        g2 = game.Game()
        g2.load_game(SAVE_NAME)
        # the loaded game must be able to run to a victory without a TTY
        g2.silent_ending = True  # not serialized in the save format
        g2.play()
        assert any(p.level > 1 for p in g2.players)

    def test_loading_clears_player_logs(self, temp_save_folder):
        g = make_game()
        for p in g.players:
            p.log('some log entry')
        g.save_game(SAVE_NAME)
        g2 = game.Game()
        g2.load_game(SAVE_NAME)
        for p in g2.players:
            assert p.plog == []

    def test_move_usage_roundtrip(self, temp_save_folder):
        g = make_game()
        p = g.players[0]
        p.move_usage['Punch'] = 7
        p.stats_dict['strikes_thrown'] = 10
        g.save_game(SAVE_NAME)
        g2 = game.Game()
        g2.load_game(SAVE_NAME)
        p2 = g2.players[0]
        assert p2.move_usage == {'Punch': 7}
        assert p2.get_stat('strikes_thrown') == 10
        # stats added after the save format was written get back-filled
        assert p2.get_stat('dam_dealt') == 0

    def test_old_saves_without_move_usage_load(self, temp_save_folder):
        # players in old saves lack move_usage; the __init__ default must survive
        g = make_game()
        g.save_game(SAVE_NAME)
        data = json.loads((temp_save_folder / SAVE_NAME).read_text())
        for pdata in data['players']:
            del pdata['atts']['move_usage']
            del pdata['atts']['stats_dict']['strikes_thrown']
        (temp_save_folder / SAVE_NAME).write_text(json.dumps(data))
        g2 = game.Game()
        g2.load_game(SAVE_NAME)
        p2 = g2.players[0]
        assert p2.move_usage == {}
        assert p2.get_stat('strikes_thrown') == 0

    def test_occupation_json_roundtrip_is_stable(self, temp_save_folder):
        g = make_game()
        occupations = {f.name: f.occupation for f in g.fighters_dict.values()}
        assert {'master', 'thug'} <= set(occupations.values())
        g.save_game(SAVE_NAME)
        data1 = json.loads((temp_save_folder / SAVE_NAME).read_text())
        # non-default occupations are serialized alongside the constructor args
        by_name = {fd['args'][0]: fd for fd in data1['fighters']}
        for name, occ in occupations.items():
            if occ == 'fighter':
                assert 'occupation' not in by_name[name]
            else:
                assert by_name[name]['occupation'] == occ

        g2 = game.Game()
        g2.load_game(SAVE_NAME)
        assert {f.name: f.occupation for f in g2.fighters_dict.values()} == occupations
        # re-saving a loaded game produces the same fighter payload
        # (fighter ordering in the roster is not preserved, so compare by name)
        g2.save_game(SAVE_NAME)
        data2 = json.loads((temp_save_folder / SAVE_NAME).read_text())
        for data in (data1, data2):
            for fd in data['fighters']:
                fd['args'][4] = sorted(fd['args'][4])  # techs come from a set
            data['fighters'].sort(key=lambda fd: fd['args'][0])
        assert data2['fighters'] == data1['fighters']


class TestOccupationQuotes:
    """Occupation drives quote pool selection (replacing the old subclasses)."""

    def make_fight(self, shown):
        return SimpleNamespace(show=shown.append)

    def test_thug_gets_thug_quotes(self):
        from kf_lib.actors import quotes

        f = fighter_factory.new_thug()
        assert f.occupation == 'thug'
        assert f.quotes == 'thug'
        shown = []
        f.current_fight = self.make_fight(shown)
        assert f.say_prefight_quote() is True
        assert shown[0].split('"')[1] in quotes.PREFIGHT_QUOTES['thug']
        shown.clear()
        f.say_win_quote()
        assert shown[0].split('"')[1] in quotes.WIN_QUOTES['thug']

    def test_master_and_plain_fighter_quotes(self):
        from kf_lib.actors import quotes

        m = fighter_factory.new_master('Test Master', 'Long Fist')
        assert m.quotes == 'master'
        shown = []
        m.current_fight = self.make_fight(shown)
        assert m.say_prefight_quote() is True
        assert shown[0].split('"')[1] in quotes.PREFIGHT_QUOTES['master']
        f = fighter_factory.new_fighter(5)
        assert f.occupation == 'fighter'
        assert f.quotes == 'fighter'
        # no quote pool for plain fighters: no output, no pause
        shown.clear()
        f.current_fight = self.make_fight(shown)
        assert f.say_prefight_quote() is False
        assert shown == []


class TestLegacyLoading:
    """Saves in the old exec-based format must still load."""

    def test_legacy_save_still_loads(self, temp_save_folder):
        (temp_save_folder / SAVE_NAME).write_text(LEGACY_SAVE)
        g = game.Game()
        g.load_game(SAVE_NAME)
        (p,) = g.players
        assert type(p).__name__ == 'SmartAIP'
        assert (p.name, p.level, p.exp, p.money) == ('Test Hero', 5, 100, 50)
        assert p.style.name == 'Drunken Boxing'
        assert sorted(p.traits) == ['brave', 'unfriendly']
        assert p.inventory == {'Tiger Herb': 1}
        assert set(g.masters) == {'Drunken Boxing', 'Long Fist', 'Tiger'}
        # the legacy Master/Thug classes load as plain Fighters with occupation set
        assert type(g.masters['Long Fist']) is Fighter
        assert g.masters['Long Fist'].occupation == 'master'
        assert g.masters['Long Fist'].quotes == 'master'
        assert [f.name for f in g.schools['Drunken Boxing']] == [
            'Wang Jing',
            'Liu Shen',
            'Chen Mao',
            'Test Hero',
        ]
        assert g.beggar.name == 'Beggar Xue'
        assert type(g.thief) is Fighter
        assert g.thief.occupation == 'thug'
        assert g.fighters_dict['Little Gu'].occupation == 'thug'
        assert g.fighters_dict['Wang Jing'].occupation == 'fighter'
        assert p.occupation == 'hero'
        assert [c.name for c in g.criminals] == ['Little Gu']
        assert set(g.stories) == {
            'BanditFianceStory',
            'ForeignerStory',
            'NinjaTurtlesStory',
            'RenownedMasterStory',
            'StolenTreasuresStory',
            'StrangeDreamsStory',
        }
        s = g.stories['ForeignerStory']
        assert s.state == -1 and s.player is p and s.boss is None
        assert (g.day, g.month, g.year) == (5, 2, 1)
        assert g.fights_total == 10
        assert g.enc_count_dict == {'Beggar': 2, 'Robbers': 3}
        # stats missing from the save are filled with defaults
        assert p.stats_dict['fights_won'] == 0
        # friend references are re-linked to the loaded fighters
        assert p.friends == [g.fighters_dict['Wang Jing']]

    def test_legacy_loaded_game_continues_playing(self, temp_save_folder):
        (temp_save_folder / SAVE_NAME).write_text(LEGACY_SAVE)
        g = game.Game()
        g.load_game(SAVE_NAME)
        # the loaded legacy game must be able to run without a TTY
        g.silent_ending = True
        g.play()
        assert g.players[0].level > 5
