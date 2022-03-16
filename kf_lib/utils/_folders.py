from pathlib import Path


MOVES_FOLDER = 'moves'
SAVE_FOLDER = 'save'
TESTS_FOLDER = 'tests'


# ensure folders exist
Path(MOVES_FOLDER).mkdir(exist_ok=True)
Path(SAVE_FOLDER).mkdir(exist_ok=True)
Path(TESTS_FOLDER).mkdir(exist_ok=True)
