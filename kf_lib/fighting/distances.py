import random


DISTANCE_FEATURES = {
    0: 'no range',
    1: 'close-range',
    2: 'mid-range',
    3: 'long-range',
    4: 'extra long-range',
}
DISTANCES_VISUALIZATION = {1: 'OX', 2: 'O.X', 3: 'O..X', 4: 'O...X'}
VALID_DISTANCES = DISTANCES_VISUALIZATION.keys()
VALID_DISTANCES_MAX = max(VALID_DISTANCES)
VALID_DISTANCES_MIN = min(VALID_DISTANCES)


def get_random_distance():
    return random.randint(VALID_DISTANCES_MIN, VALID_DISTANCES_MAX)


def visualize_distance(dist: int):
    return DISTANCES_VISUALIZATION[dist]
