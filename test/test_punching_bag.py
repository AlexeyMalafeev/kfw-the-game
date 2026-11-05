"""The punching bag in the main game: State > Moves > Punching Bag."""
import io
import random
from contextlib import redirect_stdout
from types import SimpleNamespace

import pytest

import kf_lib.game  # noqa: F401 -- first: kf_lib.actors.player can't load on its own
from kf_lib.actors.player import HumanPlayer
from kf_lib.actors.punching_bag import ART_HIT, ART_STILL, PunchingBag
from kf_lib.fighting.fight import BagPractice
from kf_lib.game._state_menu import StateMenu
from kf_lib.kung_fu import ascii_art, style_gen
from kf_lib.ui import _frontend, strip_tags


class MenuReader:
    """Answers each presented menu by its labels; a pak gets a space and a weak
    menu (the post-fight menu) is dismissed."""

    def __init__(self, answer):
        self.answer = answer  # labels -> label to choose, or None for the first
        self.pending = None

    def present(self, keys, options, weak=False):
        self.pending = (keys, [strip_tags(str(o)) for o in options], weak)

    def read(self):
        if self.pending is None:
            return ' '
        keys, labels, weak = self.pending
        self.pending = None
        if weak:
            return '\x1b'
        label = self.answer(labels)
        return keys[labels.index(label)] if label else keys[0]


@pytest.fixture
def player():
    random.seed(1)
    _frontend.install_frontend(key_reader=lambda: '1', clear_handler=lambda: None)
    try:
        with redirect_stdout(io.StringIO()):
            p = HumanPlayer('Tester', style_gen.get_new_randomly_generated_style(), 6)
    finally:
        _frontend.uninstall_frontend()
    p.game = SimpleNamespace(fights_total=0, get_date=lambda: '1/1/1')
    return p


def test_bag_art_hangs_still_and_swings_when_hit():
    bag = PunchingBag()
    bag.set_ascii('Stance')
    assert bag.ascii_r == ascii_art.get_ascii(ART_STILL)[1]
    bag.set_ascii('Hit')
    assert bag.ascii_r == ascii_art.get_ascii(ART_HIT)[1]
    for art in (ART_STILL, ART_HIT):
        lines = ascii_art.get_ascii(art)[1].split('\n')
        assert len(lines) == 6  # as tall as the fighter pictures it stands next to


def test_state_menu_practice_costs_nothing(player, monkeypatch):
    monkeypatch.setattr(player, 'get_p_info_verbose', lambda: 'info')
    exp, fights, usage = player.exp, player.get_stat('num_fights'), dict(player.move_usage)
    done = []

    def answer(labels):
        if 'Moves' in labels:  # the State menu: practice once, then leave
            return 'Back' if done else 'Moves'
        if labels == ['Punching Bag', 'Back']:
            done.append(True)
            return 'Punching Bag'
        if '20 moves' in labels:
            return '20 moves'
        return None

    reader = MenuReader(answer)
    _frontend.install_frontend(
        key_reader=reader.read, clear_handler=lambda: None, menu_handler=reader.present
    )
    game = StateMenu.__new__(StateMenu)
    game.current_player = player
    game.play_indefinitely = False
    try:
        with redirect_stdout(io.StringIO()) as out:
            game.state_menu()
    finally:
        _frontend.uninstall_frontend()
    session = player.current_fight
    assert isinstance(session, BagPractice)
    assert session.moves_made == 20
    assert session.damage > 0
    assert 'moves left: 20' in out.getvalue() and 'Practice over!' in out.getvalue()
    # no exp, no stats, no move usage, no fight counted
    assert player.exp == exp
    assert player.get_stat('num_fights') == fights
    assert player.move_usage == usage
    assert player.game.fights_total == 0
