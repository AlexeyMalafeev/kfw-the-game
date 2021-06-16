# from .. import testing_tools
# from ..actors import fighter_factory, names
# from ..actors.player import (
#     HumanPlayer,
#     ALL_AI_PLAYERS,  # used in load/new_game
# )
# from . import game_stats
# from ..kung_fu.moves import BASIC_MOVES
# from ..kung_fu import styles, style_gen, items
# from ..town import events as ev, encounters, story
from ..utils.utilities import *


class DebugMenu:
    current_player = None

    def debug_menu(self):
        cls()
        choice = menu(
            (
                ('Get Money', self.debug_get_money),
                ('Get Item', self.debug_get_item),
                ('Level up', self.debug_level_up),
                ('Learn Move', self.debug_learn_move),
            )
        )
        choice()

    def debug_get_money(self):
        p = self.current_player


    def debug_get_item(self):
        p = self.current_player


    def debug_level_up(self):
        p = self.current_player


    def debug_learn_move(self):
        p = self.current_player






    # p.level_up()
    # p.obtain_item('Dragon Herb')
    # p.obtain_item('Ox Herb')
    # from ..kung_fu.moves import get_rand_moves
    # m1 = get_rand_moves(p, 1, 4)[0]
    # m2 = get_rand_moves(p, 1, 5)[0]
    # m3 = get_rand_moves(p, 1, 7)[0]
    # m4 = get_rand_moves(p, 1, 8)[0]
    # m5 = get_rand_moves(p, 1, 10)[0]
    # for move in m1, m2, m3, m4, m5:
    #     if move:
    #         p.learn_move(move, silent=False)
    # f1 = fighter_factory.new_thug(weak=False)
    # p.fight(f1)
    # p.fight(f1)

    # t = testing_tools.Tester(self)
    # f1 = fighter_factory.new_foreigner(8, style_name='Muai Thai', country='Thailand')
    # f2 = fighter_factory.new_foreigner(8, style_name='Muai Thai', country='Thailand')
    # from kf_lib.fight import spectate
    # spectate(f1, f2)

    # t.test_story(story.ForeignerStory)
    # t.test_enc('Challenger')
    # self.current_player.learn_tech('Attack Is Defense')
    # t.two_players_fight()
    # self.current_player.learn_move("Shove")
    # self.current_player.learn_move("Charging Step")