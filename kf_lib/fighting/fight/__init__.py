import kf_lib.ui
import kf_lib.ui._interactive
import kf_lib.ui._menu
from ...things import items
from ...actors import names
from ...ui._interactive import pak
from ...ui._menu import menu, yn
from ...ui import cls

ENVIRONMENT_BONUSES = (1.2, 1.3, 1.5, 1.8, 2.0)

# legend: name of the bonus, exp mult, condition
EXP_BONUSES = (
    ('Quick victory', 1.25, 'self.timer / TIME_TO_SEC_DIVISOR <= 10'),
    ('Not a scratch', 1.25, 'not p.took_damage'),
    ('Multi-knockout', 1.25, 'p.kos_this_fight >= 3'),
    ('Strong enemy', 1.25, 'p.exp_yield < self.win_exp'),
)
DRAW_EXP_DIVISOR = 2
LOSER_EXP_DIVISOR = 4

HUMIL_DEFEAT_MIN_RATIO = 0.8
ASTON_VICTORY_MIN_RATIO = 1.2

EPIC_FIGHT_MIN_LEN = 10
EPIC_FIGHT_RATIO = 0.8
BORING_FIGHT_RATIO = 0.4
NARROW_VICTORY_HP_PCNT = 0.05
TIME_TO_SEC_DIVISOR = 2


def get_prefight_info(side_a, side_b=None, hide_enemy_stats=False, basic_info_only=False):
    fs = side_a[:]
    if side_b:
        fs.extend(side_b)
    s = ''
    first_fighter = fs[0]
    size1 = max([len(s) for s in ['NAME '] + [f.name + '  ' for f in fs]])
    size2 = max([len(s) for s in ['LEV '] + [str(f.level) + ' ' for f in fs]])
    size3 = max([len(s) for s in ['STYLE '] + [f.style.name + ' ' for f in fs]])
    att_names = ' '.join(first_fighter.att_names_short) if not basic_info_only else ''
    s += 'NAME'.ljust(size1) + 'LEV'.ljust(size2) + 'STYLE'.ljust(size3) + att_names
    if any([f.weapon for f in fs]) and not basic_info_only:
        s += ' WEAPON'
    for f in fs:
        if side_b and f == side_b[0]:
            s += '\n-vs-'
        s += '\n{:<{}}{:<{}}{:<{}}'.format(
            f.name,
            size1,
            f.level,
            size2,
            f.style.name,
            size3,
        )
        if basic_info_only:
            continue
        if (
                (not hide_enemy_stats)
                or f.is_human
                or (f in side_a and any([ff.is_human for ff in side_a]))
                or (side_b and f in side_b and any([ff.is_human for ff in side_b]))
        ):
            atts_wb = (f.get_att_str_prefight(att) for att in first_fighter.att_names)
        else:
            atts_wb = (f.get_att_str_prefight(att, hide=True) for att in first_fighter.att_names)
        s += '{:<4}{:<4}{:<4}{:<4}'.format(*atts_wb)
        if f.weapon:
            s += f'{f.weapon.name} {f.weapon.descr_short}'
        s += f"\n{' ' * (size1 + size2)}{f.style.descr_short}"
    return s


def fight(
    f1,
    f2,
    f1_allies=None,
    f2_allies=None,
    auto_fight=False,
    af_option=True,
    hide_stats=True,
    environment_allowed=True,
    items_allowed=True,
    win_messages=None,
    school_display=False,
    return_fight_obj=False,
):
    """Return True if f1 wins, False otherwise (including draw)."""
    side_a, side_b = get_sides(f1, f2, f1_allies, f2_allies)
    all_fighters = side_a + side_b
    if any((f.is_human for f in all_fighters)):
        if not any((f.is_human for f in side_a)):
            side_a, side_b = (
                side_b,
                side_a,
            )  # swap sides for human player's convenience (e.g. in tournaments)
            if win_messages:
                temp = win_messages[:]
                win_messages = [temp[1], temp[0]]  # swap win messages also
        cls()
        print(get_prefight_info(side_a, side_b, hide_stats))
        if af_option:
            auto_fight = yn('\nAuto fight?')
        else:
            pak()
            cls()
    else:
        auto_fight = True
    if auto_fight:
        f = AutoFight(
            side_a, side_b, environment_allowed, items_allowed, win_messages, school_display
        )
    else:
        f = NormalFight(
            side_a, side_b, environment_allowed, items_allowed, win_messages, school_display
        )
    if return_fight_obj:
        return f
    return f.win


def get_sides(f1, f2, f1_allies, f2_allies):
    side_a = [f1]
    if f1_allies:
        side_a.extend(f1_allies)
    side_b = [f2]
    if f2_allies:
        side_b.extend(f2_allies)
    return side_a, side_b


def spar(
    f1,
    f2,
    f1_allies=None,
    f2_allies=None,
    auto_fight=False,
    af_option=True,
    hide_stats=False,
    environment_allowed=True,
):
    """Return True if f1 wins, False otherwise (including draw).
    A sparring is different from a fight in that there are no injuries and items are not allowed.
    Everything else is the same."""
    side_a, side_b = get_sides(f1, f2, f1_allies, f2_allies)
    if any((f.is_human for f in side_a + side_b)):
        cls()
        print(get_prefight_info(side_a, side_b, hide_stats))
        if af_option:
            auto_fight = yn('\nAuto fight?')
        else:
            pak()
            cls()
    else:
        auto_fight = True
    if auto_fight:
        f = AutoSparring(side_a, side_b, environment_allowed)
    else:
        f = NormalSparring(side_a, side_b, environment_allowed)
    return f.win


