import random

from kf_lib.actors import fighter_factory
from kf_lib.kung_fu import techniques
from kf_lib.ui import pe
from kf_lib.utils import mean, percentage, rndint


class TechTester(object):
    BASELINE = 'BASELINE'
    baseline_allowed = True
    min_lv1 = 10
    max_lv1 = 15
    min_lv4 = 12
    max_lv4 = 15
    techs1 = techniques.get_upgradable_techs()
    techs2 = techniques.get_upgraded_techs()
    techs3 = techniques.get_weapon_techs()
    techs4 = techniques.get_style_techs()

    def __init__(
        self,
        n_fights=100,
        upgradable_techs=True,
        advanced_techs=True,
        weapon_techs=True,
        style_techs=True,
    ):
        self.n_fights = n_fights
        order = []
        if upgradable_techs:
            order.append(('upgradable techs', self.techs1))
        if advanced_techs:
            order.append(('advanced techs', self.techs2))
        if weapon_techs:
            order.append(('weapon techs', self.techs3))
        if style_techs:
            order.append(('style techs', self.techs4))
        self.order = order
        self.wins_vs1 = {}
        self.wins_crowd = {}
        self.wins_wp = {}
        self.wins_total = {}
        self.fight_types = (
            ('vs 1', self.wins_vs1),
            ('vs 4', self.wins_crowd),
            ('weapons', self.wins_wp),
            ('total', self.wins_total),
        )
        open('tech test.txt', 'w')  # clear the output file
        self.output = open('tech test.txt', 'a')
        self.run()
        self.output.close()
        pe()

    def run(self):
        print('\nrunning TechTester...\n')
        if self.baseline_allowed:
            self.test_tech()
        for name, techs in self.order:
            print('*' * 50)
            print(f'testing {name}...')
            print('*' * 50)
            for t in techs:
                self.test_tech(t)
            print('*' * 50)
            print('statistics...')
            print('*' * 50)
            self.stats(name, techs)

    def stats(self, name, techs):
        text = f"\n\n{'*' * 50}\n{name}\n{'*' * 50}\n\n"
        # self.wins_total = {t: 0 for t in techs}
        for legend, wins in self.fight_types:
            tuples = [(v, k) for k, v in wins.items() if k in techs]
            as_str = '\n'.join(
                [f'{v} {k} ({techniques.get_tech_descr(k)})' for v, k in sorted(tuples)]
            )
            text += f'\n  {legend}:\n{as_str}\n'
            # if not wins is self.wins_total:
            # print('wins\n', wins)
            # print('wins total\n', self.wins_total)
            # print('techs\n', techs)
            # for tech in techs:
            #     self.wins_total[tech] += wins[tech]
            mn, mx = min(wins.values()), max(wins.values())
            aver = mean(wins.values())
            rng = mx - mn
            text += f'\n min:{mn}, max:{mx}, range:{rng}, mean:{aver}'
            text += f'\n baseline: {wins[self.BASELINE]}\n\n'
            print(wins)
        print(text)
        self.output.write(text)

    def test_tech(self, t=None):
        """If t is None, False etc., get baseline result."""
        if t:
            print(f'testing {t} ({techniques.get_tech_descr(t)})')
        else:
            print('getting baseline...')
            t = self.BASELINE
        self.wins_vs1[t] = 0
        self.wins_crowd[t] = 0
        self.wins_wp[t] = 0
        self.wins_total[t] = 0
        for i in range(self.n_fights):
            a = fighter_factory.new_opponent(lv=rndint(self.min_lv1, self.max_lv1))
            b = fighter_factory.new_opponent(lv=a.level)
            if t != self.BASELINE:
                a.add_tech(t)
            if a.fight(b):
                self.wins_vs1[t] += 1
                self.wins_total[t] += 1
            a = fighter_factory.new_opponent(lv=rndint(self.min_lv4, self.max_lv4))
            if t != self.BASELINE:
                a.add_tech(t)
            c = fighter_factory.new_opponent(lv=1, n=4)
            if a.fight(c[0], en_allies=c[1:]):
                self.wins_crowd[t] += 1
                self.wins_total[t] += 1
            a = fighter_factory.new_opponent(lv=rndint(self.min_lv1, self.max_lv1))
            if t != self.BASELINE:
                a.add_tech(t)
            if random.choice((True, False)):
                a.arm('improvised')
            else:
                a.choose_best_norm_wp()
            b = fighter_factory.new_opponent(lv=a.level)
            b.arm(a.weapon.name)
            if a.fight(b):
                self.wins_wp[t] += 1
                self.wins_total[t] += 1
        print('  vs 1 wins: {}'.format(percentage(self.wins_vs1[t], self.n_fights)))
        print('  vs 4 wins: {}'.format(percentage(self.wins_crowd[t], self.n_fights)))
        print('  weapon wins: {}'.format(percentage(self.wins_wp[t], self.n_fights)))
