import os
from pathlib import Path

from kf_lib.ui import menu

sorting = menu(['cumulative', 'calls'], title="Sorting?")
path = Path('tests', f'profile_{sorting}.txt')
os.system(
    f'python -m cProfile -s "{sorting}" NG_autoplay_silent_ending.py > {path}')
print(f'Saved to {path} successfully')
