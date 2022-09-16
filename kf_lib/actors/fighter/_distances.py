from abc import ABC

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.fighting import distances


class DistanceMethods(FighterAPI, ABC):
    def change_distance(
        self,
        dist: int,
        targ: FighterAPI,
    ) -> None:
        self.momentum = -dist
        dist += self.distances[targ]
        if dist < distances.VALID_DISTANCES_MIN:
            dist = distances.VALID_DISTANCES_MIN
        elif dist > distances.VALID_DISTANCES_MAX:
            dist = distances.VALID_DISTANCES_MAX
        self.set_distance(targ, dist)

    @staticmethod
    def get_vis_distance(dist: int) -> str:
        return distances.visualize_distance(dist)

    def set_distance(self, targ: FighterAPI, dist: int) -> None:
        self.distances[targ] = targ.distances[self] = dist

    def set_distances_before_fight(self) -> None:
        self.distances = d = {}
        # todo optimize not to walk over the same pair of fighters twice
        for f2 in self.current_fight.all_fighters:
            if self is f2:
                d[f2] = 0
            else:
                dist = distances.get_random_distance()
                d[f2] = dist
                f2.distances[self] = dist
