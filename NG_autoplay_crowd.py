from kf_lib import game


try:
    g = game.Game()
    g.new_game(num_players=100, coop=False, ai_only=True, auto_save_on=False)
    g.play()

except Exception:
    from kf_lib.debug_tools import crash_report
    crash_report(g)