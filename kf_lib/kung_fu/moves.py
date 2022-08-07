import logging
from pathlib import Path
import random
import re
from typing import Dict, List, Literal, Text, Union

from kf_lib.fighting.distances import DISTANCE_FEATURES
from kf_lib.utils import roman
from .ascii_art import get_ascii
from kf_lib.utils import MOVES_FOLDER


logger = logging.getLogger()

# move container (for easy retrieval)
ALL_MOVES_DICT = {}  # list derives later
SPECIAL_FEATURES = {'drunken'}
TIER_MIN = 0
TIER_MAX = 10
# todo container for default moves istead of .is_basic


class Move:
    """
    functions are names of Fighter methods."""

    def __init__(self, **kwargs):
        self.accuracy = 0
        self.complexity = 0
        self.dist_change = 0
        self.distance = 0
        self.features = set()
        self.freq = 0
        self.functions = []
        self.is_basic = False  # default; will set True for a handful of moves below
        self.name = ''
        self.power = 0
        self.qi_cost = 0
        self.stam_cost = 0
        self.tier = 0
        self.time_cost = 0
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.special_features = set(self.features) & SPECIAL_FEATURES
        self.descr = ''
        self.descr_short = ''
        self.set_descr()
        self.ascii_l = ''
        self.ascii_r = ''
        self.set_ascii()
        if self.distance in DISTANCE_FEATURES:
            self.features.add(DISTANCE_FEATURES[self.distance])
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
            self.descr = (
                f'{t} Dist:{d} Pwr:{self.power} Acc:{self.accuracy} '
                f'Cpl:{self.complexity} Cost:S{self.stam_cost}/T{self.time_cost}/Q{self.qi_cost} '
                f'{fun}'
            )
        else:
            self.descr = (
                f'{t} Dist:{self.dist_change} Cpl:{self.complexity} '
                f'Cost:S{self.stam_cost}/T{self.time_cost}/Q{self.qi_cost} {fun}'
            )
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


move_list = read_moves(Path(MOVES_FOLDER, 'all_moves.txt'))[0]

for mv in move_list:
    m_obj = Move(**mv)


BASIC_MOVES = [
    ALL_MOVES_DICT[mn]
    for mn in (
        'Punch',
        'Kick',
        'Weak Short Punch',
        'Shove',
        'Step Forward',
        'Step Back',
        'Rush Forward',
        'Retreat',
        'Guard',
        'Focus',
        'Catch Breath',
        'Do Nothing',
        'Finishing Punch',
        'Finishing Kick',
    )
]
for m in BASIC_MOVES:
    m.is_basic = True


ALL_MOVES_LIST = list(ALL_MOVES_DICT.values())
MOVES_BY_TIERS: Dict[int, List[Move]] = {}
for mv in ALL_MOVES_LIST:
    m_tier = mv.tier
    if m_tier in MOVES_BY_TIERS:
        MOVES_BY_TIERS[m_tier].append(mv)
    else:
        MOVES_BY_TIERS[m_tier] = [mv]


def get_move_obj(move_name):
    if move_name not in ALL_MOVES_DICT:
        raise MoveNotFoundError(f'"{move_name}" is not a known move')
    return ALL_MOVES_DICT[move_name]


def get_moves_by_features(features, tier):
    moves = [
        m for m in ALL_MOVES_LIST if m.tier == tier and all((f in m.features for f in features))
    ]
    return moves


def get_rand_move(
        f,
        tier: Union[int, Literal['random', 'auto']] = 'auto',
        features: Union[List[Text], Literal['auto']] = 'auto',
):
    """Special case of get_rand_moves"""
    return get_rand_moves(f=f, n=1, tier=tier, features=features)[0]


