"""Music and sound effect hooks (kf_lib/ui/_sound.py, docs/audio.md)."""
import random
from pathlib import Path

import pytest

from kf_lib.actors.fighter_factory import new_fighter
from kf_lib.fighting.fight import AutoFight
from kf_lib.fighting.fight._normal_fight import NormalFight
from kf_lib.ui import _frontend
from kf_lib.ui import (
    MUSIC,
    STREET_FIGHT_TUNES,
    TOWN_TUNES,
    fight_music,
    fight_music_override,
    fight_start_sound,
    music,
    play_music,
)

AUDIO = Path('audio')


@pytest.fixture
def heard():
    """Install a recording frontend; yields (tunes, effects) lists."""
    tunes, effects = [], []
    _frontend.install_frontend(music_player=tunes.append, sound_player=effects.append)
    yield tunes, effects
    _frontend.uninstall_frontend()


def test_every_tune_has_intro_and_loop_files():
    for tune in set(MUSIC.values()) | set(TOWN_TUNES) | set(STREET_FIGHT_TUNES):
        assert (AUDIO / 'music' / f'{tune}_intro.ogg').is_file(), tune
        assert (AUDIO / 'music' / f'{tune}_loop.ogg').is_file(), tune


def test_silent_without_frontend():
    with music('03_morning_market'):
        play_music('08_fists_like_rain')
    assert _frontend.frontend_music_now() is None


def test_music_block_restores_previous_tune(heard):
    tunes, _effects = heard
    play_music('03_morning_market')
    play_music('03_morning_market')  # the same tune keeps playing
    with music('18_footsteps_behind_you'):
        with music('18_footsteps_behind_you'):
            pass
        with music('19_plum_blossom', enabled=False):
            pass
    assert tunes == ['03_morning_market', '18_footsteps_behind_you', '03_morning_market']


def test_fight_music_override_nests():
    with fight_music('13_tournament_day', start_sound='gong_clash'):
        with fight_music('14_the_final_platform'):
            assert fight_music_override() == '14_the_final_platform'
            assert fight_start_sound() == 'gong_clash'  # kept by the inner block
        assert fight_music_override() == '13_tournament_day'
    assert fight_music_override() is None
    assert fight_start_sound() == 'fight_start'


def test_tournament_fight_opens_with_gong_clash(heard):
    _tunes, effects = heard
    random.seed(3)
    with fight_music('13_tournament_day', start_sound='gong_clash'):
        NormalFight([new_fighter(5)], [new_fighter(5)])
    assert effects[0] == 'gong_clash'
    assert 'fight_start' not in effects


def test_bleeding_sounds_once_per_wound(heard):
    _tunes, effects = heard
    for seed in range(40):
        effects.clear()
        random.seed(seed)
        f = NormalFight([new_fighter(8)], [new_fighter(8)])
        wounds = sum('BLEEDING' in line for line in f.timeline)
        assert effects.count('bleeding') == wounds


def test_shown_fight_plays_existing_effects(heard):
    _tunes, effects = heard
    random.seed(3)
    NormalFight([new_fighter(5)], [new_fighter(5)])
    assert effects[0] == 'fight_start'
    assert {'hit', 'ko'} <= set(effects) or 'resist_ko' in effects
    missing = {e for e in effects if not (AUDIO / 'sfx' / f'{e}.ogg').is_file()}
    assert not missing


def test_headless_fight_is_silent(heard):
    tunes, effects = heard
    random.seed(3)
    AutoFight([new_fighter(5)], [new_fighter(5)])
    assert tunes == [] and effects == []


def test_sound_hooks_leave_fights_unchanged(heard):
    """The hooks draw no random numbers: a seeded fight ends the same."""
    def outcome(cls):
        random.seed(11)
        f = cls([new_fighter(6)], [new_fighter(6)])
        return [(x.name, x.hp) for x in f.all_fighters], f.timer

    with_sound = outcome(NormalFight)
    _frontend.uninstall_frontend()
    assert outcome(NormalFight) == with_sound == outcome(AutoFight)
