"""English-oriented grammar helpers, language-dispatching.

These exist because a lot of prose is assembled inline; in Russian most of them
behave differently or become no-ops (Russian has no articles, different plural
rules). Call sites that need real Russian plurals should use i18n.ngettext
directly instead of sg_or_pl.
"""

from kf_lib import i18n

AN_EXCEPTIONS = set()
ARTICLE_VARIANTS = {'a', 'an', 'A', 'An'}


def add_article(word):
    if i18n.get_language() != 'en':
        return word  # no articles in Russian
    if word[0].lower() in 'a e i o u'.split() and word not in AN_EXCEPTIONS:
        word = 'an ' + word
    else:
        word = 'a ' + word
    return word


def choose_adverb(n, adv_low, adv_high):
    if n <= 0.3:
        return adv_low + ' '
    elif n <= 0.7:
        return ''
    else:
        return adv_high + ' '


def enum_words(words_iterable):
    """Return string:
    () -> ''
    ('a') -> 'a'
    ('a', 'b') -> 'a and b'      (ru: 'a и b')
    ('a', 'b', 'c') -> 'a, b and c'  (ru: 'a, b и c')
    """
    ws = words_iterable
    if not ws:
        return ''
    elif len(ws) == 1:
        return ws[0]
    conj = 'and' if i18n.get_language() == 'en' else 'и'
    if len(ws) == 2:
        return f'{ws[0]} {conj} {ws[1]}'
    elif len(ws) >= 3:
        return f"{', '.join(ws[:-1])} {conj} {ws[-1]}"


def remove_article(word):
    """Remove article at the beginning of word if any."""
    ww = word.split()
    return ' '.join(ww[1:]) if ww[0] in ARTICLE_VARIANTS else word


def sg_or_pl(number):
    """Return 's' if number is greater than 1. Return '' if number is 1.

    English-only suffix trick; returns '' in other languages — call sites that
    matter for Russian should use i18n.ngettext instead."""
    if i18n.get_language() != 'en':
        return ''
    if number > 1:
        return 's'
    elif number == 1:
        return ''
