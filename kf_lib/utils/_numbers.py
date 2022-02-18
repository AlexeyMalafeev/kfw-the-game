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


def float_to_pcnt(x):
    """Convert a float to a percentage string, e.g. 0.4 -> '40%'."""
    return '{}%'.format(round(x * 100))


def hund(value):
    return round(value * 100)


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


def multiply(numbers):
    from functools import reduce

    return reduce(lambda x, y: x * y, numbers)


def percentage(v, max_v):
    """Calculate and output percentage in the following format: '20/40 (50%)'."""
    return '{}/{} ({}%)'.format(v, max_v, pcnt(v, max_v))


def pcnt(v, max_v, n=2, as_string=False):
    if n:
        p = round((v / max_v) * 100, n)
    else:
        p = round((v / max_v) * 100)
    if as_string:
        return str(p) + '%'
    else:
        return p


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


def sigmoid(x):
    """Numerically-stable sigmoid function."""
    import math

    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    else:
        z = math.exp(x)
        return z / (1 + z)
