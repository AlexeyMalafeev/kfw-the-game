"""Fight-balance harness: 100k seeded mirror matches (see docs/dev_scripts.md).

    python run_test_fb.py                     # the tracked report in tests/
    python run_test_fb.py -n 20000            # a quicker, noisier run
    python run_test_fb.py --variants rule_variants.py:Gc+Hb25 --out /tmp/gc_hb25.txt

--variants FILE:NAMES applies rule experiments (FILE's apply(NAMES)) in every
worker; give such runs an --out path, so they don't land in the tracked tests/.
"""
import multiprocessing  # noqa: F401 -- before the chdir: lets spawned workers find this script on Python 3.8
import os
import sys
from pathlib import Path

ORIG_CWD = os.getcwd()  # for the user's relative paths
# this has to be before imports from kf_lib; anchored on __file__ (not '..'), because
# the harness's worker processes re-run this module from the repo root
lib_path = Path(__file__).resolve().parents[2]
os.chdir(lib_path)
if str(lib_path) not in sys.path:
    sys.path.append(str(lib_path))


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('-n', type=int, default=100_000)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--variants', default='', metavar='FILE:NAMES')
    parser.add_argument('--out', default=None, help='report path (default: tests/)')
    args = parser.parse_args()
    variants = args.variants
    if variants:
        path, names = variants.rsplit(':', 1)
        variants = f'{Path(ORIG_CWD, path).resolve()}:{names}'
    out = str(Path(ORIG_CWD, args.out).resolve()) if args.out else None

    from kf_lib import game
    from kf_lib.testing import testing_tools

    g = game.Game()
    t = testing_tools.Tester(g)
    print('Random actions = False')
    t.test_fight_balance(rand_actions=False, n=args.n, seed=args.seed,
                         variants=variants, out_path=out)


if __name__ == '__main__':  # required: worker processes import this module
    try:
        main()
    except Exception:  # noqa
        import traceback
        traceback.print_exc()
        sys.exit(1)
