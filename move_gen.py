import os


TIER1_QI_COST = 5
TIER2_QI_COST = 20
TIER3_QI_COST = 35
TIER4_QI_COST = 50
TIER5_QI_COST = 70
TIER_MAX = 10


def listr(s):
    """'x,x,x'string to list"""
    return [ss for ss in s.split(',') if ss]


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

    
def add(m, k, diff, mx=None, mn=None):
    m[k] += diff
    if mx is not None and m[k] > mx:
        m[k] = mx
    if mn is not None and m[k] < mn:
        m[k] = mn


def up_tier(m, n=1):
    add(m, 'tier', n, mx=TIER_MAX)

    
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
    m['functions'] = m['functions'][:] + [n]

    
def light(m):
    m = m.copy()
    mult(m, 'power', 0.8)
    mult(m, 'accuracy', 1.1)
    mult(m, 'stam_cost', 0.75)
    add(m, 'qi_cost', TIER1_QI_COST)
    up_tier(m)
    prefix(m, 'Light')
    return m


def heavy(m):
    m = m.copy()
    mult(m, 'power', 1.2)
    mult(m, 'accuracy', 0.9)
    mult(m, 'stam_cost', 1.25)
    add(m, 'qi_cost', TIER1_QI_COST)
    up_tier(m)
    prefix(m, 'Heavy')
    return m


def long(m):
    if m['distance'] >= 4:
        return None
    m = m.copy()
    add(m, 'distance', 1)
    up_tier(m)
    add(m, 'freq', -1, mn=1)
    add(m, 'qi_cost', TIER1_QI_COST)
    prefix(m, 'Long')
    return m


def short(m):
    if m['distance'] <= 1:
        return None
    m = m.copy()
    add(m, 'distance', -1)
    up_tier(m)
    add(m, 'freq', -1, mn=1)
    add(m, 'qi_cost', TIER1_QI_COST)
    prefix(m, 'Short')
    return m


def charging(m):
    m = m.copy()
    if m['distance'] <= 1:
        add(m, 'distance', 1)
    up_tier(m)
    add(m, 'freq', -1, mn=1)
    add(m, 'qi_cost', TIER1_QI_COST)
    mult(m, 'stam_cost', 1.1)
    mult(m, 'time_cost', 1.2)
    add(m, 'dist_change', -1)
    prefix(m, 'Charging')
    return m


def retreating(m):
    if m['distance'] >= 4:
        return None
    m = m.copy()
    up_tier(m)
    add(m, 'freq', -1, mn=1)
    add(m, 'qi_cost', TIER1_QI_COST)
    mult(m, 'stam_cost', 1.15)
    mult(m, 'time_cost', 1.25)
    add(m, 'dist_change', 1)
    prefix(m, 'Retreating')
    return m


def onslaught(m):
    m = m.copy()
    if m['distance'] <= 2:
        add(m, 'distance', 2)
    up_tier(m, 2)
    add(m, 'freq', -1, mn=1)
    add(m, 'qi_cost', TIER2_QI_COST)
    mult(m, 'stam_cost', 1.2)
    mult(m, 'time_cost', 1.4)
    add(m, 'complexity', 1)
    add(m, 'dist_change', -2)
    prefix(m, 'Onslaught')
    return m


def vanishing(m):
    if m['distance'] >= 3:
        return None
    m = m.copy()
    up_tier(m, 2)
    add(m, 'freq', -1, mn=1)
    add(m, 'qi_cost', TIER2_QI_COST)
    mult(m, 'stam_cost', 1.25)
    mult(m, 'time_cost', 1.45)
    add(m, 'complexity', 1)
    add(m, 'dist_change', 2)
    prefix(m, 'Vanishing')
    return m


def backflip(m):
    if 'kick' not in m['features'] or 'do_agility_based_dam' in m['functions']:
        return None
    m = m.copy()
    up_tier(m, 2)
    add(m, 'distance', -2)
    add(m, 'freq', -1, mn=1)
    add(m, 'qi_cost', TIER2_QI_COST)
    mult(m, 'stam_cost', 1.25)
    mult(m, 'time_cost', 1.45)
    add(m, 'complexity', 2)
    add(m, 'dist_change', 2)
    add_fun(m, 'do_agility_based_dam')
    prefix(m, 'Backflip')
    add_feat(m, 'acrobatic')
    return m


def pushing(m):
    if m['distance'] >= 4:
        return None
    m = m.copy()
    up_tier(m)
    add(m, 'qi_cost', TIER1_QI_COST)
    add_fun(m, 'do_knockback')
    prefix(m, 'Pushing')
    return m


