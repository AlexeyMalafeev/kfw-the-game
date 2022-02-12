import string
import os
import random
import time

from . import getch

getch_inst = getch.Getch()

# todo split into separate modules: ui, numbers, etc.


def add_pcnt(value):
    return f'{value}%'


def add_sign(number):
    """Return signed string:
    x -> '+x'
    -x -> '-x'
    0 -> '0'
    """
    if number > 0:
        return f'+{number}'
    else:
        return str(number)


def add_to_dict(d, k, v):
    if k not in d:
        d[k] = 0
    d[k] += v


# todo consider replacing this with textwrap
def align_text(text, indent, align):
    """This function ignores \n and \t."""
    # split text into lines
    # align += 1
    words = text.split()
    lines = []
    lengths = []
    curr_line = []
    words_len = 0  # length of all words in a line, no spaces
    int_spaces = -1  # spaces between words in a line
    for word in words:
        wlen = len(word)
        if wlen + words_len + int_spaces < align:
            curr_line.append(word)
            words_len += wlen
            int_spaces += 1
        else:
            lines.append(curr_line)
            lengths.append(words_len + int_spaces)
            curr_line = [word]
            words_len = wlen
            int_spaces = 0
    lines.append(curr_line)

    # normalize lines
    for i, line in enumerate(lines[:-1]):
        nwords = len(line)
        nchars = lengths[i]
        diff = align - nchars
        if diff >= nwords:
            even_spaces, uneven_spaces = divmod(diff, nwords - 1)
        else:
            uneven_spaces = diff
            even_spaces = 0
        for j in range(uneven_spaces):
            line[j] += ' '
        line = (' ' * (1 + even_spaces)).join(line)
        lines[i] = line
    lines[-1] = ' '.join(lines[-1])
    return ' ' * indent + f"\n{' ' * indent}".join(lines)


def cls():
    os.system("cls")  # todo look into Unix compatibility


def dict_comp(d1, d2, sort_col_index=0, descending=True):
    """Return a list of tuples"""
    tups = []
    keys = set(d1.keys()) | set(d2.keys())
    for k in keys:
        if k not in d1:
            d1[k] = 0
        elif k not in d2:
            d2[k] = 0
        v1, v2 = d1[k], d2[k]
        s = v1 + v2
        m = mean((v1, v2))
        tups.append((k, v1, v2, pcnt(v1 - m, m), s))
    tups.sort(key=lambda x: x[sort_col_index], reverse=descending)
    tups = [(i + 1, *t) for i, t in enumerate(tups)]
    # noinspection PyTypeChecker
    tups = [('#', 'Key', 'D1', 'D2', 'Diff%', 'Sum')] + tups
    return tups


def dict_diff(d1, d2):
    """Return a dict"""
    d = {}
    keys = set(d1.keys()) | set(d2.keys())
    for k in keys:
        if k not in d1:
            d1[k] = 0
        elif k not in d2:
            d2[k] = 0
        d[k] = d1[k] - d2[k]
    return d


def float_to_pcnt(x):
    """Convert a float to a percentage string, e.g. 0.4 -> '40%'."""
    return '{}%'.format(round(x * 100))


def get_adverb(n, adv_low, adv_high):
    if n <= 0.3:
        return adv_low + ' '
    elif n <= 0.7:
        return ''
    else:
        return adv_high + ' '


def get_bar(numerator, denominator, filled_sym, empty_sym, bar_length, mirror=False):
    if denominator:
        ratio = numerator / denominator
    else:
        if numerator:
            raise ValueError(
                f'This is weird, numerator is {numerator}, denominator is {denominator}')
        ratio = 0
    filled = round(bar_length * ratio)
    empty = bar_length - filled
    if not mirror:
        return filled_sym * filled + empty_sym * empty
    else:
        return empty_sym * empty + filled_sym * filled


def get_key():
    """
    If key is pressed, return its string; if no key is pressed, return 0
    """
    # DEBUG MODE
    # return input('key:')
    # NORMAL MODE
    return chr(ord(getch_inst()))


def get_linear_bar(v, maxv, syma='#', symb='-'):
    """Differs from get_bar in that bar_length is not fixed and will be of len(maxv).
    Mirroring can be done by switching syma and symb and supplying maxv - v as v."""
    return syma * v + symb * (maxv - v)


def get_int_from_user(message, min_, max_) -> int:
    """
    Return an integer in range [a, b] (both included) input by user.
    """
    error_msg = 'invalid input, try again'
    while True:
        print(message)
        inp = input(f' ({min_}-{max_})>')
        try:
            inp = int(inp)
        except ValueError:
            print(error_msg)
            continue
        if min_ <= inp <= max_:
            return inp
        else:
            print(error_msg)


def get_str_from_user(message, can_be_empty=False) -> str:
    error_msg = 'invalid input, try again'
    while True:
        print(message)
        inp = input(f' > ')
        if not inp and not can_be_empty:
            print(error_msg)
        else:
            return inp


def get_prop_bar(value, max_value):
    mx = 10
    b = round(mx / max_value * value)
    return f"{'=' * b}{'-' * (mx - b)}"


def get_time():
    return time.ctime()


def hund(value):
    return round(value * 100)


def main():
    import sys

    print("Please press a key to see its value")
    input_key = getch.Getch()
    while 1:
        key = input_key()
        print("the key is")
        print(key)
        if ord(key) == 27:  # key nr 27 is escape
            sys.exit()


def mean(values):
    return round(sum(values) / len(values), 2)


def median(values):
    values = list(values)
    values.sort()
    n = len(values)
    if not n % 2:
        i = int(n / 2) - 1
        j = i + 1
        return mean((values[i], values[j]))
    else:
        i = int((n - 1) / 2)
        return values[i]


