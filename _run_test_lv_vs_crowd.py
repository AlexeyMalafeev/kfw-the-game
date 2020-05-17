#! python3

from kf_lib.events import Tournament2 as Tnt
from kf_lib import game
# from kf_lib import styles
# from kf_lib import testing_tools
# from kf_lib import fighter
from kf_lib import fighter_factory as ff
from kf_lib import testing_tools as tt
from kf_lib.utilities import *

try:
    g = game.Game()
    t = tt.Tester(g)
    t.test_level_vs_crowds(n_fights=100)
    pe()


except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')