"""What does Guard do? Controlled exchanges: fighter A guards (or not), then B strikes A once.

The fight AI's choices don't enter: for each of n samples, two fresh random
fighters at the same random level (--levels, default 1-20), both with a random
mid-fight stamina and qi (25-100% of max; full HP). B picks a random attack move
it can afford against a standing target, at that move's distance. A takes one
turn under each condition, then B strikes:
    nothing   A's turn leaves its defense as is (baseline defense)
    Guard     A uses the Guard move, with its own guard techs (as generated)
    G+AG      the same with A's guard bonus as given by Advanced Guard alone
    G+DG      ... by Dragon Guards a Treasure alone
Every condition replays the same pair, states and random rolls, so differences
come from the conditions alone (B's damage value starts at 0, a fresh
fighter's). Each --variants FILE:NAMES (repeatable) adds a column set run in its
own worker pool (the author's new Guard was measured as rule_variants.py:Gb+Grec
at commit ae74b9f, before it was adopted).

    python run_test_guard.py
    python run_test_guard.py --variants rule_variants.py:Ga
Prints a table only (no report file). Runs from any cwd.
"""
import argparse
import multiprocessing
import os
import random
import sys
from pathlib import Path

ORIG_CWD = os.getcwd()  # for the user's relative paths
lib_path = Path(__file__).resolve().parents[2]  # workers re-import this module from the repo root
os.chdir(lib_path)
if str(lib_path) not in sys.path:
    sys.path.append(str(lib_path))

from run_test_tech_ab import apply_overrides  # noqa: E402 (needs the sys.path above)

CONDS = ('nothing', 'Guard', 'G+AG', 'G+DG')
TIERS = ((1, 7), (8, 14), (15, 20))
KEYS = ('n', 'preempted', 'missed', 'thrown', 'dodged', 'full_blocked', 'part_blocked',
        'hit', 'hit0', 'dmg_a', 'dmg_a2', 'dmg_b', 'counters', 'counters_after_miss',
        'net', 'net2', 'd_dmg', 'd_dmg2', 'rec_st', 'rec_qp')


def tier_of(lv):
    return next(i for i, (lo, hi) in enumerate(TIERS) if lo <= lv <= hi)


def exchange(fgt, a, b, move, guard, guard_bonus, states, roll_seed):
    """A's turn (Guard or not), then B's strike. Returns the outcome as a dict."""
    fgt.prepare_fighters()  # full HP, statuses and fight stats reset
    a.stamina, a.qp, b.stamina, b.qp = states
    b.dam = 0
    a.set_distance(b, move.distance)
    a.guard_dfs_bonus = guard_bonus
    random.seed(roll_seed)
    a.start_fight_turn()
    a.set_target(b)
    st0, qp0 = a.stamina, a.qp
    if guard:
        a.action = guard
        a.refresh_ascii()
        a.exec_move()
    out = {'rec_st': a.stamina - st0, 'rec_qp': a.qp - qp0}
    hp_a, hp_b = a.hp, b.hp
    b.start_fight_turn()
    b.set_target(a)
    b.action = move
    b.refresh_ascii()
    b.exec_move()
    afs, bfs = a.fight_stats, b.fight_stats
    out['preempted'] = afs['preemptives']
    out['thrown'] = bfs['thrown']
    out['missed'] = 1 - afs['preemptives'] - bfs['thrown']
    out['dodged'] = afs['dodges']
    out['full_blocked'] = afs['full_blocks']
    out['part_blocked'] = afs['blocks'] - afs['full_blocks']
    out['hit'] = out['thrown'] - afs['dodges'] - afs['blocks']
    out['dmg_a'] = hp_a - a.hp
    out['hit0'] = out['hit'] and not out['dmg_a']  # toughness took it all
    out['dmg_b'] = hp_b - b.hp
    out['counters'] = afs['counters']
    out['counters_after_miss'] = afs['counters'] if out['missed'] else 0
    return out


