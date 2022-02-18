#! python3

from kf_lib import game


try:
    n_games = 100
    for i in range(n_games):
        print(i + 1, '/', n_games)
        g = game.Game()
        g.new_game(
            num_players=1,
            coop=False,
            ai_only=True,
            auto_save_on=False,
            forced_aip_class=None,
            silent_ending=True,
        )
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