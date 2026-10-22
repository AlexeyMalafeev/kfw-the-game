import multiprocessing
import os
import random
from pathlib import Path

from tqdm import tqdm, trange

from kf_lib.actors import fighter_factory as ff
from kf_lib.actors.fighter import Fighter
from kf_lib.ai import fight_ai
from kf_lib.fighting import fight
from kf_lib.happenings.encounters import Ambush
from kf_lib.kung_fu import styles, techniques
from kf_lib.things import weapons
from kf_lib.ui import cls, menu, pak, pe, pretty_table
from kf_lib.utils import (
    add_to_dict, compare_dicts, get_time, mean, median, pcnt, summary, TESTS_FOLDER
)
from . import tech_test


FB_CHUNK_SIZE = 2000  # fights per seeded chunk of test_fight_balance
FB_TABLES = (
    ('atts', 'atts:'),
    ('full_atts', 'full atts:'),
    ('att_diffs', 'att diffs:'),
    ('buffs', 'style buffs:'),
    ('techs1', 'techs 1:'),
    ('techs2', 'techs 2:'),
    ('moves', 'moves:'),
)
FB_LEGEND = (
    'D1 = winners, D2 = losers, Diff% = (D1 - D2) / Sum. +-95% = noise margin of '
    'Diff% from the chunk-to-chunk spread; * = |Diff%| beyond it. With ~150 rows, '
    'a few * are expected by chance alone.'
)


def _fight_balance_chunk(rand_actions, n, seed):
    """Play one seeded chunk of test_fight_balance and return its tallies.

    Module-level and returning plain dicts, so it can run in a worker process.
    """
    random.seed(seed)  # reproducible snapshots: same styles, levels, fights
    dummy = ff.new_dummy_fighter(1)
    att_names = dummy.att_names
    t = {key: ({}, {}) for key, _ in FB_TABLES}  # (winners, losers)
    for att in att_names:
        for d in t['atts'] + t['full_atts']:
            d[att] = 0
    stats = {key: 0 for key in (
        'fights', 'no_winner', 'thrown', 'dodges', 'blocks', 'full_blocks',
        'counters', 'preemptives', 'stunned', 'criticals', 'epics')}
    stats.update(winner_hp=0.0, stamina_left=0.0, qp_left=0.0, actions=0,
                 guards=0, focuses=0, breaths=0)
    durations = []
    for _ in range(n):
        lv = random.randint(1, 20)
        f1 = ff.new_fighter(lv=lv)
        f1.name = 'Dummy A'
        f2 = ff.new_fighter(lv=lv)
        f2.name = 'Dummy B'
        if rand_actions:
            f1.set_fight_ai(fight_ai.BaseAI)
            f2.set_fight_ai(fight_ai.BaseAI)
        fgt = fight.AutoFight([f1], [f2])
        stats['fights'] += 1
        durations.append(fgt.get_seconds())
        for ftr in (f1, f2):
            fs = ftr.fight_stats
            for key in ('thrown', 'dodges', 'blocks', 'full_blocks', 'counters',
                        'preemptives', 'stunned', 'criticals', 'epics'):
                stats[key] += fs[key]
            used = fs['moves_used']  # strikes (incl. counters) and maneuvers
            stats['actions'] += sum(used.values())
            stats['guards'] += used.get('Guard', 0)
            stats['focuses'] += used.get('Focus', 0)
            stats['breaths'] += used.get('Catch Breath', 0)
            stats['stamina_left'] += ftr.stamina / ftr.stamina_max
            stats['qp_left'] += ftr.qp / ftr.qp_max if ftr.qp_max else 0
        if not fgt.winners:
            stats['no_winner'] += 1
            continue
        wnr = fgt.winners[0]
        lsr = fgt.losers[0]
        stats['winner_hp'] += wnr.hp / wnr.hp_max
        for i, ftr in enumerate((wnr, lsr)):
            # att values
            for att in att_names:
                t['atts'][i][att] += getattr(ftr, att)
                t['full_atts'][i][att] += getattr(ftr, att + '_full')
            # att diffs
            att_vals = [getattr(ftr, att) for att in att_names]
            add_to_dict(t['att_diffs'][i], max(att_vals) - min(att_vals), 1)
            # techs
            for t_obj in ftr.techs:
                if t_obj.is_upgradable:
                    add_to_dict(t['techs1'][i], t_obj.name, 1)
                elif t_obj.is_advanced:
                    add_to_dict(t['techs2'][i], t_obj.name, 1)
                for feature in t_obj.descr_short.split(', '):
                    add_to_dict(t['buffs'][i], feature, 1)
                    if not feature.strip():
                        raise ValueError(
                            f'Missing descr feature in the following tech: {t_obj}')
            # moves
            for m in ftr.moves:
                for feat in m.features:
                    add_to_dict(t['moves'][i], feat, 1)
    return {'tables': t, 'stats': stats, 'durations': durations}


