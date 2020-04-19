#! python3

from kf_lib import game


g = game.Game()
g.new_game()
import cProfile

try:
    cProfile.run('g.play()', 'profile.txt')

except Exception as e:
    import traceback
    traceback.print_exc()
    traceback.print_exc(file=open('errors.txt', 'w'))
    try:
        g.save_game('emergency_save.txt')
    except:
        input('-FAILED TO SAVE GAME-')
    input('Press Enter to exit')