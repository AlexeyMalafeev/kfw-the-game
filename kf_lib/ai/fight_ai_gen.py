from copy import copy
from pathlib import Path
# from pprint import pprint
import random
import time
from typing import List


from tqdm import trange


from kf_lib.ai import fight_ai, fight_ai_test
from kf_lib.utils.utilities import rnd


class GeneticAlgorithm(object):
    def __init__(
            self,
            pop_size: int,
            gene_names: List[str],
            mut_prob: float,
            infighting: bool,
            comment: str = None
    ):
        """mode: if infighting is False, will train against current DefaultFightAI"""
        assert pop_size % 2 == 0, 'pop_size must be divisible by 2'
        self.pop_size = pop_size
        self.gene_names = gene_names
        self.mut_prob = mut_prob
        self.fitness_function = self.fitness_infighting if infighting else self.fitness
        self.comment = comment

        # setup
        self.n_genes: int = len(self.gene_names)
        self.n_top: int = self.pop_size // 2
        self.population = [[rnd() for _ in range(self.n_genes)] for _ in range(pop_size)]
        self.fit_values = []
        self.fit_values_sorted = []
        self.max_possible_fit_value = 0
        self.all_time_record = 0
        self.record_holder = None
        self.record_generation = None
        self.fittest = []
        self.n_generations = 0
        self.curr_generation = 0
        self.mutations_occurred = 0

    # todo remove doubles -> generate random individuals after a few failed crossover attempts
    def crossover(self):
        new_population = self.fittest[:]
        # to cancel out the effect of sorting when performing selection
        random.shuffle(new_population)
        for i in range(0, self.n_top, 2):
            parent_a = new_population[i]
            parent_b = new_population[i + 1]
            ind = list(range(self.n_genes))
            random.shuffle(ind)
            ind = ind[:random.randint(1, len(ind) - 1)]
            child_a = parent_a[:]
            child_b = parent_b[:]
            for ii in ind:
                child_a[ii], child_b[ii] = child_b[ii], child_a[ii]
            new_population.extend([child_a, child_b])
        self.population = new_population

    def fitness(self):
        """Set self.fit_values"""
        self.fit_values = []
        n_rep = 250
        self.max_possible_fit_value = n_rep * 2
        for individual in self.population:
            ai = copy(fight_ai.DefaultGeneticAIforTraining)
            for i, name in enumerate(self.gene_names):
                setattr(ai, name, individual[i])
            t = fight_ai_test.FightAITest(
                ai,
                fight_ai.DefaultFightAI,
                rep=n_rep,
                write_log=False,
                suppress_output=True,
            )
            self.fit_values.append(t.wins[0])

    def fitness_infighting(self):
        """Set self.fit_values"""
        self.fit_values = []
        n_rep = 10
        self.max_possible_fit_value = 2 * n_rep * len(self.population)
        for individual in self.population:
            score = 0
            ai = fight_ai.DefaultGeneticAIforTraining
            for i, name in enumerate(self.gene_names):
                setattr(ai, name, individual[i])
            for individual2 in self.population:
                ai2 = copy(fight_ai.DefaultGeneticAIforTraining)
                for i, name in enumerate(self.gene_names):
                    setattr(ai2, name, individual2[i])
                t = fight_ai_test.FightAITest(
                    ai,
                    ai2,
                    rep=n_rep,
                    write_log=False,
                    suppress_output=True,
                )
                score += t.wins[0]
            self.fit_values.append(score)

    def mutation(self):
        if not self.mut_prob:
            return
        for individual in self.population[len(self.fittest):]:
            if rnd() <= self.mut_prob:
                i = random.randint(0, self.n_genes - 1)
                new_val = rnd()  # random mutation
                individual[i] = new_val
                self.mutations_occurred += 1

    def output(self):
        time_s = time.ctime()
        top_res_lines = []
        for i in range(len(self.fittest)):
            top_res_lines.append(f'{self.fit_values_sorted[i]} {self.fittest[i]}')
        top_res = '\n'.join(top_res_lines)
        out_s = f'''{time_s}
Generation {self.curr_generation + 1} of {self.n_generations}
Mutations: {self.mutations_occurred} (prob {self.mut_prob})
Top fit values / individuals:
{top_res}
Max possible fit value: {self.max_possible_fit_value}
All-time record: {self.all_time_record} @ generation {self.record_generation}
Record holder: {self.record_holder}
'''
        file_name = f'fight_ai_gen output {self.comment} generation_{self.curr_generation}.txt'
        file_path = Path('tests', 'genetic', file_name)
        print(out_s, file=open(file_path, 'w', encoding='utf-8'))

    def run(self, n_generations=30):
        if self.comment is None:
            self.comment = f'pop_size={self.pop_size} n_gen={n_generations}'
        self.n_generations = n_generations
        for i in trange(n_generations):
            self.curr_generation = i
            self.fitness_function()
            self.selection()
            self.output()
            self.crossover()
            self.mutation()

    def selection(self):
        """Set self.fittest"""
        scores = [(val, self.population[i]) for i, val in enumerate(self.fit_values)]
        scores = sorted(scores, reverse=True)
        self.fittest = [tup[1] for tup in scores][:self.n_top]
        self.fit_values_sorted = [tup[0] for tup in scores][:self.n_top]
        # print('scores:')
        # pprint(scores)
        if self.fit_values_sorted[0] > self.all_time_record:
            # print('New record!')
            self.all_time_record = self.fit_values_sorted[0]
            self.record_holder = self.fittest[0]
            self.record_generation = self.curr_generation
