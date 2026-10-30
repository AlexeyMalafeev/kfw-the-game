import io
import random
from contextlib import redirect_stdout

from kf_lib.actors.fighter import Fighter
from kf_lib.kung_fu import moves, techniques
from kf_lib.minigames import MINIGAMES
from kf_lib.minigames import _chocolate as chocolate


def test_minigames_registry():
    assert set(MINIGAMES) == {'chocolate', 'ring'}


def test_chocolate_scene_content_resolves():
    scenes = chocolate.get_scenes()
    assert len(scenes) == 7
    for sc in scenes:
        for m in sc.moves:
            moves.get_move_obj(m)  # raises if the move is gone from all_moves.txt
        for t in sc.techs:
            assert isinstance(t, techniques.Tech)
        for make_opponents, _ in sc.fights:
            opps = make_opponents()
            assert opps and all(isinstance(f, Fighter) for f in opps)


def test_chocolate_techs_stay_out_of_main_game_pools():
    pools = techniques.get_upgradable_techs() + techniques.get_upgraded_techs()
    assert chocolate.MIGHTY_ELBOWS not in pools
    assert chocolate.MIGHTY_KNEES not in pools


def test_zen_starts_bare_and_does_not_level():
    zen = chocolate.new_zen()
    assert zen.level == chocolate.ZEN_LEVEL
    assert not zen.techs
    assert all(m.is_basic for m in zen.moves)


def test_chocolate_plays_through_headless(monkeypatch):
    """All seven scenes, auto-fought, with every key prompt skipped."""
    random.seed(0)
    zen = chocolate.new_zen()
    zen.auto_fight_all = True  # no prefight screen / 'Auto fight?' prompt
    for name in ('pak', 'cls'):
        monkeypatch.setattr(zen, name, lambda: None)
    monkeypatch.setattr(zen, 'show', lambda *a, **kw: None)
    with redirect_stdout(io.StringIO()):
        for sc in chocolate.get_scenes():
            chocolate.play_scene(zen, sc)
    assert zen.weapon is None
    assert chocolate.MIGHTY_KNEES in zen.techs
