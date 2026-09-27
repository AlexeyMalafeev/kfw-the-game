"""Optional Russian localization; English is the source language and the default.

Wraps stdlib gettext with two domains:

- ``kfw``       — prose / message templates, used via ``_()`` and ``ngettext()``
- ``kfw_names`` — name catalogs (move/tech/style/item/trait names), used via
  ``tr_name()``. Internal identifiers stay English (they are dict keys and
  save-file keys); only the displayed text is translated.

With language ``'en'`` everything is a pass-through (NullTranslations), so the
English game is byte-identical. Missing catalog entries fall back to English,
so catalogs can be filled and reviewed incrementally.

Catalogs live in ``locale/<lang>/LC_MESSAGES/<domain>.mo`` (cwd-relative, like
``quotes/`` and ``moves/``); the ``.po`` sources sit next to them and are
compiled by ``dev_scripts/compile_locale.py`` (compiled .mo files are
committed, players need no gettext tooling).

Leaf package: stdlib only, no kf_lib imports.
"""

import gettext
import os
import sys

SUPPORTED_LANGUAGES = ('en', 'ru')
DEFAULT_LANGUAGE = 'en'
LOCALE_DIR = 'locale'

_language = DEFAULT_LANGUAGE
_trans = gettext.NullTranslations()
_trans_names = gettext.NullTranslations()


def get_language():
    return _language


def set_language(lang=None):
    """Select the UI language. Call early, before content modules load.

    Resolution: explicit ``lang`` argument > ``KFW_LANG`` env var > 'en'.
    Unknown languages silently fall back to 'en'.
    """
    global _language, _trans, _trans_names
    if not lang:
        lang = os.environ.get('KFW_LANG') or DEFAULT_LANGUAGE
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    _language = lang
    if lang == DEFAULT_LANGUAGE:
        _trans = gettext.NullTranslations()
        _trans_names = gettext.NullTranslations()
    else:
        _trans = gettext.translation(
            'kfw', localedir=LOCALE_DIR, languages=[lang], fallback=True
        )
        _trans_names = gettext.translation(
            'kfw_names', localedir=LOCALE_DIR, languages=[lang], fallback=True
        )
    # quotes are loaded into module-level constants at import time; if the
    # module is already imported (tests, dev scripts), reload it in the new
    # language so set_language() works at any point
    quotes_mod = sys.modules.get('kf_lib.actors.quotes')
    if quotes_mod is not None and hasattr(quotes_mod, 'reload_quotes'):
        quotes_mod.reload_quotes()


def _(message):
    """Translate a prose/message template. Interpolate AFTER translating:
    ``_('You gain {} exp').format(n)``, not ``_(f'You gain {n} exp')``."""
    return _trans.gettext(message)


def ngettext(singular, plural, n):
    """Plural-aware translation (Russian has 3 plural forms)."""
    return _trans.ngettext(singular, plural, n)


def tr_name(name):
    """Translate an internal English identifier (move/tech/style/item/trait
    name) for display. The identifier itself never changes — saves, dict
    keys and ASCII-art lookups keep using the English name."""
    return _trans_names.gettext(name)


def tr_style_name(name):
    """Translate a kung-fu style name for display. Generated 'W1 W2 W3' names
    (and their '{W2} {W3}' public forms) are reassembled from Russian word
    data with adjective-noun gender agreement; everything else goes through
    the names catalog."""
    if _language == 'ru':
        from ._ru_words import render_style_name

        rendered = render_style_name(name)
        if rendered is not None:
            return rendered
    return tr_name(name)


def tr_fighter_name(name):
    """Translate a fighter name for display: the descriptive prefix
    ('Beggar Wang' -> 'Нищий Wang') or a known group name ('Thug 1') is
    translated, proper-name parts stay as-is."""
    if _language == DEFAULT_LANGUAGE:
        return name
    translated = tr_name(name)
    if translated != name:
        return translated
    first, sep, rest = name.partition(' ')
    if sep:
        tr_first = tr_name(first)
        if tr_first != first:
            return f'{tr_first} {rest}'
    return name
