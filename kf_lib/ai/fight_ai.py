import random
from pathlib import Path

from kf_lib.fighting.distances import VALID_DISTANCES
from kf_lib.kung_fu import moves


catch_breath_move = moves.get_move_obj('Catch Breath')
guard_move = moves.get_move_obj('Guard')
focus_move = moves.get_move_obj('Focus')


def has_dist4_move(f):
    return any(m.distance == 4 for m in f.moves)


def has_bigger_crowd(f):
    return len(f.act_allies) > len(f.act_targets)


def is_at_dist4(f):
    return f.distances[f.target] == 4


def set_gen_ai_params(gen_ai, params):
    for i, name in enumerate(GENETIC_AI_PARAM_NAMES):
        setattr(gen_ai, name, params[i])


class BaseAI(object):
    """Choose a random opponent and fight action.
    For a fight AI to work, it needs just the functions defined in this base class."""

    def __init__(self, owner, write_log=False):
        self.owner = owner
        self.choice = None
        self.weights = {}
        if write_log:
            file_path = Path('tests', 'AI actions', f'{self.__class__.__name__}.txt')
            self.file = open(file_path, 'a', encoding='utf-8')
        else:
            self.file = None

    def choose_move(self):
        self.choice = random.choice(self.owner.av_moves)
        if self.file:
            self.write_log()
        return self.choice

    def choose_target(self):
        """Gets called only if there are >1 active targets."""
        tgts = self.owner.act_targets
        return random.choice(tgts)

    def write_log(self):
        owner = self.owner
        target = owner.target
        dist = owner.distances[target]
        self.file.write('-' * 10 + '\n')
        self.file.write(f'owner: hp:{owner.hp} sp:{owner.stamina}\n')
        self.file.write(f'target: hp:{target.hp} sp:{target.stamina}\n')
        self.file.write(str(self.weights) + '\n')
        self.file.write('d = ' + str(dist) + ': ' + repr(self.choice) + '\n')


class GeneticAI(BaseAI):
    """Choose a random opponent and an action based on action weights (weighted random choice).
    Considers only atk_pwr * to_hit."""

    prob_atk = 10.0
    prob_move = 3.0
    prob_focus = 1.0
    prob_guard = 1.0
    prob_catch = 1.0

    def __init__(self, owner, write_log=False):
        BaseAI.__init__(self, owner, write_log)
        self.options = []

    def choose_move(self):
        owner = self.owner
        options = self.options = []
        weights = self.weights = []
        atk_move = self.get_an_atk_move()
        if atk_move is not None:
            options.append(atk_move)
            weights.append(self.prob_atk)
        maneuver = self.get_a_maneuver()
        if maneuver is not None:
            options.append(maneuver)
            weights.append(self.prob_move)
        if owner.qp < owner.qp_max:
            options.append(focus_move)
            weights.append(self.prob_focus)
        options.append(guard_move)
        weights.append(self.prob_guard)
        if owner.stamina < owner.stamina_max:
            options.append(catch_breath_move)
            weights.append(self.prob_catch)
        self.choice = random.choices(options, weights=weights, k=1)[0]
        if self.file:
            self.write_log()
        return self.choice

    def get_an_atk_move(self):
        owner = self.owner
        pool = [m for m in owner.av_moves if m.power]
        if not pool:
            return None
        else:
            weights = []
            for m in pool:
                owner.calc_atk(m)
                weights.append(owner.atk_pwr * owner.to_hit)
            return random.choices(pool, weights=weights, k=1)[0]

    def get_a_maneuver(self):
        owner = self.owner
        pool = [m for m in self.owner.av_moves if m.dist_change]
        if not pool:
            return None
        else:
            dist_table = {dist: 0.0 for dist in VALID_DISTANCES}
            for m in self.owner.moves:
                if m.distance:
                    owner.calc_atk(m)
                    w = owner.atk_pwr * owner.to_hit
                    dist_table[m.distance] += w
            curr_dist = owner.distances[owner.target]
            max_score = max(dist_table.values())
            if max_score == dist_table[curr_dist]:
                return None
            weights = []
            for m in pool:
                dist = curr_dist + m.dist_change
                weights.append(dist_table.get(dist, 0.0) * (1 + m.power))
            return random.choices(pool, weights=weights, k=1)[0]

    def write_log(self):
        owner = self.owner
        target = owner.target
        dist = owner.distances[target]
        self.file.write('-' * 10 + '\n')
        self.file.write(f'owner: hp:{owner.hp} sp:{owner.stamina}\n')
        self.file.write(f'target: hp:{target.hp} sp:{target.stamina}\n')
        self.file.write(str(self.options) + '\n')
        self.file.write(str(self.weights) + '\n')
        self.file.write('d = ' + str(dist) + ': ' + repr(self.choice) + '\n')


