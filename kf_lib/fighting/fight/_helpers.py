from ._auto_fight import AutoFight
from ._normal_fight import NormalFight
from kf_lib.ui import cls, pak, yn


def get_prefight_info(side_a, side_b=None, hide_enemy_stats=False, basic_info_only=False):
    fs = side_a[:]
    if side_b:
        fs.extend(side_b)
    s = ''
    first_fighter = fs[0]
    size1 = max([len(s) for s in ['NAME '] + [f.name + '  ' for f in fs]])
    size2 = max([len(s) for s in ['LEV '] + [str(f.level) + ' ' for f in fs]])
    size3 = max([len(s) for s in ['STYLE '] + [f.style.name + ' ' for f in fs]])
    att_names = ' '.join(first_fighter.att_names_short) if not basic_info_only else ''
    s += 'NAME'.ljust(size1) + 'LEV'.ljust(size2) + 'STYLE'.ljust(size3) + att_names
    if any([f.weapon for f in fs]) and not basic_info_only:
        s += ' WEAPON'
    for f in fs:
        if side_b and f == side_b[0]:
            s += '\n-vs-'
        s += '\n{:<{}}{:<{}}{:<{}}'.format(
            f.name,
            size1,
            f.level,
            size2,
            f.style.name,
            size3,
        )
        if basic_info_only:
            continue
        if (
                (not hide_enemy_stats)
                or f.is_human
                or (f in side_a and any([ff.is_human for ff in side_a]))
                or (side_b and f in side_b and any([ff.is_human for ff in side_b]))
        ):
            atts_wb = (f.get_att_str_prefight(att) for att in first_fighter.att_names)
        else:
            atts_wb = (f.get_att_str_prefight(att, hide=True) for att in first_fighter.att_names)
        s += '{:<4}{:<4}{:<4}{:<4}'.format(*atts_wb)
        if f.weapon:
            s += f'{f.weapon.name} {f.weapon.descr_short}'
        s += f"\n{' ' * (size1 + size2)}{f.style.descr_short}"
    return s


def fight(
    f1,
    f2,
    f1_allies=None,
    f2_allies=None,
    auto_fight=False,
    af_option=True,
    hide_stats=True,
    environment_allowed=True,
    items_allowed=True,
    win_messages=None,
    school_display=False,
    return_fight_obj=False,
):
    """Return True if f1 wins, False otherwise (including draw)."""
    side_a, side_b = get_sides(f1, f2, f1_allies, f2_allies)
    all_fighters = side_a + side_b
    if any((f.is_human for f in all_fighters)):
        if not any((f.is_human for f in side_a)):
            side_a, side_b = (
                side_b,
                side_a,
            )  # swap sides for human player's convenience (e.g. in tournaments)
            if win_messages:
                temp = win_messages[:]
                win_messages = [temp[1], temp[0]]  # swap win messages also
        cls()
        print(get_prefight_info(side_a, side_b, hide_stats))
        if af_option:
            auto_fight = yn('\nAuto fight?')
        else:
            pak()
            cls()
    else:
        auto_fight = True
    if auto_fight:
        f = AutoFight(
            side_a, side_b, environment_allowed, items_allowed, win_messages, school_display
        )
    else:
        f = NormalFight(
            side_a, side_b, environment_allowed, items_allowed, win_messages, school_display
        )
    if return_fight_obj:
        return f
    return f.win


def get_sides(f1, f2, f1_allies, f2_allies):
    side_a = [f1]
    if f1_allies:
        side_a.extend(f1_allies)
    side_b = [f2]
    if f2_allies:
        side_b.extend(f2_allies)
    return side_a, side_b
