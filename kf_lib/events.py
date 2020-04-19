#! python3

from . import fight
from .utilities import *


# chances
CH_SCHOOL_VS_SCHOOL = 0.04
CH_STORY_BEGINS = 0.1
CH_TOURNAMENT_BEGINS = 0.15

# tournaments
DFLT_TOURN_PART_NAME = 'Unknown'
TOURN_LV = (5, 10)
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
    g.msg('Old man: The people of {} are losing their \
interest in kung-fu...'.format(g.town_name))


def kungfu_up(g):
    g.cls()
    g.kung_fu = min(g.kung_fu + KUNGFU_CHANGE, MAX_KUNGFU)
    g.msg('Old man: It seems everybody in {} wants \
to practice kung-fu nowadays...'.format(g.town_name))


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
    tournaments = [(1, 4, 'beginner'), (5, 8, 'intermediate'), (9, 12, 'expert')]
    t = random.choice(tournaments)
    Tournament(g, *t)


def poverty_down(g):
    g.cls()
    g.poverty = max(g.poverty - POVERTY_CHANGE, MIN_POVERTY)
    g.msg('Old woman: There are not as many poor and homeless people in {} as before...'.format(g.town_name))


def poverty_up(g):
    g.cls()
    g.poverty = min(g.poverty + POVERTY_CHANGE, MAX_POVERTY)
    g.msg('Old woman: Many people in {} now don\'t have enough to eat...'.format(g.town_name))


def randevent(g):
    order = [(CH_STORY_BEGINS, new_story),
             (CH_SCHOOL_VS_SCHOOL, school_vs_school),
             (CH_TOURNAMENT_BEGINS, new_tournament)
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
    s = 'A fight breaks out between students of {} and {}!'.format(style_a, style_b)
    g.msg(s)
    for f in a + b:
        f.log(s)
    win_messages = tuple('{} school wins!'.format(st) for st in (style_a, style_b))
    fight.fight(a[0], b[0], a[1:], b[1:], win_messages=win_messages, school_display=True)


class Tournament(object):
    num_participants = 8

    def __init__(self, game, min_lv=1, max_lv=5, category='?', fee=None, prize=None):
        self.g = self.game = game
        self.min_lv = min_lv
        self.max_lv = max_lv
        self.category = category
        if fee:
            self.fee = fee
        else:
            self.fee = random.choice(TOURN_FEES)
        if prize:
            self.prize = prize
        else:
            self.prize = self.fee * TOURN_PRIZE_MULT
        self.temp = None
        self.run()

    def couple_fighters(self):
        self.temp = list(zip(self.temp[::2], self.temp[1::2]))

    def do_round(self):
        winners = []
        for match in self.temp:
            f1, f2 = match[0], match[1]
            f1.fight(f2, af_option=True, environment_allowed=False, items_allowed=False)
            if f1.hp:
                winners.append(f1)
            elif f2.hp:
                winners.append(f2)
            else:
                wnr = random.choice(match)
                if any((f.is_player for f in [f1, f2])):
                    self.g.msg('The judges rule the winner to be {}.'.format(wnr.name))
                if wnr.is_player:
                    wnr.inactive = 0
                winners.append(wnr)
        self.temp = winners

    def run(self):
        self.g.cls()
        self.g.msg('A kung-fu tournament ({} level) is organized in {}. The participation fee is {}.'.format(
            self.category, self.g.town_name, self.fee))

        # player participants
        participants = []
        for p in self.g.get_act_players():
            if not p.check_lv(self.min_lv, self.max_lv):
                continue
            if p.tourn_or_not():
                p.enter_tourn(self.fee)
                participants.append(p)
            if len(participants) == self.num_participants:  # for crowds of players
                break

        # return if players don't participate
        if not participants:
            return

        # known fighters
        pool = list(self.g.masters.values())
        pool += [f for s in self.g.schools.values() for f in s]
        av_fighters = ([f for f in pool if f.check_lv(self.min_lv, self.max_lv) and not f.is_player])
        k = self.num_participants - len(participants)
        add = random.sample(av_fighters, k)
        participants += add

        self.g.cls()
        self.g.show('The participants are:\n')
        spectator = participants[0]
        self.g.show(participants[0].get_prefight_info(participants, basic_info_only=True))
        self.g.pak()

        # rounds
        random.shuffle(participants)
        self.temp = participants[:]
        for _round in ('Round 1', 'Round 2', 'Final Round'):
            spectator.cls()
            spectator.msg(_round)
            self.couple_fighters()
            self.do_round()
        winner = self.temp[0]

        # prize
        if winner.name == DFLT_TOURN_PART_NAME:
            winner.name = winner.get_f_info(short=True)
        self.g.msg('{} wins the tournament!'.format(winner.name))
        if winner.is_player:
            winner.win_tourn(self.prize)


class Tournament2(object):
    def __init__(self, participants, spectate=True, **rules):
        self.participants = participants
        self.spectate = spectate
        self.rules = rules
        self.curr_round = self.participants[:]
        self.next_round = []
        self.winner = None
        self.round_num = 1
        cur = self.curr_round
        n = self.round_num
        while True:
            if len(cur) == 1:
                f = cur[0]
                self.winner = f
                cls()
                print(f.name, 'wins the tournament!')
                print(f)
                pak()
                return
            cls()
            if len(cur) == 2:
                print('Final round')
            else:
                print('Round', n)
            pak()
            random.shuffle(cur)
            nxt = []
            gr_a = cur[1::2]
            gr_b = cur[::2]
            for i, f1 in enumerate(gr_a):
                cls()
                f2 = gr_b[i]
                print(f1, '\nvs\n', f2)
                fight.fight(f1, f2, hide_stats=False)
                if f1.hp > 0:
                    print(f1.name, 'goes to next round')
                    nxt.append(f1)
                if f2.hp > 0:
                    print(f2.name, 'goes to next round')
                    nxt.append(f2)
                pak()
            if len(gr_b) > len(gr_a):
                f = gr_b[-1]
                print(f.name, 'goes to next round without competing')
                nxt.append(f)
                pak()
            cur = nxt
            n += 1
