from kf_lib.ui import pretty_table
from kf_lib.utils import mean, pcnt, median


def compare_dicts(d1, d2, sort_col_index=0, descending=True):
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


def summary(data):
    """Supports lists and dict values"""
    if isinstance(data, dict):
        data = list(data.values())
    mx, mn = max(data), min(data)
    return 'Min: {}, Max: {}, Range: {}, Median: {}, Mean: {}'.format(
        mn, mx, mx - mn, median(data), mean(data)
    )
