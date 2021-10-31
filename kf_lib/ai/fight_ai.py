from kf_lib.fighting.distances import VALID_DISTANCES
from kf_lib.kung_fu import moves
from kf_lib.utils.utilities import *


catch_breath_move = moves.get_move_obj('Catch Breath')
guard_move = moves.get_move_obj('Guard')
focus_move = moves.get_move_obj('Focus')


class BaseAI(object):
    """Choose a random opponent and fight action.
    For a fight AI to work, it needs just the functions defined in this base class."""

    def __init__(self, owner, write_log=False):
        self.owner = owner
        self.choice = None
        self.weights = {}
        if write_log:
            self.file = open(f'{self.__class__.__name__}.txt', 'a')
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
    """Choose a random opponent and an action based on action weights (weighted random choice).
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


class CarefulManeuvers5(WeightedActionsAI):
    """Kind of works with the new system, but needs improvement."""

    change_dist_mult = 50

    def factor_in_distance(self, move):
        # self.file.write('\nconsidering {}: '.format(move))
        owner = self.owner
        target = owner.target
        actual_dist = owner.distances[target]
        # self.file.write('act.dist:{} '.format(actual_dist))
        score0 = 1 + len([m for m in owner.get_av_moves() if m.power])
        owner.change_distance(move.dist_change, target)
        new_dist = owner.distances[target]
        # self.file.write('new dist:{} '.format(new_dist))
        if new_dist != actual_dist:
            score1 = 1 + len([m for m in owner.get_av_moves() if m.power])
            self.weights[move] = score1 / score0 * self.change_dist_mult
        else:
            self.weights[move] = 0
        # self.file.write('weight:{} '.format(self.weights[move]))
        owner.distances[target] = actual_dist
        target.distances[owner] = actual_dist


class NewSystemAI(BaseAI):
    """Choose a random opponent and an action based on action weights.
    Buggy."""

    def calc_weights(self):
        owner = self.owner
        self.init_weights()
        atk_weights = {}
        change_dist_weights = {}
        add_stam_weights = {}
        add_qi_weights = {}
        time_weights = {}

        # compute pre-normalization weights
        for move in self.weights:
            if move.power:
                atk_weights[move] = self.weigh_atk_move(move)
            if move.dist_change:
                change_dist_weights[move] = self.weigh_dist_change(move)
            if move.stam_cost < 0:  # move adds stamina
                add_stam_weights[move] = self.weigh_stam(move)
            if move.qi_cost < 0:  # move adds qi
                add_qi_weights[move] = self.weigh_qi(move)
            time_weights[move] = 1 / move.time_cost

        # normalize and/or finalize
        can_attack = True if atk_weights else False
        max_atk_wt = max(atk_weights.values()) if atk_weights else 1
        max_add_stam_wt = max(add_stam_weights.values())
        for move in self.weights:
            if move in atk_weights:
                self.weights[move] += atk_weights[move] / max_atk_wt
            if move in change_dist_weights:
                wt = change_dist_weights[move]
                if can_attack:
                    wt /= 2
                self.weights[move] += wt
            if move in add_stam_weights:
                wt = add_stam_weights[move] / max_add_stam_wt
                self.weights[move] += wt * (
                    1
                    - (
                        min(owner.stamina + owner.stamina_gain, owner.stamina_max)
                        / owner.stamina_max
                    )
                )
            if move in add_qi_weights:
                score = len([m for m in owner.moves if m.qi_cost > owner.qp]) / (
                    len([m for m in owner.moves if m.qi_cost > 0]) + 1
                )
                self.weights[move] += add_qi_weights[move] * score
            self.weights[move] *= time_weights[move]

    def choose_move(self):
        self.calc_weights()
        # self.file.write('\nweights before normalization: {}\n'.format(self.weights))
        movs, wts = [], []
        for k, v in self.weights.items():
            movs.append(k)
            wts.append(v)
        self.choice = random.choices(movs, weights=wts, k=1)[0]
        # print('normalized:\n', self.weights)
        # print('choice:\n', self.choice)
        # input('...')
        if self.file:
            self.write_log()
        return self.choice

    def init_weights(self):
        self.weights = {a: 0.0 for a in self.owner.av_moves}

    def weigh_atk_move(self, move):
        owner = self.owner
        owner.calc_atk(move)
        wt = owner.atk_pwr * owner.to_hit
        if move.functions:
            wt *= len(move.functions) + 1
        return wt

    def weigh_dist_change(self, move):
        owner = self.owner
        target = owner.target
        actual_dist = owner.distances[target]
        wt_denom = max([self.weigh_atk_move(m) for m in owner.get_av_moves() if m.power] + [1])
        new_dist = actual_dist + move.dist_change
        owner.distances[target] = new_dist
        wt_num = max([self.weigh_atk_move(m) for m in owner.get_av_moves() if m.power] + [0])
        owner.distances[target] = actual_dist
        return wt_num / wt_denom

    @staticmethod
    def weigh_stam(move):
        return -move.stam_cost

    @staticmethod
    def weigh_qi(move):
        return -move.qi_cost


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


class GeneticAI2(GeneticAI):
    """Just a copy of GeneticAI to use with different parameters every time.
    Used in fight_ai_gen, do not remove."""

    pass


class GeneticAIManualParams(GeneticAI):
    prob_atk = 1.0
    prob_move = 1.0
    prob_focus = 0.15
    prob_guard = 0.1
    prob_catch = 0.03


class GeneticAITrainedParams(GeneticAI):
    prob_atk = 0.9760437615470452
    prob_move = 0.9844409989619278
    prob_focus = 0.1819734524745541
    prob_guard = 0.13879693421751538
    prob_catch = 0.03401994839867584


class GeneticAITrainedParams2(GeneticAI):
    prob_atk = 0.9789123869947447
    prob_move = 0.054606967169251064
    prob_focus = 0.08542357354998587
    prob_guard = 0.2528291218177934
    prob_catch = 0.12248605813284985


class GeneticAITrainedParams3(GeneticAI):
    pass


class GeneticAITrainedParams4(GeneticAI):
    pass


class GeneticAITrainedParams5(GeneticAI):
    pass


class GeneticAITrainedParams6(GeneticAI):
    pass


class GeneticAITrainedParams7(GeneticAI):
    pass


class GeneticAITrainedParams8(GeneticAI):
    pass


class GeneticAITrainedParams9(GeneticAI):
    pass


class GeneticAITrainedParams10(GeneticAI):
    pass


class GeneticAITrainedParams11(GeneticAI):
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


class GeneticAIExtraRules1(GeneticAIExtraRules):
    group_advantage_thresh = 1.1


class GeneticAIExtraRules2(GeneticAIExtraRules):
    group_advantage_thresh = 1.2


class GeneticAIExtraRules3(GeneticAIExtraRules):
    group_advantage_thresh = 1.3


class GeneticAIExtraRules4(GeneticAIExtraRules):
    group_advantage_thresh = 1.4


class GeneticAIExtraRules5(GeneticAIExtraRules):
    group_advantage_thresh = 1.5


class GeneticAIExtraRules6(GeneticAIExtraRules):
    group_advantage_thresh = 1.6


class GeneticAIExtraRules7(GeneticAIExtraRules):
    group_advantage_thresh = 1.7


class GeneticAIExtraRules8(GeneticAIExtraRules):
    group_advantage_thresh = 1.8


class GeneticAIExtraRules9(GeneticAIExtraRules):
    group_advantage_thresh = 1.9


class GeneticAIExtraRules10(GeneticAIExtraRules):
    group_advantage_thresh = 2.0


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


# DefaultFightAI = CarefulManeuvers5
# DefaultFightAI = WeightedActionsAI
# DefaultFightAI = GeneticAI
# DefaultFightAI = GeneticAITrainedParams10  # moves around more, so easier to trick
DefaultFightAI = GeneticAIAggro
GENETIC_AI_PARAM_NAMES = ['prob_atk', 'prob_move', 'prob_focus', 'prob_guard', 'prob_catch']


def set_gen_ai_params(gen_ai, params):
    for i, name in enumerate(GENETIC_AI_PARAM_NAMES):
        setattr(gen_ai, name, params[i])


params3 = [
    0.8744186089036129,
    0.03379275893072364,
    0.07051723329372817,
    0.03379275893072364,
    0.19930517062871012,
]
set_gen_ai_params(GeneticAITrainedParams3, params3)
params4 = [
    0.9281074633432324,
    0.02765915621432158,
    0.1314327152378909,
    0.19725010868827675,
    0.02765915621432158,
]
set_gen_ai_params(GeneticAITrainedParams4, params4)
params5 = [
    0.9281074633432324,
    0.02765915621432158,
    0.1314327152378909,
    0.10447222975667958,
    0.1863387747517773,
]
set_gen_ai_params(GeneticAITrainedParams5, params5)
params6 = [
    0.9281074633432324,
    0.02765915621432158,
    0.1314327152378909,
    0.10447222975667958,
    0.1429829688487113,
]
set_gen_ai_params(GeneticAITrainedParams6, params6)
params7 = [
    0.7268550239297114,
    0.02765915621432158,
    0.1314327152378909,
    0.10447222975667958,
    0.1429829688487113,
]
set_gen_ai_params(GeneticAITrainedParams7, params7)
params8 = [
    0.9946880510412656,
    0.0142349288726894,
    0.08002718630747185,
    0.09367532368847631,
    0.051144214847717806,
]
set_gen_ai_params(
    GeneticAITrainedParams8, params8
)  # best so far; trained against GeneticAITrainedParams3
params9 = [
    0.9946880510412656,
    0.029220693875186443,
    0.08002718630747185,
    0.09519259074648034,
    0.2643083577189722,
]
set_gen_ai_params(GeneticAITrainedParams9, params9)
params10 = [
    0.9916748240763598,
    0.40989405252973,
    0.037890000127675516,
    0.15929562050637247,
    0.1338310453333521,
]
set_gen_ai_params(GeneticAITrainedParams10, params10)  # infighting 12th generation
params11 = [
    0.9916748240763598,
    0.18781151091520898,
    0.037890000127675516,
    0.07273478376240317,
    0.1338310453333521,
]
set_gen_ai_params(GeneticAITrainedParams11, params11)  # infighting 30th generation

# todo train against Params3, etc. -> cycle this
# todo train style-specific AIs

# Fri Feb  7 21:26:38 2020
#
# GeneticAITrainedParams8   1247
# GeneticAITrainedParams9   1209
# GeneticAITrainedParams4   1199
# GeneticAITrainedParams6   1196
# GeneticAITrainedParams3   1176
# GeneticAITrainedParams5   1167
# GeneticAITrainedParams2   1158
# GeneticAITrainedParams7   1133
# WeightedActionsAI         1104
# GeneticAI                 1072
# BaseAI                    292


# Fri Feb  7 21:04:42 2020
#
# GeneticAITrainedParams4  1994
# GeneticAITrainedParams6  1980
# GeneticAITrainedParams5  1925
# GeneticAITrainedParams3  1922
# GeneticAITrainedParams7  1922
# GeneticAITrainedParams2  1901
# WeightedActionsAI        1863
# BaseAI                   493


# Fri Feb  7 02:50:28 2020
#
# GeneticAITrainedParams3  2818
# WeightedActionsAI        2572
# BaseAI                   610

# Fri Feb  7 02:44:11 2020
#
# GeneticAITrainedParams3  623
# GeneticAITrainedParams2  579
# GeneticAITrainedParams4  576
# WeightedActionsAI        548
# GeneticAI                529
# BaseAI                   145
