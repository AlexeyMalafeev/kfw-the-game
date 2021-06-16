import random

from . import boosts

# constants
ATT_BOOST1 = 3

# items
MEDICINE = 'Ginseng Root'
STR_BOOSTER = 'Tiger Herb'
AGI_BOOSTER = 'Monkey Herb'
SPD_BOOSTER = 'Fly Herb'
QI_BOOSTER = 'Dragon Herb'
HLT_BOOSTER = 'Elephant Herb'
STAM_BOOSTER = 'Ox Herb'
SUPER_BOOSTER = 'Super Herb'
MANNEQUIN = 'wooden mannequin'

STD_FIGHT_ITEMS = [STR_BOOSTER, AGI_BOOSTER, SPD_BOOSTER, QI_BOOSTER, HLT_BOOSTER, STAM_BOOSTER]
FIGHT_ITEMS = STD_FIGHT_ITEMS + [SUPER_BOOSTER]
ALL_ITEMS = FIGHT_ITEMS + [MEDICINE]
ALL_STD_ITEMS = STD_FIGHT_ITEMS + [MEDICINE]
MOCK_ITEMS = ['constipation medicine', 'cough medicine', 'culinary herb mix']

PRICES = (70, 80, 100, 120, 150)


all_items = {}


class Item(object):
    """Instantiated only for descriptions."""

    def __init__(self, name, **kwargs):
        self.name = name
        for k in kwargs:
            setattr(self, k, kwargs[k])
        self.params = kwargs
        self.descr = ''
        self.descr_short = ''
        boosts.set_descr(self)
        all_items[self.name] = self


def ef_boost(target, **kwargs):
    target.boost(**kwargs)


def ef_recover(target):
    target.recover()


EFFECTS = {
    MEDICINE: (ef_recover, {}),
    STR_BOOSTER: (ef_boost, {'strength_full': ATT_BOOST1}),
    AGI_BOOSTER: (ef_boost, {'agility_full': ATT_BOOST1}),
    SPD_BOOSTER: (ef_boost, {'speed_full': ATT_BOOST1}),
    QI_BOOSTER: (ef_boost, {
        'qp_gain_mult': boosts.QP_GAIN2,
        'qp_max_mult': boosts.QP_MAX2,
        'qp_start': boosts.QP_START2,
    }),
    HLT_BOOSTER: (ef_boost, {'health_full': ATT_BOOST1}),
    STAM_BOOSTER: (
        ef_boost, {
            'stamina_max_mult': boosts.STAM_MAX2,
            'stamina_gain_mult': boosts.STAM_RESTORE2,
        },
    ),
    SUPER_BOOSTER: (
        ef_boost,
        {
            'strength_full': ATT_BOOST1,
            'agility_full': ATT_BOOST1,
            'speed_full': ATT_BOOST1,
            'qp_gain_mult': boosts.QP_GAIN2,
            'qp_max_mult': boosts.QP_MAX2,
            'qp_start': boosts.QP_START2,
            'health_full': ATT_BOOST1,
            'stamina_max_mult': boosts.STAM_MAX2,
            'stamina_gain_mult': boosts.STAM_RESTORE2,
        },
    ),
    MANNEQUIN: (ef_boost, {'home_training_exp_mult': boosts.HOME_TRAIN_BONUS}),
}


for k, v in EFFECTS.items():
    Item(k, **v[1])


def cancel_item(item, target):
    ef_func, kwargs = EFFECTS[item]
    target.unboost(**kwargs)


def get_item_descr(item_name):
    item_obj = get_item_obj(item_name)
    return item_obj.descr


def get_item_obj(item_name):
    return all_items[item_name]


def get_random_item():
    return random.choice(ALL_STD_ITEMS)


def get_random_mock_item():
    return random.choice(MOCK_ITEMS)


def use_item(item, target):
    ef_func, kwargs = EFFECTS[item]
    ef_func(target, **kwargs)
