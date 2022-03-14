import random
from pathlib import Path

from kf_lib.actors import fighter_factory, names
from kf_lib.actors.player import (
    HumanPlayer,
    ALL_AI_PLAYERS,  # used in load/new_game
)
from kf_lib.happenings import events, encounters, story
from kf_lib.things import items
from kf_lib.ui import cls, get_int_from_user, menu, pak, yn
from kf_lib.utils import rnd, rndint, SAVE_FOLDER
from . import game_stats


# todo refactor game.py into submodules


# constants
CH_STUDENT_LV_UP = 0.1
MAX_STUDENT_LEVEL = 8
WALK_EXTRA_ENC = 2


# victory conditions
GRANDMASTER_LV = 20
FOLK_HERO_REP = 200
KFLEGEND_ACCOMPL = 8
GT_FIGHTER_FIGHTS = (100, 150)  # fights_won, num_kos


class Game:

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
            days, months, years = [int(x) for x in self.get_date().split('/')]
            n_days = (years - 1) * 360 + (months - 1) * 30 + days
            self.n_days_to_win = n_days

            if not self.silent_ending:
                print('\n'.join(wins))
                input('Press Enter to see stats.')
                self.save_game('game over.txt')
                from . import game_stats

                sg = game_stats.StatGen(self)
                stats = sg.get_full_report_string()
                print(stats)
                print(stats, file=open(Path(SAVE_FOLDER, 'stats.txt'), 'w'))

                # todo decide what to do about win_data
                # this is not used anywhere
                # with open('win_data.tab', 'a') as f:
                #     for i, p in enumerate(winners):
                #         data = '\t'.join(
                #             str(x)
                #             for x in (
                #                 p.__class__.__name__,
                #                 p.style.name,
                #                 p.level,
                #                 p.get_base_atts_tup(),
                #                 p.techs,
                #                 p.traits,
                #                 self.crime,
                #                 self.poverty,
                #                 self.kung_fu,
                #                 victory_types[i],
                #                 n_days,
                #             )
                #         )
                #         f.write(f'\n{data}')
                #         print(data)
                self.play_indefinitely = yn('Keep playing indefinitely?')
            return True

    def collect_used_names(self):
        self.used_names = set(self.fighters_dict)

    def crime_down(self):
        events.crime_down(self)

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
        events.crime_up(self)
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

    def get_act_players(self):
        return [p for p in self.players if not p.inactive]

    def get_date(self):
        return f'{self.day}/{self.month}/{self.year}'

    @staticmethod
    def get_fighter_ref(fighter):
        return f'g.fighters_dict[{fighter.name!r}]'

    # noinspection PyUnresolvedReferences
    def load_game(self, file_name):
        """Read and execute the save file."""
        # todo reimplement game loading to avoid using exec
        # do not delete the below line; needed for loading
        g = self  # noqa
        with open(Path(SAVE_FOLDER, file_name), 'r') as f:
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
        events.randevent(self)
        if self.auto_save_on:
            self.save_game('auto save.txt')

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

    def show_stats(self):
        sg = game_stats.StatGen(self)
        stats = sg.get_full_report_string()
        cls()
        print(stats)
        print(stats, file=open(Path(SAVE_FOLDER, 'stats.txt'), 'w'))
        pak()

    def state_menu(self):
        p = self.current_player
        cls()
        print(p.get_p_info_verbose())
        print()
        p.show(p.get_techs_string())
        print()
        p.show('Moves:')
        print(', '.join([str(m) for m in p.moves if not m.is_basic]))
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

    def unregister_fighter(self, f):
        self.fighters_list.remove(f)
        del self.fighters_dict[f.name]
