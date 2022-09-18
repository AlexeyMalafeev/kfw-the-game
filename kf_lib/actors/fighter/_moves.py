from abc import ABC
from math import ceil
import random
from typing import List, Union

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.kung_fu import moves
from kf_lib.utils import roman


class MoveMethods(FighterAPI, ABC):
    LVS_GET_NEW_ADVANCED_MOVE = {12, 14, 16, 18, 20}

    def choose_new_move(self, sample: List[moves.Move]) -> None:
        self.learn_move(random.choice(sample))

    def get_moves_to_choose(self, tier: int) -> List[moves.Move]:
        return moves.get_rand_moves(self, self.num_moves_choose, tier)

    def get_move_tier_for_lv(self, level: int = None) -> int:
        if level is None:
            level = self.level
        return ceil(level / 2)

    @staticmethod
    def get_move_tier_string(move_obj: moves.Move) -> str:
        t = move_obj.tier
        return f' ({roman(t)})' if t else ''

    def get_tier_str_for_lv(self) -> str:
        return str(self.get_move_tier_for_lv())

    def learn_move(self, move: Union[moves.Move, str], silent: bool = False) -> None:
        # do not remove support for str
        if isinstance(move, str):
            move = moves.get_move_obj(move)
        if move not in self.moves:
            self.moves.append(move)
        else:
            print(f'warning: trying to learn move {move} that is already known by {self}')
        if not silent:
            self.show(f'{self.name} learns {move.name} ({move.descr}).')
            self.log(f'Learns {move.name} ({move.descr})')
            self.pak()

    def learn_move_from(self, other: FighterAPI) -> None:
        known = set(self.moves)
        pool = [mv for mv in other.moves if mv not in known]
        if pool:
            mv = random.choice(pool)
            self.learn_move(mv)

    def learn_random_move(self, move_tier: int, silent: bool = False) -> None:
        move_obj = moves.get_rand_move(self, move_tier)
        self.learn_move(move_obj, silent=silent)

    def replace_move(self, rep_mv: moves.Move, rep_with: moves.Move) -> None:
        def _rep_in_list(mv_a, mv_b, move_list):
            i = move_list.index(mv_a)
            move_list.remove(mv_a)
            move_list.insert(i, mv_b)
        _rep_in_list(rep_mv, rep_with, self.moves)

    def resolve_moves_on_level_up(self) -> None:
        # style move
        if self.level in self.style.move_strings:
            move_s = self.style.move_strings[self.level]
            moves.resolve_move_string(move_s, self)
        # advanced move
        elif self.level in self.LVS_GET_NEW_ADVANCED_MOVE:
            move_s = self.get_tier_str_for_lv()
            moves.resolve_move_string(move_s, self)

    def set_moves(self, move_objs: List[moves.Move]) -> None:
        for m in moves.BASIC_MOVES:
            self.learn_move(m, silent=True)  # silent = don't write log
        if not move_objs:
            self.set_rand_moves()
        else:
            for m in move_objs:
                self.learn_move(m, silent=True)

    def set_rand_moves(self) -> None:
        for lv in self.LVS_GET_NEW_ADVANCED_MOVE:
            if self.level >= lv:
                tier = self.get_move_tier_for_lv(lv)
                self.learn_move(moves.get_rand_move(self, tier))
        for lv, moves_to_learn in self.style.move_strings.items():
            if self.level >= lv:
                if isinstance(moves_to_learn, str):  # can be a tuple, can be a string
                    moves_to_learn = (moves_to_learn,)
                for move_s in moves_to_learn:
                    moves.resolve_move_string(move_s, self)
