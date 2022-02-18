from kf_lib.actors import fighter_factory
from kf_lib.ui import menu, pak


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
            print(f' Remaining attempts: {attempts}')
            pak()
        if attempts == 0:
            break
    print(f' You have reached level {p.level}.')
    print(' ***Game over***')
    pak()


try:
    main()

except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
