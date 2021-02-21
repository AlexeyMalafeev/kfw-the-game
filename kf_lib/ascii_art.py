import os


def concat(a, b):
    lines_a = a.split('\n')
    lines_b = b.split('\n')
    max_len = max([len(lines_a[i]) + len(lines_b[i]) for i in range(len(lines_a))])
    new_lines = []
    for i in range(len(lines_a)):
        cur_len = len(lines_a[i]) + len(lines_b[i])
        pad = max_len - cur_len
        new_lines.append(lines_a[i] + ' ' * pad + lines_b[i])
    return '\n'.join(new_lines)


def finalize(lines):
    # print('\n'.join(lines))
    new_lines = [line[:-1] for line in lines]
    new_lines = [line.rstrip() for line in new_lines]
    new_lines = [line.replace('s', ' ') for line in new_lines]
    # print('\n'.join(new_lines))
    # input('....')
    return '\n'.join(new_lines), new_lines


def mirror(lines):
    temp = []
    repl_table = {
        '\\': '/',
        '/': '\\',
        '>': '<',
        '<': '>',
        ')': '(',
        '(': ')',
        'p': 'q',
        'c': 'D',  # todo better 'mirroring' for this symbol
        '[': ']',
        ']': '[',
    }
    for line in lines:
        temp_s = ''
        for c in line:
            if c in repl_table:
                c = repl_table[c]
            temp_s += c
        temp.append(temp_s[::-1])
    return '\n'.join(temp)


FIGHTER_ART_L = {}
FIGHTER_ART_R = {}


def set_ascii_art():
    with open(os.path.join('move files', 'ascii mapping.txt')) as f:
        blocks = f.read().split('# ')[1:]
        for b in blocks:
            b = b.rstrip()  # remove \n
            lines = b.split('\n')
            m_names = lines[0].split(', ')
            art, as_lines = finalize(lines[1:])
            mir = mirror(as_lines)
            for mn in m_names:
                FIGHTER_ART_L[mn] = art
                FIGHTER_ART_R[mn] = mir


set_ascii_art()
DEFAULT_MOVE_ART = 'Stance'


def get_ascii(move_name):
    if move_name in FIGHTER_ART_L:
        key = move_name
    else:
        words = move_name.split()
        if 'Flying' in words:
            key = 'Flying ' + words[-1]
        else:
            for i in range(len(words) - 1):
                temp = f'{words[i]} {words[-1]}'
                # print(temp)
                if temp in FIGHTER_ART_L:
                    key = temp
                    # print(move_name, '->', key)
                    # input()
                    break
            else:
                key = words[-1]
        if key not in FIGHTER_ART_L:
            key = DEFAULT_MOVE_ART
    ascii_l = FIGHTER_ART_L[key]
    ascii_r = FIGHTER_ART_R[key]
    return ascii_l, ascii_r
