import random

from kf_lib.kung_fu import moves
from kf_lib.utils import roman
from ._base_fighter import BaseFighter

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


class MoveMethods(BaseFighter):
    def choose_new_move(self, sample):
        self.learn_move(random.choice(sample).name)

    def get_moves_to_choose(self, tier):
        return moves.get_rand_moves(self, self.num_moves_choose, tier)

    def get_move_tier_for_lv(self):
        return NEW_MOVE_TIERS[self.level]

    @staticmethod
    def get_move_tier_string(move_obj):
        t = move_obj.tier
        return f' ({roman(t)})' if t else ''

    def get_tier_str_for_lv(self):
        return str(self.get_move_tier_for_lv())

    def learn_move(self, move, silent=False):
        """move can be a Move object or a move name string"""
        if isinstance(move, str):
            move = moves.get_move_obj(move)
        if move not in self.moves:
            self.moves.append(move)
        else:
            print(f'warning: trying to learn move {move} that is already known by {self}')
            # pak()
        if not silent:
            self.show(f'{self.name} learns {move.name} ({move.descr}).')
            self.log(f'Learns {move.name} ({move.descr})')
            self.pak()

    def learn_move_from(self, other):
        known = set(self.moves)
        pool = [mv for mv in other.moves if mv not in known]
        if pool:
            mv = random.choice(pool)
            self.learn_move(mv)
            # print(f'{self} learns {mv}')

    # todo in learn_random_move, if move_tier is not given, make it relative to current level
    def learn_random_move(self, move_tier, silent=False):
        move_obj = moves.get_rand_move(self, move_tier)
        self.learn_move(move_obj, silent=silent)

    def replace_move(self, rep_mv, rep_with):
        def _rep_in_list(mv_a, mv_b, move_list):
            i = move_list.index(mv_a)
            move_list.remove(mv_a)
            move_list.insert(i, mv_b)
        _rep_in_list(rep_mv, rep_with, self.moves)

    def resolve_moves_on_level_up(self):
        # style move
        if self.level in self.style.move_strings:
            move_s = self.style.move_strings[self.level]
            moves.resolve_style_move(move_s, self)
        # advanced move
        elif self.level in LVS_GET_NEW_ADVANCED_MOVE:
            move_s = self.get_tier_str_for_lv()
            moves.resolve_style_move(move_s, self)

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
                tier = self.get_move_tier_for_lv()
                self.learn_move(moves.get_rand_moves(self, 1, tier)[0])
            else:
                break
        for lv, moves_to_learn in self.style.move_strings.items():
            if self.level >= lv:
                if isinstance(moves_to_learn, str):  # can be a tuple, can be a string
                    moves_to_learn = (moves_to_learn,)
                for move_s in moves_to_learn:
                    moves.resolve_style_move(move_s, self)
