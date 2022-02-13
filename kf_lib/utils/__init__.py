import time

from ._lang_tools import *
from ._numbers import *


def get_time():
    return time.ctime()


def add_to_dict(d: dict, k: str, v: int, start_val: int = 0) -> None:
    d[k] = d.get(k, start_val) + v