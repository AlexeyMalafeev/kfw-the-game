import os
import sys
from pathlib import Path
from typing import Callable, Dict, List
# this has to be before imports from kf_lib
lib_path = Path('..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

import pandas as pd  # noqa

from kf_lib.utils import MOVES_FOLDER  # noqa


TIER_MIN = 0
TIER_MAX = 10
QI_COST_PER_TIER = 5


module_vars = vars()


def read_move_word_combinations() -> Dict[Callable, List[Callable]]:
    result = {}
    with open(Path(MOVES_FOLDER, 'move_word_combinations.csv'), 'r', encoding='utf-8') as f:
        words = f.readline().split(',')
        words = words[1:]
        # strip is for removing trailing new line characters
        words = [module_vars[w.strip()] for w in words]
        for line in f:
            move_fun, *combinations = line.split(',')
            move_fun = module_vars[move_fun]
            result[move_fun] = [
                # strip is for removing trailing new line characters
                words[i] for i, one_or_nothing in enumerate(combinations) if one_or_nothing.strip()
            ]
    return result


def save_moves(moves, keys, file_name, sort_alph=False):
    """Save moves (a list) to file. Pipe-separated and formatted to be very human-readable."""
    if sort_alph:
        moves = sorted(moves, key=lambda x: x['name'])
    with open(file_name, 'w', encoding='utf-8') as f:
        i = 0
        end = len(moves)
        batch_size = 25
        while i < end:
            batch = moves[i:i + batch_size]
            col_lens = []
            batch_vals = []
            for m in batch:
                batch_vals.append([repr(m[k]) for k in keys])
            legend = keys[:]
            legend[0] = '# ' + legend[0]
            batch_vals = [legend] + batch_vals
            for j, k in enumerate(keys):
                col_len = max([len(vals[j]) for vals in batch_vals]) + 1
                col_lens.append(col_len)
            for vals in batch_vals:
                for j, v in enumerate(vals):
                    vals[j] = v + ' ' * (col_lens[j] - len(v))
                f.write('|'.join(vals) + '\n')
            f.write('\n')
            i += batch_size
        f.write(f'# {len(moves)} moves')


def modify(m, k, diff, mx=None, mn=None):
    m[k] += diff
    if mx is not None and m[k] > mx:
        m[k] = mx
    if mn is not None and m[k] < mn:
        m[k] = mn


def change_tier(m, n=1):
    modify(m, 'tier', n, mx=TIER_MAX, mn=TIER_MIN)
    # don't modify qi if tier is actually decreasing
    if n > 0:
        modify(m, 'qi_cost', n * QI_COST_PER_TIER)


def mult(m, k, co):
    m[k] *= co
    m[k] = round(m[k])


def prefix(m, p):
    m['name'] = p + ' ' + m['name']
    add_feat(m, p.lower())


def add_feat(m, n):
    new_features = m['features'].copy()
    new_features.add(n)
    m['features'] = new_features


def add_fun(m, n):
    # this is to avoid modifying function lists in other moves
    m['functions'] = m['functions'][:] + [n]


# todo make a table instead of separate move gen functions
# todo automatic checks for incompatible moves (when effects can't be applied)
def light(m):
    if 'takedown' in m['features']:
        return None
    m = m.copy()
    mult(m, 'power', 0.8)
    mult(m, 'accuracy', 1.1)
    mult(m, 'stam_cost', 0.75)
    change_tier(m)
    prefix(m, 'Light')
    return m


def heavy(m):
    if 'takedown' in m['features']:
        return None
    m = m.copy()
    mult(m, 'power', 1.2)
    mult(m, 'accuracy', 0.9)
    mult(m, 'stam_cost', 1.25)
    change_tier(m)
    prefix(m, 'Heavy')
    return m


def long(m):
    if m['distance'] >= 4:
        return None
    m = m.copy()
    modify(m, 'distance', 1)
    modify(m, 'freq', -1, mn=1)
    if m['distance'] == 4:
        change_tier(m, 2)
    else:
        change_tier(m)
    prefix(m, 'Long')
    return m


def short(m):
    if m['distance'] <= 1:
        return None
    m = m.copy()
    modify(m, 'distance', -1)
    change_tier(m)
    modify(m, 'freq', -1, mn=1)
    prefix(m, 'Short')
    return m


def charging(m):
    m = m.copy()
    if m['distance'] <= 1:
        modify(m, 'distance', 1)
    change_tier(m, 2)
    modify(m, 'freq', -1, mn=1)
    mult(m, 'stam_cost', 1.1)
    mult(m, 'time_cost', 1.2)
    modify(m, 'dist_change', -1)
    prefix(m, 'Charging')
    return m


def retreating(m):
    if m['distance'] >= 4:
        return None
    m = m.copy()
    change_tier(m, 2)
    modify(m, 'freq', -1, mn=1)
    mult(m, 'stam_cost', 1.15)
    mult(m, 'time_cost', 1.25)
    modify(m, 'dist_change', 1)
    prefix(m, 'Retreating')
    return m


def onslaught(m):
    m = m.copy()
    if m['distance'] <= 2:
        modify(m, 'distance', 2)
    change_tier(m, 3)
    modify(m, 'freq', -1, mn=1)
    mult(m, 'stam_cost', 1.2)
    mult(m, 'time_cost', 1.4)
    modify(m, 'complexity', 1)
    modify(m, 'dist_change', -2)
    prefix(m, 'Onslaught')
    return m


def vanishing(m):
    if m['distance'] >= 3:
        return None
    m = m.copy()
    change_tier(m, 3)
    modify(m, 'freq', -1, mn=1)
    mult(m, 'stam_cost', 1.25)
    mult(m, 'time_cost', 1.45)
    modify(m, 'complexity', 1)
    modify(m, 'dist_change', 2)
    prefix(m, 'Vanishing')
    return m


def pushing(m):
    if m['distance'] >= 4 or 'takedown' in m['features']:
        return None
    m = m.copy()
    change_tier(m)
    add_fun(m, 'do_knockback')
    prefix(m, 'Pushing')
    return m


def surprise(m):
    if any(feat in m['features'] for feat in ('shocking', 'surprise', 'debilitating')):
        return None
    m = m.copy()
    change_tier(m, 2)
    add_fun(m, 'try_shock_move')
    prefix(m, 'Surprise')
    return m


def fast(m):
    m = m.copy()
    mult(m, 'time_cost', 0.8)
    mult(m, 'stam_cost', 1.1)
    change_tier(m)
    prefix(m, 'Fast')
    return m


def strong(m):
    if 'takedown' in m['features']:
        return None
    m = m.copy()
    mult(m, 'power', 1.2)
    mult(m, 'stam_cost', 1.1)
    change_tier(m, 2)
    prefix(m, 'Strong')
    return m


def precise(m):
    if 'takedown' in m['features']:
        return None
    m = m.copy()
    mult(m, 'time_cost', 1.1)
    mult(m, 'accuracy', 1.2)
    change_tier(m, 2)
    prefix(m, 'Precise')
    return m


def flying(m):
    if m['distance'] >= 4 or 'takedown' in m['features']:
        return None
    m = m.copy()
    mult(m, 'power', 0.9)
    mult(m, 'stam_cost', 1.2)
    modify(m, 'distance', 1)
    modify(m, 'dist_change', -1)
    modify(m, 'complexity', 1)
    change_tier(m, 3)
    modify(m, 'freq', -1, mn=1)
    prefix(m, 'Flying')
    return m


def acrobatic(m):
    """More power and accuracy at the cost of increased complexity"""
    if 'do_agility_based_dam' in m['functions'] or 'do_strength_based_dam' in m['functions']:
        return None
    if 'takedown' in m['features']:
        return None
    m = m.copy()
    mult(m, 'stam_cost', 1.25)
    modify(m, 'complexity', 2)
    change_tier(m, 3)
    add_fun(m, 'do_agility_based_dam')
    add_fun(m, 'do_strength_based_dam')
    modify(m, 'freq', -2, mn=1)
    prefix(m, 'Acrobatic')
    return m


def power(m):
    if 'do_strength_based_dam' in m['functions']:
        return None
    m = m.copy()
    change_tier(m, 2)
    add_fun(m, 'do_strength_based_dam')
    prefix(m, 'Power')
    return m


def trick(m):
    if 'do_agility_based_dam' in m['functions']:
        return None
    m = m.copy()
    change_tier(m, 2)
    add_fun(m, 'do_agility_based_dam')
    prefix(m, 'Trick')
    return m


def lightning(m):
    if 'do_speed_based_dam' in m['functions']:
        return None
    m = m.copy()
    change_tier(m, 2)
    add_fun(m, 'do_speed_based_dam')
    prefix(m, 'Lightning')
    return m


def energy(m):
    if 'do_qi_based_dam' in m['functions']:
        return None
    m = m.copy()
    change_tier(m, 2)
    add_fun(m, 'do_qi_based_dam')
    prefix(m, 'Energy')
    return m


def ferocious(m):
    if 'do_speed_based_dam' in m['functions'] or 'do_strength_based_dam' in m['functions']:
        return None
    m = m.copy()
    mult(m, 'stam_cost', 1.2)
    change_tier(m, 4)
    add_fun(m, 'do_speed_based_dam')
    add_fun(m, 'do_strength_based_dam')
    prefix(m, 'Ferocious')
    return m


def piercing(m):
    if 'takedown' in m['features']:
        return None
    if 'do_agility_based_dam' in m['functions'] or 'do_speed_based_dam' in m['functions']:
        return None
    m = m.copy()
    mult(m, 'stam_cost', 1.2)
    change_tier(m, 4)
    add_fun(m, 'do_agility_based_dam')
    add_fun(m, 'do_speed_based_dam')
    prefix(m, 'Piercing')
    return m


def shocking(m):
    if any(feat in m['features'] for feat in ('shocking', 'surprise', 'debilitating')):
        return None
    m = m.copy()
    change_tier(m, 3)
    add_fun(m, 'do_shock_move')
    prefix(m, 'Shocking')
    return m


def solar(m):
    if 'takedown' in m['features']:
        return None
    m = m.copy()
    change_tier(m, 3)
    add_fun(m, 'do_stam_dam')
    prefix(m, 'Solar')
    return m


def nerve(m):
    if 'takedown' in m['features']:
        return None
    m = m.copy()
    change_tier(m, 3)
    add_fun(m, 'do_mob_dam')
    prefix(m, 'Nerve')
    return m


def debilitating(m):
    if any(feat in m['features'] for feat in ('shocking', 'surprise', 'debilitating')):
        return None
    m = m.copy()
    change_tier(m, 5)
    add_fun(m, 'do_shock_move')
    add_fun(m, 'do_stam_dam')
    add_fun(m, 'do_mob_dam')
    modify(m, 'freq', -1, mn=1)
    prefix(m, 'Debilitating')
    return m


def lethal(m):
    # if 'takedown' in m['features']:
    #     return None
    m = m.copy()
    change_tier(m, 6)
    add_fun(m, 'try_insta_ko')
    modify(m, 'freq', -2, mn=1)
    prefix(m, 'Lethal')
    return m


def slashing(m):
    if 'cause_bleeding' in m['functions']:
        return None
    m = m.copy()
    change_tier(m, 4)
    add_fun(m, 'cause_bleeding')
    modify(m, 'freq', -2, mn=1)
    prefix(m, 'Slashing')
    return m


def drunken(m):
    if 'cause_off_balance' in m['functions'] or 'do_agility_based_dam' in m['functions']:
        return None
    if 'takedown' in m['features']:
        return None
    m = m.copy()
    modify(m, 'complexity', 1)
    change_tier(m, 1)
    add_fun(m, 'cause_off_balance')
    add_fun(m, 'do_agility_based_dam')
    modify(m, 'freq', -5, mn=0)
    prefix(m, 'Drunken')
    return m


def pathetic(m):
    m = m.copy()
    change_tier(m, -2)
    mult(m, 'power', 0.8)
    mult(m, 'accuracy', 0.8)
    mult(m, 'time_cost', 1.2)
    mult(m, 'stam_cost', 1.2)
    prefix(m, 'Pathetic')
    return m


def weak(m):
    m = m.copy()
    change_tier(m, -1)
    mult(m, 'power', 0.9)
    mult(m, 'accuracy', 0.9)
    mult(m, 'time_cost', 1.1)
    mult(m, 'stam_cost', 1.1)
    prefix(m, 'Weak')
    return m


def skillful(m):
    m = m.copy()
    change_tier(m, 2)
    mult(m, 'power', 1.1)
    mult(m, 'accuracy', 1.1)
    mult(m, 'time_cost', 0.9)
    mult(m, 'stam_cost', 1.2)
    prefix(m, 'Skillful')
    return m


def superior(m):
    m = m.copy()
    change_tier(m, 3)
    mult(m, 'power', 1.2)
    mult(m, 'accuracy', 1.2)
    mult(m, 'time_cost', 0.8)
    mult(m, 'stam_cost', 1.4)
    prefix(m, 'Superior')
    return m


def advanced(m):
    m = m.copy()
    change_tier(m, 4)
    mult(m, 'power', 1.3)
    mult(m, 'accuracy', 1.3)
    mult(m, 'time_cost', 0.7)
    mult(m, 'stam_cost', 1.6)
    prefix(m, 'Advanced')
    return m


def expert(m):
    m = m.copy()
    change_tier(m, 5)
    mult(m, 'power', 1.4)
    mult(m, 'accuracy', 1.4)
    mult(m, 'time_cost', 0.6)
    mult(m, 'stam_cost', 1.8)
    prefix(m, 'Expert')
    return m


def ultimate(m):
    m = m.copy()
    change_tier(m, 6)
    mult(m, 'power', 1.5)
    mult(m, 'accuracy', 1.5)
    mult(m, 'time_cost', 0.5)
    mult(m, 'stam_cost', 2.0)
    prefix(m, 'Ultimate')
    return m


# todo ultra short kick, ultra long punch
def gen_moves(moves):
    new_moves = []  # move dicts
    move_names = set()  # strings
    gen_dict: Dict[Callable, List[Callable]] = read_move_word_combinations()
    for base_m in moves:
        chains = []  # variable-length chains of functions
        # get all chains of up to 2 functions for the base move
        for fun1, funs2 in gen_dict.items():
            chains.append((fun1,))
            for fun2 in funs2:
                chains.append((fun1, fun2))
                # used to have chains of up to 3 functions, but decided against
                # for fun3 in gen_dict[fun2]:
                #     chains.append((fun1, fun2, fun3))
        # apply the chains whenever possible
        for chain in chains:
            chain = reversed(chain)
            temp = base_m
            for fun in chain:
                new_move = fun(temp)
                if new_move is not None:
                    if new_move['name'] not in move_names:
                        new_moves.append(new_move)
                        move_names.add(new_move['name'])
                    temp = new_move
                else:
                    break

    return moves + new_moves


def main():
    from kf_lib.kung_fu.moves import read_moves

    base_moves, keys = read_moves(Path(MOVES_FOLDER, 'base_moves.txt'))
    save_moves(base_moves, keys, Path(MOVES_FOLDER, 'base_moves.txt'))
    extra_moves, keys = read_moves(Path(MOVES_FOLDER, 'extra_moves.txt'))
    save_moves(extra_moves, keys, Path(MOVES_FOLDER, 'extra_moves.txt'))
    style_moves, keys = read_moves(Path(MOVES_FOLDER, 'style_moves.txt'))
    save_moves(style_moves, keys, Path(MOVES_FOLDER, 'style_moves.txt'))
    takedown_moves = [m for m in extra_moves if 'takedown' in m['features']]
    moves = gen_moves(base_moves + takedown_moves)  # generated moves also include base_moves
    moves += extra_moves + style_moves
    save_moves(moves, keys, Path(MOVES_FOLDER, 'all_moves.txt'), sort_alph=True)
    df = pd.DataFrame(moves, columns=keys)
    df.to_csv(Path(MOVES_FOLDER, 'all_moves.csv'), sep=';')
    print(f'generated {len(moves)} moves')
    input('Press Enter to exit')


if __name__ == '__main__':
    main()
