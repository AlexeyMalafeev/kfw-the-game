import random

from kf_lib.actors.names import GROUP_NAMES
from kf_lib.ui import cls, menu, pak


ASTON_VICTORY_MIN_RATIO = 1.2
BORING_FIGHT_RATIO = 0.4
DRAW_EXP_DIVISOR = 2
ENVIRONMENT_BONUSES = (1.2, 1.3, 1.5, 1.8, 2.0)
EPIC_FIGHT_MIN_LEN = 10
EPIC_FIGHT_RATIO = 0.8
# name of the bonus, exp mult, condition
EXP_BONUSES = (
    ('Quick victory', 1.25, 'self.timer / TIME_TO_SEC_DIVISOR <= 10'),
    ('Not a scratch', 1.25, 'not p.took_damage'),
    ('Multi-knockout', 1.25, 'p.kos_this_fight >= 3'),
    ('Strong enemy', 1.25, 'p.exp_yield < self.win_exp'),
)
HUMIL_DEFEAT_MIN_RATIO = 0.8
LOSER_EXP_DIVISOR = 4
NARROW_VICTORY_HP_PCNT = 0.05
TIME_TO_SEC_DIVISOR = 2


class BaseFight(object):
    def __init__(self, side_a, side_b, environment_allowed=True):
        # fight participants
        self.side_a = side_a
        self.side_b = side_b
        self.all_fighters = self.side_a + self.side_b
        self.active_fighters = self.all_fighters[:]  # initialize active fighters
        self.active_side_a = self.side_a[:]
        self.active_side_b = self.side_b[:]
        self.players = [f for f in self.all_fighters if f.is_player]
        self.main_player = self.players[0] if self.players else None
        self.winners = []
        self.losers = []
        self.win = None
        self.win_exp = 0

        # fight settings
        self.environment_allowed = environment_allowed
        self.environment_bonus = self.environment_allowed * random.choice(ENVIRONMENT_BONUSES)
        self.items_allowed = False
        self.school_display = False
        self.win_messages = None

        # fight mechanics and interface
        self.timer = -1  # NB! not zero, to avoid skipping first fighter in fight_loop
        self.time_limit = 500000
        self.order = {}  # {time units: [1 or more fighters]}
        self.stats = {}
        self.timeline = []
        self.cartoon = ['']

        # in-attack attributes
        self.current_fighter = None

    def check_epic(self):
        unique = set(self.cartoon)
        total = len(self.cartoon)
        if total >= EPIC_FIGHT_MIN_LEN:
            if len(unique) / total >= EPIC_FIGHT_RATIO:
                return ' (epic!)'
            if len(unique) / total <= BORING_FIGHT_RATIO:
                return ' (boring...)'
        return ''

    def check_fight_over(self):
        self.active_fighters = [f for f in self.all_fighters if f.hp > 0]
        if not self.active_fighters:
            self.winners = []
            self.losers = self.all_fighters
            self.win = False
            return True
        self.active_side_a = [f for f in self.active_fighters if f in self.side_a]
        self.active_side_b = [f for f in self.active_fighters if f in self.side_b]
        if not self.active_side_a:
            self.winners = self.side_b
            self.losers = self.side_a
            self.win = False
            return True
        if not self.active_side_b:
            self.winners = self.side_a
            self.losers = self.side_b
            self.win = True
            return True
        return False

    def check_initiative(self, span, f):
        """This is used to see if a fighter has time to make another move after the current move"""
        t = self.timer
        for i in range(t, t + span + 1):
            fs = self.order.get(i, [])
            if f in fs:
                return True
        return False

    def cls(self):
        pass

    def disarm_all(self):
        """Disarm all fighters to avoid having people running around with weapons."""
        for f in self.all_fighters:
            f.disarm()

    def display(self, text, **kwargs):
        n_min, n_sec = self.get_time()
        s = f'{n_min}:{n_sec} {text}'
        self.timeline.append(s)

    def fight_loop(self):
        """
        The most important method that determines what happens and in what order during a fight.
        """

        # determine initial order
        adjust = max(f.speed_full for f in self.active_fighters)
        for f in self.active_fighters:
            self.queue(f, -f.speed_full + adjust)

        # main fight loop
        while True:
            nxt = min(self.order)
            elapsed = nxt - self.timer
            self.timer = nxt
            # print('timer', self.timer)
            # print('elapsed', elapsed)
            # print('order', self.order)
            # pak()
            fs = self.order.get(self.timer)
            self.handle_status_times(elapsed)
            # if fs is None:  # nobody's turn
            #     continue
            if len(fs) > 1:
                random.shuffle(fs)
            for f in fs:
                if f.hp > 0:
                    f.apply_bleeding()
                if f.hp <= 0:  # for newly ko'ed fighters
                    continue
                if self.check_fight_over():  # for winner allies
                    return
                if f.check_status('skip'):
                    self.queue(f, self.timer + f.status['skip'])
                    continue
                self.current_fighter = f
                f.start_fight_turn()
                f.choose_target()
                f.choose_move()
                f.refresh_ascii()
                time_cost = f.get_move_time_cost(f.action)
                f.exec_move()
                self.queue(f, self.timer + time_cost)
                self.pak()
            del self.order[self.timer]
            if self.timer >= self.time_limit:
                self.handle_time_limit_exceeded()

            # avoid infinite loop if all fighters are down
            if self.check_fight_over():
                for f in self.winners:
                    f.set_ascii('Win')
                for f in self.losers:
                    f.set_ascii('Lying')
                return

    def get_f_name_string(self, f):
        if self.school_display:
            return f'{f.name} ({f.style.name})'
        else:
            return f.name

    def get_seconds(self):
        return round(self.timer / TIME_TO_SEC_DIVISOR)

    def get_time(self):
        n_sec = self.get_seconds()
        n_min = n_sec // 60
        n_sec_left = n_sec % 60
        return n_min, n_sec_left

    def give_exp(self):
        # fight outcome (exp and statistics)
        num_w = len(self.winners)
        num_l = len(self.losers)
        num_f = len(self.all_fighters)
        if self.winners:
            self.win_exp = sum([f.exp_yield for f in self.losers]) // num_w
            los_exp = sum([w.exp_yield for w in self.winners]) // num_l // LOSER_EXP_DIVISOR
            los_mess = 'Loses.'
        else:
            los_exp = sum([f.exp_yield for f in self.all_fighters]) // num_f // DRAW_EXP_DIVISOR
            los_mess = 'Draw.'
        for p in self.players:
            if p in self.winners:
                exp = self.win_exp
                for bname, bmult, bcond in EXP_BONUSES:
                    if eval(bcond):
                        s = f'{bname}!'
                        p.show(p.name + ': ' + s)
                        p.log(s)
                        exp = round(exp * bmult)
                        p.exp_bonuses += 1
            else:
                exp = los_exp
                p.log(los_mess)
            # todo remove this when change the exp system
            if p.weapon:
                exp /= p.weapon.get_exp_mult()
                exp = round(exp)
            # todo probably reimplement this when change the exp system
            if self.items_allowed and p.used_item:
                p.cancel_item(p.used_item)
                p.used_item = ''
            p.gain_exp(exp)
        self.handle_player_stats()
        self.main_player.pak()

    def handle_accompl(self):
        if not any([w.is_player for w in self.winners]):
            return
        # single winner only
        if len(self.winners) == 1:
            w = self.winners[0]
            # win against 5 enemies
            if len(self.losers) >= 5:
                w.add_accompl('Lone Warrior')
            if w.hp <= w.hp_max * NARROW_VICTORY_HP_PCNT:
                w.add_accompl('Narrow Victory')
            if sum([f.exp_yield for f in self.losers]) >= w.exp_yield * 1.5:
                w.add_accompl('Against All Odds')
            if self.timer / TIME_TO_SEC_DIVISOR <= 1:
                w.add_accompl('Split-Second Victory')

    def handle_gossip(self):
        for p in self.players:
            if self.winners:  # not draw
                if p in self.winners and len(self.winners) == 1:
                    ratio = round(sum([f.exp_yield for f in self.losers]) / p.exp_yield, 2)
                    curr_stat = p.get_stat(
                        'aston_victory'
                    )  # tuple: (date, p.level, [enemies], big ratio)
                    if (curr_stat is None and ratio >= ASTON_VICTORY_MIN_RATIO) or (
                        curr_stat is not None and ratio > curr_stat[-1]
                    ):
                        tup = (
                            p.game.get_date(),
                            p.level,
                            [f.get_f_info(short=True) for f in self.losers],
                            ratio,
                        )
                        p.write_stat('aston_victory', tup)
                        p.log(f'What an astonishing victory! ({tup[-1]})')
                elif p in self.losers and len(self.losers) == 1:
                    ratio = round(sum([f.exp_yield for f in self.winners]) / p.exp_yield, 2)
                    curr_stat = p.get_stat(
                        'humil_defeat'
                    )  # tuple: (date, p.level, [enemies], small ratio)
                    if (curr_stat is None and ratio <= HUMIL_DEFEAT_MIN_RATIO) or (
                        curr_stat is not None and ratio < curr_stat[-1]
                    ):
                        tup = (
                            p.game.get_date(),
                            p.level,
                            [f.get_f_info(short=True) for f in self.winners],
                            ratio,
                        )
                        p.write_stat('humil_defeat', tup)
                        p.log(f'What a humiliating defeat! ({tup[-1]})')

    def handle_injuries(self):
        for f in self.all_fighters:
            if f.is_player and not f.hp:
                f.injure()

    def handle_items(self):
        if self.players and self.items_allowed:
            for p in self.players:
                if p.check_fight_items():
                    p.act_targets = self.side_b[:] if p in self.side_a else self.side_a[:]
                    p.act_allies = self.side_b[:] if p in self.side_b else self.side_a[:]
                    choice = p.use_fight_item_or_not()
                    if choice:
                        p.used_item = choice
                        p.use_item(p.used_item)
                    else:
                        p.used_item = ''

    def handle_player_stats(self):
        if self.players:
            g = self.players[0].game
            g.fights_total += 1
        for p in self.players:
            p.change_stat('num_fights', 1)
            if p in self.winners:
                p.log('Wins.')
                p.change_stat('fights_won', 1)
            if p.exp_bonuses:
                p.change_stat('exp_bonuses', p.exp_bonuses)
            if p.kos_this_fight:
                p.change_stat('num_kos', p.kos_this_fight)
            if not p.hp:
                p.change_stat('times_koed', 1)

    def handle_prefight_quote(self):
        f1 = self.side_a[0]
        f2 = self.side_b[0]
        make_pause = f1.say_prefight_quote() + f2.say_prefight_quote()
        if make_pause > 0:
            self.pak()

    def handle_win_quote(self):
        if self.winners:
            self.winners[0].say_win_quote()

    def handle_status_times(self, elapsed):
        for f in self.active_fighters:
            for status in list(f.status):  # list(f.status) to avoid error with del
                f.status[status] -= elapsed
                if f.status[status] <= 0:
                    del f.status[status]

    def handle_time_limit_exceeded(self):
        # todo add fight log dump here
        print('TIME LIMIT EXCEEDED!')
        print('all participants:')
        print(self.side_a, '\nvs\n', self.side_b)
        print('active fighters:')
        print(self.active_fighters)
        # pak()
        for f in self.active_fighters:
            f.hp = -10

    def pak(self):
        pass

    def post_fight_menu(self):
        if not self.cartoon[0]:
            self.cartoon = self.cartoon[1:]
        s = self.check_epic()
        options = (
            ('Stats', self.show_stats),
            ('Timeline', self.show_timeline),
            ('Slideshow ({})'.format(len(self.cartoon)) + s, self.slideshow),
            ('Save slideshow', self.save_slideshow),
        )
        while True:
            choice = menu(options, keys='stlv', weak=True)
            if choice:
                cls()
                choice()
            else:
                return

    def prepare_fighters(self):
        for f in self.all_fighters:
            f.current_fight = self
            f.prepare_for_fight()

    def queue(self, f, i):
        if i not in self.order:
            self.order[i] = []
        self.order[i].append(f)

    def _resolve_winner_name(self):
        s = ''
        if self.winners:
            if self.win_messages:
                if self.winners == self.side_a:
                    s = self.win_messages[0]
                elif self.winners == self.side_b:
                    s = self.win_messages[1]
            else:
                wnr = self.winners[0]
                if wnr.name in GROUP_NAMES:
                    s = f'{GROUP_NAMES[wnr.name]} win.'
                else:
                    s = f'{wnr.name} wins.'
            self.handle_win_quote()
        else:
            s = 'Draw!'
        return s

    def save_slideshow(self):
        file_name = input("Input file name: ")
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(self.cartoon))
        print('Saved successfully.')

    def show(self, *args, **kwargs):
        pass

    def show_win_message(self, who_shows_ascii=None, alternative_printing_fn=None):
        self.cls()
        if who_shows_ascii is None:
            who_shows_ascii = self.main_player
        who_shows_ascii.show_ascii()
        s = self._resolve_winner_name()
        n_min, n_sec_left = self.get_time()
        if n_min:
            t_string = f'{n_min} min. {n_sec_left} sec.'
        else:
            t_string = f'{n_sec_left} sec.'
        dur_st = f'The fight lasted {t_string}'
        sep = '-' * len(dur_st)
        s += f'\n{sep}\n{dur_st}'
        if alternative_printing_fn is None:
            self.main_player.show(s)
        else:
            alternative_printing_fn(s)

    def show_stats(self):
        print(self.stats)

    def show_timeline(self):
        print('\n'.join(self.timeline))

    def slideshow(self):
        total = len(self.cartoon)
        for i, pic in enumerate(self.cartoon):
            print(i + 1, '/', total)
            print(pic)
            pak()
            cls()
