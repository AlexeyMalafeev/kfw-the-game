"""One-shot: fill Russian prose translations from _prose_ru.py into
locale/ru/LC_MESSAGES/kfw.po. Run from dev_scripts/:

    python fill_prose_ru.py
"""

import os
import sys
from pathlib import Path

# this has to be before imports from kf_lib
lib_path = Path('..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

import i18n_common
from _prose_ru import TR, TR_PLURAL

PO_PATH = Path('locale') / 'ru' / 'LC_MESSAGES' / 'kfw.po'


def main():
    entries = i18n_common.parse_po(PO_PATH)
    filled = 0
    used = set()
    for e in entries:
        if not e['msgid'] or e['obsolete']:
            continue
        if e['msgid_plural'] is not None:
            if e['msgid'] in TR_PLURAL:
                e['msgstr'] = dict(enumerate(TR_PLURAL[e['msgid']]))
                used.add(e['msgid'])
                filled += 1
        elif e['msgid'] in TR:
            e['msgstr'] = TR[e['msgid']]
            used.add(e['msgid'])
            filled += 1
    i18n_common.write_po(entries, PO_PATH)
    unused = (set(TR) | set(TR_PLURAL)) - used
    print(f'filled {filled} entries')
    if unused:
        print(f'WARNING: {len(unused)} translations matched no msgid:')
        for u in sorted(unused):
            print(f'  {u[:80]!r}')


if __name__ == '__main__':
    main()
