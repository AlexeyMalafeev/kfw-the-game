import pprint

from kf_lib.actors import fighter_factory
from kf_lib.happenings import tournament
from kf_lib.kung_fu import techniques
from kf_lib.kung_fu.moves import resolve_move_string
from kf_lib.happenings.story import get_all_stories
from kf_lib.things import items
from kf_lib.ui import cls, get_int_from_user, get_str_from_user, menu, pak


class DebugMenu:
    def __init__(self, game_obj):
        self.g = game_obj

    def __call__(self):
        cls()
        choice = menu(
            (
                ('Get Money', self.debug_get_money),
                ('Get Item', self.debug_get_item),
                ('Level up', self.debug_level_up),
                ('Learn Move', self.debug_learn_move),
                ('Learn Tech', self.debug_learn_tech),
                ('Fight Thug(s)', self.debug_fight_thugs),
                ('Tournament', self.debug_tournament),
                ('Story', self.debug_story),
                ('Inspect Player', self.debug_inspect_player),
                ('Set Attribute', self.debug_set_att),
                ('PvP', self.debug_pvp),
            )
        )
        choice()

    def debug_fight_thugs(self):
        p = self.g.current_player
        n = get_int_from_user('How many thugs?', 1, 20)
        thugs = fighter_factory.new_thug(n=n)
        if n == 1:
            p.fight(thugs)
        else:
            p.fight(thugs[0], en_allies=thugs[1:])

    def debug_get_item(self):
        p = self.g.current_player
        item = menu(sorted(items.all_items, key=str.lower) + items.MOCK_ITEMS, title='Which item?')
        quantity = get_int_from_user(f'How many {item}s?', 1, 1000000000)
        p.obtain_item(item, quantity)

    def debug_get_money(self):
        p = self.g.current_player
        amount = get_int_from_user('How much money?', 1, 1000000000)
        p.earn_money(amount)

    def debug_inspect_player(self):
        p = self.g.current_player
        att = get_str_from_user('Input att (type "all" to see all atts)')
        if att == 'all':
            pprint.pprint(vars(p))
        else:
            if not hasattr(p, att):
                print('No such attribute!')
            else:
                val = getattr(p, att)
                pprint.pprint(val)
                print(type(val))
        pak()

    def debug_learn_move(self):
        p = self.g.current_player
        move_s = get_str_from_user('Enter move string (move name / tier / features, etc.):')
        resolve_move_string(move_s, p)

    def debug_learn_tech(self):
        p = self.g.current_player
        tech = menu(sorted(techniques.get_all_techs()), title='Choose a tech:')
        p.learn_tech(tech)

    def debug_level_up(self):
        p = self.g.current_player
        n = get_int_from_user('How many levels up?', 1, 100)
        p.level_up(n)

    def debug_pvp(self):
        p = self.g.current_player
        opp = menu([pp for pp in self.g.players if not (pp is p)])
        p.spar(opp)

    def debug_set_att(self):
        p = self.g.current_player
        att = get_str_from_user('Enter attribute:')
        if not hasattr(p, att):
            print('No such attribute!')
            pak()
        else:
            val = input('Enter value:\n > ')
            setattr(p, att, eval(val))

    def debug_story(self):
        story_class = menu(
            [(story_cls.__name__, story_cls) for story_cls in get_all_stories()],
            title="Choose a story",
        )
        story_obj = story_class(self.g)
        story_obj.start(self.g.current_player)
        while story_obj.state != -1:
            story_obj.advance()

    def debug_tournament(self):
        n = get_int_from_user('How many participants?', 2, 20)
        fee = get_int_from_user('Fee?', 0, 10000)
        min_lv = get_int_from_user('Min level?', 1, 20)
        max_lv = get_int_from_user('Max level?', min_lv, 20)
        tournament.Tournament(
            game=self.g,
            num_participants=n,
            fee=fee,
            min_lv=min_lv,
            max_lv=max_lv,
        )

    # t = testing_tools.Tester(self)
    # f1 = fighter_factory.new_foreigner(8, style='Muai Thai', country='Thailand')
    # f2 = fighter_factory.new_foreigner(8, style='Muai Thai', country='Thailand')
    # from kf_lib.fight import spectate
    # spectate(f1, f2)

    # t.test_story(story.ForeignerStory)
    # t.test_enc('Challenger')
    # self.current_player.learn_tech('Attack Is Defense')
    # t.two_players_fight()
    # self.current_player.learn_move("Shove")
    # self.current_player.learn_move("Charging Step")
