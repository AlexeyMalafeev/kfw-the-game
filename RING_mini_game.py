from kf_lib import fighter_factory
from kf_lib.utilities import *


def main():
    print(' ***Welcome to RING***')
    pak()
    play = True
    attempts = 3
    difficulty = menu([('easy', 0.9), ('normal', 1.0), ('hard', 1.1), ('extreme', 1.2)], "Choose the difficulty:")
    p = fighter_factory.new_custom_hcf()
    while play:
        opp = fighter_factory.from_exp_worth(p.get_exp_worth() * difficulty)
        if p.fight(opp[0], en_allies=opp[1:], hide_stats=difficulty >= 1.0):
            p.level_up()
        else:
            attempts -= 1
            print(' Remaining attempts: {}'.format(attempts))
            pak()
        if attempts == 0:
            break
    print(' You have reached level {}.'.format(p.level))
    print(' ***Game over***')
    pak()


try:
    main()

except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
