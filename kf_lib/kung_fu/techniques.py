from typing import Dict, List


from kf_lib.kung_fu import boosts as b
from kf_lib.things import weapons
from kf_lib.utils import add_sign


class Tech:
    def __init__(
            self,
            name,
            fav_moves: set = None,
            is_upgradable=False,
            is_advanced=False,
            is_weapon_tech=False,
            **kwargs
    ):
        self.name = name
        self.fav_moves = set()
        if fav_moves is not None:
            self.fav_moves = fav_moves
        self.is_upgradable = is_upgradable
        if self.is_upgradable:
            upgradable_tech_names.append(self.name)
        self.is_advanced = is_advanced
        if self.is_advanced:
            advanced_tech_names.append(self.name)
        self.is_weapon_tech = is_weapon_tech
        if self.is_weapon_tech:
            weapon_tech_names.append(self.name)
        for k in kwargs:
            setattr(self, k, kwargs[k])
        self.params = kwargs
        self.descr = ''
        self.descr_short = ''
        b.set_descr(self)
        all_techs[self.name] = self

    def __repr__(self):
        return (f'Tech({self.name!r}, fav_moves={self.fav_moves!r}, '
                f'is_upgradable={self.is_upgradable!r}, is_advanced={self.is_advanced!r}, '
                f'is_weapon_tech={self.is_weapon_tech!r}, {self.params!r})')

    def apply(self, f):
        for p in self.params:
            v = getattr(f, p)
            setattr(f, p, v + self.params[p])

    def undo(self, f):
        for p in self.params:
            v = getattr(f, p)
            setattr(f, p, v - self.params[p])


class WeaponTech(Tech):
    """Technique used when equipping a weapon. Adds to atk and dfs."""
    def __init__(self, name, **kwargs):
        self.wp_type = ''
        self.wp_bonus = (0, 0)
        super().__init__(name, is_weapon_tech=True, **kwargs)
        weapon_tech_names.append(self.name)

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


# tech containers (for easy retrieval)
# tech_name: tech_obj
all_techs: Dict[str, Tech] = {}

