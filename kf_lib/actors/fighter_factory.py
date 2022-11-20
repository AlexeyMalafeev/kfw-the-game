import random

from kf_lib.kung_fu import styles, style_gen
from kf_lib.ui import get_int_from_user, menu
from kf_lib.utils import rnd, rndint
from . import names
from .fighter import Fighter, Challenger, Master, Thug
from .human_controlled_fighter import HumanControlledFighter


# levels
BEGGAR_LV = (8, 12)
BODYGUARD_LV = (6, 8)
BRAWLER_LV = (3, 6)
CONVICT_LV = (3, 10)
CRAFTSMAN_LV = (5, 20)
DRUNKARD_STRONG_LV = (8, 12)
DRUNKARD_WEAK_LV = (1, 3)
FAT_GIRL_LV = (5, 7)
FOREIGNER_LV = (10, 14)
GAMBLER_LV = (3, 6)
MASTER_LV = (11, 14)
PERFORMER_LV = (7, 10)
POLICE_LV = (1, 5)
ROBBER_LV = (1, 5)
STUDENT_LV = (1, 10)
STYLE_TECH_LV = 8
THIEF_LV = (1, 3)
THUG_LV = (1, 5)
TOUGH_THIEF_LV = (7, 10)


def from_exp_worth(x):  # todo reimplement
    """Return a list of fighters with x exp worth."""
    max_diff = round(x / 10)
    too_high = x + max_diff + 1
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
    f = Master('Beggar', styles.BEGGAR_STYLE.name, level=1)
    f.level_up(lv - 1)  # to gradually learn techs and moves
    return f


def new_bodyguard(weak=False, n=1):
    fs = []
    for i in range(n):
        if not weak:
            lv = rndint(*BODYGUARD_LV)
            rand_atts_mode = 2
        else:
            lv = 1
            rand_atts_mode = 0
        style = style_gen.get_new_randomly_generated_style()
        f = Challenger('Bodyguard', style, lv, rand_atts_mode=rand_atts_mode)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_brawler():
    lv = rndint(*BRAWLER_LV)
    return Thug('Brawler', style=styles.DIRTY_FIGHTING, level=lv)


def new_convict():
    lv = rndint(*CONVICT_LV)
    return Thug('Criminal', style=styles.DIRTY_FIGHTING, level=lv)


def new_craftsman():
    lv = rndint(*CRAFTSMAN_LV)
    style = style_gen.get_new_randomly_generated_style()
    f = Master('Craftsman', level=1, style=style)
    f.level_up(lv - 1)
    return f


# todo more general function new_custom_f, then ..._hcf from it (set class, experiment)
def new_custom_hcf():
    name = input('Name: ')
    max_len = max((len(s.name) for s in styles.default_styles))
    legend = [
        ('{:<{}} {}'.format(s.name, max_len, s.descr_short), s)
        for s in styles.default_styles
    ]
    # todo select starting atts
    style = menu(legend, 'Choose a style:')
    level = get_int_from_user('Level:', 1, 20)
    f = HumanControlledFighter(name=name, style=style)
    if level > 1:
        f.level_up(level - 1)
    return f


def new_dummy_fighter(lv):
    """A fighter with flower kung-fu, only standard moves, no techs, etc."""
    return Fighter(name='Dummy', level=lv, tech_names=[], move_names=[])


def new_drunkard(strong=False):
    if strong:
        lv = rndint(*DRUNKARD_STRONG_LV)
        style = styles.DRUNKARD_STYLE.name
        rand_atts_mode = 2
        f = Master('Drunkard', style, level=1, rand_atts_mode=rand_atts_mode)
        f.level_up(lv - 1)
        return f
    else:
        lv = rndint(*DRUNKARD_WEAK_LV)
        rand_atts_mode = 0
        return Thug('Drunkard', level=lv, rand_atts_mode=rand_atts_mode)


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
    style = style_gen.get_new_randomly_generated_style()
    f = Fighter('Fat Girl', style, level=1)
    f.level_up(lv - 1)
    return f


def new_fighter(lv=0, n=1):
    fs = []
    for i in range(n):
        style = style_gen.get_new_randomly_generated_style()
        if not lv:
            lv = rndint(1, 20)
        f = Fighter('Fighter', style, lv)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_foreigner(lv=0, country=None, name=None, style=None):
    if not lv:
        lv = rndint(*FOREIGNER_LV)
    if country is None:
        country = random.choice(names.FOREIGN_COUNTRIES)
    if name is None:
        name = random.choice(names.FOREIGN_NAMES[country])
    if style is None:
        style = styles.FOREIGN_STYLES[country]
    f = Fighter(name, style, level=1)
    f.level_up(lv - 1)
    f.country = country  # used in story module
    return f


def new_gambler():
    lv = rndint(*GAMBLER_LV)
    return Thug('Gambler', styles.DIRTY_FIGHTING.name, level=lv)


def new_hcf(name='Player', lv=1):
    style = style_gen.get_new_randomly_generated_style()
    f = HumanControlledFighter(name=name, style=style, level=lv)
    return f


def new_master(name, style):
    lv = rndint(*MASTER_LV)
    f = Master(name, style, level=1)
    f.level_up(lv - 1)  # to gradually learn techs and moves
    return f


def new_master_challenger(p_lv, name):
    lv = rndint(p_lv, p_lv + 2)
    style = style_gen.get_new_randomly_generated_style()
    f = Master(name, style, level=1)
    f.level_up(lv - 1)
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
        f = Fighter(name, styles.TURTLE_NUNJUTSU.name, level=1)
        f.level_up(lv - 1)
        turtles.append(f)
    return turtles


def new_official(name):
    return Fighter(name, level=3)


def new_opponent(style=styles.FLOWER_KUNGFU, lv=1, n=1, rand_atts_mode=0):
    fs = []
    for i in range(n):
        f = Fighter('Opponent', style, lv, rand_atts_mode=rand_atts_mode)
        fs.append(f)
    if len(fs) == 1:
        return fs[0]
    else:
        add_numbers_to_names(fs)
        return fs


def new_performer():
    lv = rndint(*PERFORMER_LV)
    style = style_gen.get_new_randomly_generated_style()
    f = Master('Kung-fu Master', style, level=1)
    f.level_up(lv - 1)
    return f


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
        f = Fighter(name, style, level=1)
        f.level_up(lv - 1)
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


def new_student(name, style):
    lv = rndint(*STUDENT_LV)
    f = Challenger(name, style, level=1)
    f.level_up(lv - 1)
    return f


def new_thief(tough=False):
    if not tough:
        lv = rndint(*THIEF_LV)
        style = styles.DIRTY_FIGHTING.name
        rand_atts_mode = 0
        f = Thug('Thief', style, lv, rand_atts_mode=rand_atts_mode)
    else:
        lv = rndint(*TOUGH_THIEF_LV)
        style = styles.THIEF_STYLE.name
        rand_atts_mode = 2
        f = Thug('Thief', style, level=1, rand_atts_mode=rand_atts_mode)
        f.level_up(lv - 1)
    return f


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
