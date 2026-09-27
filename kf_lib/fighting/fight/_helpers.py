from ._auto_fight import AutoFight
from ._normal_fight import NormalFight
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.ui import cls, pak, yn


def get_prefight_info(side_a, side_b=None, hide_enemy_stats=False, basic_info_only=False,
                      groups=None):
    fs = side_a[:]
    if side_b:
        fs.extend(side_b)
    group_labels = {}
    if groups:
        for i, group in enumerate(groups):
            if group:
                label = _('--- Group {n} ---').format(n=i + 1)
                if any(f.is_human for f in group):
                    label = _('--- Group {n} (your group) ---').format(n=i + 1)
                group_labels[id(group[0])] = label
    s = ''
    first_fighter = fs[0]
    head_name = _('NAME')
    head_lev = _('LEV')
    head_style = _('STYLE')
    disp_names = [tr_fighter_name(f.name) for f in fs]
    size1 = max([len(s) for s in [head_name + ' '] + [n + '  ' for n in disp_names]])
    size2 = max([len(s) for s in [head_lev + ' '] + [str(f.level) + ' ' for f in fs]])
    size3 = max(
        [len(s) for s in [head_style + ' '] + [f.get_displayed_style_name() + ' ' for f in fs]]
    )
    att_names = ' '.join(first_fighter.att_names_short) if not basic_info_only else ''
    s += head_name.ljust(size1) + head_lev.ljust(size2) + head_style.ljust(size3) + att_names
    if any([f.weapon for f in fs]) and not basic_info_only:
        s += ' ' + _('WEAPON')
    for f, disp_name in zip(fs, disp_names):
        if id(f) in group_labels:
            s += f'\n{group_labels[id(f)]}'
        if side_b and f == side_b[0]:
            s += '\n-vs-'
        s += '\n{:<{}}{:<{}}{:<{}}'.format(
            disp_name,
            size1,
            f.level,
            size2,
            f.get_displayed_style_name(),
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
            s += f'{f.weapon.display_name} {f.weapon.descr_short}'
        s += f"\n{' ' * (size1 + size2)}{f.get_displayed_style_emph()}"
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
    hp_carry=None,
):
    """Return True if f1 wins, False otherwise (including draw)."""
    side_a, side_b = get_sides(f1, f2, f1_allies, f2_allies)
    all_fighters = side_a + side_b
    # humans who opted to auto-fight all their bouts (tournaments) don't get
    # the prefight display and the 'Auto fight?' prompt
    humans = [f for f in all_fighters if f.is_human and not f.auto_fight_all]
    if humans:
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
            auto_fight = yn(_('\nAuto fight?'))
        else:
            pak()
            cls()
    else:
        auto_fight = True
    if auto_fight:
        f = AutoFight(
            side_a, side_b, environment_allowed, items_allowed, win_messages, school_display,
            hp_carry=hp_carry,
        )
    else:
        f = NormalFight(
            side_a, side_b, environment_allowed, items_allowed, win_messages, school_display,
            hp_carry=hp_carry,
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
