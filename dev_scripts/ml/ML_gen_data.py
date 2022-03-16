import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..', '..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

from ml import ml_fighter_pwr


try:
    examples = 10000
    ml_fighter_pwr.generate_data(examples=examples)


except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
