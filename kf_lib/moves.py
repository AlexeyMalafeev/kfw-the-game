from .ascii_art import get_ascii
from .distances import DISTANCE_FEATURES
from .utilities import *


DEFAULT_STYLE_MOVE_DICT = {2: '',
                           4: '',
                           6: '',
                           8: ''}
# RARE_FEATURE = 'exotic'

# move container (for easy retrieval)
ALL_MOVES_DICT = {}  # list derives later


class Move(object):
    """
functions are names of Fighter methods."""

    def __init__(self, **kwargs):
        self.name = ''
        self.distance = 0
        self.dist_change = 0
        self.power = 0
        self.accuracy = 0
        self.complexity = 0
        self.stam_cost = 0
        self.time_cost = 0
        self.qi_cost = 0
        self.features = set()
        self.functions = []
        self.tier = 0
        self.freq = 0
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.descr = ''
        self.descr_short = ''
        self.set_descr()
        self.ascii_l = ''
        self.ascii_r = ''
        self.set_ascii()
        self.features.add(DISTANCE_FEATURES[self.distance])
        # if self.freq <= 2:
        #    self.features.add(RARE_FEATURE)
        ALL_MOVES_DICT[self.name] = self

    def __repr__(self):
        # return '{}'.format(self.name)
        return f'{self.name} ({self.tier})'

    def set_ascii(self):
        self.ascii_l, self.ascii_r = get_ascii(self.name)

    def set_descr(self):
        """Set move description."""
        fun = ', '.join(self.functions)
        t = roman(self.tier)
        if self.power:
            d = str(self.distance) if self.distance else ''
            if self.dist_change > 0:
                d += f'(+{self.dist_change})'
            elif self.dist_change < 0:
                d += f'({self.dist_change})'
            self.descr = f'{t} Dist:{d} Pwr:{self.power} Acc:{self.accuracy} '\
                f'Cpl:{self.complexity} Cost:S{self.stam_cost}/T{self.time_cost}/Q{self.qi_cost} {fun}'
        else:
            self.descr = f'{t} Dist:{self.dist_change} Cpl:{self.complexity} '\
                f'Cost:S{self.stam_cost}/T{self.time_cost}/Q{self.qi_cost} {fun}'
        self.descr_short = ''


"""
temp = '''
Chain_of_Punches    1  5 3 1  3 7 2  punch,straight          n/a
Crane's_Beak        1  3 4 1  2 6 1  palm,shocking           try_shock_move
Dragon's_Tail       3  4 3 3  3 7 2  kick,circular,extra_dam do_qi_based_dam
Drunken_Punch       2  3 3 2  2 6 1  punch,straight,exotic   n/a
Leopard_Fist        2  2 4 1  2 4 1  punch,straight          n/a
Mantis_Hook         2  2 4 1  2 5 1  palm,circular           n/a
Mantis_Whip         2  2 3 1  2 6 1  palm,circular,shocking  try_shock_move
Meteor_Fist         3  4 3 1  4 7 2  punch,circular          n/a
Monkey_Claw         1  3 4 1  2 5 1  palm,exotic             n/a
Monkey_Slap         2  3 4 1  2 7 1  palm,shocking           try_shock_move
Poisonous_Snake     1  3 3 2  2 8 2  palm,straight,shocking  try_shock_move
Snake_Strike        2  3 4 1  2 5 1  palm,straight           n/a
Tiger_Claw          2  3 4 1  2 7 1  palm,circular           n/a
Tiger's_Tail        3  5 3 3  3 8 2  kick,circular           n/a
Walking_Fist        3  3 3 1  2 7 2  punch,straight          n/a
Whirlwind_Kick      3  4 3 2  3 8 2  kick,circular           n/a
Wing_Chun_Punch     1  2 3 1  1 3 1  punch,straight          n/a
'''
temp = temp.strip()
for s in temp.split('\n'):
    STYLE_SPECIFIC_ATK_MOVES.append(string_to_atk_move(s))
"""


def read_moves(file_name):
    """Read moves from file. Move features are pipe-separated.
    Returns moves and keys as lists (every move is a dict at this point)."""
    moves = []
    with open(file_name, encoding='utf-8') as f:
        first_line = f.readline()
        first_line = first_line[1:]  # remove '#' at the beginning
        keys = [w.strip() for w in first_line.split('|')]
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            m = {}
            vals = [v.strip() for v in line.split('|')]
            for k, v in zip(keys, vals):
                m[k] = eval(v)
            moves.append(m)
    return moves, keys


move_list = read_moves('move files\\all_moves.txt')[0]
for mv in move_list:
    m_obj = Move(**mv)


BASIC_MOVES = [ALL_MOVES_DICT[mn] for mn in ('Punch', 'Kick', 'Shove', 'Step Forward', 'Step Back',
                                             'Guard', 'Focus', 'Catch Breath', 'Finishing Punch',
                                             'Finishing Kick')]


ALL_MOVES_LIST = list(ALL_MOVES_DICT.values())
MOVES_BY_TIERS = {}
for mv in ALL_MOVES_LIST:
    m_tier = mv.tier
    if m_tier in MOVES_BY_TIERS:
        MOVES_BY_TIERS[m_tier].append(mv)
    else:
        MOVES_BY_TIERS[m_tier] = [mv]


def get_move_obj(move_name):
    return ALL_MOVES_DICT[move_name]


def get_moves_by_features(features, tier):
    moves = [m for m in ALL_MOVES_LIST if m.tier == tier and all((f in m.features for f in features))]
    return moves


def get_rand_moves(f, n, tier):
    """Uses frequency of moves; should never return style moves"""
    known_moves = set(f.moves)
    pool = [m for m in MOVES_BY_TIERS[tier] if m not in known_moves]
    weights = [m.freq for m in pool]  # can never get style moves like this as their freq is 0
    return random.choices(pool, weights=weights, k=n)


# todo delete this if the game works fine:
# def get_style_moves(f_or_style_name):
#     if isinstance(f_or_style_name, str):
#         style = f_or_style_name
#     else:
#         style = f_or_style_name.style.name
#     return STYLE_MOVES_DICT.get(style, DEFAULT_STYLE_MOVE_DICT)


def resolve_style_move(move_s, f):
    pool = []
    if move_s in ALL_MOVES_DICT:
        move = ALL_MOVES_DICT[move_s]
        if move not in f.moves:
            f.learn_move(move)
            return
    elif move_s != '' and ',' in move_s:
        features = move_s.split(',')
        tier = int(features[0])
        features = features[1:]
        pool = [m for m in get_moves_by_features(features, tier) if m not in f.moves]
        n = len(pool)
        if n < f.num_moves_choose:
            if not pool:
                print(f'warning: couldn\'t find any moves for move string {move_s}')
            diff = f.num_moves_choose - n
            pool.extend(get_rand_moves(f, diff, tier))
        elif n > f.num_moves_choose:
            weights = [m.freq for m in pool]  # use move frequency
            pool = random.choices(pool, weights=weights, k=f.num_moves_choose)
    else:
        # print('warning: move {} not found'.format(move_s))
        pool = get_rand_moves(f, f.num_moves_choose, rndint_2d(1, 5))
    f.choose_new_move(pool)


# todo delete this if the game works fine:
# def try_get_style_move(f):
#     moves = get_style_moves(f)
#     lv = f.level
#     move_s = moves.get(lv, None)
#     if move_s is None:
#         return
#     else:
#         return resolve_style_move(move_s, f)