def surprise(m):
    if any(feat in m['features'] for feat in ('shocking', 'surprise', 'debilitating')):
        return None
    m = m.copy()
    up_tier(m)
    add(m, 'qi_cost', TIER1_QI_COST)
    add_fun(m, 'try_shock_move')
    prefix(m, 'Surprise')
    return m


def fast(m):
    m = m.copy()
    mult(m, 'time_cost', 0.8)
    mult(m, 'stam_cost', 1.1)
    add(m, 'qi_cost', TIER1_QI_COST)
    up_tier(m)
    prefix(m, 'Fast')
    return m


def strong(m):
    m = m.copy()
    mult(m, 'power', 1.2)
    mult(m, 'stam_cost', 1.1)
    add(m, 'qi_cost', TIER1_QI_COST)
    up_tier(m, 2)
    prefix(m, 'Strong')
    return m


def precise(m):
    m = m.copy()
    mult(m, 'time_cost', 1.1)
    mult(m, 'accuracy', 1.2)
    add(m, 'qi_cost', TIER1_QI_COST)
    up_tier(m, 2)
    prefix(m, 'Precise')
    return m


def flying(m):
    if m['distance'] >= 4:
        return None
    m = m.copy()
    mult(m, 'power', 1.2)
    mult(m, 'stam_cost', 1.2)
    add(m, 'distance', 1)
    add(m, 'dist_change', -1)
    add(m, 'complexity', 1)
    up_tier(m)
    add(m, 'freq', -1, mn=1)
    add(m, 'qi_cost', TIER1_QI_COST)
    prefix(m, 'Flying')
    return m


def acrobatic(m):
    """More power and accuracy at the cost of increased complexity; can stun"""
    if 'do_agility_based_dam' in m['functions'] or 'do_strength_based_dam' in m['functions']:
        return None
    m = m.copy()
    mult(m, 'stam_cost', 1.25)
    add(m, 'complexity', 2)
    up_tier(m, 2)
    add_fun(m, 'do_agility_based_dam')
    add_fun(m, 'do_strength_based_dam')
    add(m, 'freq', -2, mn=1)
    add(m, 'qi_cost', TIER2_QI_COST)
    prefix(m, 'Acrobatic')
    return m


def power(m):
    if 'do_strength_based_dam' in m['functions']:
        return None
    m = m.copy()
    add(m, 'qi_cost', TIER2_QI_COST)
    up_tier(m, 2)
    add_fun(m, 'do_strength_based_dam')
    prefix(m, 'Power')
    return m


def trick(m):
    if 'do_agility_based_dam' in m['functions']:
        return None
    m = m.copy()
    add(m, 'qi_cost', TIER2_QI_COST)
    up_tier(m, 2)
    add_fun(m, 'do_agility_based_dam')
    prefix(m, 'Trick')
    return m


def lightning(m):
    if 'do_speed_based_dam' in m['functions']:
        return None
    m = m.copy()
    add(m, 'qi_cost', TIER2_QI_COST)
    up_tier(m, 2)
    add_fun(m, 'do_speed_based_dam')
    prefix(m, 'Lightning')
    return m


def energy(m):
    if 'do_qi_based_dam' in m['functions']:
        return None
    m = m.copy()
    add(m, 'qi_cost', TIER2_QI_COST)
    up_tier(m, 2)
    add_fun(m, 'do_qi_based_dam')
    prefix(m, 'Energy')
    return m


def ferocious(m):
    if 'do_speed_based_dam' in m['functions'] or 'do_strength_based_dam' in m['functions']:
        return None
    m = m.copy()
    mult(m, 'stam_cost', 1.2)
    add(m, 'qi_cost', TIER3_QI_COST)
    up_tier(m, 3)
    add_fun(m, 'do_speed_based_dam')
    add_fun(m, 'do_strength_based_dam')
    prefix(m, 'Ferocious')
    return m


def piercing(m):
    if 'do_agility_based_dam' in m['functions'] or 'do_speed_based_dam' in m['functions']:
        return None
    m = m.copy()
    mult(m, 'stam_cost', 1.2)
    add(m, 'qi_cost', TIER3_QI_COST)
    up_tier(m, 3)
    add_fun(m, 'do_agility_based_dam')
    add_fun(m, 'do_speed_based_dam')
    prefix(m, 'Piercing')
    return m


def shocking(m):
    if any(feat in m['features'] for feat in ('shocking', 'surprise', 'debilitating')):
        return None
    m = m.copy()
    up_tier(m, 2)
    add(m, 'qi_cost', TIER2_QI_COST)
    add_fun(m, 'do_shock_move')
    prefix(m, 'Shocking')
    return m


