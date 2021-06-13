from .fighter import Fighter, Challenger, Master, Thug
from .human_controlled_fighter import HumanControlledFighter
from . import names
from kf_lib.kung_fu import styles
from kf_lib.utils.utilities import *


# levels
BEGGAR_LV = (8, 12)
BODYGUARD_LV = (6, 8)
BRAWLER_LV = (3, 6)
CHALLENGER_LV = (3, 10)
CONVICT_LV = (3, 10)
DRUNKARD_STRONG_LV = (8, 12)
DRUNKARD_WEAK_LV = (1, 3)
FAT_GIRL_LV = (5, 7)
FOREIGNER_LV = (10, 14)
GAMBLER_LV = (3, 6)
MASTER_LV = (8, 12)
PERFORMER_LV = (7, 10)
POLICE_LV = (1, 5)
ROBBER_LV = (1, 5)
STYLE_TECH_LV = 8
THIEF_LV = (1, 3)
THUG_LV = (1, 5)
TOUGH_THIEF_LV = (7, 10)
TOURN_PART_LV = (5, 10)


def from_exp_worth(x):  # todo reimplement
    """Return a list of fighters with x exp worth."""
    max_diff = round(x / 10)
    too_high = x + max_diff + 1
    # f = new_fighter(lv=1)
    # low_exp = f.get_exp_worth()
    # if low_exp > too_high:
    #     print('fighter_factory.from_exp_worth(x): x is too small ({})'.format(x))
    #     input('Press Enter to return.')
    #     return
    weapon_chance = 0.35
    min_lv = 1
    max_lv = 20
    max_n = 5
    i = 0
    while True:
        i += 1
        if max_n > 1:
            n = rndint(1, max_n)
        else:
            n = 1
        if max_lv <= min_lv:
            max_lv = min_lv + 1
        lv = rndint(min_lv, max_lv)
        fighters = new_fighter(lv=lv, n=n)
        if n == 1:
            f = fighters
            if rnd() <= weapon_chance:
                f.arm()
            fighters = [f]
        exp = sum([ff.get_exp_worth() for ff in fighters])
        if x <= exp < too_high:
            return fighters


def new_beggar():
    lv = rndint(*BEGGAR_LV)
    return Master('Beggar', styles.BEGGAR_STYLE.name, lv)


def new_bodyguard(weak=False, n=1):
    fs = []
    for i in range(n):
        if not weak:
            lv = rndint(*BODYGUARD_LV)
            rand_atts_mode = 2
        else:
            lv = 1
            rand_atts_mode = 0
        style = styles.get_rand_std_style().name
        f = Challenger('Bodyguard', style, lv, rand_atts_mode=rand_atts_mode)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_brawler():
    lv = rndint(*BRAWLER_LV)
    return Thug('Brawler', style_name=styles.DIRTY_FIGHTING.name, level=lv)


def new_challenger():
    lv = rndint(*CHALLENGER_LV)
    style = styles.get_rand_std_style().name
    f = Challenger('Unknown', style, lv)
    return f


def new_convict():
    lv = rndint(*CONVICT_LV)
    return Thug('Criminal', style_name=styles.DIRTY_FIGHTING.name, level=lv)


# todo more general function new_custom_f, then ..._hcf from it (set class, experiment)
def new_custom_hcf():
    name = input('Name: ')
    legend = [
        ('{:<{}} {}'.format(s.name, styles.MAX_LEN_STYLE_NAME, s.descr_short), s)
        for s in styles.default_styles
    ]
    # todo select starting atts
    style = menu(legend, 'Choose a style:')
    level = get_num_input('Level:', 1, 20)
    f = HumanControlledFighter(name=name, style_name=style.name)
    if level > 1:
        f.level_up(level - 1)  # fixme level-up doesn't work (e.g. level=10), only works once
    return f


def new_dummy_fighter(lv):
    """A fighter with flower kung-fu, only standard moves, no techs, etc."""
    return Fighter(name='Dummy', level=lv, tech_names=[], move_names=[])


def new_drunkard(strong=False):
    if strong:
        lv = rndint(*DRUNKARD_STRONG_LV)
        style = styles.DRUNKARD_STYLE.name
        rand_atts_mode = 2
        return Master('Drunkard', style, lv, rand_atts_mode=rand_atts_mode)
    else:
        lv = rndint(*DRUNKARD_WEAK_LV)
        style = None
        rand_atts_mode = 0
        return Thug('Drunkard', style, lv, rand_atts_mode=rand_atts_mode)


def new_f(name, style, lv, weapon=None, n=1):
    fs = []
    for _ in range(n):
        f = Fighter(name, style, lv)
        if weapon:
            f.arm(weapon)
        fs.append(f)
    if n == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_fat_girl():
    lv = rndint(*FAT_GIRL_LV)
    style = styles.get_rand_std_style().name
    f = Fighter('Fat Girl', style, lv)
    return f


