from ..fighting import fight
from .tournament import Tournament
from ..utils.utilities import *


# chances
CH_SCHOOL_VS_SCHOOL = 0.04
CH_STORY_BEGINS = 0.1
CH_TOURNAMENT_BEGINS = 0.15

# tournaments
DEFAULT_TOURN_FEE = 100
TOURN_FEES = (50, 75, 100, 125, 150)
TOURN_PRIZE_MULT = 4
TOURN_TYPES = (
    'beginner',
    'intermediate',
    'expert',
)
TOURN_TYPE_BGN, TOURN_TYPE_MED, TOURN_TYPE_ADV = TOURN_TYPES

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


# todo are random changes in kung-fu etc. working?
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
            'tourn_type': TOURN_TYPE_BGN,
        },
        {
            'min_lv': 5,
            'max_lv': 8,
            'tourn_type': TOURN_TYPE_MED,
        },
        {
            'min_lv': 9,
            'max_lv': 12,
            'tourn_type': TOURN_TYPE_ADV,
        },
    ]
    t = random.choice(tournaments)
    n = random.choices(
        population=(8, 16, 12, 10, 14, 18, 20),
        weights=(1.0, 0.5, 0.05, 0.05, 0.05, 0.025, 0.025),
    )[0]
    Tournament(game=g, num_participants=n, fee=random.choice(TOURN_FEES), **t)


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