# tech names (for convenient random choosing)
upgradable_tech_names: List[str] = []
advanced_tech_names: List[str] = []
style_tech_names: List[str] = []
weapon_tech_names: List[str] = []


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
        Tech('Qi Breathing', qp_gain_mult=b.QP_GAIN1, is_upgradable=True),
        Tech('Energy Breathing', qp_gain_mult=b.QP_GAIN2, is_advanced=True),
    ),
    (
        Tech('Health Breathing', hp_gain=b.HP_GAIN1, is_upgradable=True),
        Tech('Vitality Breathing', hp_gain=b.HP_GAIN2, is_advanced=True),
    ),
    (
        Tech('Monkey and Fox', block_disarm=b.BLOCK_DISARM1, hit_disarm=b.HIT_DISARM1,
             is_upgradable=True),
        Tech(
            'Flying Monkey and Golden Fox', block_disarm=b.BLOCK_DISARM2, hit_disarm=b.HIT_DISARM2,
            is_advanced=True
        ),
    ),
    (
        Tech('18 Attack Forms', atk_mult=b.ATTACK1, is_upgradable=True),
        Tech('36 Attack Forms', atk_mult=b.ATTACK2, is_advanced=True),
    ),
    (
        Tech('18 Defense Forms', dfs_mult=b.DEFENSE1, is_upgradable=True),
        Tech('36 Defense Forms', dfs_mult=b.DEFENSE2, is_advanced=True),
    ),
    (
        Tech('Advanced Guard', guard_dfs_bonus=b.GUARD_DFS1, is_upgradable=True),
        Tech('Dragon Guards a Treasure', guard_dfs_bonus=b.GUARD_DFS2, is_advanced=True),
    ),
    (
        Tech('Lotus Stance', qp_max=b.QP_MAX1, qp_start=b.QP_START1, is_upgradable=True),
        Tech('Golden Lotus Stance', qp_max=b.QP_MAX2, qp_start=b.QP_START2, is_advanced=True),
    ),
    (
        Tech(
            'Horse-like Stamina', stamina_max_mult=b.STAM_MAX1, stamina_gain_mult=b.STAM_RESTORE1,
            is_upgradable=True
        ),
        Tech(
            'Strong as an Ox', stamina_max_mult=b.STAM_MAX2, stamina_gain_mult=b.STAM_RESTORE2,
            is_advanced=True
        ),
    ),
    (
        Tech('Fierce Strikes', critical_chance_mult=b.CRIT_CH1, critical_dam_mult=b.CRIT_M1,
             is_upgradable=True),
        Tech('Explosive Strikes', critical_chance_mult=b.CRIT_CH2, critical_dam_mult=b.CRIT_M2,
             is_advanced=True),
    ),
    (
        Tech('Iron Vest', dam_reduc=b.DAM_REDUC1, is_upgradable=True),
        Tech('Superior Iron Vest', dam_reduc=b.DAM_REDUC2, is_advanced=True),
    ),
    (
        Tech('Shadow Slips Away', dodge_mult=b.EVADE1, is_upgradable=True),
        Tech('Shadow of a Shadow', dodge_mult=b.EVADE2, is_advanced=True),
    ),
    (
        Tech('Wall-like Protection', block_mult=b.BLOCK1, is_upgradable=True),
        Tech('Emperor\'s Fortress', block_mult=b.BLOCK2, is_advanced=True),
    ),
    (
        Tech('Behind You', dfs_penalty_step=b.DFS_PEN1, is_upgradable=True),
        Tech('Behind You All', dfs_penalty_step=b.DFS_PEN2, is_advanced=True),
    ),
    (
        Tech('Iron Fist', punch_strike_mult=b.STRIKE_MULT1, is_upgradable=True),
        Tech('Cannon Fist', punch_strike_mult=b.STRIKE_MULT2, is_advanced=True),
    ),
    (
        Tech('Powerful Kicks', kick_strike_mult=b.STRIKE_MULT1, is_upgradable=True),
        Tech('Hurricane Legs', kick_strike_mult=b.STRIKE_MULT2, is_advanced=True),
    ),
    (
        Tech('Elbow Boxing', elbow_strike_mult=b.RARE_STRIKE_MULT1, is_upgradable=True),
        Tech('Mighty Elbows', elbow_strike_mult=b.RARE_STRIKE_MULT2, is_advanced=True),
    ),
    (
        Tech('Knee Boxing', knee_strike_mult=b.RARE_STRIKE_MULT1, is_upgradable=True),
        Tech('Mighty Knees', knee_strike_mult=b.RARE_STRIKE_MULT2, is_advanced=True),
    ),
    (
        Tech('Flying Strikes', flying_strike_mult=b.RARE_STRIKE_MULT1, is_upgradable=True),
        Tech('Sky Dragon', flying_strike_mult=b.RARE_STRIKE_MULT2, is_advanced=True),
    ),
    (
        Tech('Hardened Palms', palm_strike_mult=b.RARE_STRIKE_MULT1, is_upgradable=True),
        Tech('Palms of Justice', palm_strike_mult=b.RARE_STRIKE_MULT2, is_advanced=True),
    ),
    # todo fix this
    # (Tech('Uncanny Strikes', exotic_strike_mult=b.RARE_STRIKE_MULT1),
    #  Tech('Whole Body Weapon', exotic_strike_mult=b.RARE_STRIKE_MULT2)),
    # todo implement Weapon Competence tech
    # (
    #     Tech('Weapon Competence', weapon_strike_mult=b.WP_STRIKE_MULT1),
    #     Tech('Weapon Mastery', weapon_strike_mult=b.WP_STRIKE_MULT2),
    # ),
    (
        Tech('Environment Fighting', environment_chance=b.ENVIRONMENT_CH1, is_upgradable=True),
        Tech('Environment Domination', environment_chance=b.ENVIRONMENT_CH2, is_advanced=True),
    ),
    (
        Tech('Unlikely Weapons', in_fight_impro_wp_chance=b.IN_FIGHT_IMPRO_WP_CH1,
             is_upgradable=True),
        Tech('Anything Is a Weapon', in_fight_impro_wp_chance=b.IN_FIGHT_IMPRO_WP_CH2,
             is_advanced=True),
    ),
    (
        Tech('Debilitating Strikes', stun_chance=b.STUN_CH1, is_upgradable=True),
        Tech('Crippling Strikes', stun_chance=b.STUN_CH2, is_advanced=True),
    ),
    (
        Tech('Brawler\'s Resilience', resist_ko=b.RESIST_KO1, is_upgradable=True),
        Tech('Hero\'s Resilience', resist_ko=b.RESIST_KO2, is_advanced=True),
    ),
    (
        Tech('Guard While Striking', guard_while_attacking=b.GUARD_WHILE_ATTACKING1,
             is_upgradable=True),
        Tech('Attack Is Defense', guard_while_attacking=b.GUARD_WHILE_ATTACKING2, is_advanced=True),
    ),
    (
        Tech('Retaliative Blows', counter_chance_mult=b.COUNTER_CH_MULT1, is_upgradable=True),
        Tech('Vengeful Fox', counter_chance_mult=b.COUNTER_CH_MULT2, is_advanced=True),
    ),
    (
        Tech('Preemptive Strikes', preemptive_chance=b.PREEMPTIVE_CH1, is_upgradable=True),
        Tech('Enraged Mantis', preemptive_chance=b.PREEMPTIVE_CH2, is_advanced=True),
    ),
    (
        Tech('Fast Movement', maneuver_time_cost_mult=b.MANEUVER_TIME_COST_MULT1,
             is_upgradable=True),
        Tech('Lightning-Fast Movement', maneuver_time_cost_mult=b.MANEUVER_TIME_COST_MULT2,
             is_advanced=True),
    ),
    (
        Tech('Fast Strikes', strike_time_cost_mult=b.STRIKE_TIME_COST_MULT1,
             is_upgradable=True),
        Tech('Lightning-Fast Strikes', strike_time_cost_mult=b.STRIKE_TIME_COST_MULT1,
             is_advanced=True),
    ),
    (
        Tech('Fist of Fury', fury_chance=b.FURY_CH1, is_upgradable=True),
        Tech('Fist of Fury II', fury_chance=b.FURY_CH2, is_advanced=True),
    ),
    (
        Tech('Blood Strikes', chance_cause_bleeding=b.BLEEDING_CH1, is_upgradable=True),
        Tech('Advanced Blood Strikes', chance_cause_bleeding=b.BLEEDING_CH2, is_advanced=True),
    ),
    # todo 'momentum' technique - bonus after moving forward '+' and '++'
    # possibly another technique that improves defense after moving back
]

