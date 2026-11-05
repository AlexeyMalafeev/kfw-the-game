import builtins
import io
import random
from contextlib import redirect_stdout

import pytest

from kf_lib.actors import fighter_factory
from kf_lib.actors.fighter import Fighter
from kf_lib.kung_fu import moves, style_gen, techniques
from kf_lib.minigames import MINIGAMES
from kf_lib.actors.human_controlled_fighter import HumanControlledFighter
from kf_lib.actors.punching_bag import BAG_HP, PunchingBag
from kf_lib.fighting.fight import TimedBagRound
from kf_lib.minigames import _chocolate as chocolate
from kf_lib.minigames import _punching_bag as punching_bag
from kf_lib.minigames import _records
from kf_lib.minigames import _ring as ring
from kf_lib.kung_fu import styles
from kf_lib.ui import MUSIC, _frontend


@pytest.fixture(autouse=True)
def records_in_tmp(tmp_path, monkeypatch):
    """Mini-game records go to a temporary folder, not the real save/."""
    monkeypatch.setattr(_records, 'SAVE_FOLDER', str(tmp_path))
    return tmp_path


def test_minigames_registry():
    assert set(MINIGAMES) == {'chocolate', 'ring', 'bag'}


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


def test_ring_opponents_match_a_high_level_player():
    """The old fixed level-20 cap on opponents made this search loop forever
    once the player passed level ~40."""
    random.seed(1)
    p = Fighter('P', style_gen.get_new_randomly_generated_style(), 1)
    p.level_up(44)
    x = p.get_exp_worth() * 1.2
    opp = fighter_factory.from_exp_worth(x, max_lv=p.level + ring.OPP_LV_MARGIN)
    worth = sum(f.get_exp_worth() for f in opp)
    assert x <= worth < x + round(x / 10) + 1


def test_from_exp_worth_settles_for_the_closest_group():
    random.seed(0)
    opp = fighter_factory.from_exp_worth(10_000, max_lv=3, max_tries=20)
    assert 1 <= len(opp) <= 5
    assert all(f.level <= 3 for f in opp)


def test_ring_styles_are_generated_and_can_be_rerolled(monkeypatch):
    random.seed(5)
    shown = []

    def present(keys, options, weak=False):
        shown.append(options)

    keys = iter('a1')  # 'a' is the 11th option: other styles; then the first
    _frontend.install_frontend(
        key_reader=lambda: next(keys), clear_handler=lambda: None, menu_handler=present
    )
    try:
        with redirect_stdout(io.StringIO()):
            style = fighter_factory.choose_generated_style()
    finally:
        _frontend.uninstall_frontend()
    assert len(shown) == 2 and len(shown[0]) == 11
    assert style not in styles.default_styles
    assert style.display_public_name in shown[1][0]
    assert shown[0][0] != shown[1][0]


def test_ring_plays_through_headless(monkeypatch):
    """Extreme difficulty, auto fights, first option everywhere, until the
    three attempts are spent."""
    random.seed(3)
    answers = iter(['', 'Tester', '3'])  # an empty name is asked again
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(answers))
    monkeypatch.setattr(ring, 'menu', lambda *a, **kw: 'extreme')  # difficulty
    tunes, effects = [], []
    _frontend.install_frontend(
        key_reader=lambda: '1',
        clear_handler=lambda: None,
        music_player=tunes.append,
        sound_player=effects.append,
    )
    try:
        with redirect_stdout(io.StringIO()) as out:
            ring.play_ring()
    finally:
        _frontend.uninstall_frontend()
    text = out.getvalue()
    assert text.count('Remaining attempts') == ring.ATTEMPTS
    assert 'Game over' in text
    assert tunes[0] == MUSIC['new_game']
    assert 'level_up' in effects  # reaching the chosen starting level


def test_ring_records_keep_the_best_run():
    random.seed(0)
    p = Fighter('Tester', style_gen.get_new_randomly_generated_style(), 1)
    p.level_up(3)
    with redirect_stdout(io.StringIO()) as out:
        ring.update_record('hard', p, 1, 2)
        ring.update_record('hard', p, 1, 1)  # worse: the record stays
        ring.update_record('normal', p, 1, 0)  # no fight won: no record
    assert out.getvalue().count('New record') == 1
    records = _records.get_records('ring')
    assert set(records) == {'hard'}
    assert records['hard']['wins'] == 2
    assert (records['hard']['start_level'], records['hard']['level']) == (1, 4)
    with redirect_stdout(io.StringIO()) as out:
        ring.show_records()
    assert '2 fights won (Tester, ' in out.getvalue()
    assert 'lv.1 to lv.4' in out.getvalue()


def test_damaged_records_file_counts_as_no_records(records_in_tmp):
    (records_in_tmp / _records.FILE_NAME).write_text('{not json', encoding='utf-8')
    assert _records.get_records('ring') == {}
    _records.save_record('ring', 'easy', {'wins': 'many'})
    assert _records.get_score(_records.get_records('ring')['easy'], 'wins') == 0


@pytest.fixture
def first_option_everywhere():
    _frontend.install_frontend(key_reader=lambda: '1', clear_handler=lambda: None)
    yield
    _frontend.uninstall_frontend()


def test_bag_round_is_one_minute_of_free_hits(first_option_everywhere):
    random.seed(2)
    with redirect_stdout(io.StringIO()) as out:
        f = HumanControlledFighter('Tester', style_gen.get_new_randomly_generated_style())
        f.level_up(punching_bag.FIGHTER_LEVEL - 1)
        bag = PunchingBag()
        rnd = TimedBagRound(f, bag)
    text = out.getvalue()
    assert rnd.timer == rnd.time_limit == 60 * 2  # TIME_TO_SEC_DIVISOR per second
    # every move started before the bell
    assert rnd.timeline and all(line.startswith('0:') for line in rnd.timeline)
    assert rnd.damage == BAG_HP - bag.hp > 0
    fs = f.fight_stats
    assert fs['landed'] == fs['thrown'] > 0  # the bag never dodges or blocks
    assert not bag.status  # never falls, never stunned
    assert 'Punching Bag:' not in text  # the bag never takes a turn
    assert 'BLEEDING' not in text and 'gasps' not in text
    assert 'time left: 1:00' in text and 'Time!' in text


def test_bag_keeps_the_best_round(first_option_everywhere, monkeypatch):
    random.seed(4)
    answers = iter(['Tester'])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(answers))
    more = iter([True, False])  # two rounds
    monkeypatch.setattr(punching_bag, 'yn', lambda *a: next(more))
    damages = []
    play_round = punching_bag.play_round
    monkeypatch.setattr(
        punching_bag, 'play_round', lambda f: damages.append(play_round(f)) or damages[-1]
    )
    with redirect_stdout(io.StringIO()) as out:
        punching_bag.play_punching_bag()
    assert len(damages) == 2
    record = _records.get_records('bag')['best']
    assert record['damage'] == max(damages) and record['name'] == 'Tester'
    assert out.getvalue().count('New record!') == (2 if damages[1] > damages[0] else 1)
