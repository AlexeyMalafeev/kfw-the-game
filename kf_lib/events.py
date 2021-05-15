from typing import Any, Optional

from . import fight
from .fighter import Fighter, HumanControlledFighter
from .player import Player
from .utilities import *


# chances
CH_SCHOOL_VS_SCHOOL = 0.04
CH_STORY_BEGINS = 0.1
CH_TOURNAMENT_BEGINS = 0.15

# tournaments
DEFAULT_TOURN_FEE = 100
TOURN_FEES = (50, 75, 100, 125, 150)
TOURN_PRIZE_MULT = 4

# town
MAX_CRIME = 0.5
MIN_CRIME = 0.0
CRIME_INCREASE_MONTHLY = 0.00
CRIME_DECREASE = 0.002
MAX_KUNGFU = 0.25
MIN_KUNGFU = 0.05
KUNGFU_CHANGE = 0.05
MAX_POVERTY = 0.25
MIN_POVERTY = 0.05
POVERTY_CHANGE = 0.05


# todo show message (g.msg) when crime/kungfu/poverty reaches minimum/maximum
def crime_down(g, rate=CRIME_DECREASE, mult=1.0):
    g.crime = max(round((g.crime - rate * mult), 3), MIN_CRIME)


def crime_up(g, rate=CRIME_INCREASE_MONTHLY, mult=1.0):
    g.crime = min(round((g.crime + rate * mult), 3), MAX_CRIME)


# todo festival
# def festival(g):
#     pass


def kungfu_down(g):
    g.cls()
    g.kung_fu = max(g.kung_fu - KUNGFU_CHANGE, MIN_KUNGFU)
    g.msg(f'Old man: The people of {g.town_name} are losing their interest in kung-fu...')


def kungfu_up(g):
    g.cls()
    g.kung_fu = min(g.kung_fu + KUNGFU_CHANGE, MAX_KUNGFU)
    g.msg(
        'Old man: It seems everybody in {} wants \
to practice kung-fu nowadays...'.format(
            g.town_name
        )
    )


def new_story(g):
    av_stories = [s for s in g.stories.values() if s.check_hasnt_started()]
    if av_stories:
        s = random.choice(av_stories)
        av_players = [p for p in g.players if not p.current_story and s.test(p)]
        if av_players:
            p = random.choice(av_players)
            s.start(p)
            # print(p.name, p.level, s.name)


def new_tournament(g):
    # game, num_participants=8, min_lv=1, max_lv=5, tourn_type='?', fee='random', prize='auto'
    tournaments = [
        {
            'min_lv': 1,
            'max_lv': 4,
            'tourn_type': 'beginner',
        },
        {
            'min_lv': 5,
            'max_lv': 8,
            'tourn_type': 'intermediate',
        },
        {
            'min_lv': 9,
            'max_lv': 12,
            'tourn_type': 'expert',
        },
    ]
    t = random.choice(tournaments)
    n = random.choices(
        population=(8, 16, 12, 10, 14, 18, 20),
        weights=(1.0, 0.5, 0.05, 0.05, 0.05, 0.025, 0.025),
    )[0]
    # print(t, n)
    Tournament(game=g, num_participants=n, **t)


def poverty_down(g):
    g.cls()
    g.poverty = max(g.poverty - POVERTY_CHANGE, MIN_POVERTY)
    g.msg(
        'Old woman: There are not as many poor and homeless people in {} as before...'.format(
            g.town_name
        )
    )


def poverty_up(g):
    g.cls()
    g.poverty = min(g.poverty + POVERTY_CHANGE, MAX_POVERTY)
    g.msg('Old woman: Many people in {} now don\'t have enough to eat...'.format(g.town_name))


def randevent(g):
    # todo use poverty/crime/kungfu_up/down in randevent
    order = [
        (CH_STORY_BEGINS, new_story),
        (CH_SCHOOL_VS_SCHOOL, school_vs_school),
        (CH_TOURNAMENT_BEGINS, new_tournament),
    ]
    random.shuffle(order)
    for chance, func in order:
        if rnd() <= chance:
            func(g)
    # todo add festival to events when it's ready