def menu(
    opt_list,
    title='',
    keys='1234567890' + string.ascii_lowercase,
    new_line=True,
    weak=False,
    options_per_page=20,
):
    """
    Ask the user to choose one of the options from the option list.
    The option list is either a list of strings
    (then return the selected option string on user choice),
    or a list of tuples (string, object),
    (then return the object matching the choice).
    """
    if isinstance(opt_list[0], tuple) and len(opt_list[0]) == 2:
        options = []
        returnables = []
        for a, b in opt_list:
            options.append(a)
            returnables.append(b)
    else:
        options = returnables = opt_list
    i = 0
    has_pages = False
    while True:
        curr_options = options[i: i + options_per_page]
        curr_returnables = returnables[i: i + options_per_page]
        curr_keys = keys[: len(curr_options)]
        if len(opt_list) > options_per_page:
            curr_options += ['Previous page', 'Next page']
            curr_keys += '<>'
            has_pages = True
        if title:
            print(title)
        if new_line:
            st = '\n'
        else:
            st = '; '
        print(st.join([f' {curr_keys[j]} - {curr_options[j]}' for j in range(len(curr_keys))]))
        while True:
            choice = get_key()
            if has_pages and choice in '<>':
                cls()
                if choice == '<':
                    i = max(0, i - options_per_page)
                elif options[i + options_per_page:]:
                    i += options_per_page
                break
            elif choice in curr_keys:
                return curr_returnables[curr_keys.index(choice)]
            elif weak:
                return


def msg(message):
    print(message)
    pak()


def multiply(numbers):
    from functools import reduce

    return reduce(lambda x, y: x * y, numbers)


def my_trace(*args, show_time=True, blank_line=True):
    if show_time:
        import time

        time_string = time.ctime()
    else:
        time_string = ''
    if blank_line:
        blank_string = '\n'
    else:
        blank_string = ''
    print(blank_string, time_string, *args, file=open('tracer.txt', 'a'))


def rnd():
    """Return a random number between 0 and 1."""
    return random.random()


def rndint(a, b):
    """Return a random integer between a and b."""
    return random.randint(a, b)


def rndint_2d(a, b):
    """Return a random number between a and b as if it was generated by two dice.
    E.g., running rndint_2d(2, 12) a thousand times and collecting the results in a Counter might
    yield:
    Counter({7: 161, 6: 153, 8: 128, 5: 112, 9: 110, 10: 91, 4: 67, 11: 61, 3: 55, 12: 32, 2: 30})
    Alternatively, Counter([rndint_2d(5, 7) for _ in range(1000)]) might result in:
    Counter({6: 484, 7: 270, 5: 246}) or Counter({6: 519, 5: 244, 7: 237})
    """
    if not a % 2:
        a1 = a2 = a // 2
    else:
        a1 = a // 2
        a2 = a1 + 1
    if not b % 2:
        b1 = b2 = b // 2
    else:
        b1 = b // 2
        b2 = b1 + 1
    return random.randint(a1, b1) + random.randint(a2, b2)


def pak(silent=True):
    """
    Press any key.
    Wait for user to press any key.
    """
    if not silent:
        print('(Press any key)')
    get_key()


def pcnt(v, max_v, n=2, as_string=False):
    if n:
        p = round((v / max_v) * 100, n)
    else:
        p = round((v / max_v) * 100)
    if as_string:
        return str(p) + '%'
    else:
        return p


def pe():
    input('Press Enter')


def percentage(v, max_v):
    """Calculate and output percentage in the following format: '20/40 (50%)'."""
    return '{}/{} ({}%)'.format(v, max_v, pcnt(v, max_v))


def pretty_table(table, sep='  ', as_list=False):
    """table is a list of equal-length tuples/lists – lines"""
    columns = [[] for _ in range(len(table[0]))]
    for line in table:
        for i, elt in enumerate(line):
            columns[i].append(elt)
    max_lens = [max([len(str(elt)) for elt in col]) for col in columns]
    new_lines = []
    for line in table:
        new_lines.append(
            sep.join(('{:<{}}'.format(elt, max_lens[i]) for i, elt in enumerate(line)))
        )
    if as_list:
        return new_lines
    else:
        return '\n'.join(new_lines)


def ranked(d, as_string=True, descending=True, diff_from_mean=True):
    """Sort d by values"""
    tups = [(k, v) for k, v in d.items()]
    tups.sort(key=lambda x: x[1], reverse=descending)
    if as_string:
        if diff_from_mean:
            m = mean(d.values())
            new_tups = []
            for k, v in tups:
                diff = v - m
                diff_p = pcnt(diff, m, as_string=True)
                new_tups.append((k, v, diff_p))
            return pretty_table(new_tups)
        else:
            return pretty_table(tups)
    else:
        return tups


def roman(x):
    """Incomplete."""
    tens = x // 10
    rem = x % 10
    repl = {
        1: "I",
        2: "II",
        3: "III",
        4: "IV",
        5: "V",
        6: "VI",
        7: "VII",
        8: "VIII",
        9: "IX",
        0: "",
    }
    return 'X' * tens + repl[rem]


def sigmoid_old(z):
    import math

    ans = 1.0 / (1.0 + math.exp(-z))
    return ans


def sigmoid(x):
    """Numerically-stable sigmoid function."""
    import math

    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    else:
        z = math.exp(x)
        return z / (1 + z)


def summary(data):
    """Supports lists and dict values"""
    if isinstance(data, dict):
        data = list(data.values())
    mx, mn = max(data), min(data)
    return 'Min: {}, Max: {}, Range: {}, Median: {}, Mean: {}'.format(
        mn, mx, mx - mn, median(data), mean(data)
    )


def yn(message):
    return menu((('yes', True), ('no', False)), message)


if __name__ == '__main__':
    main()