def spectate(f1, f2, f1_allies=None, f2_allies=None, environment_allowed=True, win_messages=None):
    side_a, side_b = get_sides(f1, f2, f1_allies, f2_allies)
    SpectateFight(
        side_a, side_b, environment_allowed=environment_allowed, win_messages=win_messages
    )


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
                items.cancel_item(p.used_item, p)
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

    def save_slideshow(self):
        file_name = input("Input file name: ")
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(self.cartoon))
        print('Saved successfully.')

    def show(self, *args, **kwargs):
        pass

    def show_win_message(self):
        self.cls()
        # pprint.pp(vars(self.side_b[0]))
        self.main_player.show_ascii()
        s = ''
        if self.winners:
            if self.win_messages:
                if self.winners == self.side_a:
                    s = self.win_messages[0]
                elif self.winners == self.side_b:
                    s = self.win_messages[1]
            else:
                wnr = self.winners[0]
                if wnr.name in names.GROUP_NAMES:
                    s = f'{names.GROUP_NAMES[wnr.name]} win.'
                else:
                    s = f'{wnr.name} wins.'
            self.handle_win_quote()
        else:
            s = 'Draw!'
        n_min, n_sec_left = self.get_time()
        if n_min:
            t_string = f'{n_min} min. {n_sec_left} sec.'
        else:
            t_string = f'{n_sec_left} sec.'
        dur_st = f'The fight lasted {t_string}'
        sep = '-' * len(dur_st)
        s += f'\n{sep}\n{dur_st}'
        self.main_player.show(s)

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


class AutoFight(BaseFight):
    """Has all fight mechanics but no output of what happens during the fight."""

    def __init__(
        self,
        side_a,
        side_b,
        environment_allowed=True,
        items_allowed=True,
        win_messages=None,
        school_display=False,
    ):
        BaseFight.__init__(self, side_a, side_b, environment_allowed=environment_allowed)
        self.items_allowed = items_allowed
        self.win_messages = win_messages
        self.school_display = school_display
        self.players = [f for f in self.all_fighters if f.is_player]
        humans = [f for f in self.all_fighters if f.is_human]
        if humans:
            self.main_player = humans[0]
        elif self.players:
            self.main_player = self.players[0]
        else:
            self.main_player = self.side_a[0]
        self.handle_items()
        self.prepare_fighters()
        self.handle_prefight_quote()
        self.fight_loop()
        if self.main_player.is_human:
            self.show_win_message()
            self.post_fight_menu()
        if self.main_player.is_player:
            self.handle_injuries()
            self.handle_gossip()
            self.give_exp()
            self.handle_accompl()
        self.disarm_all()


class NormalFight(AutoFight):
    """Does not only have fight mechanics, but also outputs what happens during the fight."""

    def cls(self):
        kf_lib.ui.cls()

    def display(self, text, **kwargs):
        BaseFight.display(self, text, **kwargs)
        self.show(text, **kwargs)

    def pak(self):
        kf_lib.ui._interactive.pak()

    def prepare_fighters(self):
        AutoFight.prepare_fighters(self)
        for f in self.all_fighters:
            if f.is_human:
                f.is_auto_fighting = False

    def show(self, text, **kwargs):
        self.main_player.show(text, **kwargs)


class SpectateFight(NormalFight):
    def __init__(
        self, side_a, side_b, environment_allowed=True, win_messages=None, school_display=False
    ):
        BaseFight.__init__(
            self, side_a=side_a, side_b=side_b, environment_allowed=environment_allowed
        )
        self.win_messages = win_messages
        self.school_display = school_display
        self.cls()
        self.show(get_prefight_info(side_a, side_b, hide_enemy_stats=False))
        self.pak()
        # cls()
        self.players = []
        self.prepare_fighters()
        self.fight_loop()
        self.show_win_message()
        self.disarm_all()

    def cls(self):
        cls()

    def show(self, text, **kwargs):
        print(text)

    def show_win_message(self):
        self.cls()
        self.side_a[0].show_ascii()
        s = ''
        if self.winners:
            if self.win_messages:
                if self.winners == self.side_a:
                    s = self.win_messages[0]
                elif self.winners == self.side_b:
                    s = self.win_messages[1]
            else:
                wnr = self.winners[0]
                if wnr.name in names.GROUP_NAMES:
                    s = f'{names.GROUP_NAMES[wnr.name]} win.'
                else:
                    s = f'{wnr.name} wins.'
            self.handle_win_quote()
        else:
            s = 'Draw!'
        n_min, n_sec_left = self.get_time()
        if n_min:
            t_string = f'{n_min} min. {n_sec_left} sec.'
        else:
            t_string = f'{n_sec_left} sec.'
        dur_st = f'The fight lasted {t_string}'
        sep = '-' * len(dur_st)
        s += f'\n{sep}\n{dur_st}'
        self.show(s)
        self.pak()

    def pak(self):
        pak()


class BaseSparring(BaseFight):
    """Doesn't have items, accomplishments, injuries, stats, quotes or gossip."""

    def handle_accompl(self):
        pass

    def handle_injuries(self):
        pass

    def handle_items(self):
        pass

    def handle_player_stats(self):
        pass

    def handle_prefight_quote(self):
        pass

    def handle_win_quote(self):
        pass

    def handle_gossip(self):
        pass


class AutoSparring(BaseSparring, AutoFight):
    pass


class NormalSparring(BaseSparring, NormalFight):
    pass