def solar(m):
    m = m.copy()
    up_tier(m, 2)
    add(m, 'qi_cost', TIER2_QI_COST)
    add_fun(m, 'do_stam_dam')
    prefix(m, 'Solar')
    return m


def nerve(m):
    m = m.copy()
    up_tier(m, 2)
    add(m, 'qi_cost', TIER2_QI_COST)
    add_fun(m, 'do_mob_dam')
    prefix(m, 'Nerve')
    return m


def debilitating(m):
    if any(feat in m['features'] for feat in ('shocking', 'surprise', 'debilitating')):
        return None
    m = m.copy()
    up_tier(m, 4)
    add(m, 'qi_cost', TIER4_QI_COST)
    add_fun(m, 'do_shock_move')
    add_fun(m, 'do_stam_dam')
    add_fun(m, 'do_mob_dam')
    add(m, 'freq', -1, mn=1)
    prefix(m, 'Debilitating')
    return m


def lethal(m):
    m = m.copy()
    add(m, 'qi_cost', TIER5_QI_COST)
    up_tier(m, 5)
    add_fun(m, 'try_insta_ko')
    add(m, 'freq', -2, mn=1)
    prefix(m, 'Lethal')
    return m


def skillful(m):
    m = m.copy()
    add(m, 'qi_cost', TIER1_QI_COST)
    up_tier(m, 1)
    mult(m, 'power', 1.1)
    mult(m, 'accuracy', 1.1)
    mult(m, 'time_cost', 0.9)
    mult(m, 'stam_cost', 1.2)
    prefix(m, 'Skillful')
    return m


def superior(m):
    m = m.copy()
    add(m, 'qi_cost', TIER2_QI_COST)
    up_tier(m, 2)
    mult(m, 'power', 1.2)
    mult(m, 'accuracy', 1.2)
    mult(m, 'time_cost', 0.8)
    mult(m, 'stam_cost', 1.4)
    prefix(m, 'Superior')
    return m


def advanced(m):
    m = m.copy()
    add(m, 'qi_cost', TIER3_QI_COST)
    up_tier(m, 3)
    mult(m, 'power', 1.3)
    mult(m, 'accuracy', 1.3)
    mult(m, 'time_cost', 0.7)
    mult(m, 'stam_cost', 1.6)
    prefix(m, 'Advanced')
    return m


def expert(m):
    m = m.copy()
    add(m, 'qi_cost', TIER4_QI_COST)
    up_tier(m, 4)
    mult(m, 'power', 1.4)
    mult(m, 'accuracy', 1.4)
    mult(m, 'time_cost', 0.6)
    mult(m, 'stam_cost', 1.8)
    prefix(m, 'Expert')
    return m


def ultimate(m):
    m = m.copy()
    add(m, 'qi_cost', TIER5_QI_COST)
    up_tier(m, 5)
    mult(m, 'power', 1.5)
    mult(m, 'accuracy', 1.5)
    mult(m, 'time_cost', 0.5)
    mult(m, 'stam_cost', 2.0)
    prefix(m, 'Ultimate')
    return m


