import random
from pathlib import Path

from kf_lib.actors import fighter_factory, names
from kf_lib.happenings import events
from kf_lib.things import items
from kf_lib.ui import cls, pak, yn
from kf_lib.utils import rnd, SAVE_FOLDER
from . import game_stats
from ._base_game import BaseGame


# misc constants
CH_STUDENT_LV_UP = 0.1
MAX_STUDENT_LEVEL = 8
WALK_EXTRA_ENC = 2


# victory conditions
GRANDMASTER_LV = 20
FOLK_HERO_REP = 200
KFLEGEND_ACCOMPL = 8
GT_FIGHTER_FIGHTS = (100, 150)  # fights_won, num_kos


class Playing(BaseGame):
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
                self.show_stats(do_cls=False, do_pak=False)
                self.play_indefinitely = yn('Keep playing indefinitely?')
            return True

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

    def hook_up_players(self):
        for p in self.players:
            p.game = self
            p.refresh_school_rank()

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

    def show_stats(self, do_cls=True, do_pak=True):
        sg = game_stats.StatGen(self)
        stats = sg.get_full_report_string()
        if do_cls:
            cls()
        print(stats)
        print(stats, file=open(Path(SAVE_FOLDER, 'stats.txt'), 'w'))
        if do_pak:
            pak()
