from kf_lib.ui import pretty_table
from kf_lib.utils import mean, pcnt


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
