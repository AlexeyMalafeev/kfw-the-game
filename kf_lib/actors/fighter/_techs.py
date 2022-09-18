from abc import ABC
import random
from typing import List, Optional, Text

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.kung_fu import techniques
from kf_lib.kung_fu.techniques import Tech


class TechMethods(FighterAPI, ABC):
    def add_tech(self, tech: Tech) -> None:
        self.techs.add(tech)
        self.apply_tech(tech)

    def apply_tech(self, *techs: Tech) -> None:
        for tech in techs:
            techniques.apply_tech(tech, self)

    def choose_new_tech(self) -> None:
        sample = self.get_techs_to_choose()
        if sample:
            self.learn_tech(random.choice(sample))

    def choose_tech_to_upgrade(self) -> None:
        av_techs = self.get_techs_to_choose(for_upgrade=True)
        if not av_techs:
            return
        self.upgrade_tech(random.choice(av_techs))

    def get_style_tech_if_any(self) -> Optional[Tech]:
        return self.style.techs.get(self.level)

    def get_techs_string(self, show_descr: bool = True, header: Text = 'Techniques:') -> Text:
        if not self.techs:
            return ''
        align = max((len(t.name) for t in self.techs)) + 1
        output = []
        for t in self.techs:
            if show_descr:
                output.append(f'{t.name:<{align}}{t.descr}')
            else:
                output.append(f'{t.name:<{align}}')
        output = [header] + sorted(output)
        return '\n'.join(output)

    def get_techs_to_choose(self, annotated: bool = False, for_upgrade: bool = False) -> List[Tech]:
        if for_upgrade:
            num = self.num_techs_choose_upgrade
            av_techs = techniques.get_upgradable_techs(self)
        else:
            num = self.num_techs_choose
            av_techs = techniques.get_learnable_techs(self)
        if annotated:
            av_techs = [(f'{t.name} ({t.descr})', t) for t in av_techs]
        if 0 < len(av_techs) < num:
            return av_techs
        elif not av_techs:
            return []
        else:
            return random.sample(av_techs, num)

    def get_weapon_techs(self) -> List[Tech]:
        return techniques.get_weapon_techs(self)

    def learn_random_new_tech(self) -> None:
        pool = techniques.get_learnable_techs(self)
        if pool:
            t = random.choice(pool)
            self.learn_tech(t)
        else:
            print(f'warning: {self} cannot learn any more techs!')

    def learn_tech(self, *techs: Tech) -> None:
        for tech in techs:
            if tech not in self.techs:
                self.add_tech(tech)
                self.show(f'{self.name} learns {tech.name} ({tech.descr}).')
                self.log(f'Learns {tech.name} ({tech.descr})')
                self.pak()

    def resolve_techs_on_level_up(self) -> None:
        if not self.style.is_tech_style:
            return
        # learn new style tech if possible
        if t := self.get_style_tech_if_any():
            self.learn_tech(t)
        # upgrade tech if possible
        if self.level == self.ADVANCED_TECH_AT_LV:
            self.choose_tech_to_upgrade()
        # learn new general tech if possible
        if self.level in self.LVS_GET_GENERAL_TECH:
            self.choose_new_tech()

    def set_rand_techs(self, forced: bool = False) -> None:
        if forced or self.style.is_tech_style:
            # style techs
            for lv, tech in self.style.techs.items():
                if self.level >= lv:
                    self.techs.add(tech)
            # general techs
            n = len([lv for lv in self.LVS_GET_GENERAL_TECH if lv <= self.level])
            if n:
                self.techs |= set(random.sample(techniques.get_upgradable_techs(), n))
            if self.level >= self.ADVANCED_TECH_AT_LV:
                t = random.choice(techniques.get_upgradable_techs(self))
                self.upgrade_tech(t)

    def set_techs(self, tech_names: List[Text]) -> None:
        self.techs = set()
        if not tech_names:
            self.set_rand_techs()
        else:
            self.techs = set(techniques.get_tech_obj(tn) for tn in tech_names)
        self.apply_tech(*self.techs)

    def unlearn_tech(self, tech: Tech) -> None:
        self.techs.remove(tech)
        techniques.undo(tech, self)

    def upgrade_tech(self, tech: Tech) -> None:
        self.unlearn_tech(tech)
        new_tech = techniques.reg_to_adv(tech)
        self.learn_tech(new_tech)
