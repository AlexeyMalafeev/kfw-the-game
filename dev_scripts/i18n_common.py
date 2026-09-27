"""Shared minimal .po parsing/writing and .mo compilation (stdlib only).

Used by i18n_extract.py, compile_locale.py and i18n_coverage.py. The game ships
committed .mo files, so players never need gettext tooling.

Entry model: dict with keys
    msgid        str
    msgid_plural str or None
    msgstr       str, or dict[int, str] for plural entries
    flags        set[str]      e.g. {'fuzzy'}
    refs         list[str]     '#:' source references, extractor only
    obsolete     bool
"""

import ast
import struct

RU_PLURAL_FORMS = (
    'nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : '
    'n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : 2);'
)

HEADER_FIELDS = {
    'Project-Id-Version': 'kfw',
    'Report-Msgid-Bugs-To': '',
    'POT-Creation-Date': '',
    'PO-Revision-Date': '',
    'Last-Translator': '',
    'Language-Team': '',
    'Language': 'ru',
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=UTF-8',
    'Content-Transfer-Encoding': '8bit',
    'Plural-Forms': RU_PLURAL_FORMS,
}

N_RU_PLURALS = 3


def new_header():
    msgstr = ''.join(f'{k}: {v}\n' for k, v in HEADER_FIELDS.items())
    return {
        'msgid': '',
        'msgid_plural': None,
        'msgstr': msgstr,
        'flags': set(),
        'refs': [],
        'obsolete': False,
    }


def _unquote(token):
    """Parse a po string literal body (already stripped of surrounding quotes)."""
    try:
        return ast.literal_eval('"' + token + '"')
    except (SyntaxError, ValueError):
        return token.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')


def _escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\t', '\\t').replace(
        '\n', '\\n'
    )


def parse_po(path):
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    entries = []
    cur = None  # current entry dict
    last_field = None  # 'msgid' | 'msgid_plural' | 'msgstr' | int (plural index)
    obsolete = False

    def flush():
        nonlocal cur
        if cur is not None:
            cur['obsolete'] = obsolete
            entries.append(cur)
            cur = None

    for line in lines:
        if not line.strip():
            flush()
            last_field = None
            obsolete = False
            continue
        if line.startswith('#~'):
            obsolete = True
            line = line[2:].lstrip()
            if not line:
                continue
        elif line.startswith('#'):
            if line.startswith('#:') and cur is not None:
                cur['refs'].extend(line[2:].split())
            elif line.startswith('#,') and cur is not None:
                cur['flags'] |= {f.strip() for f in line[2:].split(',') if f.strip()}
            continue
        if line.startswith('msgid_plural'):
            cur['msgid_plural'] = _unquote(line[len('msgid_plural'):].strip()[1:-1])
            last_field = 'msgid_plural'
        elif line.startswith('msgid'):
            flush()
            cur = {
                'msgid': _unquote(line[len('msgid'):].strip()[1:-1]),
                'msgid_plural': None,
                'msgstr': '',
                'flags': set(),
                'refs': [],
            }
            last_field = 'msgid'
        elif line.startswith('msgstr['):
            idx = int(line[line.index('[') + 1: line.index(']')])
            if not isinstance(cur['msgstr'], dict):
                cur['msgstr'] = {}
            cur['msgstr'][idx] = _unquote(line[line.index(']') + 1:].strip()[1:-1])
            last_field = idx
        elif line.startswith('msgstr'):
            cur['msgstr'] = _unquote(line[len('msgstr'):].strip()[1:-1])
            last_field = 'msgstr'
        elif line.startswith('"'):
            chunk = _unquote(line.strip()[1:-1])
            if last_field == 'msgid':
                cur['msgid'] += chunk
            elif last_field == 'msgid_plural':
                cur['msgid_plural'] += chunk
            elif last_field == 'msgstr':
                cur['msgstr'] += chunk
            elif isinstance(last_field, int):
                cur['msgstr'][last_field] += chunk
    flush()
    return entries


def _format_string(field, value):
    """Format one po field; strings with newlines use the multiline form."""
    if '\n' not in value:
        return [f'{field} "{_escape(value)}"']
    out = [f'{field} ""']
    parts = value.split('\n')
    for i, part in enumerate(parts):
        suffix = '\\n' if i < len(parts) - 1 else ''
        if part or suffix:
            out.append(f'"{_escape(part)}{suffix}"')
    return out


def write_po(entries, path):
    """Write entries sorted by msgid (header entry first)."""
    out = []
    header = None
    regular = []
    for e in entries:
        if e['msgid'] == '' and not e['obsolete']:
            header = e
        else:
            regular.append(e)
    regular.sort(key=lambda e: e['msgid'].lower())
    if header is None:
        header = new_header()

    def emit(e):
        if e['flags']:
            out.append('#, ' + ', '.join(sorted(e['flags'])))
        if e['refs']:
            out.append('#: ' + ' '.join(sorted(e['refs'])))
        prefix = '#~ ' if e['obsolete'] else ''
        out.extend(prefix + ln for ln in _format_string('msgid', e['msgid']))
        if e['msgid_plural'] is not None:
            out.extend(
                prefix + ln for ln in _format_string('msgid_plural', e['msgid_plural'])
            )
        if isinstance(e['msgstr'], dict):
            for idx in sorted(e['msgstr']):
                out.extend(
                    prefix + ln
                    for ln in _format_string(f'msgstr[{idx}]', e['msgstr'][idx])
                )
        else:
            out.extend(prefix + ln for ln in _format_string('msgstr', e['msgstr']))
        out.append('')

    emit(header)
    for e in regular:
        emit(e)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))


def _entry_key(e):
    if e['msgid_plural'] is not None:
        return e['msgid'] + '\x00' + e['msgid_plural']
    return e['msgid']


def _entry_value(e):
    if isinstance(e['msgstr'], dict):
        forms = [e['msgstr'].get(i, '') for i in range(max(e['msgstr'] or {0: 0}) + 1)]
        return '\x00'.join(forms)
    return e['msgstr']


def compile_mo(entries):
    """Compile entries to .mo bytes (like msgfmt: skip obsolete, fuzzy and
    untranslated entries; the header is always included)."""
    messages = {}
    for e in entries:
        if e['obsolete'] or 'fuzzy' in e['flags']:
            continue
        value = _entry_value(e)
        if e['msgid'] != '' and not value.replace('\x00', ''):
            continue  # untranslated
        messages[_entry_key(e)] = value
    keys = sorted(messages)
    offsets = []
    ids = strs = b''
    for k in keys:
        kid = k.encode('utf-8')
        kstr = messages[k].encode('utf-8')
        offsets.append((len(ids), len(kid), len(strs), len(kstr)))
        ids += kid + b'\x00'
        strs += kstr + b'\x00'
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    return b''.join(
        [
            struct.pack('Iiiiiii', 0x950412DE, 0, len(keys), 7 * 4,
                        7 * 4 + len(keys) * 8, 0, 0),
            struct.pack('i' * len(koffsets), *koffsets),
            struct.pack('i' * len(voffsets), *voffsets),
            ids,
            strs,
        ]
    )
