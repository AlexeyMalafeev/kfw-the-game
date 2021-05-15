#! python3

from kf_lib import game


try:
    days_dict = {game.BaselineAIP:0, game.SmartAIP:0, game.LazyAIP:0, game.VanillaAIP:0}
    results = {ai_class:0 for ai_class in days_dict}
    n_games = 100
    for ai_class in days_dict:
        for i in range(n_games):
            print(ai_class, i + 1, '/', n_games)
            g = game.Game()
            g.new_game(num_players=1, coop=False, ai_only=True, auto_save_on=False, forced_aip_class=ai_class,
                       output_stats=False, write_win_data=False)
            g.play()
            days_dict[ai_class] += g.n_days_to_win
        results[ai_class] = days_dict[ai_class] / n_games
    print(results)
    with open('AI players comparison.txt', 'w') as f:
        lines = [f'{ai_class}: {av_days}' for ai_class, av_days in results.items()]
        f.write('\n'.join(lines))
    input('Press Enter to exit')


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