def _apply_variants(variants):
    """'FILE:NAMES' -> FILE's apply(NAMES) (rule experiments); '' does nothing."""
    if not variants:
        return
    import importlib.util
    path, names = variants.rsplit(':', 1)
    spec = importlib.util.spec_from_file_location('fb_variants', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply(names)


def _fb_worker_init(cwd, variants):
    os.chdir(cwd)  # workers import kf_lib, which reads data files relative to the cwd
    _apply_variants(variants)


def _fight_balance_chunk_indexed(i_chunk):
    i, chunk = i_chunk
    return i, _fight_balance_chunk(*chunk)


def _diff_margin(chunk_pairs, key):
    """95% margin of the pooled Diff% of `key`, from the spread between chunks
    (cluster variance of the ratio sum(D1 - D2) / sum(D1 + D2)); None if < 2."""
    ys = [w.get(key, 0) - lo.get(key, 0) for w, lo in chunk_pairs]
    ss = [w.get(key, 0) + lo.get(key, 0) for w, lo in chunk_pairs]
    k, total = len(ys), sum(ss)
    if k < 2 or not total:
        return None
    ratio = sum(ys) / total
    var = k / (k - 1) * sum((y - ratio * s) ** 2 for y, s in zip(ys, ss))
    return 1.96 * 100 * var ** 0.5 / total


def _format_fb_table(results, key):
    chunk_pairs = [r['tables'][key] for r in results]
    d_wnr, d_lsr = {}, {}
    for w, lo in chunk_pairs:
        for k, v in w.items():
            add_to_dict(d_wnr, k, v)
        for k, v in lo.items():
            add_to_dict(d_lsr, k, v)
    tups = compare_dicts(d_wnr, d_lsr, sort_col_index=3)
    rows = [tups[0] + ('+-95%', '')]
    for row in tups[1:]:
        margin = _diff_margin(chunk_pairs, row[1])
        if margin is None:
            rows.append(row + ('-', ''))
        else:
            rows.append(row + (round(margin, 1), '*' if abs(row[4]) > margin else ''))
    lines = ['\n', pretty_table(rows), '', summary(d_wnr), FB_LEGEND, '']
    return '\n'.join(lines)


def _format_fight_stats(results):
    st = {}
    durations = []
    for r in results:
        for k, v in r['stats'].items():
            st[k] = st.get(k, 0) + v
        durations.extend(r['durations'])
    durations.sort()
    n_f = st['fights']
    n_won = n_f - st['no_winner']
    thrown = st['thrown'] or 1
    clean = st['thrown'] - st['dodges'] - st['blocks']

    def per_fight(k, nd=2):
        return round(st[k] / n_f, nd)

    def share(v):
        return f'{v / thrown * 100:.1f}%'

    def act_share(v):
        return f'{v / (st["actions"] or 1) * 100:.1f}%'

    lines = [
        '',
        f'fights: {n_f}, no winner: {st["no_winner"]}',
        f'fight length, s: mean {mean(durations):.1f}, median {median(durations)}, '
        f'slowest 10% from {durations[int(len(durations) * 0.9)]}',
        f'per fight: strikes {per_fight("thrown", 1)}, counters {per_fight("counters")}, '
        f'preemptives {per_fight("preemptives")}, criticals {per_fight("criticals")}, '
        f'epics {per_fight("epics", 3)}, stuns {per_fight("stunned")}',
        f'strike outcomes: dodged {share(st["dodges"])}, '
        f'fully blocked {share(st["full_blocks"])}, '
        f'partly blocked {share(st["blocks"] - st["full_blocks"])}, '
        f'clean hits {share(clean)}',
        f'actions (counters included): strikes {act_share(st["thrown"])}, '
        f'Guard {act_share(st["guards"])}, Focus {act_share(st["focuses"])}, '
        f'Catch Breath {act_share(st["breaths"])}, other maneuvers '
        f'{act_share(st["actions"] - st["thrown"] - st["guards"] - st["focuses"] - st["breaths"])}',
        f'at fight end: winner\'s HP {st["winner_hp"] / max(n_won, 1) * 100:.1f}% of max; '
        f'stamina {st["stamina_left"] / (2 * n_f) * 100:.1f}%, '
        f'QP {st["qp_left"] / (2 * n_f) * 100:.1f}% of max (both fighters)',
        '',
    ]
    return '\n'.join(lines)


class Tester(object):
    def __init__(self, game):
        self.game = self.g = game

    def test_crowd_significance(self):
        f1 = []
        f2 = []
        print('testing crowd significance')
        for j in range(2, 11):
            wins = 0
            for i in range(100):
                f1 = ff.new_opponent(lv=5, n=5)
                f2 = ff.new_opponent(lv=5, n=j)
                if f1[0].fight(f2[0], allies=f1[1:], en_allies=f2[1:]):
                    wins += 1
            exp1 = sum(f.get_exp_worth() for f in f1)
            exp2 = sum(f.get_exp_worth() for f in f2)
            print('exp:', exp1, exp2)
            print(f'wins: {wins}')
        pe()

    # def test_disarm(self):
    #     fs = ff.new_fighter(5, n=2)
    #     for f in fs:
    #         f.add_tech('Leaping Monkey')
    #         f.add_tech('Crouching Monkey')
    #         f.arm()
    #     # f1, f2 = fs
    #     fight.spectate(*fs)
    #     pak()

    def test_enc(self, enc_class_string, test=False):
        self.g.enc.run_enc(enc_class_string, test)

    def test_enemy(self):
        p = self.g.current_player
        e = ff.new_thug()
        if not p.enemies:
            p.add_enemy(e)
        Ambush(p, False)

    def test_exp(self, lv_max=20, n=100):
        results = []
        for lv in range(1, lv_max + 1):
            exp = []
            for _ in range(n):
                f = ff.new_fighter(lv=lv)
                exp.append(f.get_exp_worth())
            v = mean(exp)
            print(lv, v)
            results.append(v)
        return results

    def test_ffa_win_rates(self, n_min=2, n_max=8, lv=10, n_fights=100):
        """Compare win rates in free-for-all vs united-group fights at equal levels.
        In a plain FFA of n equal fighters, fighter 1 should win ~1/n of the time;
        against a united group of n-1 the win rate should be much lower; in a group
        FFA of g groups, group 1 should win ~1/g."""
        lines = [['n', 'FFA', 'expected 1/n', 'vs united n-1']]
        for n in range(n_min, n_max + 1):
            ffa_wins = united_wins = 0
            for _ in trange(n_fights):
                fs = ff.new_fighter(lv=lv, n=n)
                if fight.free_for_all(fs):
                    ffa_wins += 1
                f1 = ff.new_fighter(lv=lv)
                enemies = ff.new_fighter(lv=lv, n=n - 1)
                if not isinstance(enemies, list):
                    enemies = [enemies]
                if f1.fight(enemies[0], en_allies=enemies[1:]):
                    united_wins += 1
            lines.append([
                str(n),
                pcnt(ffa_wins, n_fights, as_string=True),
                pcnt(1, n, as_string=True),
                pcnt(united_wins, n_fights, as_string=True),
            ])
        table1 = pretty_table(lines, sep='\t')
        group_lines = [['groups', 'group size', 'win rate', 'expected 1/g']]
        for n_groups in range(2, 5):
            for group_size in (2, 3):
                wins = 0
                for _ in trange(n_fights):
                    groups = [ff.new_fighter(lv=lv, n=group_size) for _ in range(n_groups)]
                    if fight.group_free_for_all(groups):
                        wins += 1
                group_lines.append([
                    str(n_groups),
                    str(group_size),
                    pcnt(wins, n_fights, as_string=True),
                    pcnt(1, n_groups, as_string=True),
                ])
        table2 = pretty_table(group_lines, sep='\t')
        legend = f'free-for-all win rates, all fighters lv.{lv}, {n_fights} fights per cell'
        print(f'\n{legend}\n')
        print('plain FFA vs united group:\n')
        print(table1)
        print('\ngroup FFA:\n')
        print(table2)
        file_path = Path(TESTS_FOLDER, f'ffa win rates lv={lv} n={n_fights}.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            print(get_time(), file=f)
            print(f'\n{legend}\n', file=f)
            print('plain FFA vs united group:\n', file=f)
            print(table1, file=f)
            print('\ngroup FFA:\n', file=f)
            print(table2, file=f)
        print(f'\nSaved results to "{file_path}"')

    def test_fight(self, num_fighters1=1, num_fighters2=1, armed=False):
        p = self.g.current_player
        allies = []
        if num_fighters1 > 1:
            for i in range(1, num_fighters1):
                allies.append(Fighter(f'Ally {i}'))
        enemies = []
        for i in range(1, num_fighters2 + 1):
            enemies.append(Fighter(f'Enemy {i}'))
        if len(enemies) > 1:
            en_allies = enemies[1:]
        else:
            en_allies = []
        if armed:
            for f in [p] + allies + enemies:
                f.arm('chopsticks')
        p.fight(enemies[0], allies, en_allies, hide_stats=False)

    def test_fight_balance(self, rand_actions=True, n=100_000, seed=42,
                           chunk_size=FB_CHUNK_SIZE, workers=None,
                           file_name_prefix='test f.b.', variants='', out_path=None):
        """Mirror matches at random levels, tallying what winners vs losers had.

        The n fights are split into chunks of chunk_size; chunk i is seeded with
        seed + i, so the report depends only on (n, seed, chunk_size), not on how
        many worker processes play the chunks. The chunk-to-chunk spread gives
        each row's 95% noise margin.

        variants='FILE:NAMES' calls FILE's apply(NAMES) in every worker before
        its fights — monkeypatched rule experiments, see
        dev_scripts/testing/rule_variants.py. out_path overrides the report path.
        """
        file_name = f'{file_name_prefix} rand.act.={rand_actions} n={n}.txt'
        file_path = Path(out_path) if out_path else Path(TESTS_FOLDER, file_name)
        if variants:
            path, names = variants.rsplit(':', 1)
            variants = f'{Path(path).resolve()}:{names}'  # workers start elsewhere
        chunks = [(rand_actions, min(chunk_size, n - start), seed + i)
                  for i, start in enumerate(range(0, n, chunk_size))]
        output = '-' * 40 + '\n\n'
        if not rand_actions:
            output += f'fight AI={fight_ai.DefaultFightAI.__name__}\n'
        output += (f'rand_actions={rand_actions}\nseed={seed}\nn={n}\n'
                   f'chunks={len(chunks)} x {chunk_size} fights (chunk i: seed + i)\n'
                   + (f'variants={variants}\n' if variants else '') + '\n')
        print(output, end='')

        results = [None] * len(chunks)
        workers = min(workers or os.cpu_count() or 1, len(chunks))
        with tqdm(total=n) as bar:
            if workers == 1:
                _apply_variants(variants)
                for i, chunk in enumerate(chunks):
                    results[i] = _fight_balance_chunk(*chunk)
                    bar.update(chunk[1])
            else:
                # spawn (the default on macOS/Windows) everywhere: fresh worker
                # processes, so results never depend on the platform
                ctx = multiprocessing.get_context('spawn')
                with ctx.Pool(workers, initializer=_fb_worker_init,
                              initargs=(os.getcwd(), variants)) as pool:
                    for i, res in pool.imap_unordered(_fight_balance_chunk_indexed,
                                                      enumerate(chunks)):
                        results[i] = res
                        bar.update(chunks[i][1])

        with open(file_path, 'w', encoding='utf-8') as fh:
            print(get_time(), file=fh)
            fh.write(output)
            sections = [('fight stats:', _format_fight_stats(results))]
            for key, legend in FB_TABLES:
                sections.append((legend, _format_fb_table(results, key)))
            for legend, s in sections:
                print(legend, s, sep='\n\n')
                print(legend, s, sep='\n\n', file=fh)
        print(f'\nSaved results to "{file_path}"')

    def test_level_vs_crowds(self, n_crowd_min=2, n_crowd_max=5, lv_max=20, n_fights=1000):
        for lv_in_crowd in range(1, 6):
            print()
            print('Level in crowd:', lv_in_crowd)
            lines = [[''] + [f'n={n}' for n in range(n_crowd_min, n_crowd_max + 1)]]
            print('\t'.join(lines[0]))
            for lv in range(1, lv_max + 1):
                s = f'lv.{lv}'
                lines.append([s])
                print(s, end='\t')
                for n in range(n_crowd_min, n_crowd_max + 1):
                    wins = 0
                    for i in range(n_fights):
                        f1 = ff.new_fighter(lv=lv)
                        fs2 = ff.new_fighter(lv=lv_in_crowd, n=n)
                        if f1.fight(fs2[0], en_allies=fs2[1:]):
                            wins += 1
                    s = pcnt(wins, n_fights, as_string=True)
                    lines[-1].append(s)
                    print(s, end='\t')
                print('')
            table = pretty_table(lines, sep='\t')
            file_path = Path(TESTS_FOLDER, f'lv_vs_crowd {lv_in_crowd} {n_fights}.txt')
            print(table, file=open(file_path, 'w', encoding='utf-8'))

    def test_level_significance(self, rep=100):
        """Make a table of 1-20 levels fighting against each other"""
        first_line = ('LV',) + tuple(range(1, 21))
        table = [first_line]
        sm_table = [first_line]
        for lv1 in range(1, 21):
            print('level', lv1)
            table.append(
                [
                    lv1,
                ]
            )
            sm_table.append(
                [
                    lv1,
                ]
            )
            for lv2 in range(1, 21):
                wins = 0
                for i in range(rep):
                    f1 = ff.new_opponent(lv=lv1)
                    f2 = ff.new_opponent(lv=lv2)
                    if f1.fight(f2):
                        wins += 1
                table[-1].append(pcnt(wins, rep, n=0, as_string=True))
                sm_table[-1].append(pcnt(wins + 1, rep + 1, n=0, as_string=True))
        s = pretty_table(table)
        s += '\n\nWith smoothing:\n\n'
        s += pretty_table(sm_table)
        print(s)
        file_path = Path(TESTS_FOLDER, f'test level significance rep={rep}.txt')
        print(s, file=open(file_path, 'w'))

    def test_rand_att_schemes(self):
        wins = {'0': 0, '1': 0, '2': 0}
        for k in (1, 1, 5, 5, 10, 10, 10, 20, 20, 20):
            group_0 = []
            group_1 = []
            group_2 = []
            # for s in styles.default_styles:
            for s in [styles.BEGGAR_STYLE, styles.THIEF_STYLE, styles.DRUNKARD_STYLE]:
                group_0.append(Fighter(name='0', style=s.name, level=k, rand_atts_mode=0))
                group_1.append(Fighter(name='1', style=s.name, level=k, rand_atts_mode=1))
                group_2.append(Fighter(name='2', style=s.name, level=k, rand_atts_mode=2))
            for i in range(len(group_0)):
                print(i + 1)
                print(group_0[i])
                print(group_1[i])
                print(group_2[i])
                for gr_a, gr_b in (
                    (group_0, group_1),
                    (group_0, group_2),
                    (group_1, group_2),
                    (group_1, group_0),
                    (group_2, group_0),
                    (group_2, group_1),
                ):
                    wins_loc = 0
                    f1 = gr_a[i]
                    f2 = gr_b[i]
                    for j in range(10):
                        if f1.fight(f2):
                            wins[f1.name] += 1
                            wins_loc += 1
                    print(f1.name, 'wins vs', f2.name, '-', wins_loc)
        print('\nTOTAL WINS')
        print(wins)
        input('Press Enter')

    # todo remove this, deprecated?
    def test_story(self, story_class):
        s = story_class(self.g)
        s.start(self.g.current_player)
        while s.state != -1:
            s.advance()
        print("End of the story")
        pak()

    def test_techs(self):
        tech_test.TechTester()

    def test_tech_significance(self):
        lv = 10
        for j in range(1, 11):
            # f = ff.new_opponent(lv=j)
            # print('enemy at lv.{} = {} exp'.format(f.level, f.get_exp_worth()))
            wins = 0
            f1, f2 = None, None  #
            for i in range(100):
                f1 = ff.new_opponent(lv=lv)
                pool1 = techniques.get_learnable_techs(f1)
                sample1 = random.sample(pool1, 5)
                for t in sample1:
                    f1.learn_tech(t)
                f2 = ff.new_opponent(lv=lv)
                pool2 = techniques.get_learnable_techs(f2)
                sample2 = random.sample(pool2, j)
                for t in sample2:
                    f2.learn_tech(t)
                if f1.fight(f2):
                    wins += 1
            print('exp1', f1.get_exp_worth(), 'exp2', f2.get_exp_worth())
            print(f'wins: {wins}')
        pe()

    def test_weapons(self):
        p = self.g.current_player
        while True:
            cls()
            print(p.get_all_atts_str(), p.weapon)
            w = menu(weapons.all_weapons + ('go back',), 'Choose a weapon to equip:')
            if w == 'go back':
                break
            p.arm(w)

    def two_players_fight(self):
        self.g.players[0].fight(self.g.players[1], hide_stats=False)

    def quick_exp(self, exp=1000):
        self.g.current_player.gain_exp(exp)

    def quick_money(self, money=10000):
        self.g.current_player.earn_money(money)
