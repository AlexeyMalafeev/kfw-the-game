from kf_lib import game
from kf_lib.testing import testing_tools

try:
    g = game.Game()
    t = testing_tools.Tester(g)
    print('Random actions = False')
    t.test_fight_balance(rand_actions=False, n=5000)


except Exception:  # noqa
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
