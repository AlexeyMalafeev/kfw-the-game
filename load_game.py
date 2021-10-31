from kf_lib import game


try:
    g = game.Game()
    g.load_game('save.txt')
    g.play()

except Exception:
    from kf_lib.debug_tools import crash_report
    crash_report(g)  # noqa
