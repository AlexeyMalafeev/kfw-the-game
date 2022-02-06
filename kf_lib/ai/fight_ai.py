from pathlib import Path


from kf_lib.fighting.distances import VALID_DISTANCES
from kf_lib.kung_fu import moves
from kf_lib.utils.utilities import *


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


class WeightedActionsAI(BaseAI):
    """Choose a random opponent and an action based on action weights
    (weighted random choice).
    Considers only atk_pwr * to_hit."""

    force_integer_weights = True
    catch_breath_mult = 50
    change_dist_mult = 40
    guard_mult = 50

    def calc_weights(self):
        self.init_weights()
        for move in self.weights:
            if move.power:
                self.weights[move] = self.weigh_atk_move(move)
            elif move.dist_change:
                self.factor_in_distance(move)

    def choose_move(self):
        self.calc_weights()
        # self.file.write('\nweights before normalization: {}\n'.format(self.weights))
        self.choice = self.wtd_rnd_choice()
        if self.file:
            self.write_log()
        return self.choice

    def factor_in_distance(self, move):
        owner = self.owner
        target = owner.target
        actual_dist = owner.distances[target]
        n_moves0 = len(owner.get_av_moves())
        owner.change_distance(move.dist_change, target)
        new_dist = owner.distances[target]
        if new_dist != actual_dist:
            n_moves = len(owner.get_av_moves())
            self.weights[move] = n_moves / n_moves0 * self.change_dist_mult
        else:
            self.weights[move] = 0
        # self.file.write('weight:{} '.format(self.weights[move]))
        owner.distances[target] = actual_dist
        target.distances[owner] = actual_dist

    def init_weights(self):
        self.weights = {a: 1 for a in self.owner.av_moves}
        self.weights[catch_breath_move] = (
            self.owner.stamina / self.owner.stamina_max
        ) * self.catch_breath_mult
        self.weights[guard_move] = (self.owner.stamina / self.owner.stamina_max) * self.guard_mult

    def weigh_atk_move(self, move):
        owner = self.owner
        owner.calc_atk(move)
        return owner.atk_pwr * owner.to_hit

    def wtd_rnd_choice(self):
        return weighted_rand_choice(self.weights, self.force_integer_weights)


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


class GeneticAIMoreAggroTrainedTop(GeneticAIMoreAggro):
    pass


class GeneticAIMoreAggroTrainedRecord(GeneticAIMoreAggro):
    pass


# DefaultFightAI = GeneticAIAggro
DefaultFightAI = GeneticAIMoreAggro
DefaultGeneticAIforTraining = GeneticAIMoreAggro
GENETIC_AI_PARAM_NAMES = ['prob_atk', 'prob_move', 'prob_focus', 'prob_guard', 'prob_catch']


params8 = [
    0.9946880510412656,
    0.0142349288726894,
    0.08002718630747185,
    0.09367532368847631,
    0.051144214847717806,
]
# best so far; trained against GeneticAITrainedParams3
set_gen_ai_params(GeneticAITrainedParams8, params8)

params202202_top = [
    0.9543835165930256,
    0.14426817184508778,
    0.21546881760407965,
    0.02730274577937364,
    0.07500520467563832,
]
set_gen_ai_params(GeneticAIMoreAggroTrainedTop, params202202_top)

params202202_record = [
    0.9265512291096116,
    0.1390143232558788,
    0.300289180607353,
    0.19937525325991945,
    0.6037660409072123
]
set_gen_ai_params(GeneticAIMoreAggroTrainedRecord, params202202_record)

# todo train against Params3, etc. -> cycle this
# todo train style-specific AIs
