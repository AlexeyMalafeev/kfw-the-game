import multiprocessing  # noqa: F401 -- before the chdir: lets spawned workers find this script on Python 3.8
import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib; anchored on __file__ (not '..'), because
# the harness's worker processes re-run this module from the repo root
lib_path = Path(__file__).resolve().parents[2]
os.chdir(lib_path)
if str(lib_path) not in sys.path:
    sys.path.append(str(lib_path))


def main():
    from kf_lib import game
    from kf_lib.testing import testing_tools

    g = game.Game()
    t = testing_tools.Tester(g)
    print('Random actions = False')
    t.test_fight_balance(rand_actions=False, n=100_000)


if __name__ == '__main__':  # required: worker processes import this module
    try:
        main()
    except Exception:  # noqa
        import traceback
        traceback.print_exc()
        input('Press Enter to exit')