def school_vs_school(g):
    a, b = random.sample([s for s in g.schools.values() if s], 2)  # avoid empty schools
    a = [f for f in a if not f.is_player or not f.inactive]
    b = [f for f in b if not f.is_player or not f.inactive]
    style_a = a[0].style.name
    style_b = b[0].style.name
    s = f'A fight breaks out between students of {style_a} and {style_b}!'
    g.msg(s)
    for f in a + b:
        f.log(s)
    win_messages = tuple(f'{st} school wins!' for st in (style_a, style_b))
    fight.fight(a[0], b[0], a[1:], b[1:], win_messages=win_messages, school_display=True)


class Tournament(object):
    def __init__(
            self,
            game,
            num_participants=8,
            min_lv=1,
            max_lv=5,
            tourn_type='?',
            fee='random',
            prize='auto',
    ):
        self.g = self.game = game  # todo decouple tournament from game
        self.num_participants = num_participants
        self.min_lv = min_lv
        self.max_lv = max_lv
        self.tourn_type = tourn_type
        self.fee = fee if fee != 'random' else random.choice(TOURN_FEES)
        self.prize = prize if prize != 'auto' else self._calc_prize()
        self.participants: Optional[list] = None
        self.spectator: Optional[HumanControlledFighter] = None
        self.last_draw_winner: Optional[Fighter] = None
        self.winner: Any[Fighter, Player] = None
        self.current_round = 0
        self.run()

    def _calc_prize(self):
        return int(round(self.fee * self.num_participants / 2, -1))

    def _do_fight(self, f1, f2):
        f1.fight(f2, af_option=True, environment_allowed=False, items_allowed=False)
        if f1.hp <= 0 and f2.hp <= 0:
            self.last_draw_winner = wnr = random.choice((f1, f2))
            if f1.is_player or f2.is_player:
                self.g.msg(f'Draw! The judges rule the winner to be {wnr.name}.')

    def _do_rounds(self):
        participants = self.participants
        while (remaining_participants := len(participants)) > 1:
            self.current_round += 1
            self.spectator.cls()
            self.spectator.msg(
                f'Round {self.current_round}\n'
                f'tournament participants left: {remaining_participants}'
            )
            random.shuffle(participants)
            for i in range(0, remaining_participants - 1, 2):
                # if odd, one random fighter is left out, but that's ok
                f1, f2 = participants[i:i + 2]
                self._do_fight(f1, f2)
            participants[:] = [f for f in participants if f.hp > 0]
        if participants:
            self.winner = participants[0]
        else:  # in case of a draw
            self.winner = self.last_draw_winner

    def _gather_participants(self):
        # player participants
        self.participants = participants = []
        for p in self.g.get_act_players():
            if not p.check_lv(self.min_lv, self.max_lv):
                continue
            if p.tourn_or_not():
                p.enter_tourn(self.fee)
                participants.append(p)
            if len(participants) == self.num_participants:  # for crowds of players
                break

        # known fighters
        pool = list(self.g.masters.values())
        pool += [f for s in self.g.schools.values() for f in s]
        av_fighters = [f for f in pool if
                       f.check_lv(self.min_lv, self.max_lv) and not f.is_player]
        k = self.num_participants - len(participants)
        if k > len(av_fighters) or k < 0:
            # print('warning: invalid k in Tournament._gather_participants')
            # print(f'{participants = }, {self.participants = }, {len(av_fighters) = }, {k = }')
            # input('setting k to len(av_fighters), press Enter to continue')
            k = len(av_fighters)
        add = random.sample(av_fighters, k)
        participants += add

    def _give_prize(self):
        winner = self.winner
        self.g.msg(f'{winner.name} wins the tournament!')
        if winner.is_player:
            winner.win_tourn(self.prize)

    def run(self):
        self.g.cls()
        self.g.msg(
            f'A kung-fu tournament ({self.tourn_type} level) is organized in {self.g.town_name}. '
            f'The participation fee is {self.fee}.'
        )

        self._gather_participants()
        self.spectator = self.participants[0]
        self._show_participants()
        self._do_rounds()
        self._give_prize()

    def _show_participants(self):
        participants = self.participants
        self.g.cls()
        self.g.show('The participants are:\n')
        self.g.show(participants[0].get_prefight_info(participants, basic_info_only=True))
        self.g.pak()
