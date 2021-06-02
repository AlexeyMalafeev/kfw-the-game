AN_EXCEPTIONS = ''


def add_article(word):
    if word[0].lower() in 'a e i o u'.split() and not word in AN_EXCEPTIONS:
        word = 'an ' + word
    else:
        word = 'a ' + word
    return word


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
    if ww[0] in 'a an A An'.split():
        return ' '.join(ww[1:])
    else:
        return word


def sg_or_pl(number):
    """Return 's' if number is greater than 1. Return '' if number is 1."""
    if number > 1:
        return 's'
    elif number == 1:
        return ''


def sign_number(number):
    pass
