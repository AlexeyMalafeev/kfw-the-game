import time

# todo split into separate modules: ui, numbers, etc.


def add_to_dict(d: dict, k: str, v: int, start_val: int = 0) -> None:
    d[k] = d.get(k, start_val) + v


# I considered replacing this with built-in textwrap, but textwrap doesn't seem to be able to do
# text justification out of the box.
# todo refactor align_text
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


def get_linear_bar(v, maxv, syma='#', symb='-'):
    """Differs from get_bar in that bar_length is not fixed and will be of len(maxv).
    Mirroring can be done by switching syma and symb and supplying maxv - v as v."""
    return syma * v + symb * (maxv - v)


def get_prop_bar(value, max_value):
    mx = 10
    b = round(mx / max_value * value)
    return f"{'=' * b}{'-' * (mx - b)}"


def get_time():
    return time.ctime()


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
