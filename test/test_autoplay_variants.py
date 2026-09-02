"""Slower integration variants: bigger AI-only games run to completion."""
import random

import pytest

from kf_lib import game


@pytest.mark.slow
def test_full_autoplay_game_six_players_completes():
    random.seed(42)
    g = game.Game()
    g.new_game(
        num_players=6,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=True,
        silent_ending=True,
    )
    g.play()
    assert g.day > 0
    assert g.n_days_to_win is not None
    assert any(p.level > 1 for p in g.players)


@pytest.mark.slow
def test_full_autoplay_game_baseline_ai_completes():
    # BaselineAIP picks random day actions, exercising more encounter branches
    from kf_lib.actors.player import BaselineAIP

    random.seed(7)
    g = game.Game()
    g.new_game(
        num_players=3,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=True,
        silent_ending=True,
        forced_aip_class=BaselineAIP,
    )
    g.play()
    assert g.n_days_to_win is not None
