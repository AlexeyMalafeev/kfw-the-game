# from pprint import pprint
import multiprocessing
import os
import random
import time
from collections import Counter
from pathlib import Path
from typing import List

from tqdm import tqdm, trange

from kf_lib.ai import fight_ai, fight_ai_test
from kf_lib.utils import rnd


ACTION_KINDS = ('attack', 'maneuver', 'guard', 'focus', 'catch breath')


def _action_kind(move):
    if move is fight_ai.guard_move:
        return 'guard'
    if move is fight_ai.focus_move:
        return 'focus'
    if move is fight_ai.catch_breath_move:
        return 'catch breath'
    return 'attack' if move.power else 'maneuver'


def _play(task):
    """Worker task: one AI (params) vs another (params, or None = DefaultFightAI).

    task = (params, opp_params, tests, seed, count_actions); tests is a tuple of
    (test class, rep). Returns (wins per test as [a, b] pairs, action Counter of a).
    Seeds the global random module when seed is not None."""
    params, opp_params, tests, seed, count_actions = task
    ai = fight_ai.DefaultGeneticAIforTraining
    fight_ai.set_gen_ai_params(ai, params)
    if opp_params is None:
        ai2 = fight_ai.DefaultFightAI
    else:
        ai2 = fight_ai.DefaultGeneticAIforTraining2
        fight_ai.set_gen_ai_params(ai2, opp_params)
    if seed is not None:
        random.seed(seed)
    counts = Counter()
    if count_actions:
        def choose_move(self):
            move = fight_ai.GeneticAIAttackWhenReady.choose_move(self)
            counts[_action_kind(move)] += 1
            return move
        ai.choose_move = choose_move
    try:
        wins = []
        for ai_test, n_rep in tests:
            t = ai_test(ai, ai2, rep=n_rep, write_log=False, suppress_output=True)
            wins.append(list(t.wins))
    finally:
        if count_actions:
            del ai.choose_move
    return wins, counts


def _worker_init(cwd):
    os.chdir(cwd)  # workers import kf_lib, which reads data files relative to the cwd


def _new_pool(workers):
    """None for workers=1, else a pool of fresh (spawned, as in the fight-balance
    harness) worker processes."""
    if workers == 1:
        return None
    ctx = multiprocessing.get_context('spawn')
    return ctx.Pool(workers, initializer=_worker_init, initargs=(os.getcwd(),))


def _run_tasks(tasks, pool, progress=False):
    """Results of _play for each task, in order. Without a pool, plays them here,
    saving and restoring the random state, so seeded results don't depend on it."""
    if pool is None:
        state = random.getstate()
        try:
            it = tqdm(tasks, leave=False) if progress else tasks
            return [_play(task) for task in it]
        finally:
            random.setstate(state)
    it = pool.imap(_play, tasks)
    if progress:
        it = tqdm(it, total=len(tasks), leave=False)
    return list(it)


def evaluate(params, opp_params=None, n_1on1=10_000, n_crowd=2_500, seed=0,
             workers=None, chunk=250):
    """Win rates of the default AI class with `params` against `opp_params`
    (None = DefaultFightAI as it is). n_* are reps (each played twice, sides
    swapped), split into chunks seeded seed, seed + 1, ... Returns
    {'1on1': (wins, losses), 'crowd': (wins, losses), 'actions': Counter} where
    'actions' counts the tested AI's choices in the 1-on-1 fights only."""
    workers = workers or os.cpu_count() or 1
    tasks = []
    for test, n in ((fight_ai_test.FightAITest, n_1on1),
                    (fight_ai_test.CrowdVsCrowdFair, n_crowd)):
        for start in range(0, n, chunk):
            tasks.append((tuple(params), opp_params, ((test, min(chunk, n - start)),),
                          seed + len(tasks), True))
    res = {'1on1': [0, 0], 'crowd': [0, 0], 'actions': Counter()}
    pool = _new_pool(workers)
    try:
        results = _run_tasks(tasks, pool, progress=True)
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    for task, (wins, counts) in zip(tasks, results):
        key = '1on1' if task[2][0][0] is fight_ai_test.FightAITest else 'crowd'
        res[key][0] += wins[0][0]
        res[key][1] += wins[0][1]
        if key == '1on1':
            res['actions'] += counts
    res['1on1'] = tuple(res['1on1'])
    res['crowd'] = tuple(res['crowd'])
    return res


