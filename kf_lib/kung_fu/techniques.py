from kf_lib.kung_fu import boosts as b
from kf_lib.things import weapons
from kf_lib.utils.utilities import *


# tech containers (for easy retrieval)
# tech_name: tech_obj
all_techs = {}

# tech names (for convenient random choosing)
upgradable_techs = []
advanced_techs = []
style_techs = []
weapon_techs = []


class Tech(object):
    """
    General technique class;
    params is parameters dict,
    descr is tech description."""

    is_style_tech = False
    is_unique = False
    is_upgradable = False
    is_advanced = False
    is_weapon_tech = False

    def __init__(self, name, **kwargs):
        self.name = name
        for k in kwargs:
            setattr(self, k, kwargs[k])
        self.params = kwargs
        self.descr = ''
        self.descr_short = ''
        b.set_descr(self)
        all_techs[self.name] = self

    def apply(self, f):
        for p in self.params:
            v = getattr(f, p)
            setattr(f, p, v + self.params[p])

    def undo(self, f):
        for p in self.params:
            v = getattr(f, p)
            setattr(f, p, v - self.params[p])


class UpgradableTech(Tech):
    is_upgradable = True

    def __init__(self, name, **kwargs):
        Tech.__init__(self, name, **kwargs)
        upgradable_techs.append(self.name)


class AdvancedTech(Tech):
    is_advanced = True

    def __init__(self, name, **kwargs):
        Tech.__init__(self, name, **kwargs)
        advanced_techs.append(self.name)


class StyleTech(Tech):
    is_style_tech = True
    is_upgradable = False

    def __init__(self, name, **kwargs):
        Tech.__init__(self, name, **kwargs)
        style_techs.append(self.name)


class WeaponTech(Tech):
    """Technique used when equipping a weapon. Adds to atk and dfs."""

    is_weapon_tech = True

    def __init__(self, name, **kwargs):
        self.wp_type = ''
        self.wp_bonus = (0, 0)
        Tech.__init__(self, name, **kwargs)
        weapon_techs.append(self.name)

    def apply(self, f):
        if self.wp_type in f.weapon_bonus:
            bonus = f.weapon_bonus[self.wp_type]  # list of 2
        else:
            bonus = f.weapon_bonus[self.wp_type] = [0, 0]
        bonus[0] += self.wp_bonus[0]
        bonus[1] += self.wp_bonus[1]

    def set_descr(self):
        a = add_sign(self.wp_bonus[0])
        d = add_sign(self.wp_bonus[1])
        if self.wp_type in weapons.WEAPON_TYPES:
            w = f'{self.wp_type} weapons'
        else:
            w = self.wp_type
        self.descr = f'{w} {a}/{d}'

    def undo(self, f):
        bonus = f.weapon_bonus[self.wp_type]  # list of 2
        bonus[0] -= self.wp_bonus[0]
        bonus[1] -= self.wp_bonus[1]


# todo weapon techniques do nothing; implement
_WEAPON_TECHS = [
    WeaponTech('Strange But Deadly'),
    WeaponTech('Weapons Competence'),
    WeaponTech('Butterfly Swords'),
    WeaponTech('Sky Saber'),
    WeaponTech('Lightning Spear'),
    WeaponTech('Thunder Staff'),
    WeaponTech('Star Sword'),
]

