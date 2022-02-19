from kf_lib import game
from kf_lib.actors.player import SmartAIP, SmartAIPVisible
from kf_lib.ui import yn

try:
    g = game.Game()
    visible_ai = yn("Do you want to see what AI players do?")
    DefaultAI = SmartAIPVisible if visible_ai else SmartAIP
    g.new_game(forced_aip_class=DefaultAI, confirm_styles_with_player=True)
    g.play()

except Exception:  # noqa
    from kf_lib.testing.debug_tools import crash_report
    crash_report(g)  # noqa
