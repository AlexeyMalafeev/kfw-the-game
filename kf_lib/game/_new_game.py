import random

from kf_lib.actors import fighter_factory
from kf_lib.actors.player import (
    HumanPlayer,
    ALL_AI_PLAYERS,
)
from kf_lib.happenings import story
from kf_lib.kung_fu import styles
from kf_lib.ui import cls, get_int_from_user, menu, yn
from kf_lib.utils import rndint
from ._base_game import BaseGame


MAX_NUM_PLAYERS = 6
MAX_NUM_STUDENTS = 8


class NewGame(BaseGame):
    # todo reimplement g.MAX_NUM_STUDENTS
    MAX_NUM_STUDENTS = MAX_NUM_STUDENTS

    def _get_new_ai_player(self, klass=None):
        # style = styles.get_rand_std_style()
        style = random.choice(self.style_list)
        if klass is None:
            klass = random.choice(ALL_AI_PLAYERS)
        return klass(name=self.get_new_name(), style=style)

    def _get_new_human_player(self):
        while True:
            cls()
            p = HumanPlayer(name=self.get_new_name())
            print(p.get_f_info())
            if yn('Is this character ok?'):
                break

        max_len = max((len(s.name) for s in self.style_list))
        legend = [
            ('{:<{}} {}'.format(s.name, max_len, s.descr_short), s)
            for s in self.style_list
        ]

        style = menu(legend, 'Choose a style')
        p.set_style(style.name)
        # p.set_moves(None)  # to properly add lv1 style moves
        return p

    # This method is actually used outside this module, so it is not protected
    def get_new_student(self, style_name):
        name = self.get_new_name()
        return fighter_factory.new_student(name, style_name)

    def new_game(
        self,
        num_players=0,
        coop='?',
        ai_only=False,
        auto_save_on='?',
        forced_aip_class=None,
        generated_styles='?',
        confirm_styles_with_player=False,
        silent_ending=False,
    ):
        self.silent_ending = silent_ending
        # options
        if not num_players:
            num_players = get_int_from_user('Number of players?', 1, MAX_NUM_PLAYERS)
        if auto_save_on == '?':
            self.auto_save_on = yn('Auto save?')
        elif auto_save_on in (True, False):
            self.auto_save_on = auto_save_on
        assert generated_styles in {
            '?',
            True,
            False,
        }, 'generated_styles option must be in (True, False, "?")'
        if generated_styles == '?':
            generated_styles = yn('Randomly generated styles?')
        if generated_styles:
            style_list = self.get_new_random_styles()
            max_len = max((len(s.name) for s in style_list))
            if confirm_styles_with_player:
                while True:
                    pretty_styles = [f'{s.name:<{max_len}} {s.descr_short}'
                                     for s in style_list]
                    cls()
                    print('\n'.join(pretty_styles))
                    if yn('Are these styles ok?'):
                        break
                    else:
                        style_list = self.get_new_random_styles()
                        max_len = max((len(s.name) for s in style_list))
            self.style_list = style_list
            # todo styles.py attributes shouldn't be modified from inside Game
            styles.default_styles = self.style_list

        self._init_schools()
        self._init_players(num_players, coop, ai_only, forced_aip_class)
        self._init_stories()
        for p in self.players:
            p.school_rank = (
                    p.get_school().index(p) + 1
            )  # for the subsequent rerank to work properly
        self.rerank_schools()

    def _init_players(self, num_players, coop, ai_only, forced_aip_class):
        coop_mode = False
        if num_players > 1 and coop == '?':
            coop_mode = menu(
                (('Full co-op', 'full'), ('2x2', '2x2'), ('3x3', '3x3'), ('No co-op', 'no')),
                title='Co-op mode?',
            )
        for i in range(num_players):
            if not ai_only and yn(f'Player {i + 1} -- human player?'):
                pp = self._get_new_human_player()
            else:
                pp = self._get_new_ai_player(forced_aip_class)
            # 'bind' player
            self.register_fighter(pp)
            self.players.append(pp)
            pp.game = self
            # 'join' school
            style = pp.style.name
            school = self.schools[style]
            school.append(pp)
        n_players = len(self.players)
        if coop_mode == 'full':
            for p1 in self.players:
                for p2 in self.players:
                    if p1 != p2:
                        p1.add_friend(p2)
        elif (coop_mode == '2x2' and n_players == 4) or (coop_mode == '3x3' and n_players == 6):
            def _lets_be_friends(players):
                for p in players:
                    for p2 in players:
                        if p != p2:
                            p.add_friend(p2)
            half = n_players // 2
            _lets_be_friends(self.players[:half])
            _lets_be_friends(self.players[half:])

    def _init_schools(self):
        for style in self.style_list:
            m = fighter_factory.new_master(self.get_new_name('Master'), style.name)
            self.register_fighter(m)
            self.masters[style.name] = m

            school = []
            self.schools[style.name] = school
            num_students = rndint(6, MAX_NUM_STUDENTS)
            for i in range(num_students):
                new_student = self.get_new_student(style.name)
                school.append(new_student)
                self.register_fighter(new_student)
            # print(school)

    def _init_stories(self):
        self.stories = {
            f'{story_cls.__name__}': story_cls(self) for story_cls in story.get_all_stories()
        }
