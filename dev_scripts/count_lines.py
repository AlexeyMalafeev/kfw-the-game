import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))
print(os.getcwd())

files = os.listdir('.')
count = 0
n_files = 0
while files:
    for fn in files[:]:
        files.remove(fn)
        if fn.endswith('.py'):
            n_files += 1
            with open(fn, 'r', encoding='utf-8') as f:
                s = f.read()
                count += len([ss for ss in s.split('\n') if ss.strip()])
        if os.path.isdir(fn):
            files.extend([os.path.join(fn, ffn) for ffn in os.listdir(fn)])
    
print(count, 'non-empty lines of code')
print(n_files, 'files with code')
input('Press Enter to exit')