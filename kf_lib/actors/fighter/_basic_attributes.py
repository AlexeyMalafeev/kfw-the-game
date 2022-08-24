from abc import ABC
import random
from typing import Dict, List, Optional, Text, Tuple

from kf_lib.actors.fighter._abc import FighterAPI


class BasicAttributes(FighterAPI, ABC):
    att_names: Tuple[str, str, str, str] = ('strength', 'agility', 'speed', 'health')
    att_names_short: Tuple[str, str, str, str] = ('Str', 'Agi', 'Spd', 'Hlt')

    def change_att(
            self,
            att: Text,
            amount: int,
    ) -> None:
        setattr(self, att, getattr(self, att) + amount)
        self.refresh_full_atts()

    def check_lv(
            self,
            minlv: int,
            maxlv: Optional[int] = None,
    ) -> bool:
        if maxlv is None:
            return self.level >= minlv
        else:
            return minlv <= self.level <= maxlv

    # todo refactor the inefficient and unclear choose_better_att, possibly with random.choices
    def choose_better_att(
            self,
            atts: List[Text],
    ) -> Text:
        temp_dict: Dict[int, List[Text]] = {}
        for att in atts:
            weight = self.att_weights[att]
            if weight not in temp_dict:
                temp_dict[weight] = []
            temp_dict[weight].append(att)
        weights = sorted([w for w in temp_dict.keys()])
        att = random.choice(temp_dict[weights[-1]])  # several atts might have the same weight
        return att

    def get_all_atts_str(self) -> Text:
        atts_info: List[Text] = []
        for i, att in enumerate(self.att_names):
            short = self.att_names_short[i]
            v = self.get_att_str(att)
            atts_info.append(f'{short}:{v}')
        return ' '.join(atts_info)

    def get_att_str(self, att: Text) -> Text:
        base, full = self.get_base_att_value(att), self.get_full_att_value(att)
        return f'{full}({base})' if full > base else str(base)

    def get_att_str_prefight(
            self,
            att: Text,
            hide: bool = False,
    ) -> Text:
        base, full = self.get_base_att_value(att), self.get_full_att_value(att)
        s = str(full) if not hide else '?'
        aster = '*' if full > base else ''
        return s + aster

    # noinspection PyTypeChecker
    def get_att_values_full(self) -> Tuple[int, int, int, int]:
        return tuple(self.get_full_att_value(att) for att in self.att_names)

    def get_atts_to_choose(self) -> List[Text]:
        return random.sample(self.att_names, self.num_atts_choose)

    def get_base_att_value(
            self,
            att: Text,
    ) -> int:
        return getattr(self, att)

    def get_base_atts_tup(self) -> Tuple[int, int, int, int]:
        return self.strength, self.agility, self.speed, self.health

    def get_full_att_value(
            self,
            att: Text,
    ) -> int:
        return getattr(self, att + '_full')

    def refresh_full_atts(self) -> None:
        for att in self.att_names:
            base = getattr(self, att)
            mult = getattr(self, att + '_mult')
            setattr(self, att + '_full', round(base * mult))

    def set_att_weights(self) -> None:
        """This is used for choosing better atts when upgrading / randomly generating fighters"""
        for att in self.att_names:
            setattr(self, att, 3)
            self.att_weights[att] = 0  # default weights

        # default, 'old' method
        if self.rand_atts_mode == 0:
            pass
        # random weights
        elif self.rand_atts_mode in {1, 2}:
            for att in self.att_names:
                # self.att_weights[att] = random.randint(1, 2)
                self.att_weights[att] = 1
        # TODO: more intelligent att selection depending on the style perks

    def set_atts(
            self,
            atts: Tuple[int, int, int, int],
    ) -> None:
        if not atts:
            self.set_rand_atts()
        else:
            for i, att in enumerate(self.att_names):
                setattr(self, att, atts[i])

    def set_rand_atts(self) -> None:
        for i in range(self.level + 2):
            atts = self.get_atts_to_choose()
            att = self.choose_better_att(atts)
            value = getattr(self, att)
            setattr(self, att, value + 1)

    def upgrade_att(self) -> None:
        atts = self.get_atts_to_choose()
        att = self.choose_better_att(atts)
        self.change_att(att, 1)
