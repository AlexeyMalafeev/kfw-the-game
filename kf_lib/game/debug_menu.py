from ..actors import fighter_factory
from ..things import items
from ..utils.utilities import *


class DebugMenu:
    def __init__(self, game_obj):
        self.current_player = game_obj.current_player

    def __call__(self):
        cls()
        choice = menu(
            (
                ('Get Money', self.debug_get_money),
                ('Get Item', self.debug_get_item),
                ('Level up', self.debug_level_up),
                ('Learn Move', self.debug_learn_move),
                ('Fight Thug(s)', self.debug_fight_thugs),
            )
        )
        choice()

    def debug_fight_thugs(self):
        p = self.current_player
        n = get_int_from_user('How many thugs?', 1, 20)
        thugs = fighter_factory.new_thug(n=n)
        if n == 1:
            p.fight(thugs)
        else:
            p.fight(thugs[0], en_allies=thugs[1:])

    def debug_get_item(self):
        p = self.current_player
        item = menu(sorted(items.all_items, key=str.lower) + items.MOCK_ITEMS, title='Which item?')
        quantity = get_int_from_user(f'How many {item}s?', 1, 1000000000)
        p.obtain_item(item, quantity)

    def debug_get_money(self):
        p = self.current_player
        amount = get_int_from_user('How much money?', 1, 1000000000)
        p.earn_money(amount)

    def debug_learn_move(self):
        p = self.current_player
        move_name = input('Enter move name or tier: ')
        if move_name.isdigit() and 1 <= (move_tier := int(move_name)) <= 10:
            p.learn_random_move(move_tier)
        else:
            p.learn_move(move_name)

    def debug_level_up(self):
        p = self.current_player
        n = get_int_from_user('How many levels up?', 1, 100)
        p.level_up(n)

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