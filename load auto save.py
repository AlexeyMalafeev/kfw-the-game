#! python3

from kf_lib import game

try:
    g = game.Game()
    g.load_game('auto save.txt')
    g.play()

except Exception:
    import traceback, time
    print(time.ctime(), file=open('errors.txt', 'w'))
    traceback.print_exc()
    traceback.print_exc(file=open('errors.txt', 'a'))
    try:
        g.save_game('emergency_save.txt')
    except:
        input('-FAILED TO SAVE GAME-')
    input('Press Enter to exit')