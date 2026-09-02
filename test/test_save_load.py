"""Save system characterization tests.

The save format is executable Python (see kf_lib/game/_save_game.py); loading
exec()s the file line by line (kf_lib/game/_load_game.py). These tests keep the
user's real save/ folder untouched by monkeypatching SAVE_FOLDER in both
modules to a pytest tmp_path.
"""
import random
from pathlib import Path

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
import kf_lib.game._save_game as save_mod
import kf_lib.game._load_game as load_mod
from kf_lib.actors import fighter_factory
from kf_lib.actors.fighter import Challenger, Fighter, Master, Thug
from kf_lib.actors.player import SmartAIP
from kf_lib.happenings import story

SAVE_NAME = 'pytest save.txt'


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


class TestSaving:
    def test_save_creates_file_in_save_folder(self, temp_save_folder):
        g = make_game()
        g.save_game(SAVE_NAME)
        assert (temp_save_folder / SAVE_NAME).is_file()

    def test_save_file_is_python_referencing_fighters(self, temp_save_folder):
        g = make_game()
        g.save_game(SAVE_NAME)
        text = (temp_save_folder / SAVE_NAME).read_text()
        assert 'g.fighters_dict = fsd = {}' in text
        for p in g.players:
            assert repr(p.name) in text
        assert 'g.players.append(' in text
        # game attributes are serialized as plain assignments
        assert f'g.day = {g.day}' in text

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
    actual save-format contract (old saves break if it changes)."""

    EVAL_NS = dict(
        Challenger=Challenger,
        Fighter=Fighter,
        Master=Master,
        Thug=Thug,
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

    def test_named_npc_classes(self):
        random.seed(0)
        for f in (
            fighter_factory.new_thug(),
            fighter_factory.new_master('Test Master', 'Long Fist'),
            fighter_factory.new_convict(),
        ):
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
    def test_load_game_raises_name_error(self, temp_save_folder):
        # BUG?: game loading is broken on Python 3.13 (and any CPython 3.x):
        # _load_game.load_game() exec()s the save file line by line inside a
        # method, but names assigned by one exec'd line (e.g. `fsd` in
        # `g.fighters_dict = fsd = {}`) do not persist into the local namespace
        # seen by the next exec() call, so loading ANY save fails with
        # NameError on the first fighter line. This test pins the broken
        # behavior; delete/rewrite it when load_game is fixed.
        g = make_game()
        g.save_game(SAVE_NAME)
        g2 = make_game(seed=99)  # any Game instance
        with pytest.raises(NameError):
            g2.load_game(SAVE_NAME)
