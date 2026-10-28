"""Music and sound effects (see docs/audio.md).

The game names a tune or an effect; an installed frontend plays the file
(only Android installs one, see _frontend.py). Without one every call here is
a no-op, so the desktop game stays silent. Tune and effect names are the file
stems that dev_scripts/audio/render.py --game writes to audio/.
"""
from contextlib import contextmanager

from ._frontend import (
    frontend_has_sound,
    frontend_music_now,
    frontend_play_music,
    frontend_play_sound,
)

__all__ = [
    'MUSIC',
    'STREET_FIGHT_TUNES',
    'TOWN_TUNES',
    'fight_music',
    'fight_music_override',
    'music',
    'next_street_fight_tune',
    'play_music',
    'play_sound',
    'town_tune',
]

# where each tune plays: dev_scripts/audio/playlist.md
TOWN_TUNES = ('03_morning_market', '04_teahouse_afternoon', '05_lanterns_at_dusk')
STREET_FIGHT_TUNES = ('08_fists_like_rain', '09_alley_cats', '10_thugs_at_the_bridge')
MUSIC = {
    'title': '01_path_of_the_fist',  # played by the Android title screen itself
    'new_game': '02_choosing_a_style',
    'practice': '06_bamboo_courtyard',
    'teaching': '07_words_of_the_master',
    'outnumbered': '11_outnumbered',
    'free_for_all': '12_every_fist_for_itself',
    'tournament': '13_tournament_day',
    'tournament_final': '14_the_final_platform',
    'boss': '15_shadow_of_the_boss',
    'story': '16_strange_dreams',
    'seedy': '17_dice_in_the_back_room',
    'crime': '18_footsteps_behind_you',
    'romance': '19_plum_blossom',
    'injured': '20_healing_herbs',
    'own_school': '21_master_of_the_house',
    'game_won': '22_a_legend_is_born',
}

_fight_override = None  # tune for fights inside a `fight_music` block
_street_fights = 0


def play_sound(effect):
    frontend_play_sound(effect)


def play_music(tune):
    """Switch to `tune` (None stops the music). The same tune keeps playing."""
    frontend_play_music(tune)


@contextmanager
def music(tune, enabled=True):
    """Play `tune` inside the block, then go back to the previous tune.

    enabled=False makes the block do nothing, for scenes nobody watches
    (AI players' turns).
    """
    if not enabled or not frontend_has_sound():
        yield
        return
    previous = frontend_music_now()
    play_music(tune)
    try:
        yield
    finally:
        play_music(previous)


@contextmanager
def fight_music(tune):
    """Fights watched inside the block play `tune` (tournaments)."""
    global _fight_override
    previous = _fight_override
    _fight_override = tune
    try:
        yield
    finally:
        _fight_override = previous


def fight_music_override():
    return _fight_override


def next_street_fight_tune():
    """Street fights take turns through their pool, starting with the first."""
    global _street_fights
    tune = STREET_FIGHT_TUNES[_street_fights % len(STREET_FIGHT_TUNES)]
    _street_fights += 1
    return tune


def town_tune(day_number):
    """Day 1 plays the first town tune, day 2 the second, and so on."""
    return TOWN_TUNES[(day_number - 1) % len(TOWN_TUNES)]
