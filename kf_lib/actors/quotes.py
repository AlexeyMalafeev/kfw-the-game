import os

from kf_lib import i18n


def load_quotes(file_name):
    """Load one quote file; in a non-English language the localized
    ``quotes/<lang>/<file_name>`` is used when it exists, else English."""
    path = os.path.join('quotes', file_name)
    lang = i18n.get_language()
    if lang != i18n.DEFAULT_LANGUAGE:
        localized = os.path.join('quotes', lang, file_name)
        if os.path.exists(localized):
            path = localized
    with open(path, encoding='utf-8') as f:
        quotes = f.read().split('\n')
    return quotes


MISC = ''


def reload_quotes():
    """(Re)load all quote pools in the current language. Runs at import time
    and again from i18n.set_language() if the language changes later."""
    global CHALLENGER_PREFIGHT, CHALLENGER_WIN, HERO_PREFIGHT, HERO_WIN
    global THUG_PREFIGHT, THUG_WIN, WISDOM, MASTER_CRITICISM, TRAINING_INJURY
    global PREFIGHT_QUOTES, WIN_QUOTES
    CHALLENGER_PREFIGHT = load_quotes('challenger_prefight.txt')
    CHALLENGER_WIN = load_quotes('challenger_win.txt')
    HERO_PREFIGHT = load_quotes('hero_prefight.txt')
    HERO_WIN = load_quotes('hero_win.txt')
    THUG_PREFIGHT = load_quotes('thug_prefight.txt')
    THUG_WIN = load_quotes('thug_win.txt')
    WISDOM = load_quotes('wisdom.txt')
    MASTER_CRITICISM = load_quotes('master_criticism.txt')
    TRAINING_INJURY = load_quotes('training_injury.txt')

    PREFIGHT_QUOTES = {
        'challenger': CHALLENGER_PREFIGHT,
        'hero': HERO_PREFIGHT,
        'thug': THUG_PREFIGHT,
        'master': WISDOM,
    }
    WIN_QUOTES = {
        'challenger': CHALLENGER_WIN,
        'hero': HERO_WIN,
        'thug': THUG_WIN,
        'master': WISDOM
    }


reload_quotes()
