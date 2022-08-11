import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..', '..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

from kf_lib import game
from kf_lib.testing import testing_tools


try:
    g = game.Game()
    t = testing_tools.Tester(g)
    print('Random actions = False')
    t.test_fight_balance(rand_actions=False, n=20000)


except Exception:  # noqa
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
