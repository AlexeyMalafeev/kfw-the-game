from kf_lib import game
from kf_lib.testing import testing_tools as tt
from kf_lib.ui._interactive import pe

try:
    g = game.Game()
    t = tt.Tester(g)
    t.test_level_vs_crowds(n_fights=100)
    pe()


except Exception:  # noqa
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')