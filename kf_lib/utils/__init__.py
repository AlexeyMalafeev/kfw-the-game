import time

from ._data import *
from ._validators import *
from ._folders import *
from ._lang_tools import *
from ._numbers import *
from ._random import *


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
        filename=f'kfw.log',
        mode='w',
        encoding='utf-8',
    )
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_time():
    return time.ctime()


def add_to_dict(d: dict, k: str, v: int, start_val: int = 0) -> None:
    d[k] = d.get(k, start_val) + v
