import random


from ._base_fighter import BaseFighter
from ...kung_fu import techniques


ADVANCED_TECH_AT_LV = 20
LVS_GET_GENERAL_TECH = {11, 13, 15, 17, 19}


class TechMethods(BaseFighter):
    adv_tech_at_lv = ADVANCED_TECH_AT_LV
    num_techs_choose = 3
    num_techs_choose_upgrade = 3
    techs = None  # set of tech names

    def add_tech(self, tn):
        self.techs.add(tn)
        self.apply_tech(tn)

    def apply_tech(self, *tech_names):
        for tn in tech_names:
            techniques.apply(tn, self)

    def choose_new_tech(self):
        sample = self.get_techs_to_choose()
        if sample:
            self.learn_tech(random.choice(sample))

    def choose_tech_to_upgrade(self):
        av_techs = self.get_techs_to_choose(for_upgrade=True)
        if not av_techs:
            return
        self.upgrade_tech(random.choice(av_techs))

    def get_style_tech_if_any(self):
        return self.style.techs.get(self.level)

    def get_techs_string(self, descr=True, header='Techniques:'):
        if not self.techs:
            return ''
        align = max((len(t) for t in self.techs)) + 1
        output = []
        d = ''
        for t in self.techs:
            if descr:
                d = f'- {techniques.get_descr(t)}'
            output.append('{:<{}}{}'.format(t, align, d))
        output = [header] + sorted(output)
        return '\n'.join(output)

    def get_techs_to_choose(self, annotated=False, for_upgrade=False):
        if for_upgrade:
            num = self.num_techs_choose_upgrade
            av_techs = techniques.get_upgradable_techs(self)
        else:
            num = self.num_techs_choose
            av_techs = techniques.get_learnable_techs(self)
        if annotated:
            d = techniques.get_descr
            av_techs = [('{} ({})'.format(t, d(t)), t) for t in av_techs]
        if 0 < len(av_techs) < num:
            return av_techs
        elif not av_techs:
            return []
        else:
            return random.sample(av_techs, num)

    def get_weapon_techs(self):
        return techniques.get_weapon_techs(self)

    def learn_random_new_tech(self):
        pool = techniques.get_learnable_techs(self)
        if pool:
            t = random.choice(pool)
            self.learn_tech(t)
        else:
            print(f'warning: {self} cannot learn any more techs!')

    def learn_tech(self, *techs):
        """techs can be Tech objects or tech name strings (or mixed)"""
        for tn in techs:
            if isinstance(tn, techniques.Tech):
                tn = tn.name
            if tn not in self.techs:
                descr = techniques.get_descr(tn)
                self.add_tech(tn)
                self.show(f'{self.name} learns {tn} ({descr}).')
                self.log(f'Learns {tn} ({descr})')
                self.pak()

    def resolve_techs_on_level_up(self):
        if not self.style.is_tech_style:
            return
        # learn new style tech if possible
        if t := self.get_style_tech_if_any():
            self.learn_tech(t.name)
        # upgrade tech if possible
        if self.level == self.adv_tech_at_lv:
            self.choose_tech_to_upgrade()
        # learn new general tech if possible
        if self.level in LVS_GET_GENERAL_TECH:
            self.choose_new_tech()

    def set_rand_techs(self, forced=False):
        if forced or self.style.is_tech_style:
            # style techs
            for lv, t in self.style.techs.items():
                if self.level >= lv:
                    self.techs.add(t.name)
            # general techs
            n = len([lv for lv in LVS_GET_GENERAL_TECH if lv <= self.level])
            if n:
                self.techs |= set(random.sample(techniques.get_upgradable_techs(), n))
            if self.level >= self.adv_tech_at_lv:
                t = random.choice(techniques.get_upgradable_techs(self))
                self.upgrade_tech(t)

    def set_techs(self, tech_names):
        self.techs = set()
        if not tech_names:
            self.set_rand_techs()
        else:
            self.techs = set(tech_names)
        self.apply_tech(*self.techs)

    def unlearn_tech(self, tech):
        self.techs.remove(tech)
        techniques.undo(tech, self)

    def upgrade_tech(self, tech):
        self.unlearn_tech(tech)
        new_tech = techniques.reg_to_adv(tech)
        self.learn_tech(new_tech)
