import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..', '..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

from kf_lib.ai import fight_ai_gen


try:
    ga = fight_ai_gen.GeneticAlgorithm(
        pop_size=16,
        n_fights_1on1=8,
        n_fights_crowd=2,
        mutation_prob=0.1,
        infighting=True,
    )
    ga.run(128)

    ga = fight_ai_gen.GeneticAlgorithm(
        pop_size=32,
        n_fights_1on1=64,
        n_fights_crowd=16,
        mutation_prob=0.1,
        infighting=False,
    )
    ga.run(128)

    input('Press Enter to exit')


except Exception: # noqa
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
