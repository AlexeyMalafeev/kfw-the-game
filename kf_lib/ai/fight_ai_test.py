from tqdm import trange


from kf_lib.fighting.fight import AutoFight
from kf_lib.actors import fighter_factory as ff
from kf_lib.utils import rndint


TESTS_FOLDER = 'tests'


class FightAITest(object):
    def __init__(self, ai1, ai2, rep=1000, write_log=False, suppress_output=False):
        """rep will be effectively doubled for fairness - each random fighter will use both
        tested AIs in turn."""
        self.ai1 = ai1
        self.ai2 = ai2
        self.wins = [0, 0]
        self.aname = self.ai1.__name__
        self.bname = self.ai2.__name__
        self.rep = rep
        self.write_log = write_log
        self.suppress_output = suppress_output
        self.output_file = open(os.path.join(TESTS_FOLDER, 'fight ai test.txt'), 'a')
        self.run_test()
        self.output_total()
        self.output_file.close()

    def get_allies(self):
        return [], []

    def get_levels(self):
        lv = rndint(1, 20)
        return lv, lv

    def run_test(self):
        if not self.suppress_output:
            s = f'\n{self.__class__.__name__}\n{self.aname} vs {self.bname}'
            print(s)
            print(s, file=self.output_file)
            range_fun = trange
        else:
            range_fun = range
        for _ in range_fun(self.rep):
            lv1, lv2 = self.get_levels()
            f1 = ff.new_opponent(lv=lv1)
            f2 = ff.new_opponent(lv=lv2)
            al1, al2 = self.get_allies()
            for ai1, ai2, ind1, ind2 in ((self.ai1, self.ai2, 0, 1), (self.ai2, self.ai1, 1, 0)):
                f1.set_fight_ai(ai1, self.write_log)
                f2.set_fight_ai(ai2, self.write_log)
                for al in al1:
                    al.set_fight_ai(ai1, self.write_log)
                for al in al2:
                    al.set_fight_ai(ai2, self.write_log)
                f = AutoFight([f1] + al1, [f2] + al2)
                if f.winners and f1 in f.winners:
                    self.wins[ind1] += 1
                elif f.winners and f2 in f.winners:
                    self.wins[ind2] += 1

    def output_total(self):
        if not self.suppress_output:
            s = 'total: {}\n{} wins: {}\n{} wins: {}'.format(
                self.rep * 2, self.aname, self.wins[0], self.bname, self.wins[1]
            )
            print(s)
            print(s, file=self.output_file)


class CrowdVsCrowd(FightAITest):
    def get_allies(self):
        al1, al2 = [], []
        n1 = rndint(0, 3)
        n2 = rndint(0, 3)
        for i in range(n1):
            al1.append(ff.new_opponent(lv=rndint(1, 5)))
        for i in range(n2):
            al2.append(ff.new_opponent(lv=rndint(1, 5)))
        return al1, al2


class CrowdVsCrowdFair(FightAITest):
    def get_allies(self):
        al1, al2 = [], []
        n1 = n2 = rndint(4, 9)
        al_lv = lv = rndint(1, 5)
        for i in range(n1):
            al1.append(ff.new_opponent(lv=al_lv))
        for i in range(n2):
            al2.append(ff.new_opponent(lv=al_lv))
        return al1, al2


class OneVsCrowd(FightAITest):
    def get_allies(self):
        al1, al2 = [], []
        n2 = rndint(0, 3)
        for i in range(n2):
            al2.append(ff.new_opponent(lv=1))
        return al1, al2

    def get_levels(self):
        return rndint(1, 20), 1
