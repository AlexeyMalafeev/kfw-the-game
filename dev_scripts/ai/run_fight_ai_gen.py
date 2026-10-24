"""Train the default fight AI's weights with the genetic algorithm (see docs/dev_scripts.md).

    python run_fight_ai_gen.py                    # the two classic runs, one process
    python run_fight_ai_gen.py --mode vs-default --pop 32 --n1 1000 --nc 250 \\
        --gens 128 --workers 15 --seed 1
    python run_fight_ai_gen.py --eval 0.83,0.008,0.79,0.78,0.91 --workers 15

--eval plays the given weights (prob_atk, prob_move, prob_focus, prob_guard,
prob_catch) against the current DefaultFightAI (or --vs weights) and prints the
win rates and the action shares; --n1/--nc then set its reps (default 10000/2500).
"""
import multiprocessing  # noqa: F401 -- before the chdir: lets spawned workers find this script on Python 3.8
import os
import sys
from pathlib import Path

# this has to be before imports from kf_lib; anchored on __file__ (not '..'), because
# the worker processes re-run this module from the repo root
lib_path = Path(__file__).resolve().parents[2]
os.chdir(lib_path)
if str(lib_path) not in sys.path:
    sys.path.append(str(lib_path))


def parse_params(s):
    params = [float(x) for x in s.split(',')]
    assert len(params) == 5, 'need 5 comma-separated weights'
    return params


def print_eval(res):
    from math import sqrt
    for key in ('1on1', 'crowd'):
        w, l_ = res[key]
        n = w + l_
        p = w / n if n else 0.0
        margin = 1.96 * sqrt(p * (1 - p) / n) if n else 0.0
        print(f'{key:6} wins {w} / losses {l_}: {p * 100:.1f}% +-{margin * 100:.1f}')
    total = sum(res['actions'].values())
    from kf_lib.ai.fight_ai_gen import ACTION_KINDS
    shares = ', '.join(f'{k} {res["actions"][k] / total * 100:.1f}%' for k in ACTION_KINDS)
    per_fight = total / sum(res['1on1']) if sum(res['1on1']) else 0.0
    print(f'1-on-1 actions of the tested AI: {per_fight:.1f} per fight; {shares}')


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--mode', choices=('both', 'infight', 'vs-default'),
                        default='both')
    parser.add_argument('--pop', type=int, default=None)
    parser.add_argument('--n1', type=int, default=None, help='1-on-1 reps')
    parser.add_argument('--nc', type=int, default=None, help='crowd reps')
    parser.add_argument('--gens', type=int, default=128)
    parser.add_argument('--mutation', type=float, default=0.1)
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--eval', type=parse_params, default=None, metavar='W1,...,W5')
    parser.add_argument('--vs', type=parse_params, default=None, metavar='W1,...,W5')
    args = parser.parse_args()

    from kf_lib.ai import fight_ai_gen

    if args.eval:
        res = fight_ai_gen.evaluate(
            args.eval, args.vs,
            n_1on1=10_000 if args.n1 is None else args.n1,
            n_crowd=2_500 if args.nc is None else args.nc,
            seed=args.seed or 0, workers=args.workers,
        )
        print_eval(res)
        return

    # GeneticAlgorithm.output() writes per-generation files to tests/genetic/;
    # the dir is gitignored, so create it here
    Path('tests', 'genetic').mkdir(parents=True, exist_ok=True)

    # (mode, infighting, default pop, 1-on-1 reps, crowd reps)
    runs = [('infight', True, 16, 8, 2), ('vs-default', False, 32, 64, 16)]
    for mode, infighting, pop, n1, nc in runs:
        if args.mode not in ('both', mode):
            continue
        ga = fight_ai_gen.GeneticAlgorithm(
            pop_size=args.pop or pop,
            n_fights_1on1=n1 if args.n1 is None else args.n1,
            n_fights_crowd=nc if args.nc is None else args.nc,
            mutation_prob=args.mutation,
            infighting=infighting,
            workers=args.workers,
            seed=args.seed,
        )
        ga.run(args.gens)


if __name__ == '__main__':  # required: worker processes import this module
    try:
        main()
    except Exception:  # noqa
        import traceback
        traceback.print_exc()
        input('Press Enter to exit')
