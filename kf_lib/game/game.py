"""
To play:

g = Game()
g.new_game() OR g.load_game('save.txt')
g.play()

"""

from .. import testing_tools  # noqa
from ..actors import fighter_factory, names
from ..actors.player import (
    HumanPlayer,
    ALL_AI_PLAYERS,  # used in load/new_game
)
from .debug_menu import DebugMenu
from . import game_stats
from ..kung_fu.moves import BASIC_MOVES
from ..kung_fu import styles, style_gen
from ..things import items
from ..happenings import events as ev, encounters, story
from ..utils.utilities import *


# todo refactor game.py into submodules


# constants
# AI_NAMES = {LazyAIP: 'Lazy AI', SmartAIP: 'Smart AI', VanillaAIP: 'Vanilla AI',
# BaselineAIP: 'Baseline AI'}
CH_STUDENT_LV_UP = 0.1
MAX_NUM_PLAYERS = 6
MAX_NUM_STUDENTS = 8
MAX_STUDENT_LEVEL = 8
NUM_CONVICTS = 5
SAVE_FOLDER = 'save'
TOWN_STAT_VALUES = [0.05, 0.1, 0.15, 0.2]
WALK_EXTRA_ENC = 2

# victory conditions
GRANDMASTER_LV = 20
FOLK_HERO_REP = 200
KFLEGEND_ACCOMPL = 8
GT_FIGHTER_FIGHTS = (100, 150)  # fights_won, num_kos


