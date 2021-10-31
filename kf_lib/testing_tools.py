from .happenings import encounters
from .fighting import fight
from .ai import fight_ai
from .actors.fighter import Fighter
from .actors import fighter_factory as ff
from .kung_fu import styles, techniques
from .things import weapons
from . import tech_test
from .utils.utilities import *

TESTS_FOLDER = 'tests'


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

    def test_disarm(self):
        fs = ff.new_fighter(5, n=2)
        for f in fs:
            f.add_tech('Leaping Monkey')
            f.add_tech('Crouching Monkey')
            f.arm()
        # f1, f2 = fs
        fight.spectate(*fs)
        pak()

    def test_enc(self, enc_class_string, test=False):
        self.g.enc.run_enc(enc_class_string, test)

    def test_enemy(self):
        p = self.g.current_player
        e = ff.new_thug()
        if not p.enemies:
            p.add_enemy(e)
        encounters.Ambush(p, False)

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

    def test_fight_balance(self, rand_actions=True, n=1000, file_name_prefix='test f.b.'):
        file_name = f'{file_name_prefix} rand.act.={rand_actions} n={n}.txt'
        file_path = os.path.join(TESTS_FOLDER, file_name)
        with open(file_path, 'w') as f:
            f.write(get_time() + '\n')

        def _output_results(d_wnr, d_lsr, first_line=''):
            tups = dict_comp(d_wnr, d_lsr, sort_col_index=3)
            lines = ['\n' + first_line, pretty_table(tups), '', summary(d_wnr), '']
            s = '\n'.join(lines)
            print(s)
            with open(file_name, 'a') as f_out:
                f_out.write(s)

        output = '-' * 40 + '\n\n'
        if not rand_actions:
            output += f'fight AI={fight_ai.DefaultFightAI.__name__}\n'
        output += f'rand_actions={rand_actions}\n\n'
        # init dicts
        dummy = ff.new_dummy_fighter(1)
        att_names = dummy.att_names
        d_atts_wnr = {att: 0 for att in att_names}
        d_atts_lsr = {att: 0 for att in att_names}
        d_full_atts_wnr = {att: 0 for att in att_names}
        d_full_atts_lsr = {att: 0 for att in att_names}
        att_diffs_wnr = {}
        att_diffs_lsr = {}
        styles_wnr = {}
        styles_lsr = {}
        techs1_wnr = {}
        techs1_lsr = {}
        techs2_wnr = {}
        techs2_lsr = {}
        moves_wnr = {}
        moves_lsr = {}
        # fight!
        for i in range(n):
            if not i % (n / 20):
                print(f'fight {i + 1} / {n}')
            lv = random.randint(1, 20)
            f1 = ff.new_fighter(lv=lv)
            f1.name = 'Dummy A'
            f2 = ff.new_fighter(lv=lv)
            f2.name = 'Dummy B'
            if rand_actions:
                f1.set_fight_ai(fight_ai.BaseAI)
                f2.set_fight_ai(fight_ai.BaseAI)
            f = fight.AutoFight([f1], [f2])
            if f.winners:
                wnr = f.winners[0]
                lsr = f.losers[0]
                # att values
                for att in att_names:
                    for f, d, d_full in (
                        (wnr, d_atts_wnr, d_full_atts_wnr),
                        (lsr, d_atts_lsr, d_full_atts_lsr),
                    ):
                        d[att] += getattr(f, att)
                        d_full[att] += getattr(f, att + '_full')
                # att diffs
                for f, d in ((wnr, att_diffs_wnr), (lsr, att_diffs_lsr)):
                    att_vals = [getattr(f, att) for att in att_names]
                    att_diff = max(att_vals) - min(att_vals)
                    add_to_dict(d, att_diff, 1)
                # styles
                add_to_dict(styles_wnr, wnr.style.name, 1)
                add_to_dict(styles_lsr, lsr.style.name, 1)
                # techs
                for f, d1, d2 in ((wnr, techs1_wnr, techs2_wnr), (lsr, techs1_lsr, techs2_lsr)):
                    for t in f.techs:
                        t_obj = techniques.get_tech_obj(t)
                        if t_obj.is_upgradable:
                            add_to_dict(d1, t, 1)
                        elif t_obj.is_upgraded:
                            add_to_dict(d2, t, 1)
                # moves
                for f, d in ((wnr, moves_wnr), (lsr, moves_lsr)):
                    for m in f.moves:
                        for feat in m.features:
                            add_to_dict(d, feat, 1)
        # output
        tuples = (
            (d_atts_wnr, d_atts_lsr, 'atts:'),
            (d_full_atts_wnr, d_full_atts_lsr, 'full atts:'),
            (att_diffs_wnr, att_diffs_lsr, 'att diffs:'),
            (styles_wnr, styles_lsr, 'styles:'),
            (techs1_wnr, techs1_lsr, 'techs 1:'),
            (techs2_wnr, techs2_lsr, 'techs 2:'),
            (moves_wnr, moves_lsr, 'moves:'),
        )
        for d_w, d_l, legend in tuples:
            _output_results(d_w, d_l, legend)
        input('Press Enter')

    def test_level_vs_crowds(self, n_crowd_min=2, n_crowd_max=5, lv_max=20, n_fights=1000):
        for lv_in_crowd in range(1, 6):
            print()
            print('Level in crowd:', lv_in_crowd)
            lines = [[''] + [f'n={n}' for n in range(n_crowd_min, n_crowd_max + 1)]]
            print('\t'.join(lines[0]))
            for lv in range(1, lv_max + 1):
                f1 = ff.new_fighter(lv=lv)
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
            file_path = os.path.join(TESTS_FOLDER, f'lv_vs_crowd {lv_in_crowd} {n_fights}.txt')
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
        file_path = os.path.join(TESTS_FOLDER, f'test level significance rep={rep}.txt')
        print(s, file=open(file_path, 'w'))

    def test_rand_att_schemes(self):
        wins = {'0': 0, '1': 0, '2': 0}
        for k in (1, 1, 5, 5, 10, 10, 10, 20, 20, 20):
            group_0 = []
            group_1 = []
            group_2 = []
            # for s in styles.default_styles:
            for s in [styles.BEGGAR_STYLE, styles.THIEF_STYLE, styles.DRUNKARD_STYLE]:
                group_0.append(Fighter(name='0', style_name=s.name, level=k, rand_atts_mode=0))
                group_1.append(Fighter(name='1', style_name=s.name, level=k, rand_atts_mode=1))
                group_2.append(Fighter(name='2', style_name=s.name, level=k, rand_atts_mode=2))
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

    def quick_exp(self, exp=10000):
        self.g.current_player.gain_exp(exp)

    def quick_money(self, money=10000):
        self.g.current_player.earn_money(money)
