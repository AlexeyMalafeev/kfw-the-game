from kf_lib import game
from kf_lib.actors.player import SmartAIP, SmartAIPVisible
from kf_lib.ui._menu import yn

try:
    g = game.Game()
    visible_ai = yn("Do you want to see what AI players do?")
    DefaultAI = SmartAIPVisible if visible_ai else SmartAIP
    g.new_game(forced_aip_class=DefaultAI)
    g.play()

except Exception:  # noqa
    from kf_lib.debug_tools import crash_report
    crash_report(g)  # noqa
