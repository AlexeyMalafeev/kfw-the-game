"""What is a technique worth? A/B test: mirror matches where one side gets the tech.

For each tech: n fights between two fresh random fighters at the same random level
(--levels, default 13-20: general techs arrive at 13/15/17); one side, picked at
random, is given the tech (pairs where it already had it are skipped). Diff% =
2 * win rate - 1, in the fight-balance harness's units. Every tech plays the same
seeded fighter pairs, so techs compare against each other with less noise.

    python run_test_tech_ab.py "Iron Fist" "18 Defense Forms"
    python run_test_tech_ab.py --all-general -n 8000        # every general tech + median
    python run_test_tech_ab.py "Shadow Slips Away" --scale dodge_mult=1.5
    python run_test_tech_ab.py "Advanced Guard" --set GUARD_POWER=2.0
    python run_test_tech_ab.py "Advanced Guard" --variants path/to/variants.py:Ga+Gb
    python run_test_tech_ab.py +strength +agility +speed +health --levels 1-7

A name '+ATT' (+strength, +agility, +speed, +health) gives one extra point of that
attribute instead of a tech: what an attribute point is worth.

--set CONST=VALUE overrides a Fighter class constant; --scale PARAM=FACTOR multiplies
that param in every Tech (e.g. to try another boost value); --variants FILE:NAMES calls
FILE's apply(NAMES), a hook for monkeypatched rule experiments (see docs/dev_scripts.md).
Prints a table only (no report file). Runs from any cwd.
"""
import argparse
import multiprocessing
import os
import random
import statistics
import sys
from pathlib import Path

lib_path = Path(__file__).resolve().parents[2]  # workers re-import this module from the repo root
os.chdir(lib_path)
if str(lib_path) not in sys.path:
    sys.path.append(str(lib_path))


def apply_overrides(sets, scales, variants):
    """Runs in every worker before its fights."""
    os.chdir(lib_path)
    # import everything that creates Tech objects first (style_gen builds the
    # generated styles' techs at import), or --scale would miss them
    from kf_lib.actors import fighter_factory  # noqa: F401
    from kf_lib.actors.fighter import Fighter
    from kf_lib.fighting import fight  # noqa: F401
    from kf_lib.kung_fu import techniques
    for item in sets:
        name, value = item.split('=', 1)
        cur = getattr(Fighter, name)
        setattr(Fighter, name, float(value) if isinstance(cur, float) else int(value))
    for item in scales:
        param, factor = item.split('=', 1)
        hits = 0
        for tech in techniques.get_all_techs_dict().values():
            if param in getattr(tech, 'params', {}):
                tech.params[param] *= float(factor)
                hits += 1
        if not hits:  # a typo would silently measure nothing
            raise ValueError(f'--scale {item}: no technique has the param {param!r}')
    if variants:
        import importlib.util
        path, names = variants.rsplit(':', 1)
        spec = importlib.util.spec_from_file_location('variants', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.apply(names)


def play(job):
    """One tech: returns (tech name, wins, played)."""
    from kf_lib.actors import fighter_factory as ff
    from kf_lib.fighting import fight
    from kf_lib.kung_fu import techniques
    tech_name, n, seed, lv_min, lv_max = job
    att = tech_name[1:] if tech_name.startswith('+') else None
    tech = None if att else techniques.get_tech_obj(tech_name)
    random.seed(seed)
    wins = played = 0
    for _ in range(n):
        lv = random.randint(lv_min, lv_max)
        f1 = ff.new_fighter(lv=lv)
        f1.name = 'Dummy A'
        f2 = ff.new_fighter(lv=lv)
        f2.name = 'Dummy B'
        treated = f1 if random.random() < 0.5 else f2
        if att:
            treated.change_att(att, 1)
            treated.refresh_dependent_atts()  # HP, counter/critical chance
        elif tech in treated.techs:
            continue
        else:
            treated.add_tech(tech)
        f = fight.AutoFight([f1], [f2])
        if f.winners:
            played += 1
            wins += f.winners[0] is treated
    return tech_name, wins, played


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('techs', nargs='*', help='tech names, as in techniques.py')
    parser.add_argument('--all-general', action='store_true', help='add every general tech')
    parser.add_argument('-n', type=int, default=16000, help='fights per tech')
    parser.add_argument('--seed', type=int, default=11)
    parser.add_argument('--levels', default='13-20', help='fighter level range, e.g. 13-20')
    parser.add_argument('--set', action='append', default=[], metavar='CONST=VALUE')
    parser.add_argument('--scale', action='append', default=[], metavar='PARAM=FACTOR')
    parser.add_argument('--variants', default='', metavar='FILE:NAMES')
    parser.add_argument('--workers', type=int, default=None)
    args = parser.parse_args()

    from kf_lib.kung_fu import techniques
    names = list(args.techs)
    if args.all_general:
        names += [t.name for t in techniques.get_upgradable_techs() if t.name not in names]
    if not names:
        parser.error('name some techs or pass --all-general')
    for name in names:  # fail fast on a typo
        if name.startswith('+'):
            if name[1:] not in ('strength', 'agility', 'speed', 'health'):
                parser.error(f'unknown attribute: {name}')
        else:
            techniques.get_tech_obj(name)
    lv_min, lv_max = (int(x) for x in args.levels.split('-'))
    if args.variants:
        path, rest = args.variants.rsplit(':', 1)
        args.variants = f'{Path(path).resolve()}:{rest}'  # workers start in the repo root
    # once here too, so a bad override fails at once instead of crashing every
    # worker on startup (the pool would respawn them forever)
    apply_overrides(args.set, args.scale, args.variants)
    jobs = [(name, args.n, args.seed, lv_min, lv_max) for name in names]
    workers = min(args.workers or os.cpu_count() or 1, len(jobs))
    ctx = multiprocessing.get_context('spawn')
    with ctx.Pool(workers, initializer=apply_overrides,
                  initargs=(args.set, args.scale, args.variants)) as pool:
        results = pool.map(play, jobs)

    rows = []
    for name, wins, played in results:
        p = wins / played
        rows.append((200 * p - 100, 196 * 2 * (p * (1 - p) / played) ** 0.5, name, played))
    rows.sort(reverse=True)
    overrides = ' '.join(args.set + args.scale + ([args.variants] if args.variants else []))
    print(f'\nA/B, lv {args.levels}, n={args.n} per tech, seed {args.seed}'
          + (f', overrides: {overrides}' if overrides else ''))
    for diff, margin, name, played in rows:
        print(f'{name:30s} {diff:+6.1f} +-{margin:.1f}  ({played} fights)')
    if len(rows) > 2:
        print(f'{"median":30s} {statistics.median(r[0] for r in rows):+6.1f}')


if __name__ == '__main__':  # required: worker processes import this module
    main()