def get_rand_moves(
        f,
        n: int,
        tier: Union[int, Literal['random', 'auto']] = 'auto',
        features: Union[List[Text], Literal['auto']] = 'auto',
):
    """Uses frequency of moves; should never return style moves"""
    if tier == 'auto':
        tier = f.get_move_tier_for_lv()
    elif tier == 'random':
        tier = random.randint(TIER_MIN, TIER_MAX)
    if features == 'auto':
        features = f.fav_move_features
    known_moves = set(f.moves)
    pool = [m for m in MOVES_BY_TIERS[tier]
            if m not in known_moves
            and not (m.special_features - f.fav_move_features)]
    if not pool:
        logger.warning(
            f'The pool in get_rand_moves is empty: '
            f'\n{f=}'
            f'\n{n=}'
            f'\n{tier=}'
            f'\n{features=}'
            f'\nSetting pool to all moves at tier'
        )
        pool = MOVES_BY_TIERS[tier]
    random.shuffle(pool)
    print(
        f'{"*"*20}\nPOOL: '
        f'\n{f=}'
        f'\n{n=}'
        f'\n{tier=}'
        f'\n{features=}'
        )
    print(pool[:10])
    pool.sort(
        key=lambda m: len([feat for feat in features if feat in m.features]),
        reverse=True,
    )
    if len(pool) < n:
        logger.warning(
            f'Cannot select enough moves: '
            f'\n{f=}'
            f'\n{n=}'
            f'\n{tier=}'
            f'\n{features=}'
            f'\n{len(pool)=}'
            f'\nReturning <n moves'
        )
    pool = pool[:n * 3]  # for a bit more variety
    print(pool[:10])
    weights = [m.freq for m in pool]
    selected = random.choices(pool, weights=weights, k=n)
    print(f'{selected=}')
    input('...')
    return selected


def resolve_move_string(move_s: Text, f):
    pool = []
    features = None
    tier = None
    # a special case with tier-only move_s
    if move_s.isdigit():
        # todo reimplement: make .techs store tech objects, not names; convert on save/load only
        from .techniques import get_tech_obj

        features = []
        for t in f.techs:
            t_obj = get_tech_obj(t)
            for par in t_obj.params:
                if par.endswith('_strike_mult'):
                    par = par.replace('_strike_mult', '')
                    features.append(par)
                # todo reimplement adding distance feature to style move, without regex
                elif par.startswith('dist') and par.endswith('_bonus'):
                    from kf_lib.fighting.distances import DISTANCE_FEATURES
                    tier = int(re.findall(r'dist(\d)_bonus', par)[0])
                    features.append(DISTANCE_FEATURES[tier])  # this matches move features
        if features:
            feat = random.choice(features)
            move_s += f',{feat}'
        else:
            # todo reimplement function
            pool = get_rand_moves(f, f.num_moves_choose, int(move_s))
            f.choose_new_move(pool)
            return
    if move_s in ALL_MOVES_DICT:
        move = ALL_MOVES_DICT[move_s]
        if move not in f.moves:
            f.learn_move(move)
            return
    elif move_s and ',' in move_s:
        features = move_s.split(',')
        if features[0].isdigit():
            tier = int(features[0])
            features = features[1:]
        else:
            tier = f.get_move_tier_for_lv()
        pool = [m for m in get_moves_by_features(features, tier) if m not in f.moves]
        n = len(pool)
        if not n:
            logger.warning(f'couldn\'t find any moves for move string {move_s}, fighter {f}')
            pool = get_rand_moves(f, f.num_moves_choose)
        elif n == 1:
            f.learn_move(pool[0])
            return
        elif n > f.num_moves_choose:
            weights = [m.freq for m in pool]  # use move frequency
            pool = random.choices(pool, weights=weights, k=f.num_moves_choose)
    else:
        pool = get_rand_moves(f, f.num_moves_choose)
    try:
        f.choose_new_move(pool)
    except IndexError:
        print(
            f'Cannot choose new move for {pool=}, {move_s}, {features=}, {tier=} {f=}'
        )
        input('...')


class MoveNotFoundError(Exception):
    """Raised when move is not found in known moves."""
    pass
