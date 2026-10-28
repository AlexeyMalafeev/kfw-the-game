_key_reader = None
_clear_handler = None
_menu_handler = None
_wraps_lines = False
_music_player = None
_sound_player = None
_music_now = None  # the tune last sent to music_player


def install_frontend(
    key_reader=None,
    clear_handler=None,
    menu_handler=None,
    wraps_lines=False,
    music_player=None,
    sound_player=None,
):
    """wraps_lines: the frontend word-wraps long lines to its own width, so the
    game should not hard-wrap paragraphs at a fixed column.
    music_player(tune or None) / sound_player(effect): play the files rendered
    by dev_scripts/audio (see ui/_sound.py and docs/audio.md)."""
    global _key_reader, _clear_handler, _menu_handler, _wraps_lines
    global _music_player, _sound_player, _music_now
    _key_reader = key_reader
    _clear_handler = clear_handler
    _menu_handler = menu_handler
    _wraps_lines = wraps_lines
    _music_player = music_player
    _sound_player = sound_player
    _music_now = None


def uninstall_frontend():
    global _key_reader, _clear_handler, _menu_handler, _wraps_lines
    global _music_player, _sound_player, _music_now
    _key_reader = None
    _clear_handler = None
    _menu_handler = None
    _wraps_lines = False
    _music_player = None
    _sound_player = None
    _music_now = None


def frontend_wraps_lines():
    return _wraps_lines


def read_key(fallback):
    if _key_reader is not None:
        return _key_reader()
    return fallback()


def clear_screen(fallback):
    if _clear_handler is not None:
        _clear_handler()
    else:
        fallback()


def present_menu(keys, options, weak=False):
    if _menu_handler is not None:
        _menu_handler(keys, options, weak)


def frontend_has_sound():
    return _music_player is not None or _sound_player is not None


def frontend_music_now():
    return _music_now


def frontend_play_music(tune):
    """Switch to `tune` (None stops the music). The same tune keeps playing."""
    global _music_now
    if _music_player is not None and tune != _music_now:
        _music_now = tune
        _music_player(tune)


def frontend_play_sound(effect):
    if _sound_player is not None:
        _sound_player(effect)
