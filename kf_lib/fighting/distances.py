import random


DISTANCE_FEATURES = {
    1: 'dist1',
    2: 'dist2',
    3: 'dist3',
    4: 'dist4',
}
DISTANCES_VISUALIZATION = {1: 'OX', 2: 'O.X', 3: 'O..X', 4: 'O...X'}
VALID_DISTANCES = DISTANCES_VISUALIZATION.keys()
VALID_DISTANCES_MAX = max(VALID_DISTANCES)
VALID_DISTANCES_MIN = min(VALID_DISTANCES)


def get_random_distance():
    return random.randint(VALID_DISTANCES_MIN, VALID_DISTANCES_MAX)


def visualize_distance(dist: int):
    return DISTANCES_VISUALIZATION[dist]
