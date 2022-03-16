import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..', '..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

from kf_lib import game
from kf_lib.testing import testing_tools as tt
from kf_lib.ui import pe


try:
    g = game.Game()
    t = tt.Tester(g)
    t.test_level_vs_crowds(n_fights=100)
    pe()


except Exception:  # noqa
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