LINKED_TECHS = [
    (
        UpgradableTech('Qi Breathing', qp_gain=b.QP_GAIN1),
        AdvancedTech('Energy Breathing', qp_gain=b.QP_GAIN2),
    ),
    (
        UpgradableTech('Health Breathing', hp_gain=b.HP_GAIN1),
        AdvancedTech('Vitality Breathing', hp_gain=b.HP_GAIN2),
    ),
    (
        UpgradableTech('Monkey and Fox', block_disarm=b.BLOCK_DISARM1, hit_disarm=b.HIT_DISARM1),
        AdvancedTech(
            'Flying Monkey and Golden Fox', block_disarm=b.BLOCK_DISARM2, hit_disarm=b.HIT_DISARM2
        ),
    ),
    (
        UpgradableTech('18 Attack Forms', atk_mult=b.ATTACK1),
        AdvancedTech('36 Attack Forms', atk_mult=b.ATTACK2),
    ),
    (
        UpgradableTech('18 Defense Forms', dfs_mult=b.DEFENSE1),
        AdvancedTech('36 Defense Forms', dfs_mult=b.DEFENSE2),
    ),
    (
        UpgradableTech('Advanced Guard', guard_dfs_bonus=b.GUARD_DFS1),
        AdvancedTech('Dragon Guards a Treasure', guard_dfs_bonus=b.GUARD_DFS2),
    ),
    (
        UpgradableTech('Lotus Stance', qp_max=b.QP_MAX1, qp_start=b.QP_START1),
        AdvancedTech('Golden Lotus Stance', qp_max=b.QP_MAX2, qp_start=b.QP_START2),
    ),
    (
        UpgradableTech(
            'Horse-like Stamina', stamina_max_mult=b.STAM_MAX1, stamina_gain_mult=b.STAM_RESTORE1
        ),
        AdvancedTech(
            'Strong as an Ox', stamina_max_mult=b.STAM_MAX2, stamina_gain_mult=b.STAM_RESTORE2
        ),
    ),
    (
        UpgradableTech('Fierce Strikes', critical_chance_mult=b.CRIT_CH1, critical_mult=b.CRIT_M1),
        AdvancedTech('Explosive Strikes', critical_chance_mult=b.CRIT_CH2, critical_mult=b.CRIT_M2),
    ),
    (
        UpgradableTech('Iron Vest', dam_reduc=b.DAM_REDUC1),
        AdvancedTech('Superior Iron Vest', dam_reduc=b.DAM_REDUC2),
    ),
    (
        UpgradableTech('Shadow Slips Away', dodge_mult=b.EVADE1),
        AdvancedTech('Shadow of a Shadow', dodge_mult=b.EVADE2),
    ),
    (
        UpgradableTech('Wall-like Protection', block_mult=b.BLOCK1),
        AdvancedTech('Emperor\'s Fortress', block_mult=b.BLOCK2),
    ),
    (
        UpgradableTech('Behind You', dfs_penalty_step=b.DFS_PEN1),
        AdvancedTech('Behind You All', dfs_penalty_step=b.DFS_PEN2),
    ),
    (
        UpgradableTech('Iron Fist', punch_strike_mult=b.STRIKE_MULT1),
        AdvancedTech('Cannon Fist', punch_strike_mult=b.STRIKE_MULT2),
    ),
    (
        UpgradableTech('Powerful Kicks', kick_strike_mult=b.STRIKE_MULT1),
        AdvancedTech('Hurricane Legs', kick_strike_mult=b.STRIKE_MULT2),
    ),
    (
        UpgradableTech('Elbow Boxing', elbow_strike_mult=b.RARE_STRIKE_MULT1),
        AdvancedTech('Mighty Elbows', elbow_strike_mult=b.RARE_STRIKE_MULT2),
    ),
    (
        UpgradableTech('Knee Boxing', knee_strike_mult=b.RARE_STRIKE_MULT1),
        AdvancedTech('Mighty Knees', knee_strike_mult=b.RARE_STRIKE_MULT2),
    ),
    (
        UpgradableTech('Flying Strikes', flying_strike_mult=b.RARE_STRIKE_MULT1),
        AdvancedTech('Sky Dragon', flying_strike_mult=b.RARE_STRIKE_MULT2),
    ),
    (
        UpgradableTech('Hardened Palms', palm_strike_mult=b.RARE_STRIKE_MULT1),
        AdvancedTech('Palms of Justice', palm_strike_mult=b.RARE_STRIKE_MULT2),
    ),
    # todo fix this
    # (UpgradableTech('Uncanny Strikes', exotic_strike_mult=b.RARE_STRIKE_MULT1),
    #  AdvancedTech('Whole Body Weapon', exotic_strike_mult=b.RARE_STRIKE_MULT2)),
    # todo implement Weapon Competence tech
    # (
    #     UpgradableTech('Weapon Competence', weapon_strike_mult=b.WP_STRIKE_MULT1),
    #     AdvancedTech('Weapon Mastery', weapon_strike_mult=b.WP_STRIKE_MULT2),
    # ),
    (
        UpgradableTech('Environment Fighting', environment_chance=b.ENVIRONMENT_CH1),
        AdvancedTech('Environment Domination', environment_chance=b.ENVIRONMENT_CH2),
    ),
    (
        UpgradableTech('Unlikely Weapons', in_fight_impro_wp_chance=b.IN_FIGHT_IMPRO_WP_CH1),
        AdvancedTech('Anything Is a Weapon', in_fight_impro_wp_chance=b.IN_FIGHT_IMPRO_WP_CH2),
    ),
    (
        UpgradableTech('Debilitating Strikes', stun_chance=b.STUN_CH1),
        AdvancedTech('Crippling Strikes', stun_chance=b.STUN_CH2),
    ),
    (
        UpgradableTech('Brawler\'s Resilience', resist_ko=b.RESIST_KO1),
        AdvancedTech('Hero\'s Resilience', resist_ko=b.RESIST_KO2),
    ),
    (
        UpgradableTech('Guard While Striking', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
        AdvancedTech('Attack Is Defense', guard_while_attacking=b.GUARD_WHILE_ATTACKING2),
    ),
    (
        UpgradableTech('Retaliative Blows', counter_chance_mult=b.COUNTER_CH_MULT1),
        AdvancedTech('Vengeful Fox', counter_chance_mult=b.COUNTER_CH_MULT2),
    ),
    (
        UpgradableTech('Preemptive Strikes', preemptive_chance_mult=b.PREEMPTIVE_CH1),
        AdvancedTech('Enranged Mantis', preemptive_chance_mult=b.PREEMPTIVE_CH2),
    ),
    (
        UpgradableTech('Fast Movement', maneuver_time_cost_mult=b.MANEUVER_TIME_COST_MULT1),
        AdvancedTech('Lightning-Fast Movement', maneuver_time_cost_mult=b.MANEUVER_TIME_COST_MULT2),
    ),
    (
        UpgradableTech('Fast Strikes', strike_time_cost_mult=b.STRIKE_TIME_COST_MULT1),
        AdvancedTech('Lightning-Fast Strikes', strike_time_cost_mult=b.STRIKE_TIME_COST_MULT1),
    ),
    (
        UpgradableTech('Fist of Fury', fury_chance=b.FURY_CH1),
        AdvancedTech('Fist of Fury II', fury_chance=b.FURY_CH2),
    )
    # todo 'momentum' technique - bonus after moving forward '+' and '++'
    # possibly another technique that improves defense after moving back
]

UPG_MAP_ADV_REG = {t[1].name: t[0].name for t in LINKED_TECHS}
UPG_MAP_REG_ADV = {t[0].name: t[1].name for t in LINKED_TECHS}


def adv_to_reg(tech_name):
    return UPG_MAP_ADV_REG[tech_name]


def apply(tn, f):
    t = get_tech_obj(tn)
    t.apply(f)
    f.refresh_full_atts()  # in case techs affects them
    f.refresh_level_dependent_atts()  # in case techs affects them


def get_all_techs():
    return all_techs


def get_descr(tech_name):
    """Return description of tech."""
    return get_tech_obj(tech_name).descr


# todo optimize techniques.get_learnable_techs
def get_learnable_techs(fighter=None):
    """Return names of techs fighter can learn."""
    techs = get_upgradable_techs()[:]
    if fighter is not None:
        for t in fighter.techs:
            if t in techs:
                techs.remove(t)
            elif t in advanced_techs:
                techs.remove(adv_to_reg(t))
    return techs


def get_style_techs(fighter=None):
    if fighter is None:
        return style_techs
    else:
        return [t for t in fighter.techs if t in style_techs]


def get_tech_obj(tech_name):
    return all_techs[tech_name]


def get_upgradable_techs(fighter=None):
    """If fighter is None, return list of all upgradable techs.
    If fighter is given, return names of techs fighter can upgrade."""
    if fighter is None:
        return upgradable_techs
    else:
        return [t for t in fighter.techs if get_tech_obj(t).is_upgradable]


def get_upgraded_techs(fighter=None):
    """If fighter is None, return list of all upgraded techs.
    If fighter is given, return names of upgraded techs fighter doesn't have."""
    if fighter is None:
        return advanced_techs
    else:
        return [t for t in advanced_techs if t not in fighter.techs]


def get_weapon_techs(fighter=None):
    """If fighter is None, return list of all weapon techs.
    If fighter is given, return list of weapon techs fighter has."""
    if fighter is None:
        return weapon_techs
    else:
        return [t for t in fighter.techs if get_tech_obj(t).is_weapon_tech]


def reg_to_adv(tech_name):
    return UPG_MAP_REG_ADV[tech_name]


def undo(tn, f):
    t = get_tech_obj(tn)
    t.undo(f)
