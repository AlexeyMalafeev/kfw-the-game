import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..', '..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

"""Group FFA effective-opposition experiment.

Measures how hard a group free-for-all actually is for group 1 ("my group"),
by win rate, and maps that win rate onto an equivalent *united* enemy group
size k (from a calibration curve of my-group vs k united enemies). Runs tiers
where my group is a few levels above the enemies so win rates don't saturate
at 0%. eff.k is measured in enemy fighters; since both eff.k and the candidate
formulas scale with enemy exp yield, comparing eff.k to the average enemy
group size is level-independent.

eff.ratio = eff.k / my group size; pred.ratio = avg grp size / my group size —
the ratio the exp formula (losers_yield / winners_yield) would use.
"""

import math

from kf_lib.actors import fighter_factory as ff
from kf_lib.fighting import fight


N = 300
# (my_lv, enemy_lv) tiers: equal levels, then the player side stronger
TIERS = [(10, 10), (13, 10), (14, 10)]

MY_SIZES = (1, 2, 3, 4)

CONFIGS = [
    # solo
    [1, 8, 2],
    [1, 6, 2],
    [1, 5, 5, 5, 5, 5],
    [1, 4, 4],
    [1, 3, 3],
    [1, 2, 2],
    # with one ally
    [2, 8, 2],
    [2, 5, 5, 5],
    [2, 4, 4],
    [2, 3, 3],
    [2, 2, 2],
    # with two allies
    [3, 5, 5, 5, 5, 5],
    [3, 3, 3],
    # with three allies
    [4, 8, 2],
    [4, 5, 5, 5, 5, 5],
    [4, 4, 4],
    # sanity checks: a single enemy group == a plain united fight
    [1, 5],
    [2, 4],
    [4, 6],
]


def as_list(f):
    return f if isinstance(f, list) else [f]


def group_ffa_winrate(sizes, my_lv, en_lv, n=N):
    wins = 0
    for _ in range(n):
        groups = [as_list(ff.new_fighter(lv=my_lv, n=sizes[0]))]
        groups += [as_list(ff.new_fighter(lv=en_lv, n=s)) for s in sizes[1:]]
        if fight.group_free_for_all(groups):
            wins += 1
    return wins / n


def united_winrate(my_size, k, my_lv, en_lv, n=N):
    wins = 0
    for _ in range(n):
        me = as_list(ff.new_fighter(lv=my_lv, n=my_size))
        enemies = as_list(ff.new_fighter(lv=en_lv, n=k))
        if fight.AutoFight(me, enemies).win:
            wins += 1
    return wins / n


def calibrate(my_size, k_max, my_lv, en_lv, n=N):
    return {k: united_winrate(my_size, k, my_lv, en_lv, n) for k in range(1, k_max + 1)}


def effective_k(winrate, curve):
    """Interpolate the win rate onto the calibration curve (winrate vs k)."""
    ks = sorted(curve)
    if winrate >= curve[ks[0]]:
        return float(ks[0])
    if winrate <= curve[ks[-1]]:
        return float(ks[-1])
    for k1, k2 in zip(ks, ks[1:]):
        w1, w2 = curve[k1], curve[k2]
        if w1 >= winrate >= w2:
            if w1 == w2:
                return float(k1)
            return k1 + (w1 - winrate) / (w1 - w2)
    return float(ks[-1])


def run_tier(my_lv, en_lv):
    print(f'\n=== tier: my group lv.{my_lv}, enemies lv.{en_lv}, {N} fights per cell ===\n')
    curves = {}
    for m in MY_SIZES:
        print(f'calibrating {m} vs k united...')
        curves[m] = calibrate(m, m * 3 + 8, my_lv, en_lv)
    for m in MY_SIZES:
        print(f'{m} vs k united win rates:',
              {k: round(v, 3) for k, v in curves[m].items()})

    header = (
        'config', 'my win%', 'eff.k', 'eff.ratio', 'pred.ratio', 'avg grp size',
        'RMS', 'max grp',
    )
    print('\n' + '\t'.join(header))
    for sizes in CONFIGS:
        my_size, enemy_groups = sizes[0], sizes[1:]
        curve = curves[my_size]
        wr = group_ffa_winrate(sizes, my_lv, en_lv)
        eff_k = effective_k(wr, curve)
        n_groups = len(enemy_groups)
        avg_size = sum(enemy_groups) / n_groups
        rms = math.sqrt(sum(s * s for s in enemy_groups) / n_groups)
        row = (
            str(sizes),
            f'{wr:.1%}',
            f'{eff_k:.1f}',
            f'{eff_k / my_size:.2f}',
            f'{avg_size / my_size:.2f}',
            f'{avg_size:.1f}',
            f'{rms:.1f}',
            str(max(enemy_groups)),
        )
        print('\t'.join(row))


def main():
    for my_lv, en_lv in TIERS:
        run_tier(my_lv, en_lv)


if __name__ == '__main__':
    main()
