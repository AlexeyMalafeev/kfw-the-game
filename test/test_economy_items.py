"""Economy (money, stats) and item characterization — headless-safe paths only."""
import random

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib.actors import fighter_factory
from kf_lib.actors.player import SmartAIP
from kf_lib.things import items


def make_player(seed=0, **kwargs):
    random.seed(seed)
    atts = dict(name='Test Player', style='Drunken Boxing')
    atts.update(kwargs)
    return SmartAIP(**atts)


class TestMoney:
    def test_check_money(self):
        p = make_player()
        p.money = 100
        assert p.check_money(100)
        assert p.check_money(50)
        assert not p.check_money(101)

    def test_pay(self):
        p = make_player()
        p.money = 100
        p.pay(30)
        assert p.money == 70

    def test_pay_into_negative_is_allowed(self):
        # by design: a negative balance is the game's debt (docs/gameplay.md)
        p = make_player()
        p.money = 10
        p.pay(30)
        assert p.money == -20

    def test_earn_money_updates_stat(self):
        p = make_player()
        p.money = 0
        p.earn_money(50)
        assert p.money == 50
        assert p.get_stat('money_earned') == 50
        p.earn_money(25)
        assert p.get_stat('money_earned') == 75

    def test_earn_money_silent_skips_stat(self):
        p = make_player()
        p.earn_money(50, silent=True)
        assert p.get_stat('money_earned') == 0

    def test_earn_prize_and_reward_stats(self):
        p = make_player()
        p.earn_prize(100)
        p.earn_reward(40)
        assert p.money == 150  # 10 starting money + 100 + 40
        assert p.get_stat('prize_money_earned') == 100
        assert p.get_stat('rew_money_earned') == 40

    def test_donate(self):
        p = make_player()
        p.money = 100
        p.donate(50)
        assert p.money == 50
        assert p.get_stat('donated') == 50
        assert p.reputation == 10  # round(50 * 0.2)

    def test_donate_zero(self):
        p = make_player()
        p.money = 100
        p.donate(0)
        assert p.money == 100
        assert p.reputation == 0

    def test_steal_from(self):
        p = make_player()
        p.money = 100
        p.steal_from(25)
        assert p.money == 75
        assert p.get_stat('stolen_from') == 25

    def test_starting_money(self):
        p = make_player()
        assert p.money == 10


class TestInventory:
    def test_obtain_and_check_item(self):
        p = make_player()
        assert p.check_item(items.MEDICINE) == 0
        p.obtain_item(items.MEDICINE)
        assert p.check_item(items.MEDICINE) == 1
        p.obtain_item(items.MEDICINE, 2)
        assert p.check_item(items.MEDICINE) == 3
        assert p.get_stat('items_obtained') == 3

    def test_lose_item(self):
        p = make_player()
        p.obtain_item(items.MEDICINE, 2)
        p.lose_item(items.MEDICINE)
        assert p.check_item(items.MEDICINE) == 1

    def test_use_med_spends_one_root_with_a_log_line(self):
        p = make_player()
        p.obtain_item(items.MEDICINE, 2)
        p.inactive, p.inact_status = 3, 'injured'
        log_len = len(p.plog)
        p.use_med()
        assert p.check_item(items.MEDICINE) == 1
        assert (p.inactive, p.inact_status) == (0, '')
        assert p.get_stat('healers_used') == 1
        new_lines = p.plog[log_len:]
        assert f'{items.MEDICINE}: -1(1)' in new_lines  # the lose_item line

    def test_buy_item(self):
        p = make_player()
        p.money = 100
        p.buy_item(items.STR_BOOSTER, 70)
        assert p.money == 30
        assert p.check_item(items.STR_BOOSTER) == 1
        assert p.get_stat('items_bought') == 1

    def test_get_items_lists_fight_items(self):
        p = make_player()
        p.obtain_item(items.STR_BOOSTER, 2)
        p.obtain_item(items.MEDICINE)
        assert sorted(p.get_items()) == [items.STR_BOOSTER, items.STR_BOOSTER]
        assert p.get_items(incl_healer=True) == [items.STR_BOOSTER, items.STR_BOOSTER] + [
            items.MEDICINE
        ]
        assert p.get_items(as_dict=True) == {items.STR_BOOSTER: 2}

    def test_get_items_excludes_mock_items(self):
        p = make_player()
        mock = items.MOCK_ITEMS[0]
        p.obtain_item(mock)
        assert p.get_items() == []
        assert p.get_items(incl_mock=True) == [mock]

    def test_check_fight_items(self):
        p = make_player()
        assert p.check_fight_items() is False
        p.obtain_item(items.MEDICINE)  # medicine is not a fight item
        assert p.check_fight_items() is False
        p.obtain_item(items.SUPER_BOOSTER)
        assert p.check_fight_items()


class TestItemEffects:
    def test_boost_item_raises_full_atts(self):
        random.seed(0)
        f = fighter_factory.new_fighter(5)
        base_str = f.strength_full
        items.use_item(items.STR_BOOSTER, f)
        assert f.strength_full > base_str

    def test_cancel_item_restores_atts(self):
        random.seed(0)
        f = fighter_factory.new_fighter(5)
        before = (f.strength_full, f.agility_full, f.speed_full, f.health_full)
        items.use_item(items.SUPER_BOOSTER, f)
        items.cancel_item(items.SUPER_BOOSTER, f)
        assert (f.strength_full, f.agility_full, f.speed_full, f.health_full) == before

    def test_medicine_recovers_player(self):
        p = make_player()
        p.obtain_item(items.MEDICINE)
        p.injure(3)
        assert p.inactive == 3
        assert p.inact_status == 'injured'
        p.use_med()
        assert p.inactive == 0
        assert p.inact_status == ''
        assert p.check_item(items.MEDICINE) == 0
        assert p.get_stat('healers_used') == 1

    def test_item_without_effect_is_kept_with_a_warning(self, caplog):
        # mock items and the mannequin have no EFFECTS entry; using one used
        # to raise KeyError (unreachable from gameplay, but guarded anyway)
        p = make_player()
        mock = items.MOCK_ITEMS[0]
        p.obtain_item(mock)
        p.use_item(mock)
        assert p.check_item(mock) == 1
        p.cancel_item(mock)
        assert 'has no effect' in caplog.text

    def test_use_item_via_player_wrapper(self):
        p = make_player()
        p.obtain_item(items.HLT_BOOSTER)
        hp_before = p.hp_max
        p.use_item(items.HLT_BOOSTER)
        assert p.hp_max > hp_before


class TestItemData:
    def test_all_items_have_descriptions(self):
        for name in items.ALL_ITEMS:
            descr = items.get_item_descr(name)
            assert isinstance(descr, str)

    def test_get_random_item_returns_known_item(self):
        random.seed(0)
        for _ in range(20):
            item = items.get_random_item()
            assert item in items.ALL_ITEMS

    def test_mock_items_are_not_real_items(self):
        random.seed(0)
        for _ in range(20):
            mock = items.get_random_mock_item()
            assert mock in items.MOCK_ITEMS
            assert mock not in items.ALL_ITEMS

    def test_prices_are_positive_ints(self):
        assert all(isinstance(p, int) and p > 0 for p in items.PRICES)
