_key_reader = None
_clear_handler = None
_menu_handler = None
_wraps_lines = False


def install_frontend(
    key_reader=None, clear_handler=None, menu_handler=None, wraps_lines=False
):
    """wraps_lines: the frontend word-wraps long lines to its own width, so the
    game should not hard-wrap paragraphs at a fixed column."""
    global _key_reader, _clear_handler, _menu_handler, _wraps_lines
    _key_reader = key_reader
    _clear_handler = clear_handler
    _menu_handler = menu_handler
    _wraps_lines = wraps_lines


def uninstall_frontend():
    global _key_reader, _clear_handler, _menu_handler, _wraps_lines
    _key_reader = None
    _clear_handler = None
    _menu_handler = None
    _wraps_lines = False


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