# todo ultra short kick
def gen_moves(moves):
    new_moves = []  # move dicts
    move_names = set()  # strings
    gen_dict = {
        light: (shocking, solar, nerve),
        heavy: (shocking, solar, nerve),
        long: (light, heavy, charging, onslaught, backflip, pushing, surprise, shocking, solar, nerve, debilitating,
               lethal, fast, strong, precise, acrobatic, power, trick, lightning, energy, ferocious, piercing),
        short: (light, heavy, retreating, pushing, surprise, shocking, solar, nerve, debilitating, lethal, fast,
                strong, precise, acrobatic, power, trick, lightning, energy, ferocious, piercing),
        charging: (light, heavy, surprise, shocking, solar, nerve, debilitating, lethal, fast, strong, precise, power,
                   trick, lightning, energy, ferocious, piercing),
        retreating: (light, heavy, surprise, shocking, solar, nerve, debilitating, lethal, fast, strong, precise,
                     power, trick, lightning, energy, piercing),
        onslaught: (light, heavy, surprise, shocking, solar, nerve, debilitating, lethal, fast, strong, precise,
                    power, trick, lightning, energy, ferocious, piercing),
        vanishing: (light, heavy, surprise, shocking, solar, nerve, debilitating, lethal, fast, strong, precise,
                    power, trick, lightning, energy, piercing),
        backflip: (solar, nerve),
        pushing: (heavy, surprise, shocking, solar, nerve, fast, strong, precise),
        surprise: (light, backflip, fast, trick, lightning, piercing),
        fast: (light, backflip, flying, acrobatic, power, trick, lightning, energy, piercing, shocking, solar, nerve,
               debilitating, lethal),
        strong: (backflip, flying, acrobatic, trick, lightning, energy, piercing, shocking, solar, nerve, debilitating,
                 lethal),
        precise: (light, backflip, flying, acrobatic, trick, lightning, energy, piercing, shocking, solar, nerve,
                  debilitating, lethal),
        flying: (light, heavy, shocking, solar, nerve, power, trick, lightning, energy, ferocious, piercing,
                 debilitating, lethal),
        acrobatic: (charging, retreating, onslaught, vanishing, flying, shocking, solar, nerve, lightning, energy,
                    piercing, debilitating, lethal),
        power: (solar, nerve, debilitating, lethal),
        trick: (solar, nerve, debilitating, lethal),
        lightning: (solar, nerve, debilitating, lethal),
        energy: (solar, nerve, debilitating, lethal),
        ferocious: (solar, nerve, debilitating, lethal),
        piercing: (solar, nerve, debilitating, lethal),
        shocking: (solar, nerve, power, trick, lightning, energy, ferocious, piercing),
        solar: (),
        nerve: (),
        debilitating: (),
        lethal: (),
        skillful: (light, heavy, long, short, charging, retreating, onslaught, vanishing, backflip, pushing,
                   surprise, fast, strong, precise, flying, acrobatic, power, trick, lightning, energy, ferocious,
                   piercing, shocking, solar, nerve, debilitating, lethal),
        superior: (light, heavy, long, short, charging, retreating, onslaught, vanishing, backflip, pushing,
                   surprise, fast, strong, precise, flying, acrobatic, power, trick, lightning, energy, ferocious,
                   piercing, shocking, solar, nerve, debilitating, lethal),
        advanced: (light, heavy, long, short, charging, retreating, onslaught, vanishing, backflip, pushing,
                   surprise, fast, strong, precise, flying, acrobatic, power, trick, lightning, energy, ferocious,
                   piercing, shocking, solar, nerve, debilitating, lethal),
        expert: (light, heavy, long, short, charging, retreating, onslaught, vanishing, backflip, pushing,
                 surprise, fast, strong, precise, flying, acrobatic, power, trick, lightning, energy, ferocious,
                 piercing, shocking, solar, nerve, debilitating, lethal),
        ultimate: (light, heavy, long, short, charging, retreating, onslaught, vanishing, backflip, pushing,
                   surprise, fast, strong, precise, flying, acrobatic, power, trick, lightning, energy, ferocious,
                   piercing, shocking, solar, nerve, debilitating, lethal),
    }
    for base_m in moves:
        chains = []  # variable-length tuples of functions
        # get all 'chains' of up to 3 functions for the base move
        for fun1, funs2 in gen_dict.items():
            chains.append((fun1, ))
            for fun2 in funs2:
                chains.append((fun1, fun2))
                for fun3 in gen_dict[fun2]:
                    chains.append((fun1, fun2, fun3))
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


def gen_throws(moves):
    new_moves = []
    for m in moves:
        # todo generate more throws (function x function like other moves)
        for f, others in (
                (long, ()),
                (charging, ()),
                (fast, ()),
                (power, ()),
                (trick, ()),
                (lightning, ()),
                (energy, ()),
                (lethal, ()),
                (skillful, ()),
                (superior, ()),
                (advanced, ()),
                (expert, ()),
                (ultimate, ()),
        ):
            new = f(m)
            if new is not None:
                new_moves.append(new)

    return new_moves


def main():
    from kf_lib.moves import read_moves
    base_moves, keys = read_moves(os.path.join('move files', 'base_moves.txt'))
    save_moves(base_moves, keys, os.path.join('move files', 'base_moves.txt'))
    extra_moves, keys = read_moves(os.path.join('move files', 'extra_moves.txt'))
    save_moves(extra_moves, keys, os.path.join('move files', 'extra_moves.txt'))
    style_moves, keys = read_moves(os.path.join('move files', 'style_moves.txt'))
    save_moves(style_moves, keys, os.path.join('move files', 'style_moves.txt'))
    moves = gen_moves(base_moves)  # generated moves also include base_moves
    moves += extra_moves + style_moves
    throw = [m for m in extra_moves if m['name'] == 'Throw']  # this is awkward, but oh well
    throws = gen_throws(throw)  # generated moves DO NOT include source move(s) in this case
    moves += throws
    save_moves(moves, keys, os.path.join('move files', 'all_moves.txt'), sort_alph=True)

    input('Press Enter to exit')


if __name__ == '__main__':
    main()
