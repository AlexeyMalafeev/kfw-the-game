import random

from kf_lib.things import weapons
from ._base_fighter import BaseFighter


class WeaponMethods(BaseFighter):
    def arm(self, weapon=None):
        """Arm fighter with weapon (default = random).
        weapon can also be weapon type"""
        # disarm fighter to avoid double weapon bonus
        self.disarm()
        # make new weapon
        if weapon is None:
            wp = random.choice(weapons.ALL_WEAPONS_LIST)
        elif weapon in weapons.WEAPON_TYPES:
            wp = weapons.get_rnd_wp_by_type(weapon)
        elif weapon in weapons.ALL_WEAPONS_SET:
            wp = weapon
        else:
            wp = weapons.get_wp(weapon)
        self.weapon = wp
        self.wp_dfs_bonus = wp.dfs_bonus

    def arm_improv(self):
        """Arm fighter with a random improvised weapon"""
        self.arm('improvised')

    def arm_normal(self):
        """Arm fighter with a random normal weapon"""
        self.arm('normal')

    def arm_police(self):
        """Arm fighter with a random police weapon"""
        self.arm('police')

    def arm_robber(self):
        """Arm fighter with a random robber weapon"""
        self.arm('robber')

    def choose_best_norm_wp(self):
        self.arm_normal()
        # todo add choose best normal weapon logic at this level? or not?
        # wp_techs = self.get_weapon_techs()
        # if wp_techs:
        # wns = weapons.NORMAL_WEAPONS
        # best_bonus = 0
        # if t.wp_type == 'normal' or t.wp_type in wns:
        #     bon = t.wp_bonus[0] + t.wp_bonus[1]
        #     if bon > best_bonus:
        #         best_bonus = bon
        #         chosen_tech = t
        # # or:
        # chosen_tech = random.choice(wp_techs)
        # if chosen_tech:
        #     self.arm(chosen_tech.wp_type)
        # self.arm_normal()

    def disarm(self):
        if self.weapon:
            self.weapon = None
            self.wp_dfs_bonus = 1.0
