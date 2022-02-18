from kf_lib import game


try:
    g = game.Game()
    g.new_game(
        num_players=4,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=True,
        silent_ending=True,
    )
    g.play()


except Exception:  # noqa
    from kf_lib.testing.debug_tools import crash_report
    crash_report(g)  # noqa
