def crash_report(game_inst):
    import traceback, time, pprint
    print(time.ctime(), file=open('errors.txt', 'w'))
    traceback.print_exc()
    traceback.print_exc(file=open('errors.txt', 'a'))
    print(time.ctime(), file=open('debug.txt', 'w'))
    pprint.pprint(vars(game_inst), stream=open('debug.txt', 'a'))
    print('debugging info saved to "debug.txt"')
    try:
        game_inst.save_game('emergency_save.txt')
    except:
        input('-FAILED TO SAVE GAME-')
    input('Press Enter to exit')
