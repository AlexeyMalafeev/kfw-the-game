from ._base_fighter import BaseFighter
from ...fighting.distances import visualize_distance


class DistanceMethods(BaseFighter):
    def change_distance(self, dist, targ):
        dist = self.distances[targ] + dist
        if dist < 1:
            dist = 1  # don't just skip turn, as some maneuvers may still work, e.g. 2 - 2 = 0 -> 1
        elif dist > 4:
            dist = 4  # e.g. 3 + 2 = 5 -> 4
        self.distances[targ] = targ.distances[self] = dist

    @staticmethod
    def get_vis_distance(dist):
        return visualize_distance(dist)
