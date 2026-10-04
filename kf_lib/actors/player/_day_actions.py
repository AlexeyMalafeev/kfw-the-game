from kf_lib.happenings import encounters
from kf_lib.i18n import _


def buy_items(p):
    p.log(_('Goes to the marketplace.'))
    encs = encounters.BUY_ITEMS_ENCS
    encounters.random_encounters(p, encs)