def play(job):
    """One chunk of samples: returns {cond: totals} and {cond: per-tier [n, dmg_a]}."""
    from kf_lib.actors import fighter_factory as ff
    from kf_lib.fighting.fight import BaseFight
    from kf_lib.kung_fu import boosts, moves
    start, count, seed, lv_min, lv_max = job
    guard_move = moves.get_move_obj('Guard')
    totals = {c: dict.fromkeys(KEYS, 0) for c in CONDS}
    tiers = {c: [[0, 0] for _ in TIERS] for c in CONDS}
    for i in range(start, start + count):
        s = seed * 1_000_003 + i
        random.seed(s)
        lv = random.randint(lv_min, lv_max)
        a = ff.new_fighter(lv=lv)
        a.name = 'Dummy A'
        b = ff.new_fighter(lv=lv)
        b.name = 'Dummy B'
        rng = random.Random(s)
        fr = [rng.uniform(0.25, 1.0) for _ in range(4)]
        states = (round(a.stamina_max * fr[0]), round(a.qp_max * fr[1]),
                  round(b.stamina_max * fr[2]), round(b.qp_max * fr[3]))
        cands = [m for m in b.moves if m.power and m.distance
                 and 'antiground only' not in m.features
                 and states[2] >= m.stam_cost and states[3] >= m.qi_cost]
        if not cands:
            continue
        move = rng.choice(cands)
        fgt = BaseFight([a], [b], environment_allowed=False)
        own_bonus = a.guard_dfs_bonus
        conds = {'nothing': (None, own_bonus), 'Guard': (guard_move, own_bonus),
                 'G+AG': (guard_move, 1.0 + boosts.GUARD_DFS1),
                 'G+DG': (guard_move, 1.0 + boosts.GUARD_DFS2)}
        base_dmg = None
        for c in CONDS:
            g, bonus = conds[c]
            out = exchange(fgt, a, b, move, g, bonus, states, s + 1)
            t = totals[c]
            t['n'] += 1
            for k in ('preempted', 'missed', 'thrown', 'dodged', 'full_blocked',
                      'part_blocked', 'hit', 'hit0', 'dmg_a', 'dmg_b', 'counters',
                      'counters_after_miss', 'rec_st', 'rec_qp'):
                t[k] += out[k]
            net = out['dmg_a'] - out['dmg_b']
            t['dmg_a2'] += out['dmg_a'] ** 2
            t['net'] += net
            t['net2'] += net ** 2
            if base_dmg is None:
                base_dmg = out['dmg_a']
            d = out['dmg_a'] - base_dmg  # paired with 'nothing'
            t['d_dmg'] += d
            t['d_dmg2'] += d ** 2
            tr = tiers[c][tier_of(lv)]
            tr[0] += 1
            tr[1] += out['dmg_a']
    return totals, tiers


def run_set(variants, args):
    jobs = []
    chunk = 2000
    for start in range(0, args.n, chunk):
        jobs.append((start, min(chunk, args.n - start), args.seed, *args.lv))
    apply_overrides([], [], variants)  # fail fast on a bad variant name
    ctx = multiprocessing.get_context('spawn')
    with ctx.Pool(args.workers or os.cpu_count() or 1, initializer=apply_overrides,
                  initargs=([], [], variants)) as pool:
        results = pool.map(play, jobs)
    totals = {c: dict.fromkeys(KEYS, 0) for c in CONDS}
    tiers = {c: [[0, 0] for _ in TIERS] for c in CONDS}
    for tot, tie in results:
        for c in CONDS:
            for k in KEYS:
                totals[c][k] += tot[c][k]
            for j, (n, dmg) in enumerate(tie[c]):
                tiers[c][j][0] += n
                tiers[c][j][1] += dmg
    return totals, tiers


