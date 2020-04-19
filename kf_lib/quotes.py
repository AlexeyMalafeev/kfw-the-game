#! python3


def load_quotes(file_name):
    try:
        with open('quotes//' + file_name) as f:
            quotes = f.read().split('\n')
        return quotes
    except:
        print('Failed to load quotes from ' + file_name)
        return ['<empty quote>']


MISC = ''

CHALLENGER_PREFIGHT = load_quotes('challenger_prefight.txt')
CHALLENGER_WIN = load_quotes('challenger_win.txt')
HERO_PREFIGHT = load_quotes('hero_prefight.txt')
HERO_WIN = load_quotes('hero_win.txt')
THUG_PREFIGHT = load_quotes('thug_prefight.txt')
THUG_WIN = load_quotes('thug_win.txt')
WISDOM = load_quotes('wisdom.txt')
MASTER_CRITICISM = load_quotes('master_criticism.txt')
TRAINING_INJURY = load_quotes('training_injury.txt')

PREFIGHT_QUOTES = {'challenger': CHALLENGER_PREFIGHT, 'hero': HERO_PREFIGHT, 'thug': THUG_PREFIGHT,
                   'master': WISDOM}
WIN_QUOTES = {'challenger': CHALLENGER_WIN, 'hero': HERO_WIN, 'thug': THUG_WIN, 'master': WISDOM}
