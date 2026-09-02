"""Integration test: a full AI-only game must run to completion."""
import random

from kf_lib import game


def test_full_autoplay_game_completes():
    random.seed(0)
    g = game.Game()
    g.new_game(
        num_players=4,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=True,
        silent_ending=True,
    )
    g.play()
    # reaching this line without an exception means the game ran to a victory;
    # sanity-check that the game actually progressed
    assert g.day > 0
    assert any(p.level > 1 for p in g.players)