# todo refactor upgradable to advanced tech mapping as attributes
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


# todo refactor and optimize the functions in techniques.py, they are a mess

def get_learnable_techs(fighter=None):
    """Return names of techs fighter can learn."""
    techs = get_upgradable_techs()[:]
    if fighter is not None:
        for t in fighter.techs:
            if t in techs:
                techs.remove(t)
            elif t in advanced_tech_names:
                techs.remove(adv_to_reg(t))
    return techs


def get_style_techs(fighter=None):
    if fighter is None:
        return style_tech_names
    else:
        return [t for t in fighter.techs if t in style_tech_names]


def get_tech_obj(tech_name):
    if tech_name not in all_techs:
        raise ValueError(f'unable to find tech name "{tech_name!r}" in all_techs (keys are tech '
                         f'names)')
    return all_techs[tech_name]


def get_upgradable_techs(fighter=None):
    """If fighter is None, return list of all upgradable techs.
    If fighter is given, return names of techs fighter can upgrade."""
    if fighter is None:
        return upgradable_tech_names
    else:
        return [t for t in fighter.techs if get_tech_obj(t).is_upgradable]


def get_upgraded_techs(fighter=None):
    """If fighter is None, return list of all upgraded techs.
    If fighter is given, return names of upgraded techs fighter doesn't have."""
    if fighter is None:
        return advanced_tech_names
    else:
        return [t for t in advanced_tech_names if t not in fighter.techs]


def get_weapon_techs(fighter=None):
    """If fighter is None, return list of all weapon techs.
    If fighter is given, return list of weapon techs fighter has."""
    if fighter is None:
        return weapon_tech_names
    else:
        return [t for t in fighter.techs if get_tech_obj(t).is_weapon_tech]


def reg_to_adv(tech_name):
    return UPG_MAP_REG_ADV[tech_name]


def undo(tn, f):
    t = get_tech_obj(tn)
    t.undo(f)
