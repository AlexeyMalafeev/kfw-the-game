"""Integration test: a full AI-only game must run to completion."""
import random

from kf_lib import game
from kf_lib.kung_fu import styles as styles_mod

# styles.default_styles is mutated by Game when a generated-styles game starts
# (in-code todo in _new_game.py), so snapshot it at import time, before any
# test in the suite has run a game
PRISTINE_DEFAULT_STYLES = list(styles_mod.default_styles)


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


def test_default_styles_new_game_boots():
    # regression: 'Eagle Claw III' passed a nonexistent `critical_mult`
    # attribute, crashing _init_schools (masters are lv 11-14 and learn it at
    # creation) for every default-styles new game
    styles_mod.default_styles = list(PRISTINE_DEFAULT_STYLES)  # unpollute
    random.seed(0)
    g = game.Game()
    g.new_game(
        num_players=2,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=False,
        silent_ending=True,
    )
    assert g.players and g.masters
    eagle_masters = [m for m in g.fighters_dict.values() if m.style.name == 'Eagle Claw']
    assert any('Eagle Claw III' in [t.name for t in m.techs] for m in eagle_masters)