class Game:
    MAX_NUM_STUDENTS = MAX_NUM_STUDENTS

    def __init__(self):
        # players
        self.players = []
        self.current_player = None
        self.spectator = None
        # NPCs
        self.used_names = set()
        self.masters = {}
        self.schools = {}
        self.fighters_list = []  # need both list and dict
        self.fighters_dict = {}
        # special NPCs
        self.beggar = fighter_factory.new_beggar()
        self.beggar.name = self.get_new_name(prefix='Beggar')
        self.register_fighter(self.beggar)
        self.criminals = [fighter_factory.new_convict() for _ in range(NUM_CONVICTS)]
        for c in self.criminals:
            c.name = self.get_new_name(prefix=random.choice(names.ROBBER_NICKNAMES))
            self.register_fighter(c)
        self.drunkard = fighter_factory.new_drunkard(strong=True)
        self.drunkard.name = self.get_new_name(prefix='Drunkard')
        self.register_fighter(self.drunkard)
        self.thief = fighter_factory.new_thief(tough=True)
        self.thief.name = self.get_new_name(prefix='Thief')
        self.register_fighter(self.thief)
        self.fat_girl = fighter_factory.new_fat_girl()
        self.register_fighter(self.fat_girl)
        # misc
        self.auto_save_on = '?'
        self.style_list = styles.default_styles
        self.stories = {}
        self.day = 1
        self.month = 1
        self.year = 1
        self.town_name = 'Foshan'
        self.poverty = random.choice(TOWN_STAT_VALUES)
        self.crime = random.choice(TOWN_STAT_VALUES)
        self.kung_fu = random.choice(
            TOWN_STAT_VALUES
        )  # todo g.kung_fu is used only for tournaments
        self.fights_total = 0
        self.chosen_quit = False
        self.chosen_load = False
        self.output_stats = True
        self.write_win_data = False
        self.n_days_to_win = 'n/a'
        self.play_indefinitely = False

        self.enc_count_dict = {}  # counter for how many times encounters happened
        for e in encounters.ENC_LIST:
            self.enc_count_dict[e.__name__] = 0
        self.enc = encounters.EncControl(self)
        self.debug_menu = DebugMenu(self)

        self.savable_atts = '''town_name poverty crime kung_fu day month year auto_save_on 
        play_indefinitely fights_total enc_count_dict'''.split()

    @staticmethod
    def check_inactive_player(p):
        def skip_day():
            p.change_stat('days_inactive', 1)
            p.inactive -= 1

        if p.inactive:
            p.show(p.get_inact_info())
            if p.check_item(items.MEDICINE) and p.check_injured():
                if p.use_med_or_not():
                    p.use_med()
                    # self.pak()
                    p.cls()
                    p.see_day_info()
                    return False
                else:
                    skip_day()
                    return True  # to skip turn
            else:
                skip_day()
                p.pak()
                return True  # to skip turn
        else:
            p.inact_status = ''
            return False

    def check_victory(self):
        if self.play_indefinitely:
            return False
        wins = []
        winners = []
        victory_types = []
        for p in self.players:
            # victory conditions
            vc = {
                'Grandmaster': p.check_lv(GRANDMASTER_LV),
                'Folk Hero': p.reputation >= FOLK_HERO_REP,
                'Kung-fu Legend': len(p.accompl) >= KFLEGEND_ACCOMPL,
                'Greatest Fighter': (
                    p.get_stat('fights_won') >= GT_FIGHTER_FIGHTS[0]
                    and p.get_stat('num_kos') >= GT_FIGHTER_FIGHTS[1]
                ),
            }
            for k in vc:
                if vc[k]:
                    wins.append(f'{p.name} becomes {k}!')
                    winners.append(p)
                    victory_types.append(k)
        if wins:
            if self.output_stats:
                print('\n'.join(wins))
                input('Press Enter to see stats.')
                self.save_game('game over.txt')
                from . import game_stats

                sg = game_stats.StatGen(self)
                stats = sg.get_full_report_string()
                print(stats)
                print(stats, file=open(os.path.join(SAVE_FOLDER, 'stats.txt'), 'w'))
                self.play_indefinitely = yn('Keep playing indefinitely?')
                # input('Press Enter to exit game.')
                # self.quit()
            days, months, years = [int(x) for x in self.get_date().split('/')]
            n_days = (years - 1) * 360 + months * 30 + days
            if self.write_win_data:
                with open('win_data.tab', 'a') as f:
                    for i, p in enumerate(winners):
                        data = '\t'.join(
                            str(x)
                            for x in (
                                p.__class__.__name__,
                                p.style.name,
                                p.level,
                                p.get_base_atts_tup(),
                                p.techs,
                                p.traits,
                                self.crime,
                                self.poverty,
                                self.kung_fu,
                                victory_types[i],
                                n_days,
                            )
                        )
                        f.write(f'\n{data}')
                        print(data)
            self.n_days_to_win = n_days
            return True

    def cls(self):
        if self.spectator:
            cls()

    def collect_used_names(self):
        self.used_names = set(self.fighters_dict)

    def do_daily(self):
        """This is guaranteed to execute only once per day"""
        self.cls()
        for p in self.players:
            p.log_new_day()
            if not p.inactive:
                p.practice_home(suppress_log=True)

    def do_monthly(self):
        """This is guaranteed to execute only once per month"""
        # increase crime
        ev.crime_up(self)
        # add new escaped convict
        self.criminals.append(fighter_factory.new_convict())
        c = self.criminals[-1]
        c.name = self.get_new_name(prefix=random.choice(names.ROBBER_NICKNAMES))
        self.register_fighter(c)
        # chance for school students to level up
        for school in self.schools.values():
            for student in school:
                if not student.is_player:
                    if rnd() <= CH_STUDENT_LV_UP and student.level < MAX_STUDENT_LEVEL:
                        student.level_up()
        self.rerank_schools()
        # for p in self.players:
        #     p.refresh_school_rank()

    def game_loop(self):
        self.chosen_quit = False
        self.chosen_load = False
        while True:
            for p in self.players:
                if p.ended_turn:
                    continue
                self.current_player = p
                while True:
                    # output info if human player
                    p.see_day_info()
                    # inactivity check
                    if self.check_inactive_player(p):
                        choice = p.rest
                        break

                    # make a decision about what to do
                    choice = p.choose_day_action()

                    # do it
                    brk = choice()

                    # break out of loop if actually did something
                    if brk:
                        break

                    # check for load_game or quit
                    if self.chosen_load:
                        return True
                    elif self.chosen_quit:
                        return False

                # enc chance
                if choice not in (p.rest,):
                    self.enc.rand_enc()
                # extra enc chance for walks
                if choice == p.go_walk:
                    for i in range(WALK_EXTRA_ENC):
                        self.enc.rand_enc()

                # end turn
                p.end_turn()
                p.ended_turn = True

            if self.check_victory():
                return
            self.next_day()

    def get_act_players(self):
        return [p for p in self.players if not p.inactive]

    def get_date(self):
        return f'{self.day}/{self.month}/{self.year}'

    @staticmethod
    def get_fighter_ref(fighter):
        return f'g.fighters_dict[{fighter.name!r}]'

    def get_new_ai_player(self, klass=None):
        style = styles.get_rand_std_style()
        if klass is None:
            klass = random.choice(ALL_AI_PLAYERS)
        return klass(name=self.get_new_name(), style_name=style.name)

    def get_new_human_player(self):
        while True:
            cls()
            p = HumanPlayer(name=self.get_new_name())
            print(p.get_f_info())
            if yn('Is this character ok?'):
                break

        legend = [
            ('{:<{}} {}'.format(s.name, styles.MAX_LEN_STYLE_NAME, s.descr_short), s)
            for s in self.style_list
        ]

        style = menu(legend, 'Choose a style')
        p.set_style(style.name)
        p.set_moves(None)  # to properly add lv1 style moves
        return p

    def get_new_name(self, prefix=''):
        while True:
            for i in range(1000):
                sur = random.choice(names.SURNAME_PARTS)
                if not prefix:
                    nf = rndint(1, 2)
                    fir = ''.join(random.sample(names.FIRST_NAME_PARTS, nf))
                    name = f'{sur} {fir}'.title()
                else:
                    name = f'{prefix} {sur}'.title()
                if name not in self.used_names:
                    return name
            print('1000 names failed')
            print(prefix)

    def get_new_student(self, style_name):
        name = self.get_new_name()
        lv = rndint(1, 7)
        return fighter_factory.new_student(name, style_name, lv)

    def hook_up_players(self):
        for p in self.players:
            p.game = self
            p.refresh_school_rank()

    # noinspection PyUnresolvedReferences
    def load_game(self, file_name):
        """Read and execute the save file."""
        # todo reimplement game loading to avoid using exec
        # do not delete the below line; needed for loading
        g = self  # noqa
        with open(os.path.join(SAVE_FOLDER, file_name), 'r') as f:
            from ..actors.fighter import (
                Fighter,
                Challenger,
                Master,
                Thug,
            )  # this is used for loading, do not delete
            from ..actors.player import (
                LazyAIP,
                SmartAIP,
                VanillaAIP,
                BaselineAIP,
            )  # this is used for loading, do not delete

            for line in f:
                # print(line)
                exec(line)
        # loading clears logs
        # (do not use 'p' as variable here as it breaks exec code)
        for player in self.players:
            player.plog = []
            # initialize player statistics that aren't in the save file
            for sname, sval in game_stats.DEFAULT_STATS:
                if sname not in player.stats_dict:
                    player.stats_dict[sname] = sval

    def msg(self, text, align=True):
        if self.spectator:
            self.spectator.show(text, align=align)
            self.spectator.pak()

    def new_game(
        self,
        num_players=0,
        coop='?',
        ai_only=False,
        auto_save_on='?',
        forced_aip_class=None,
        output_stats=True,
        write_win_data=False,
        generated_styles='?',
    ):
        """Initialize a new game."""
        self.output_stats = output_stats
        self.write_win_data = write_win_data
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
            self.style_list = style_gen.generate_new_styles(10)  # todo this is a magic number
            styles.default_styles = self.style_list  # todo boy is this ugly
            styles.MAX_LEN_STYLE_NAME = max(
                (len(s.name) for s in styles.default_styles)
            )  # todo oh wow...

        def _init_players():
            coop_mode = False
            if num_players > 1 and coop == '?':
                coop_mode = menu(
                    (('Full co-op', 'full'), ('2x2', '2x2'), ('3x3', '3x3'), ('No co-op', 'no')),
                    title='Co-op mode?',
                )
            for i in range(num_players):
                if not ai_only and yn(f'Player {i + 1} -- human player?'):
                    pp = self.get_new_human_player()
                else:
                    if forced_aip_class is None:
                        pp = self.get_new_ai_player()
                    else:
                        pp = self.get_new_ai_player(forced_aip_class)
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

        def _init_schools():
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

        def _init_stories():
            self.stories = {f'{S.__name__}': S(self) for S in story.all_stories}

        _init_schools()
        _init_players()
        _init_stories()
        for p in self.players:
            p.school_rank = (
                p.get_school().index(p) + 1
            )  # for the subsequent rerank to work properly
        self.rerank_schools()
        self.save_game('test save.txt')

    def next_day(self):
        s = self
        s.day += 1
        s.do_daily()
        if s.day == 31:
            s.month += 1
            s.day = 1
            s.do_monthly()
            if s.month == 13:
                s.year += 1
                s.month = 1
        for p in self.players:
            p.ended_turn = False
        ev.randevent(self)
        if self.auto_save_on:
            self.save_game('auto save.txt')

    def pak(self):
        if self.spectator:
            self.spectator.pak()

    def play(self):
        """Play the (previously initialized or loaded) game."""
        self.prepare_for_playing()
        play = True
        while play:
            play = self.game_loop()
        else:
            if self.play_indefinitely and not self.chosen_quit:
                self.play()

    def prepare_for_playing(self):
        """Prepare for playing a new or previously saved game."""
        for p in self.players:
            if p.is_human:
                self.spectator = p
                break
        # the default for self.spectator is None (in __init__)
        self.hook_up_players()
        self.collect_used_names()

    @staticmethod
    def quit():
        import sys

        sys.exit()

    def refresh_roster(self):
        """Only for fighter ordering when saving"""
        bosses = []
        for s in self.stories.values():
            if s.boss:
                bosses.append(s.boss)
        students = [s for school in self.schools.values() for s in school if not s.is_player]
        special_npcs = [
            f for f in (self.beggar, self.drunkard, self.thief, self.fat_girl) if f is not None
        ]
        self.fighters_list = (
            self.players
            + list(self.masters.values())
            + bosses
            + students
            + special_npcs
            + self.criminals
            + [en for p in self.players for en in p.enemies]
        )
        for p in self.players:
            for fr in p.friends:
                if fr not in self.fighters_list:
                    self.fighters_list.append(fr)
        self.fighters_dict = {f.name: f for f in self.fighters_list}

    def register_fighter(self, f):
        if f.name in self.fighters_dict:
            raise Exception(
                f'Cannot register {f} because a fighter with this name is already registered.')
        self.fighters_list.append(f)
        self.fighters_dict[f.name] = f
        self.used_names.add(f.name)

    def rerank_schools(self):
        for school in self.schools.values():
            school.sort(key=lambda s: -s.get_exp_worth())
            for p in self.players:
                if p in school:
                    new_rank = school.index(p) + 1
                    if p.school_rank != new_rank:
                        p.msg(f'{p.name} is now number {new_rank} at his school.')
                        p.school_rank = new_rank

    def show(self, text, align=True):
        if self.spectator:
            self.spectator.show(text, align)

    def show_stats(self):
        sg = game_stats.StatGen(self)
        stats = sg.get_full_report_string()
        cls()
        print(stats)
        print(stats, file=open(os.path.join(SAVE_FOLDER, 'stats.txt'), 'w'))
        pak()

    def save_game(self, file_name):
        def _save_all():
            _save_fighters()
            _save_masters()
            _save_schools()
            _save_special_npcs()
            _save_stories()
            _save_game_atts()
            _save_players()

        def _save_fighters():
            self.refresh_roster()  # this is only to order the fighters
            f.write('g.fighters_dict = fsd = {}')
            for ftr in self.fighters_list:
                f.write(f'\n\nfsd[{ftr.name!r}] = {ftr.get_init_string()}')
            f.write('\n\ng.fighters_list = list(fsd.values())')

        def _save_game_atts():
            f.write('\n')
            for att in self.savable_atts:
                f.write('\ng.{} = {!r}'.format(att, getattr(self, att)))

        def _save_masters():
            f.write('\n\ng.masters = md = {}')
            for sn in sorted(self.masters):
                m = self.masters[sn]
                f.write(f'\nmd[{sn!r}] = {self.get_fighter_ref(m)}')

        def _save_players():
            f.write('\n\ng.players = []')
            for p in self.players:
                f.write('\n\n' + '#' * 80)
                f.write(f'\n\ng.players.append({self.get_fighter_ref(p)})\n')
                f.write('p = g.players[-1]\n')

                # save player attributes
                for att in p.savable_atts:
                    f.write('p.{} = {!r}\n'.format(att, getattr(p, att)))

                # save current story
                if p.current_story:
                    f.write(
                        'p.current_story = g.stories[{!r}]\n'.format(
                            p.current_story.__class__.__name__
                        )
                    )

                # friends
                f.write('\np.friends = [')
                for friend in p.friends:
                    f.write(f'{self.get_fighter_ref(friend)}, ')
                f.write(']\n')

                # enemies
                f.write('\np.enemies = [')
                for en in p.enemies:
                    f.write(f'{self.get_fighter_ref(en)}, ')
                f.write(']\n')

                # students
                f.write(f'\np.students = {p.students!r}\n')
                best = p.best_student.get_init_string() if p.best_student else 'None'
                f.write(f'\np.best_student = {best}')

                # dump log
                path = os.path.join(SAVE_FOLDER, '{}\'s log.txt'.format(p.name))
                with open(path, 'a') as log_file:
                    log_file.write('\n'.join(p.plog))
                    p.plog = []

        def _save_schools():
            f.write('\n\ng.schools = {}')
            for sn in sorted(self.schools):
                f.write(f'\n\ng.schools[{sn!r}] = school = []')
                for student in self.schools[sn]:
                    f.write(f'\nschool.append({self.get_fighter_ref(student)})')

        def _save_special_npcs():
            bgr = self.beggar
            drkd = self.drunkard
            thf = self.thief
            crmls = self.criminals
            fg = self.fat_girl
            f.write(
                f"\n\ng.beggar = {self.get_fighter_ref(bgr) if bgr is not None else 'None'}"
            )
            f.write(
                '\ng.drunkard = {}'.format(
                    self.get_fighter_ref(drkd) if drkd is not None else 'None'
                )
            )
            f.write(
                f"\ng.thief = {self.get_fighter_ref(thf) if thf is not None else 'None'}"
            )
            f.write('\ng.criminals = []')
            for c in crmls:
                f.write(f'\ng.criminals.append({self.get_fighter_ref(c)})')
            f.write(
                f"\ng.fat_girl = {self.get_fighter_ref(fg) if fg is not None else 'None'}"
            )

        def _save_stories():
            f.write(f'\n\ng.stories = {self.stories!r}')

        with open(os.path.join(SAVE_FOLDER, file_name), 'w') as f:
            _save_all()

    def state_menu(self):
        p = self.current_player
        cls()
        print(p.get_p_info_verbose())
        print()
        p.show(p.get_techs_string())
        print()
        p.show('Moves:')
        print(', '.join([str(m) for m in p.moves if m not in BASIC_MOVES]))
        print()
        # add move screen with more detailed descriptions
        choice = menu(
            ('Items', 'Back', 'Save', 'Load', 'Quit', 'Save and Quit', 'Debug Menu'),
            keys='ibslqxd',
            new_line=False,
        )
        if choice == 'Items':
            cls()
            print(p.get_inventory_info())
            pak()
        elif choice == 'Save':
            self.save_game('save.txt')
        elif choice == 'Load':
            self.load_game('save.txt')
            self.prepare_for_playing()  # otherwise loading fails
            self.chosen_load = True
        elif choice == 'Quit':
            self.chosen_quit = True
        elif choice == 'Save and Quit':
            self.save_game('save.txt')
            self.chosen_quit = True
        elif choice == 'Debug Menu':
            self.debug_menu()

    def test(self):
        p = self.current_player
        # p.level_up()
        p.obtain_item('Dragon Herb')
        p.obtain_item('Ox Herb')
        from ..kung_fu.moves import get_rand_moves
        m1 = get_rand_moves(p, 1, 4)[0]
        m2 = get_rand_moves(p, 1, 5)[0]
        m3 = get_rand_moves(p, 1, 7)[0]
        m4 = get_rand_moves(p, 1, 8)[0]
        m5 = get_rand_moves(p, 1, 10)[0]
        for move in m1, m2, m3, m4, m5:
            if move:
                p.learn_move(move, silent=False)
        f1 = fighter_factory.new_thug(weak=False)
        p.fight(f1)
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

    def unregister_fighter(self, f):
        self.fighters_list.remove(f)
        del self.fighters_dict[f.name]

    def yn(self, text):
        if self.spectator:
            return yn(text)
        else:
            return True
