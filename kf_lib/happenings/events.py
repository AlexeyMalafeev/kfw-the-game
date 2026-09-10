import random

from kf_lib.fighting import fight
from kf_lib.utils import rnd
from .tournament import Tournament


# chances
CH_SCHOOL_VS_SCHOOL = 0.04
CH_STORY_BEGINS = 0.1
CH_TOURNAMENT_BEGINS = 0.15
CH_TOURNAMENT_FFA = 0.25
CH_ALL_SCHOOLS_TOURN = 0.02

# all-schools tournament
ALL_SCHOOLS_TEAM_SIZE = 3  # master + top students
ALL_SCHOOLS_PRIZE = 200
ALL_SCHOOLS_WIN_EXP = 20
ALL_SCHOOLS_WIN_REP = 5

# tournaments
TOURN_FEES = (50, 75, 100, 125, 150)
TOURN_TYPES = (
    'beginner',
    'intermediate',
    'advanced',
    'master',
)
TOURN_TYPE_BGN, TOURN_TYPE_MED, TOURN_TYPE_ADV, TOURN_TYPE_MAS = TOURN_TYPES
TOURNAMENTS = [
        {
            'min_lv': 1,
            'max_lv': 3,
            'tourn_type': TOURN_TYPE_BGN,
        },
        {
            'min_lv': 4,
            'max_lv': 6,
            'tourn_type': TOURN_TYPE_MED,
        },
        {
            'min_lv': 7,
            'max_lv': 10,
            'tourn_type': TOURN_TYPE_ADV,
        },
        {
            'min_lv': 11,
            'max_lv': 14,
            'tourn_type': TOURN_TYPE_MAS,
        },
    ]

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


def all_schools_tournament(g):
    """Mega-tournament: every school fields a team (master + top students),
    resolved as a group free-for-all between schools."""
    teams = []
    for school_name, roster in g.schools.items():
        team = []
        master = g.masters.get(school_name)
        if master is not None and not (master.is_player and master.inactive):
            team.append(master)
        students = sorted(
            (f for f in roster if not (f.is_player and f.inactive)),
            key=lambda f: -f.get_exp_worth(),
        )
        team += students[: ALL_SCHOOLS_TEAM_SIZE - 1]
        if len(team) >= 2:
            teams.append(team)
    if len(teams) < 2:
        return
    # teams with players come first (protagonist perspective in the fight)
    teams.sort(key=lambda team: not any(f.is_player for f in team))
    g.cls()
    g.msg(
        f'The masters of {g.town_name} gather for the All-Schools Tournament! Every school '
        'fields its master and best students — last school standing wins!'
    )
    fight_obj = fight.group_free_for_all(
        teams,
        environment_allowed=False,
        items_allowed=False,
        school_display=True,
        return_fight_obj=True,
    )
    if not fight_obj.winners:
        g.msg('The All-Schools Tournament ends in a draw — no school prevails!')
        return
    win_team = next(team for team in teams if fight_obj.winners[0] in team)
    win_school = None
    for school_name, roster in g.schools.items():
        if any(f in roster or g.masters.get(school_name) is f for f in win_team):
            win_school = school_name
            break
    # don't leak the style's secret true name to a player who hasn't learned it
    viewer = next((f for f in win_team if f.is_player), win_team[0])
    displayed_school = viewer.get_displayed_style_name()
    g.msg(f'{displayed_school} wins the All-Schools Tournament!')
    for f in win_team:
        f.log(f'Wins the All-Schools Tournament with {win_school}.')
    for p in (f for f in win_team if f.is_player):
        p.gain_exp(ALL_SCHOOLS_WIN_EXP)
        p.gain_rep(ALL_SCHOOLS_WIN_REP)
        p.earn_prize(ALL_SCHOOLS_PRIZE)
        p.add_accompl('All-Schools Champion')


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
    t = random.choice(TOURNAMENTS)
    ffa = rnd() <= CH_TOURNAMENT_FFA
    if ffa:
        n = 8
    else:
        n = random.choices(
            population=(8, 16, 12, 10, 14, 18, 20),
            weights=(1.0, 0.5, 0.05, 0.05, 0.05, 0.025, 0.025),
        )[0]
    Tournament(game=g, num_participants=n, fee=random.choice(TOURN_FEES), ffa=ffa, **t)


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
        (CH_ALL_SCHOOLS_TOURN, all_schools_tournament),
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
    style_a = a[0].style.public_name
    style_b = b[0].style.public_name
    s = f'A fight breaks out between students of {style_a} and {style_b}!'
    g.msg(s)
    for f in a + b:
        f.log(s)
    win_messages = tuple(f'{st} school wins!' for st in (style_a, style_b))
    fight.fight(a[0], b[0], a[1:], b[1:], win_messages=win_messages, school_display=True)
