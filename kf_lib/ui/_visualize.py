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