class GeneticAlgorithm(object):
    def __init__(
            self,
            pop_size: int,
            n_fights_1on1: int,
            n_fights_crowd: int,
            mutation_prob: float,
            infighting: bool,
            workers: int = 1,
            seed=None,
    ):
        """mode: if infighting is False, will train against current DefaultFightAI.

        workers > 1 plays the fitness fights in that many processes. With a seed,
        the run is reproducible (whatever the workers), and within a generation
        every individual meets the same fighters (seed + generation, per opponent
        in infighting) -- common random numbers, so fitness gaps are less noisy."""
        assert pop_size % 2 == 0, 'pop_size must be divisible by 2'
        self.pop_size = pop_size
        self.n_fights_1on1 = n_fights_1on1
        self.n_fights_crowd = n_fights_crowd
        self.mutation_prob = mutation_prob
        self.infighting = infighting
        self.workers = workers
        self.pool = None  # set by run()
        self.seed = seed
        if seed is not None:
            random.seed(seed)

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

    def _gen_seed(self, k=0):
        if self.seed is None:
            return None
        return self.seed + 1_000_000 * (self.curr_generation + 1) + k

    def fitness(self):
        """Set self.fit_values"""
        tasks = [(ind, None, self.tests, self._gen_seed(), False)
                 for ind in self.population]
        results = _run_tasks(tasks, self.pool)
        self.fit_values = [sum(w[0] for w in wins) for wins, _ in results]

    def fitness_infighting(self):
        """Set self.fit_values"""
        tasks, owners = [], []
        for i, individual in enumerate(self.population):
            for j, individual2 in enumerate(self.population):
                if individual2 == individual:
                    continue
                tasks.append((individual, individual2, self.tests, self._gen_seed(j),
                              False))
                owners.append(i)
        results = _run_tasks(tasks, self.pool)
        self.fit_values = [0] * len(self.population)
        for i, (wins, _) in zip(owners, results):
            self.fit_values[i] += sum(w[0] for w in wins)

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
        pcnt = round(self.all_time_record / self.max_possible_fit_value * 100)
        if self.record_generation is None:
            # no record yet (e.g. every fitness score was 0 in generation 0)
            record_s = ''
        else:
            record_s = f' @ generation {self.record_generation + 1}'
        out_s = f'''{time_s}
Generation {self.curr_generation + 1} of {self.n_generations}
Mutations: {self.mutations_occurred} (prob {self.mutation_prob})
Gene names: {self.gene_names}
Top fit values / individuals:
{top_res}
Max possible fit value for one individual: {self.max_possible_fit_value}
All-time record: {self.all_time_record} ({pcnt}%){record_s}
Record holder: {self.record_holder}
'''
        infight_s = ' infight' if self.infighting else ''
        seed_s = '' if self.seed is None else f' seed={self.seed}'
        file_name = f'pop={self.pop_size} fights={self.max_possible_fit_value} ' \
                    f'n_gen={self.n_generations}{infight_s}{seed_s} ' \
                    f'gen={self.curr_generation + 1}.txt'
        file_path = Path('tests', 'genetic', file_name)
        print(out_s, file=open(file_path, 'w', encoding='utf-8'))

    def run(self, n_generations=30):
        self.n_generations = n_generations
        total_fights_per_generation = self.max_possible_fit_value * self.pop_size
        total_fights = total_fights_per_generation * n_generations
        print(f'{total_fights_per_generation=}\n{total_fights=}')
        self.pool = _new_pool(self.workers)
        try:
            for i in trange(n_generations):
                self.curr_generation = i
                self.fitness_function()
                self.selection()
                self.output()
                self.crossover()
        finally:
            if self.pool is not None:
                self.pool.close()
                self.pool.join()
            self.pool = None

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
