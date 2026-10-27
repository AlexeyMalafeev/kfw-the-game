"""Compare fight-balance reports side by side (`tests/test f.b. *.txt` or any harness output).

    python compare_fb_reports.py OLD.txt NEW.txt [MORE.txt ...]
    python compare_fb_reports.py OLD.txt NEW.txt --section "style buffs" --section "techs 1"
    python compare_fb_reports.py a.txt b.txt c.txt --key guard --key counters

Prints each report's fight-stats lines, then for every table row the Diff% in each
report. A '*' after a value marks a change from the FIRST report that exceeds the
two reports' combined noise margin (sqrt(m1^2 + m2^2), from the +-95% column; reports
of the old single-process harness have no margins, so they never get a '*').
Rows are sorted by the last report's Diff%. Runs from any cwd.
"""
import argparse
import re
from pathlib import Path

ROW = re.compile(r'^(\d+)\s+(.+?)\s+(-?\d+)\s+(-?\d+)\s+(-?[\d.]+)\s+(\d+)(?:\s+([\d.]+|-))?')


def parse(path):
    """-> (fight stats lines, {section: {key: (diff, margin or None, sum)}})"""
    stats, tables, section = [], {}, None
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.endswith(':') and line[:1].isalpha() and '=' not in line:
            section = line[:-1]
            tables[section] = {}
            continue
        if section and section.startswith('fight stats') and line.strip():
            # per-tier stats (since 2026-10-27) prefixed with their tier
            stats.append(line if section == 'fight stats' else f'{section[12:]}: {line}')
            continue
        m = ROW.match(line)
        if m and section:
            margin = float(m.group(7)) if m.group(7) not in (None, '-') else None
            tables[section][m.group(2).strip()] = (float(m.group(5)), margin, int(m.group(6)))
    return stats, tables


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('reports', nargs='+')
    parser.add_argument('--section', action='append', default=[], help='only these tables')
    parser.add_argument('--key', action='append', default=[], help='only these rows')
    args = parser.parse_args()

    parsed = [parse(p) for p in args.reports]
    labels = [f'[{i + 1}]' for i in range(len(parsed))]
    for label, path, (stats, _) in zip(labels, args.reports, parsed):
        print(f'{label} {path}')
        for line in stats:
            print(f'    {line}')
    sections = args.section or list(parsed[-1][1])
    width = 10
    for section in sections:
        keys = set()
        for _, tables in parsed:
            keys |= set(tables.get(section, {}))
        if args.key:
            keys &= set(args.key)
        if not keys:
            continue

        def last_diff(k):
            return parsed[-1][1].get(section, {}).get(k, (float('-inf'),))[0]

        print(f'\n{section}:' + ''.join(f'{lb:>{width}}' for lb in labels))
        for k in sorted(keys, key=last_diff, reverse=True):
            first = parsed[0][1].get(section, {}).get(k)
            cells = []
            for _, tables in parsed:
                row = tables.get(section, {}).get(k)
                if row is None:
                    cells.append(f'{"-":>{width}}')
                    continue
                mark = ''
                if first and row is not first and first[1] and row[1]:
                    if abs(row[0] - first[0]) > (first[1] ** 2 + row[1] ** 2) ** 0.5:
                        mark = '*'
                cells.append(f'{row[0]:>{width - 1}.2f}{mark or " "}')
            print(f'  {k[:28]:28s}' + ''.join(cells))


if __name__ == '__main__':
    main()
