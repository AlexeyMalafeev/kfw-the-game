"""Profile a headless autoplay game with cProfile.

Run from dev_scripts/ (the chdir hack below assumes it):
    cd dev_scripts && ../.venv/bin/python profile_game.py
Output goes to tests/profile_<sorting>.txt
"""
import os
import sys
from pathlib import Path

# this has to be before imports from kf_lib
lib_path = Path('..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

from kf_lib.ui import menu

sorting = menu(['cumulative', 'calls'], title="Sorting?")
path = Path('tests', f'profile_{sorting}.txt')
os.system(
    f'{sys.executable} -m cProfile -s "{sorting}" kfw.py --autoplay --silent-ending > {path}')
print(f'Saved to {path} successfully')
