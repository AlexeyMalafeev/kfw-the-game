from copy import copy
from pprint import pprint
import random
import time


from kf_lib.ai import fight_ai, fight_ai_test
from kf_lib.utils.utilities import rnd


class GeneticAlgorithm(object):
    def __init__(self, pop_size, n_genes, gene_names, n_top, mut_prob, comment=None):
        self.pop_size = pop_size
        self.n_genes = n_genes
        self.gene_names = gene_names
        self.n_top = n_top
        self.mut_prob = mut_prob
        self.comment = comment
        self.population = [[rnd() for _ in range(n_genes)] for _ in range(pop_size)]
        self.fit_values = []
        self.fit_values_sorted = []
        self.max_possible_fit_value = 0
        self.all_time_record = 0
        self.record_holder = None
        self.fittest = []
        self.n_generations = 0
        self.curr_generation = 0
        self.mutations_occurred = 0

    def crossover(
        self,
    ):  # todo remove doubles -> generate random individuals after a few failed crossover attempts
        print(time.ctime())
        print('starting crossover')
        new_population = self.fittest[:]
        random.shuffle(
            new_population
        )  # to cancel out the effect of sorting when performing selection
        for i in range(0, self.n_top, 2):
            parent_a = new_population[i]
            parent_b = new_population[i + 1]
            print('parents:')
            pprint(parent_a)
            pprint(parent_b)
            ind = list(range(self.n_genes))
            random.shuffle(ind)
            ind = ind[: random.randint(1, len(ind) - 1)]
            print('crossing genes with indices:')
            pprint(ind)
            child_a = parent_a[:]
            child_b = parent_b[:]
            for ii in ind:
                child_a[ii], child_b[ii] = child_b[ii], child_a[ii]
            new_population.extend([child_a, child_b])
            print('children:')
            pprint(child_a)
            pprint(child_b)
        self.population = new_population

    def fitness(self):
        """Set self.fit_values"""
        print(time.ctime())
        print('starting fitness evaluation')
        self.fit_values = []
        n_rep = 25
        self.max_possible_fit_value = n_rep * 2
        for individual in self.population:
            print(time.ctime())
            print('evaluating individual:')
            pprint(individual)
            # ai = fight_ai.GeneticAI
            ai = copy(fight_ai.DefaultGeneticAIforTraining)
            for i, name in enumerate(self.gene_names):
                setattr(ai, name, individual[i])
            t = fight_ai_test.FightAITest(
                # ai, fight_ai.GeneticAITrainedParams3, rep=n_rep, write_log=False
                ai, fight_ai.DefaultFightAI, rep=n_rep, write_log=False
            )
            self.fit_values.append(t.wins[0])
            print('result:', t.wins[0])
        print('all fit values:')
        pprint(self.fit_values)

    def fitness_infighting(self):
        """Set self.fit_values"""
        print(time.ctime())
        print('starting fitness evaluation')
        self.fit_values = []
        n_rep = 10
        self.max_possible_fit_value = 2 * n_rep * len(self.population)
        for individual in self.population:
            print(time.ctime())
            print('evaluating individual:')
            pprint(individual)
            score = 0
            ai = fight_ai.GeneticAI
            for i, name in enumerate(self.gene_names):
                setattr(ai, name, individual[i])
            for individual2 in self.population:
                ai2 = fight_ai.GeneticAI2
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
            print('result:', score)
        print('all fit values:')
        pprint(self.fit_values)

    def mutation(self):
        if not self.mut_prob:
            return
        print(time.ctime())
        print('starting mutation')
        # only the new children mutate to ensure preserving top fit values from the previous
        # generation
        for individual in self.population[len(self.fittest):]:
            if rnd() <= self.mut_prob:
                print('mutation occurs for individual:')
                pprint(individual)
                i = random.randint(0, self.n_genes - 1)
                new_val = rnd()  # random mutation
                individual[i] = new_val
                # random increase/decrease
                # new_val = individual[i] * random.choice([0.8, 0.9, 1.1, 1.2])
                # i2 = i
                # while i2 == i:
                #     i2 = random.randint(0, self.n_genes - 1)
                # individual[i], individual[i2] = individual[i2], individual[i]  # random swap
                print('after mutation:')
                pprint(individual)
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
All-time record: {self.all_time_record}
Record holder: {self.record_holder}
'''
        print(out_s)
        file_name = f'fight_ai_gen output {self.comment}.txt'
        print(out_s, file=open(file_name, 'w'))

    def run(self, n_generations=30):
        if self.comment is None:
            self.comment = f'pop_size={self.pop_size} n_gen={n_generations}'
        self.n_generations = n_generations
        for i in range(n_generations):
            self.curr_generation = i
            print('generation', i + 1, '/', n_generations)
            # self.fitness()
            self.fitness_infighting()
            self.selection()
            self.output()
            self.crossover()
            self.mutation()

    def selection(self):
        """Set self.fittest"""
        print(time.ctime())
        print('starting selection')
        scores = [(val, self.population[i]) for i, val in enumerate(self.fit_values)]
        scores = sorted(scores, reverse=True)
        self.fittest = [tup[1] for tup in scores][: self.n_top]
        self.fit_values_sorted = [tup[0] for tup in scores][: self.n_top]
        print('scores:')
        pprint(scores)
        if self.fit_values_sorted[0] > self.all_time_record:
            print('New record!')
            self.all_time_record = self.fit_values_sorted[0]
            self.record_holder = self.fittest[0]
