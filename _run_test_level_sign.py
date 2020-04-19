#! python3

from kf_lib import game
from kf_lib import testing_tools

try:
    g = game.Game()
    t = testing_tools.Tester(g)
    print('Testing level significance')
    t.test_level_significance(rep=100)
    input('Press Enter to exit')


except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')