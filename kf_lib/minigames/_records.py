"""Best results of the mini-games, kept next to the saves.

save/minigame_records.json maps a mini-game to its records, e.g.
{"ring": {"normal": {"wins": 5, ...}}, "bag": {"best": {"damage": 950, ...}}}.
A missing or damaged file means no records yet; a file that can't be written
just loses the new record. Android's load and export lists skip the file:
they list valid saves only.
"""
import json
from pathlib import Path

from kf_lib.utils import SAVE_FOLDER

FILE_NAME = 'minigame_records.json'


def _path():
    return Path(SAVE_FOLDER, FILE_NAME)


def _load_all():
    try:
        data = json.loads(_path().read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def get_records(game):
    """{key: record dict} of one mini-game; only well-formed records."""
    section = _load_all().get(game)
    if not isinstance(section, dict):
        return {}
    return {k: v for k, v in section.items() if isinstance(v, dict)}


def get_score(record, field):
    """A record's numeric score, or 0 when it is missing or damaged."""
    value = record.get(field) if record else None
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def save_record(game, key, record):
    data = _load_all()
    section = data.get(game)
    if not isinstance(section, dict):
        section = data[game] = {}
    section[key] = record
    path = _path()
    tmp = path.with_suffix('.tmp')
    try:
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        tmp.replace(path)
    except OSError:
        pass
