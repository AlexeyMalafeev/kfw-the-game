AN_EXCEPTIONS = set()
ARTICLE_VARIANTS = {'a', 'an', 'A', 'An'}


def add_article(word):
    if word[0].lower() in 'a e i o u'.split() and word not in AN_EXCEPTIONS:
        word = 'an ' + word
    else:
        word = 'a ' + word
    return word


def choose_adverb(x: float, adv_low: str, adv_high: str):
    if x <= 0.3:
        return f'{adv_low} '
    elif x <= 0.7:
        return ''
    else:
        return f'{adv_high} '


def enum_words(words_iterable):
    """Return string:
    () -> ''
    ('a') -> 'a'
    ('a', 'b') -> 'a and b'
    ('a', 'b', 'c') -> 'a, b and c'
    """
    ws = words_iterable
    if not ws:
        return ''
    elif len(ws) == 1:
        return ws[0]
    elif len(ws) == 2:
        return f'{ws[0]} and {ws[1]}'
    elif len(ws) >= 3:
        return f"{', '.join(ws[:-1])} and {ws[-1]}"


def remove_article(word):
    """Remove article at the beginning of word if any."""
    ww = word.split()
    return ' '.join(ww[1:]) if ww[0] in ARTICLE_VARIANTS else word


def sg_or_pl(number):
    """Return 's' if number is greater than 1. Return '' if number is 1."""
    if number > 1:
        return 's'
    elif number == 1:
        return ''
