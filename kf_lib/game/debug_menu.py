import ast
import pprint

from kf_lib.actors import fighter_factory
from kf_lib.happenings.encounters import all_random_encounter_classes
from kf_lib.happenings import tournament
from kf_lib.kung_fu import techniques
from kf_lib.kung_fu.moves import ALL_MOVES_DICT, resolve_move_string
from kf_lib.happenings.story import get_all_stories
from kf_lib.i18n import _, ngettext, tr_name
from kf_lib.things import items
from kf_lib.ui import cls, get_int_from_user, get_str_from_user, menu, pak


class DebugMenu:
    def __init__(self, game_obj):
        self.g = game_obj

    def __call__(self):
        cls()
        choice = menu(
            (
                (_('Get Money'), self.debug_get_money),
                (_('Get Item'), self.debug_get_item),
                (_('Level up'), self.debug_level_up),
                (_('Learn Move'), self.debug_learn_move),
                (_('Learn Tech'), self.debug_learn_tech),
                (_('Fight Thug(s)'), self.debug_fight_thugs),
                (_('Tournament'), self.debug_tournament),
                (_('Encounter'), self.debug_encounter),
                (_('Story'), self.debug_story),
                (_('Inspect Player'), self.debug_inspect_player),
                (_('Set Attribute'), self.debug_set_att),
                (_('Spar'), self.debug_spar),
                (_('Back'), None),
            )
        )
        if choice is not None:
            choice()

    def debug_encounter(self):
        enc_class = menu(
            [(enc_cls.__name__, enc_cls) for enc_cls in all_random_encounter_classes],
            title=_('Choose an encounter'),
            back=True,
        )
        if enc_class is None:
            return
        enc_class(self.g.current_player, check_if_happens=False)

    def debug_fight_thugs(self):
        p = self.g.current_player
        n = get_int_from_user(_('How many thugs?'), 1, 20, can_cancel=True)
        if n is None:
            return
        thugs = fighter_factory.new_thug(n=n)
        if n == 1:
            p.fight(thugs)
        else:
            p.fight(thugs[0], en_allies=thugs[1:])

    def debug_get_item(self):
        p = self.g.current_player
        item = menu(
            [(tr_name(it), it) for it in sorted(items.all_items, key=str.lower)]
            + [(tr_name(it), it) for it in items.MOCK_ITEMS],
            title=_('Which item?'),
            back=True,
        )
        if item is None:
            return
        quantity = get_int_from_user(
            ngettext('How many {item}?', 'How many {item}s?', 2).format(
                item=tr_name(item)
            ),
            1,
            1000000000,
            can_cancel=True,
        )
        if quantity is None:
            return
        p.obtain_item(item, quantity)

    def debug_get_money(self):
        p = self.g.current_player
        amount = get_int_from_user(_('How much money?'), 1, 1000000000, can_cancel=True)
        if amount is None:
            return
        p.earn_money(amount)

    def debug_inspect_player(self):
        p = self.g.current_player
        att = get_str_from_user(_('Input att (type "all" to see all atts)'))
        if att == 'all':
            pprint.pprint(vars(p))
        else:
            if not hasattr(p, att):
                print(_('No such attribute!'))
            else:
                val = getattr(p, att)
                pprint.pprint(val)
                print(type(val))
        pak()

    def debug_learn_move(self):
        p = self.g.current_player
        move_s = get_str_from_user(_('Enter move string (move name / tier / features, etc.):'))
        if move_s and not move_s.isdigit() and ',' not in move_s and move_s not in ALL_MOVES_DICT:
            print(_('No such move: {!r}').format(move_s))
            pak()
            return
        resolve_move_string(move_s, p)

    def debug_learn_tech(self):
        p = self.g.current_player
        tech_name = menu(sorted(techniques.get_all_techs_dict()), title=_('Choose a tech:'), back=True)
        if tech_name is None:
            return
        tech = techniques.get_tech_obj(tech_name)
        p.learn_tech(tech)

    def debug_level_up(self):
        p = self.g.current_player
        n = get_int_from_user(_('How many levels up?'), 1, 100, can_cancel=True)
        if n is None:
            return
        p.level_up(n)

    def debug_spar(self):
        p = self.g.current_player
        opp = menu([pp for pp in self.g.players if not (pp is p)], back=True)
        if opp is None:
            return
        p.spar(opp)

    def debug_set_att(self):
        p = self.g.current_player
        att = get_str_from_user(_('Enter attribute:'))
        if not hasattr(p, att):
            print(_('No such attribute!'))
            pak()
            return
        if callable(getattr(p, att)):
            print(_('{!r} is a method, not overwriting it!').format(att))
            pak()
            return
        val = input(_('Enter value:\n > '))
        try:
            val = ast.literal_eval(val)
        except (ValueError, SyntaxError):
            print(_('Cannot parse {!r} as a Python literal, not setting anything!').format(val))
            pak()
            return
        setattr(p, att, val)

    def debug_story(self):
        story_class = menu(
            [(story_cls.__name__, story_cls) for story_cls in get_all_stories()],
            title=_('Choose a story'),
            back=True,
        )
        if story_class is None:
            return
        story_obj = self.g.stories[story_class.__name__]
        if not story_obj.check_hasnt_started():
            print(_('{name} has already started!').format(name=story_obj.name))
            pak()
            return
        p = self.g.current_player
        try:
            story_obj.start(p)
            while story_obj.state != -1:
                story_obj.advance()
        except Exception:
            # detach the player and reset the story so that the save stays consistent
            p.current_story = None
            story_obj.player = None
            if story_obj.boss:
                story_obj.delete_boss()
            story_obj.state = None
            raise

    def debug_tournament(self):
        n = get_int_from_user(_('How many participants?'), 2, 20, can_cancel=True)
        if n is None:
            return
        fee = get_int_from_user(_('Fee?'), 0, 10000, can_cancel=True)
        if fee is None:
            return
        min_lv = get_int_from_user(_('Min level?'), 1, 20, can_cancel=True)
        if min_lv is None:
            return
        max_lv = get_int_from_user(_('Max level?'), min_lv, 20, can_cancel=True)
        if max_lv is None:
            return
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