def mean_margin(s, s2, n):
    m = s / n
    var = max(s2 / n - m * m, 0.0)
    return m, 1.96 * (var / n) ** 0.5


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('-n', type=int, default=100_000, help='samples (fighter pairs)')
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--levels', default='1-20', help='fighter level range, e.g. 13-20')
    parser.add_argument('--variants', action='append', default=[], metavar='FILE:NAMES')
    parser.add_argument('--workers', type=int, default=None)
    args = parser.parse_args()
    args.lv = tuple(int(x) for x in args.levels.split('-'))
    sets = [('engine', '')]
    for v in args.variants:
        path, names = v.rsplit(':', 1)
        sets.append((names, f'{Path(ORIG_CWD, path).resolve()}:{names}'))

    cols = []  # (set label, cond, totals, tiers)
    for label, variants in sets:
        totals, tiers = run_set(variants, args)
        for c in CONDS:
            if c == 'nothing' and cols:
                continue  # the same as the engine's unless a variant changes defense
            cols.append((label, c, totals[c], tiers[c]))

    def pct(key, of='n'):
        return [(100 * t[key] / t[of], None) for _, _, t, _ in cols]

    def rate_margin(key, of='n'):
        out = []
        for _, _, t, _ in cols:
            p = t[key] / t[of]
            out.append((100 * p, 196 * (p * (1 - p) / t[of]) ** 0.5))
        return out

    rows = [
        ('B preempted by A, %', pct('preempted')),
        ('B missed (move failed), %', pct('missed')),
        ('dodged, % of strikes', rate_margin('dodged', 'thrown')),
        ('fully blocked, %', rate_margin('full_blocked', 'thrown')),
        ('partly blocked, %', rate_margin('part_blocked', 'thrown')),
        ('hit, %', rate_margin('hit', 'thrown')),
        ('  of which 0 HP (toughness), %', pct('hit0', 'thrown')),
        ('HP lost by A', [mean_margin(t['dmg_a'], t['dmg_a2'], t['n']) for _, _, t, _ in cols]),
        ('  vs nothing (paired)', [mean_margin(t['d_dmg'], t['d_dmg2'], t['n']) for _, _, t, _ in cols]),
        ('A counters per strike', [(t['counters'] / t['n'], None) for _, _, t, _ in cols]),
        ('  of which after a miss', [(t['counters_after_miss'] / t['n'], None) for _, _, t, _ in cols]),
        ('HP lost by B (counters etc.)', [(t['dmg_b'] / t['n'], None) for _, _, t, _ in cols]),
        ('net HP, A lost - B lost', [mean_margin(t['net'], t['net2'], t['n']) for _, _, t, _ in cols]),
        ('A recovered stamina', [(t['rec_st'] / t['n'], None) for _, _, t, _ in cols]),
        ('A recovered qi', [(t['rec_qp'] / t['n'], None) for _, _, t, _ in cols]),
    ]
    base_tiers = cols[0][3]
    for j, (lo, hi) in enumerate(TIERS):
        vals = []
        for _, _, _, tie in cols:
            n, dmg = tie[j]
            bn, bdmg = base_tiers[j]
            vals.append((100 * (dmg / n) / (bdmg / bn) if bdmg else 0.0, None))
        rows.append((f'lv {lo}-{hi}: HP lost, % of nothing', vals))

    w0, w = 32, 13
    print(f'\nGuard exchanges: n={args.n} pairs, lv {args.levels}, seed {args.seed}; '
          f'one column per rule set and condition')
    print(' ' * w0 + ''.join(f'{lbl[:w - 1]:>{w}}' for lbl, *_ in cols))
    print(' ' * w0 + ''.join(f'{c:>{w}}' for _, c, *_ in cols))
    for name, vals in rows:
        cells = []
        for v, m in vals:
            cells.append(f'{v:.2f}+-{m:.2f}'.rjust(w) if m is not None else f'{v:{w}.2f}')
        print(f'{name:{w0}s}' + ''.join(cells))


if __name__ == '__main__':  # required: worker processes import this module
    main()