def new_fighter(lv=0, n=1):
    fs = []
    for i in range(n):
        style = styles.get_rand_std_style().name
        if not lv:
            lv = rndint(1, 20)
        f = Fighter('Fighter', style, lv)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_foreigner(lv=0, country=None, name=None, style_name=None):
    if not lv:
        lv = rndint(*FOREIGNER_LV)
    if country is None:
        country = random.choice(names.FOREIGN_COUNTRIES)
    if name is None:
        name = random.choice(names.FOREIGN_NAMES[country])
    if style_name is None:
        style_name = styles.FOREIGN_STYLES[country].name
    f = Fighter(name, style_name, lv)
    f.country = country  # used in story module
    return f


def new_gambler():
    lv = rndint(*GAMBLER_LV)
    return Thug('Gambler', styles.DIRTY_FIGHTING.name, level=lv)


def new_hcf(name='Player', lv=1):
    style = styles.get_rand_std_style()
    f = HumanControlledFighter(name=name, style_name=style.name, level=lv)
    return f


def new_master(name, style):
    lv = rndint(*MASTER_LV)
    f = Master(name, style, lv)
    return f


def new_master_challenger(p_lv, name):
    lv = rndint(p_lv, p_lv + 2)
    style = styles.get_rand_std_style().name
    f = Master(name, style, lv)
    return f


def new_master_frn_chall(p_lv):
    lv = rndint(p_lv, p_lv + 2)
    return new_foreigner(lv=lv)


def new_monster(lv=0):
    if lv == 0:
        lv = rndint(1, 20)
    return Fighter('Monster', styles.MONSTER_KUNGFU.name, lv)


def new_ninja_turtles(lv=8):
    turtles = []
    for name in names.TURTLE_NAMES:
        turtles.append(Fighter(name, styles.TURTLE_NUNJUTSU.name, lv))
    return turtles


def new_official(name):
    return Fighter(name, level=3)


def new_opponent(style_name=styles.FLOWER_KUNGFU.name, lv=1, n=1, rand_atts_mode=0):
    fs = []
    for i in range(n):
        f = Fighter('Opponent', style_name, lv, rand_atts_mode=rand_atts_mode)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_performer():
    lv = rndint(*PERFORMER_LV)
    style = styles.get_rand_std_style().name
    return Master('Kung-fu Master', style, lv)


def new_police(n=1):
    fs = []
    for i in range(n):
        lv = rndint(*POLICE_LV)
        f = Fighter('Officer', styles.POLICE_KUNGFU.name, lv)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_prize_fighter(lv):
    name = 'Prize Fighter'
    return Thug(name, styles.DIRTY_FIGHTING.name, lv)


def new_random_fighter(styles_to_choose=None, n=1):
    if styles_to_choose is None:
        styles_to_choose = list(styles.all_styles.values())
    fs = []
    name = 'Random Fighter'
    for i in range(n):
        style = random.choice(styles_to_choose).name
        lv = rndint(1, 20)
        f = Fighter(name, style, lv)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_robber(weak=False, n=1):
    fs = []
    for i in range(n):
        if not weak:
            lv = rndint(*ROBBER_LV)
        else:
            lv = 1
        f = Thug('Robber', styles.DIRTY_FIGHTING.name, lv)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_student(name, style, lv):
    f = Challenger(name, style, lv)
    return f


def new_tourn_part(n=1):
    fs = []
    for i in range(n):
        lv = rndint(*TOURN_PART_LV)
        style = styles.get_rand_std_style().name
        f = Fighter(names.DFLT_TOURN_PART_NAME, style, lv)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_thief(tough=False):
    if not tough:
        lv = rndint(*THIEF_LV)
        style = styles.DIRTY_FIGHTING.name
        rand_atts_mode = 0
    else:
        lv = rndint(*TOUGH_THIEF_LV)
        style = styles.THIEF_STYLE.name
        rand_atts_mode = 2
    return Thug('Thief', style, lv, rand_atts_mode=rand_atts_mode)


def new_thug(weak=False, n=1):
    fs = []
    for i in range(n):
        if not weak:
            lv = rndint(*THUG_LV)
        else:
            lv = 1
        f = Thug('Thug', styles.DIRTY_FIGHTING.name, lv)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


# utility functions
def add_numbers_to_names(fighters):
    for i, f in enumerate(fighters):
        f.name += f' {i + 1}'


def copy_fighter(orig):
    """Return a Fighter copy of original fighter/player, e.g. for simulation.
    Weapons are included."""
    atts = Fighter.get_init_atts(orig)
    new = Fighter(*atts)
    if orig.weapon:
        new.arm(orig.weapon.name)
    return new