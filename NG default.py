#! python3

from kf_lib import game
from kf_lib.player import SmartAIP, SmartAIPVisible
from kf_lib.utilities import yn


try:
    g = game.Game()
    visible_ai = yn("Do you want to see what AI players do?")
    DefaultAI = SmartAIPVisible if visible_ai else SmartAIP
    g.new_game(forced_aip_class=DefaultAI)
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