# todo GeneticAI2 pending removal
class GeneticAI2(GeneticAI):
    """Just a copy of GeneticAI to use with different parameters every time.
    Used in fight_ai_gen, do not remove."""
    pass


class GeneticAITrainedParams8(GeneticAI):
    pass


class GeneticAIExtraRules(GeneticAITrainedParams8):
    group_advantage_thresh = 1.0

    def choose_move(self):
        owner = self.owner
        options = self.options = []
        weights = self.weights = []
        atk_move = self.get_an_atk_move()
        if atk_move is not None:
            options.append(atk_move)
            weights.append(self.prob_atk)
        maneuver = self.get_a_maneuver()
        if maneuver is not None:
            options.append(maneuver)
            weights.append(self.prob_move)
        force_move = (
                maneuver is not None
                and (len(owner.act_allies) / len(owner.act_targets)) >= self.group_advantage_thresh
                and atk_move is None
                and owner.stamina >= owner.stamina_max / 2
        )
        if owner.qp < owner.qp_max and not force_move:
            options.append(focus_move)
            weights.append(self.prob_focus)
        if not force_move:
            options.append(guard_move)
            weights.append(self.prob_guard)
        if owner.stamina < owner.stamina_max and not force_move:
            options.append(catch_breath_move)
            weights.append(self.prob_catch)
        self.choice = random.choices(options, weights=weights, k=1)[0]
        if self.file:
            self.write_log()
        return self.choice


# weakness: doesn't move in when oppontent has dist4 moves
# weakness: doesn't move in when has superiority in numbers
# strong, but boring (doesn't move around often)
class GeneticAIAggro(GeneticAITrainedParams8):
    def choose_move(self):
        owner = self.owner
        options = self.options = []
        weights = self.weights = []
        atk_move = self.get_an_atk_move()
        if atk_move is not None:
            options.append(atk_move)
            weights.append(self.prob_atk)
        maneuver = self.get_a_maneuver()
        if maneuver is not None:
            options.append(maneuver)
            weights.append(self.prob_move)
        if not atk_move and owner.qp < owner.qp_max / 2:
            options.append(focus_move)
            weights.append(self.prob_focus)
        if not atk_move:
            options.append(guard_move)
            weights.append(self.prob_guard)
        if not atk_move and owner.stamina < owner.stamina_max / 2:
            options.append(catch_breath_move)
            weights.append(self.prob_catch)
        self.choice = random.choices(options, weights=weights, k=1)[0]
        if self.file:
            self.write_log()
        return self.choice


# moves in when oppontent has dist4 moves
# moves in when has superiority in numbers
# strong, more dynamic, but slightly weaker than GeneticAIAggro
class GeneticAIMoreAggro(GeneticAITrainedParams8):
    def choose_move(self):
        owner = self.owner
        target = owner.target
        options = self.options = []
        weights = self.weights = []
        atk_move = self.get_an_atk_move()
        if atk_move is not None:
            options.append(atk_move)
            weights.append(self.prob_atk)
        maneuver = self.get_a_maneuver()
        if maneuver is not None:
            options.append(maneuver)
            weights.append(self.prob_move)
            if is_at_dist4(owner):
                if (
                        (has_dist4_move(target) and not has_dist4_move(owner))
                        or has_bigger_crowd(owner)
                ):
                    if self.file:
                        self.write_log()
                    return maneuver
        if not atk_move and owner.qp < owner.qp_max / 2:
            options.append(focus_move)
            weights.append(self.prob_focus)
        if not atk_move:
            options.append(guard_move)
            weights.append(self.prob_guard)
        if not atk_move and owner.stamina < owner.stamina_max / 2:
            options.append(catch_breath_move)
            weights.append(self.prob_catch)
        self.choice = random.choices(options, weights=weights, k=1)[0]
        if self.file:
            self.write_log()
        return self.choice


class GeneticAIAttackWhenReady(GeneticAITrainedParams8):
    def choose_move(self):
        owner = self.owner
        target = owner.target
        options = self.options = []
        weights = self.weights = []
        atk_move = self.get_an_atk_move()
        if atk_move is not None:
            options.append(atk_move)
            weights.append(self.prob_atk)
        maneuver = self.get_a_maneuver()
        if maneuver is not None:
            options.append(maneuver)
            weights.append(self.prob_move)
            if is_at_dist4(owner):
                if (
                        (has_dist4_move(target) and not has_dist4_move(owner))
                        or has_bigger_crowd(owner)
                ) or (owner.qp == owner.qp_max and owner.stamina == owner.stamina_max):
                    if self.file:
                        self.write_log()
                    return maneuver
        if not atk_move and owner.qp < owner.qp_max / 2:
            options.append(focus_move)
            weights.append(self.prob_focus)
        if not atk_move:
            options.append(guard_move)
            weights.append(self.prob_guard)
        if not atk_move and owner.stamina < owner.stamina_max / 2:
            options.append(catch_breath_move)
            weights.append(self.prob_catch)
        self.choice = random.choices(options, weights=weights, k=1)[0]
        if self.file:
            self.write_log()
        return self.choice


