#! python3

from kf_lib import game


try:
    g = game.Game()
    g.new_game(num_players=4, coop=False, ai_only=True, auto_save_on=True)
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