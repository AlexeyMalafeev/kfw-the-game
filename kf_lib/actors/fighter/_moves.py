import kf_lib.kung_fu.moves
from ...kung_fu import moves


LVS_GET_NEW_ADVANCED_MOVE = {10, 12, 14, 16, 18, 20}  # should be ordered, ascending
# todo use NEW_MOVE_TIERS
NEW_MOVE_TIERS = {
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 4,
    8: 4,
    9: 5,
    10: 5,
    11: 6,
    12: 6,
    13: 7,
    14: 7,
    15: 8,
    16: 8,
    17: 9,
    18: 9,
    19: 10,
    20: 10,
}


class MoveUser:
    moves = []

    def choose_new_move(self, sample):
        self.learn_move(random.choice(sample).name)

    def get_move_fail_chance(self, move_obj):
        return move_obj.complexity ** 2 / self.agility_full ** 2

    def get_moves_to_choose(self, tier):
        return moves.get_rand_moves(self, self.num_moves_choose, tier)

    @staticmethod
    def get_move_tier_string(move_obj):
        t = move_obj.tier
        return f' ({roman(t)})' if t else ''

    def get_move_time_cost(self, move_obj):
        if self.check_status('slowed down'):
            mob_mod = 1 - MOB_DAM_PENALTY
        else:
            mob_mod = 1
        cost = round(move_obj.time_cost / (self.speed_full * mob_mod))
        return cost

    def learn_move(self, move, silent=False):
        """move can be a Move object or a move name string"""
        if isinstance(move, str):
            try:
                move = moves.get_move_obj(move)
            except kf_lib.kung_fu.moves.MoveNotFoundError as e:
                print(e)
                pak()
                return
        self.moves.append(move)
        if not silent:
            self.show(f'{self.name} learns {move.name} ({move.descr}).')
            self.log(f'Learns {move.name} ({move.descr})')
            self.pak()

    def learn_random_move(self, move_tier, silent=False):
        try:
            move_obj = moves.get_rand_move(self, move_tier)
        except kf_lib.kung_fu.moves.MoveNotFoundError as e:
            print(e)
            pak()
            return
        self.learn_move(move_obj, silent=silent)

    def replace_move(self, rep_mv, rep_with):
        def _rep_in_list(mv_a, mv_b, move_list):
            i = move_list.index(mv_a)
            move_list.remove(mv_a)
            move_list.insert(i, mv_b)
        _rep_in_list(rep_mv, rep_with, self.moves)

    def set_moves(self, move_names):
        for m in moves.BASIC_MOVES:
            self.learn_move(m.name, silent=True)  # silent = don't write log
        if not move_names:
            self.set_rand_moves()
        else:
            for mn in move_names:
                self.learn_move(mn, silent=True)

    def set_rand_moves(self):
        for lv in LVS_GET_NEW_ADVANCED_MOVE:
            if self.level >= lv:
                tier = NEW_MOVE_TIERS[lv]
                self.learn_move(moves.get_rand_moves(self, 1, tier)[0])
            else:
                break
        for lv, moves_to_learn in self.style.move_strings.items():
            if self.level >= lv:
                if isinstance(moves_to_learn, str):  # can be a tuple, can be a string
                    moves_to_learn = (moves_to_learn,)
                for move_s in moves_to_learn:
                    moves.resolve_style_move(move_s, self)
