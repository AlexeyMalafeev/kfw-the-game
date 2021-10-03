import random


COUNTER_CHANCE_BASE = 0.1
COUNTER_CHANCE_INCR_PER_LV = 0.02
HP_PER_HEALTH_LV = 50
QP_BASE = 0
QP_INCR_PER_LV = 5
STAMINA_BASE = 50  # for all fighter levels
STAMINA_INCR_PER_LV = 10


class Attributes:
    att_names = ('strength', 'agility', 'speed', 'health')
    att_names_short = ('Str', 'Agi', 'Spd', 'Hlt')
    att_weights = {}
    strength = 0
    strength_full = 0
    agility = 0
    agility_full = 0
    speed = 0
    speed_full = 0
    health = 0
    health_full = 0

    rand_atts_mode = 0  # 0, 1, 2
    num_atts_choose = 3

    level = 1

    counter_chance = 0.0
    counter_chance_mult = 1.0
    hp = 0
    hp_max = 0
    hp_gain = 0
    qp = 0
    qp_gain = 0
    qp_gain_mult = 1.0
    qp_max = 0
    qp_max_mult = 1.0
    stamina = 0
    stamina_gain = 0
    stamina_gain_mult = 1.0
    stamina_max = 0
    stamina_max_mult = 1.0

    def boost(self, **kwargs):
        """Boost fighter's attribute(s); k = att_name, v = quantity"""
        for k, v in kwargs.items():
            curr_v = getattr(self, k)
            setattr(self, k, curr_v + v)
        self.refresh_full_atts()

    def change_att(self, att, amount):
        setattr(self, att, getattr(self, att) + amount)
        self.refresh_full_atts()

    def choose_att_to_upgrade(self):
        atts = self.get_atts_to_choose()
        att = self.choose_better_att(atts)
        self.change_att(att, 1)

    def choose_better_att(self, atts):
        temp_dict = {}
        for att in atts:
            weight = self.att_weights[att]
            if weight in temp_dict:
                temp_dict[weight].append(att)
            else:
                temp_dict[weight] = [att]
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
        self.hp_max = self.health_full * HP_PER_HEALTH_LV
        self.stamina_max = round(
            (STAMINA_BASE + STAMINA_INCR_PER_LV * self.level) * self.stamina_max_mult
        )
        self.stamina_gain = round(self.stamina_max / 10 * self.stamina_gain_mult)
        self.qp_max = round(
            (QP_BASE + QP_INCR_PER_LV * self.level) * self.qp_max_mult
        )
        self.qp_gain = round(self.qp_max / 5 * self.qp_gain_mult)
        self.counter_chance = (
            (COUNTER_CHANCE_BASE + COUNTER_CHANCE_INCR_PER_LV * self.level) *
            self.counter_chance_mult
        )

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

    def unboost(self, **kwargs):
        """'Unboost' fighter's attributes."""
        kwargs_copy = {}
        for k, v in kwargs.items():
            kwargs_copy[k] = -v
        self.boost(**kwargs_copy)
        self.refresh_full_atts()