# todo how to reimplement AI classes to avoid cloning?
# have to make clones as parameters are shared even if you copy or deepcopy classes dynamically
class GeneticAIMoreAggroClone(GeneticAIMoreAggro):
    pass


class GeneticAIMoreAggroClone2(GeneticAIMoreAggro):
    pass


class GeneticAIMoreAggroTrainedTop(GeneticAIMoreAggro):
    pass


class GeneticAIMoreAggroTrainedRecord(GeneticAIMoreAggro):
    pass


class GeneticAIMoreAggroTrainedTopInf(GeneticAIMoreAggro):
    pass


class GeneticAIMoreAggroTrainedRecordInf(GeneticAIMoreAggro):
    pass


class GeneticAIMoreAggroTrainedTopCrowd(GeneticAIMoreAggro):
    pass


class GeneticAIMoreAggroTrainedRecordCrowd(GeneticAIMoreAggro):
    pass


# DefaultFightAI = GeneticAIAggro
# DefaultFightAI = GeneticAIMoreAggro
DefaultFightAI = GeneticAIAttackWhenReady
# this AI is the strongest, yet it is too defensive and boring; todo fix fight AI defensiveness
# DefaultFightAI = GeneticAIMoreAggroTrainedRecord  # trained Feb 11, 2022
DefaultGeneticAIforTraining = GeneticAIMoreAggroClone
DefaultGeneticAIforTraining2 = GeneticAIMoreAggroClone2
GENETIC_AI_PARAM_NAMES = ['prob_atk', 'prob_move', 'prob_focus', 'prob_guard', 'prob_catch']

params8 = [
    0.9946880510412656,
    0.0142349288726894,
    0.08002718630747185,
    0.09367532368847631,
    0.051144214847717806,
]
# best so far; trained against GeneticAITrainedParams3
# the problem with it is that
set_gen_ai_params(GeneticAITrainedParams8, params8)

# Feb 11, 2022, pop=32 fights=160 n_gen=128 gen=128; 5th place
params202202_top = [0.11745140504203222, 0.00777924778884409, 0.21401517744007748,
                    0.888394617200464, 0.7916523164493331]
set_gen_ai_params(GeneticAIMoreAggroTrainedTop, params202202_top)

# Feb 11, 2022, pop=32 fights=160 n_gen=128 gen=84; 1st place
params202202_record = [0.8330525416664358, 0.00777924778884409, 0.7897769161203186,
                       0.7812461127357897, 0.9131024054734007]
set_gen_ai_params(GeneticAIMoreAggroTrainedRecord, params202202_record)
set_gen_ai_params(GeneticAIAttackWhenReady, params202202_record)

# Feb 11, 2022, pop=16 fights=300 n_gen=128 infight gen=128; 5th place
params202202_top_inf = [0.47562433421266803, 0.009057428537260992, 0.8716937253181152,
                        0.9475943689024402, 0.9027385729485755]
set_gen_ai_params(GeneticAIMoreAggroTrainedTopInf, params202202_top_inf)

# Feb 11, 2022, pop=16 fights=300 n_gen=128 infight gen=2; 6th place
params202202_record_inf = [0.8019874503863862, 0.03620216104410978, 0.6110961391332028,
                           0.9475943689024402, 0.5987323606932059]
set_gen_ai_params(GeneticAIMoreAggroTrainedRecordInf, params202202_record_inf)

# Feb 11, 2022, pop=64 fights=64 (crowd only) n_gen=128 gen=128; 3rd place
params202202_top_crowd = [0.985030334660097, 0.004696383021808415, 0.1223626700730519,
                          0.2440865205719437, 0.7263327881555984]
set_gen_ai_params(GeneticAIMoreAggroTrainedTopCrowd, params202202_top_crowd)

# Feb 11, 2022, pop=64 fights=64 (crowd only) n_gen=128 gen=90; 4th place
params202202_record_crowd = [0.985030334660097, 0.004696383021808415, 0.5251826392446703,
                             0.19061750461806992, 0.8036603052306912]
set_gen_ai_params(GeneticAIMoreAggroTrainedRecordCrowd, params202202_record_crowd)

# Total
# GeneticAIMoreAggroTrainedRecord       21728
# GeneticAIMoreAggroTrainedTopInf       21435
# GeneticAIMoreAggroTrainedTopCrowd     21196
# GeneticAIMoreAggroTrainedRecordCrowd  20955
# GeneticAIMoreAggroTrainedTop          20795
# GeneticAIMoreAggroTrainedRecordInf    19205
# GeneticAIAggro                        18416
# GeneticAIMoreAggro                    18176
# GeneticAIMoreAggroTrainedInFighting   17293
# BaseAI                                801

# todo train against Params3, etc. -> cycle this
# todo train style-specific AIs
