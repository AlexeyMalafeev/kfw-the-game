from ...happenings import encounters


def buy_items(p):
    p.log('Goes to the marketplace.')
    encs = encounters.BUY_ITEMS_ENCS
    encounters.random_encounters(p, encs)
