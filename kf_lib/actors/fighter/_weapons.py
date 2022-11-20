from abc import ABC
import random
from typing import Optional, Union

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.things import weapons


class WeaponMethods(FighterAPI, ABC):
    def arm(self, weapon: Optional[Union[weapons.Weapon, str]] = None) -> None:
        """Arm fighter with weapon (default = random).
        weapon can also be weapon type"""
        # disarm fighter to avoid double weapon bonus
        self.disarm()
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

    def arm_improv(self) -> None:
        """Arm fighter with a random improvised weapon"""
        self.arm('improvised')

    def arm_normal(self) -> None:
        """Arm fighter with a random normal weapon"""
        self.arm('normal')

    def arm_police(self) -> None:
        """Arm fighter with a random police weapon"""
        self.arm('police')

    def arm_robber(self) -> None:
        """Arm fighter with a random robber weapon"""
        self.arm('robber')

    def choose_best_norm_wp(self) -> None:
        self.arm_normal()
        # todo add choose best normal weapon logic at this level? or not?

    def disarm(self) -> None:
        if self.weapon:
            self.weapon = None
            self.wp_dfs_bonus = 1.0
