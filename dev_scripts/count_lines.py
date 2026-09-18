import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

SKIP_DIRS = {'.git', '.venv', '__pycache__', '.pytest_cache'}

count = 0
n_files = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
    for fn in files:
        if not fn.endswith('.py'):
            continue
        n_files += 1
        with open(
            os.path.join(root, fn), 'r', encoding='utf-8', errors='ignore'
        ) as f:
            s = f.read()
        count += len([ss for ss in s.split('\n') if ss.strip()])

print(count, 'non-empty lines of code')
print(n_files, 'files with code')
input('Press Enter to exit')
