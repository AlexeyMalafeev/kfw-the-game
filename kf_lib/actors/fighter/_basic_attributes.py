import random


class BasicAttributes:
    att_names = ('strength', 'agility', 'speed', 'health')
    att_names_short = ('Str', 'Agi', 'Spd', 'Hlt')

    def __init__(self):
        self.att_weights = {}
        self.strength = 0
        self.strength_full = 0
        self.agility = 0
        self.agility_full = 0
        self.speed = 0
        self.speed_full = 0
        self.health = 0
        self.health_full = 0

        self.level = 1
        self.num_atts_choose = 3
        self.rand_atts_mode = 0  # 0, 1, 2

    def change_att(self, att, amount):
        setattr(self, att, getattr(self, att) + amount)
        self.refresh_full_atts()

    def check_lv(self, minlv, maxlv=None):
        if maxlv is None:
            return self.level >= minlv
        else:
            return minlv <= self.level <= maxlv

    def upgrade_att(self):
        atts = self.get_atts_to_choose()
        att = self.choose_better_att(atts)
        self.change_att(att, 1)

    # todo refactor choose_better_att with random.choices?
    def choose_better_att(self, atts):
        temp_dict = {}
        for att in atts:
            weight = self.att_weights[att]
            if weight not in temp_dict:
                temp_dict[weight] = []
            temp_dict[weight].append(att)
        weights = sorted([w for w in temp_dict.keys()])
        att = random.choice(temp_dict[weights[-1]])  # several atts might have the same weight
        return att

    def get_all_atts_str(self):
        atts_info = []
        for i, att in enumerate(self.att_names):
            short = self.att_names_short[i]
            v = self.get_att_str(att)
            atts_info.append(f'{short}:{v}')
        return ' '.join(atts_info)

    def get_att_str(self, att):
        base, full = self.get_base_att_value(att), self.get_full_att_value(att)
        return f'{full}({base})' if full > base else str(base)

    def get_att_str_prefight(self, att, hide=False):
        base, full = self.get_base_att_value(att), self.get_full_att_value(att)
        s = str(full) if not hide else '?'
        aster = '*' if full > base else ''
        return s + aster

    def get_att_values_full(self):
        return tuple(self.get_full_att_value(att) for att in self.att_names)

    def get_atts_to_choose(self):
        return random.sample(self.att_names, self.num_atts_choose)

    def get_base_att_value(self, att):
        return getattr(self, att)

    def get_base_atts_tup(self):
        return self.strength, self.agility, self.speed, self.health

    def get_full_att_value(self, att):
        return getattr(self, att + '_full')

    def get_max_att_value(self):
        return max(self.get_base_atts_tup())

    def refresh_full_atts(self):
        for att in self.att_names:
            base = getattr(self, att)
            mult = getattr(self, att + '_mult')
            setattr(self, att + '_full', round(base * mult))

    def set_att_weights(self):
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

    def set_atts(self, atts):
        if not atts:
            self.set_rand_atts()
        else:
            for i, att in enumerate(self.att_names):
                setattr(self, att, atts[i])

    def set_rand_atts(self):
        for i in range(self.level + 2):
            atts = self.get_atts_to_choose()
            att = self.choose_better_att(atts)
            value = getattr(self, att)
            setattr(self, att, value + 1)
