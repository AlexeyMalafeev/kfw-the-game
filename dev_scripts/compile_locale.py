"""Compile all locale/**/LC_MESSAGES/*.po files to .mo next to them.

Pure-Python msgfmt replacement (stdlib only) so no gettext tooling is needed;
the compiled .mo files are committed to the repo.

Run from dev_scripts/:  python compile_locale.py
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


def main():
    po_files = sorted(Path('locale').glob('*/LC_MESSAGES/*.po'))
    if not po_files:
        print('no .po files found under locale/')
        return
    for po_path in po_files:
        entries = i18n_common.parse_po(po_path)
        mo_path = po_path.with_suffix('.mo')
        mo_path.write_bytes(i18n_common.compile_mo(entries))
        translated = sum(
            1
            for e in entries
            if e['msgid'] and not e['obsolete'] and 'fuzzy' not in e['flags']
        )
        print(f'{po_path} -> {mo_path} ({translated} entries)')


if __name__ == '__main__':
    main()
