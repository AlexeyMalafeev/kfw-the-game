import pprint
import time
import traceback


def crash_report(game_inst):
    now = time.ctime()
    traceback.print_exc()
    with open('errors.txt', 'a') as f:
        print(f'\n\n{now}\n', file=f)
        traceback.print_exc(file=f)
    with open('debug.txt', 'a') as f:
        print(f'\n\n{now}\n', file=f)
        if game_inst is not None:
            pprint.pprint(vars(game_inst), stream=f)
    print('debugging info saved to "debug.txt"')
    if game_inst is not None:
        try:
            game_inst.save_game('emergency_save.txt')
        except:  # noqa
            input('-FAILED TO SAVE GAME-')
    input('Press Enter to exit')
