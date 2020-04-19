import os


files = os.listdir('.')
files.remove('count lines.py')
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