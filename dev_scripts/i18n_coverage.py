"""Report translation coverage for locale/ru/LC_MESSAGES/*.po.

Run from dev_scripts/:  python i18n_coverage.py
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


def is_translated(e):
    if isinstance(e['msgstr'], dict):
        return any(e['msgstr'].values())
    return bool(e['msgstr'])


def main():
    po_files = sorted(Path('locale').glob('*/LC_MESSAGES/*.po'))
    if not po_files:
        print('no .po files found under locale/')
        return
    for po_path in po_files:
        entries = i18n_common.parse_po(po_path)
        active = [e for e in entries if e['msgid'] and not e['obsolete']]
        fuzzy = [e for e in active if 'fuzzy' in e['flags']]
        done = [e for e in active if is_translated(e) and e not in fuzzy]
        missing = len(active) - len(done) - len(fuzzy)
        pct = 100 * len(done) / len(active) if active else 100
        print(
            f'{po_path.name}: {len(done)}/{len(active)} translated ({pct:.0f}%), '
            f'{len(fuzzy)} fuzzy, {missing} missing'
        )


if __name__ == '__main__':
    main()
