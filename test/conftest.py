import os
import sys

# The game loads moves/quotes via cwd-relative paths at import time,
# so make sure tests always run as if from the repo root.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
