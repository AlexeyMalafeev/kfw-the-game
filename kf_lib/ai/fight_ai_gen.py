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
            n_fights_1on1: int,
            n_fights_crowd: int,
            mutation_prob: float,
            infighting: bool,
    ):
        """mode: if infighting is False, will train against current DefaultFightAI"""
        assert pop_size % 2 == 0, 'pop_size must be divisible by 2'
        self.pop_size = pop_size
        self.n_fights_1on1 = n_fights_1on1
        self.n_fights_crowd = n_fights_crowd
        self.mutation_prob = mutation_prob
        self.infighting = infighting

        # setup
        self.gene_names: List[str] = fight_ai.GENETIC_AI_PARAM_NAMES
        self.n_genes: int = len(self.gene_names)
        self.n_top: int = self.pop_size // 2
        self.max_possible_fit_value = (self.n_fights_1on1 + self.n_fights_crowd) * 2
        if self.infighting:
            self.fitness_function = self.fitness_infighting
            self.max_possible_fit_value *= (self.pop_size - 1)
        else:
            self.fitness_function = self.fitness
        self.tests = (
            (fight_ai_test.FightAITest, self.n_fights_1on1),
            (fight_ai_test.CrowdVsCrowdFair, self.n_fights_crowd),
        )
        self.population = tuple(
            tuple(rnd() for _ in range(self.n_genes))
            for _ in range(self.pop_size)
        )
        self.fit_values = []
        self.fit_values_sorted = []
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
        parents_set = set(new_population)
        for i in range(0, self.n_top, 2):
            parent_a = new_population[i]
            parent_b = new_population[i + 1]
            ind = list(range(self.n_genes))
            random.shuffle(ind)
            ind = ind[:random.randint(1, len(ind) - 1)]
            child_a = list(parent_a[:])
            child_b = list(parent_b[:])
            for ii in ind:
                child_a[ii], child_b[ii] = child_b[ii], child_a[ii]  # noqa
            if self.mutation_prob:
                if rnd() <= self.mutation_prob:
                    child_a = self.mutation(child_a)
                if rnd() <= self.mutation_prob:
                    child_b = self.mutation(child_b)
            for child in (child_a, child_b):
                if tuple(child) in parents_set:
                    child = self.mutation(child)
                new_population.append(tuple(child))
        self.population = tuple(new_population)

    def fitness(self):
        """Set self.fit_values"""
        self.fit_values = []
        for individual in self.population:
            score = 0
            ai = fight_ai.DefaultGeneticAIforTraining
            for i, name in enumerate(self.gene_names):
                setattr(ai, name, individual[i])
            # for param in self.gene_names:
            #     print(f'{param}, {getattr(ai, param)}, {getattr(fight_ai.DefaultFightAI, param)}')
            # input('...')
            for ai_test, n_rep in self.tests:
                t = ai_test(
                    ai,
                    fight_ai.DefaultFightAI,
                    rep=n_rep,  # rep is effectively doubled for fairness
                    write_log=False,
                    suppress_output=True,
                )
                score += t.wins[0]
            self.fit_values.append(score)

    def fitness_infighting(self):
        """Set self.fit_values"""
        self.fit_values = []
        for individual in self.population:
            score = 0
            ai = fight_ai.DefaultGeneticAIforTraining
            for i, name in enumerate(self.gene_names):
                setattr(ai, name, individual[i])
            for individual2 in self.population:
                if individual2 == individual:
                    continue
                ai2 = fight_ai.DefaultGeneticAIforTraining2
                for i, name in enumerate(self.gene_names):
                    setattr(ai2, name, individual2[i])
                # for param in self.gene_names:
                #     print(f'{param}, {getattr(ai, param)}, {getattr(ai2, param)}')
                # input('...')
                for ai_test, n_rep in self.tests:
                    t = ai_test(
                        ai,
                        ai2,
                        rep=n_rep,
                        write_log=False,
                        suppress_output=True,
                    )
                    score += t.wins[0]
            self.fit_values.append(score)

    def mutation(self, child):
        gene_index = random.randint(0, self.n_genes - 1)
        new_val = rnd()  # random mutation
        child[gene_index] = new_val
        self.mutations_occurred += 1
        return child

    def output(self):
        time_s = time.ctime()
        top_res_lines = []
        for i in range(len(self.fittest)):
            top_res_lines.append(f'{self.fit_values_sorted[i]} {self.fittest[i]}')
        top_res = '\n'.join(top_res_lines)
        out_s = f'''{time_s}
Generation {self.curr_generation + 1} of {self.n_generations}
Mutations: {self.mutations_occurred} (prob {self.mutation_prob})
Gene names: {self.gene_names}
Top fit values / individuals:
{top_res}
Max possible fit value for one individual: {self.max_possible_fit_value}
All-time record: {self.all_time_record} @ generation {self.record_generation}
Record holder: {self.record_holder}
'''
        infight_s = ' infight' if self.infighting else ''
        file_name = f'pop={self.pop_size} fights={self.max_possible_fit_value} ' \
                    f'n_gen={self.n_generations}{infight_s} ' \
                    f'gen={self.curr_generation + 1}.txt'
        file_path = Path('tests', 'genetic', file_name)
        print(out_s, file=open(file_path, 'w', encoding='utf-8'))

    def run(self, n_generations=30):
        self.n_generations = n_generations
        total_fights_per_generation = self.max_possible_fit_value * self.pop_size
        total_fights = total_fights_per_generation * n_generations
        print(f'{total_fights_per_generation=}\n{total_fights=}')
        for i in trange(n_generations):
            self.curr_generation = i
            self.fitness_function()
            self.selection()
            self.output()
            self.crossover()

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
