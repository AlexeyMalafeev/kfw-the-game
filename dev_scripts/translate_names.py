"""Machine-draft Russian translations for the kfw_names domain.

Most of the ~14k names are combinatorial move names ([modifiers...] HEAD),
translated deterministically via the ADJ/HEAD/POSS dictionaries in
_names_ru.py with adjective-noun gender agreement; non-compositional names
(styles, techs, items, weapons, traits, ...) come from OVERRIDES.

Existing translations in the .po are NOT overwritten — only empty msgstr
entries are filled, so human-reviewed entries survive re-runs.

Names that can't be translated are reported to stdout (add ADJ/HEAD/POSS or
OVERRIDES entries and re-run).

Run from dev_scripts/:  python translate_names.py
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
from _names_ru import ADJ, HEAD, OVERRIDES, POSS

PO_PATH = Path('locale') / 'ru' / 'LC_MESSAGES' / 'kfw_names.po'
ROMAN = {'I', 'II', 'III'}


def translate(name):
    if name in OVERRIDES:
        return OVERRIDES[name]
    tokens = name.split()
    suffix = []
    while tokens and tokens[-1] in ROMAN:
        suffix.insert(0, tokens.pop())
    if not tokens:
        return None
    # 'Advanced <tech/style name>' -> '<name> (продвинутый)' (parenthetical
    # form sidesteps adjective-noun gender agreement with the base name)
    if tokens[0] == 'Advanced' and len(tokens) > 1:
        base = translate(' '.join(tokens[1:]) + (' ' + ' '.join(suffix) if suffix else ''))
        if base is not None:
            return f'{base} (продвинутый)'
    poss = []
    mods = []
    for t in tokens[:-1]:
        if t.endswith("'s") and t in POSS:
            poss.append(POSS[t])
        elif t in ADJ:
            mods.append(t)
        else:
            return None
    head_tok = tokens[-1]
    if head_tok not in HEAD:
        return None
    head_ru, gender = HEAD[head_tok]
    parts = [ADJ[m][gender] for m in mods] + [head_ru] + poss + suffix
    res = ' '.join(parts)
    return res[0].upper() + res[1:]


def main():
    entries = i18n_common.parse_po(PO_PATH)
    filled = 0
    untranslated = []
    for e in entries:
        if not e['msgid'] or e['obsolete']:
            continue
        if isinstance(e['msgstr'], str) and e['msgstr']:
            continue  # keep existing (possibly human-reviewed) translations
        tr = translate(e['msgid'])
        if tr is None:
            untranslated.append(e['msgid'])
        else:
            e['msgstr'] = tr
            filled += 1
    i18n_common.write_po(entries, PO_PATH)
    print(f'filled {filled} names; {len(untranslated)} untranslated:')
    for name in untranslated:
        print(f'  {name!r},')


if __name__ == '__main__':
    main()
