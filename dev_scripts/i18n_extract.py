"""Extract translatable strings into locale/ru/LC_MESSAGES/*.po.

Two passes:
1. AST scan of kf_lib/ for _()/ngettext() calls -> kfw.po (prose templates).
   tr_name()/add_accompl() literal calls go to kfw_names.po instead.
2. Name harvest: imports kf_lib and collects identifier names (moves, techs,
   styles incl. style-gen words, items, traits, name prefixes) -> kfw_names.po.

Existing translations and fuzzy flags are preserved; entries that disappeared
from the code are kept but marked obsolete (#~), so no translation work is lost.

Run from dev_scripts/:  python i18n_extract.py
Then compile with:      python compile_locale.py
"""

import ast
import os
import sys
from pathlib import Path

# this has to be before imports from kf_lib
lib_path = Path('..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))

import i18n_common

PO_DIR = Path('locale') / 'ru' / 'LC_MESSAGES'
N = i18n_common.N_RU_PLURALS

# extra display names that can't be harvested from code structure
EXTRA_NAMES = {
    # fighter-name prefixes (kf_lib/game/_base_game.py)
    'Beggar', 'Drunkard', 'Thief', 'Master',
    # victory conditions (kf_lib/game/_playing.py)
    'Grandmaster', 'Folk Hero', 'Kung-fu Legend', 'Greatest Fighter', 'Uniter of Schools',
    'Famous Master', 'Living Legend', 'Master of Masters',
    # misc display names
    'Unknown', 'Gang Leader', 'Foshan',
}


def scan_code():
    """Yield (kind, msgid, msgid_plural, ref) from all kf_lib sources.

    kind is 'prose' or 'name'."""
    paths = sorted(Path('kf_lib').rglob('*.py')) + [Path('kfw.py')]
    for path in paths:
        ref = str(path)
        try:
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=ref)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name):
                fname = func.id
            elif isinstance(func, ast.Attribute):
                fname = func.attr  # e.g. p.add_accompl('...')
            else:
                continue
            args = node.args
            where = f'{ref}:{node.lineno}'
            if fname == '_' and args and _is_str(args[0]):
                yield 'prose', args[0].value, None, where
            elif fname == 'ngettext' and len(args) >= 2 and _is_str(args[0]) and _is_str(
                args[1]
            ):
                yield 'prose', args[0].value, args[1].value, where
            elif fname == 'tr_name' and args and _is_str(args[0]):
                yield 'name', args[0].value, None, where
            elif fname == 'add_accompl' and args and _is_str(args[0]):
                yield 'name', args[0].value, None, where


def _is_str(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def harvest_names():
    """Collect identifier names that get translated only at display time."""
    from kf_lib.actors import names as actor_names
    from kf_lib.actors import traits
    from kf_lib.kung_fu import moves, style_gen, styles, techniques
    from kf_lib.things import items, weapons

    found = set()
    found |= set(moves.ALL_MOVES_DICT)
    found |= set(techniques._all_techs)  # noqa: SLF001 (dev script)
    # upgraded style techs ('Advanced X') are created lazily at runtime
    # (techniques.get_upgraded_style_tech); harvest the names they will get
    for st in styles.all_styles.values():
        if st.techs:
            for t in st.techs.values():
                found.add(techniques.UPGRADED_STYLE_TECH_PREFIX + t.name)
    found |= set(styles.all_styles)
    found |= set(style_gen.W1) | set(style_gen.W2) | set(style_gen.W3)
    found |= set(items.all_items)
    found |= set(traits.TRAIT_EFFECTS)
    found |= set(weapons.all_weapons)
    found |= set(actor_names.GROUP_NAMES) | set(actor_names.GROUP_NAMES.values())
    found |= set(actor_names.ROBBER_NICKNAMES)
    found |= EXTRA_NAMES
    found.discard('')
    return sorted(found)


def merge(entries, scanned):
    """Merge scanned {(msgid, plural): [refs]} into existing po entries.

    Returns a new entry list: existing translations preserved, new msgids added
    empty, vanished msgids marked obsolete.
    """
    by_key = {(e['msgid'], e['msgid_plural']): e for e in entries}
    out = []
    seen = set()
    for (msgid, plural), refs in scanned.items():
        key = (msgid, plural)
        seen.add(key)
        e = by_key.get(key)
        if e is None:
            e = {
                'msgid': msgid,
                'msgid_plural': plural,
                'msgstr': {i: '' for i in range(N)} if plural is not None else '',
                'flags': set(),
                'refs': [],
            }
        e['refs'] = refs
        e['obsolete'] = False
        out.append(e)
    for e in entries:
        key = (e['msgid'], e['msgid_plural'])
        if key not in seen and e['msgid'] != '':
            e['obsolete'] = True
            out.append(e)
    return out


def load_existing(path):
    return i18n_common.parse_po(path) if path.exists() else [i18n_common.new_header()]


def main():
    PO_DIR.mkdir(parents=True, exist_ok=True)

    prose = {}
    names = {}
    for kind, msgid, plural, ref in scan_code():
        target = prose if kind == 'prose' else names
        target.setdefault((msgid, plural), [])
        if ref not in target[(msgid, plural)]:
            target[(msgid, plural)].append(ref)
    for name in harvest_names():
        names.setdefault((name, None), [])

    for path, scanned, label in (
        (PO_DIR / 'kfw.po', prose, 'prose'),
        (PO_DIR / 'kfw_names.po', names, 'names'),
    ):
        entries = merge(load_existing(path), scanned)
        i18n_common.write_po(entries, path)
        active = [e for e in entries if not e['obsolete'] and e['msgid']]
        done = [
            e
            for e in active
            if 'fuzzy' not in e['flags']
            and (
                e['msgstr'].replace('\x00', '')
                if isinstance(e['msgstr'], str)
                else any(e['msgstr'].values())
            )
        ]
        print(f'{path}: {len(active)} {label} entries, {len(done)} translated')


if __name__ == '__main__':
    main()
