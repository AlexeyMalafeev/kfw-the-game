import random

from ._auto_fight import AutoFight
from ._base_fight import BaseFight
from ._helpers import get_prefight_info
from ._normal_fight import NormalFight
from kf_lib.ui import cls, pak, yn


def free_for_all(
    fighters,
    auto_fight=False,
    af_option=True,
    hide_stats=True,
    environment_allowed=True,
    items_allowed=True,
    win_messages=None,
    school_display=False,
    return_fight_obj=False,
):
    """Everyone fights everyone, last man standing wins.
    Return True if fighters[0] wins, False otherwise (including draw)."""
    if any((f.is_human for f in fighters)):
        cls()
        print(get_prefight_info(fighters, hide_enemy_stats=hide_stats))
        if af_option:
            auto_fight = yn('\nAuto fight?')
        else:
            pak()
            cls()
    else:
        auto_fight = True
    if auto_fight:
        f = AutoFreeForAll(
            fighters, [], environment_allowed, items_allowed, win_messages, school_display
        )
    else:
        f = NormalFreeForAll(
            fighters, [], environment_allowed, items_allowed, win_messages, school_display
        )
    if return_fight_obj:
        return f
    return f.win


def group_free_for_all(
    groups,
    auto_fight=False,
    af_option=True,
    hide_stats=True,
    environment_allowed=True,
    items_allowed=True,
    win_messages=None,
    school_display=False,
    return_fight_obj=False,
):
    """Groups fight each other (no infighting), last group standing wins.
    Return True if groups[0] wins, False otherwise (including draw)."""
    fighters = [f for group in groups for f in group]
    if any((f.is_human for f in fighters)):
        cls()
        print(get_prefight_info(fighters, hide_enemy_stats=hide_stats))
        if af_option:
            auto_fight = yn('\nAuto fight?')
        else:
            pak()
            cls()
    else:
        auto_fight = True
    if auto_fight:
        f = AutoGroupFreeForAll(
            groups, environment_allowed, items_allowed, win_messages, school_display
        )
    else:
        f = NormalGroupFreeForAll(
            groups, environment_allowed, items_allowed, win_messages, school_display
        )
    if return_fight_obj:
        return f
    return f.win


class BaseFreeForAll(BaseFight):
    """Free-for-all fight: every fighter for themselves, last man standing wins.

    All fighters are passed as side_a (side_b is empty); the protagonist whose
    perspective `win` reports is the first fighter in the list."""

    def check_fight_over(self):
        self.active_fighters = [f for f in self.all_fighters if f.hp > 0]
        if len(self.active_fighters) > 1:
            return False
        if self.active_fighters:
            self.winners = self.active_fighters[:]
            self.losers = [f for f in self.all_fighters if f not in self.winners]
        else:
            self.winners = []
            self.losers = self.all_fighters
        self.win = bool(self.winners) and self.winners[0] is self.side_a[0]
        return True

    def get_act_allies(self, f):
        return [f]

    def get_act_targets(self, f):
        return [ff for ff in self.active_fighters if ff is not f]

    def handle_prefight_quote(self):
        if len(self.all_fighters) < 2:
            return
        f1, f2 = random.sample(self.all_fighters, 2)
        make_pause = f1.say_prefight_quote() + f2.say_prefight_quote()
        if make_pause > 0:
            self.pak()


class AutoFreeForAll(BaseFreeForAll, AutoFight):
    pass


class NormalFreeForAll(BaseFreeForAll, NormalFight):
    pass


class BaseGroupFreeForAll(BaseFreeForAll):
    """Group free-for-all: several groups fight each other, with no infighting
    within a group; the last group with anyone still standing wins.
    The protagonist group is groups[0]."""

    def __init__(self, groups, *args, **kwargs):
        self.groups = groups
        fighters = [f for group in groups for f in group]
        super().__init__(fighters, [], *args, **kwargs)

    def _get_own_group(self, f):
        for group in self.groups:
            if f in group:
                return group
        return [f]

    def check_fight_over(self):
        self.active_fighters = [f for f in self.all_fighters if f.hp > 0]
        active_groups = [g for g in self.groups if any(f.hp > 0 for f in g)]
        if len(active_groups) > 1:
            return False
        if active_groups:
            self.winners = active_groups[0][:]
            self.losers = [f for f in self.all_fighters if f not in self.winners]
        else:
            self.winners = []
            self.losers = self.all_fighters
        self.win = bool(self.winners) and self.side_a[0] in self.winners
        return True

    def get_act_allies(self, f):
        return [ff for ff in self._get_own_group(f) if ff.hp > 0]

    def get_act_targets(self, f):
        own_group = self._get_own_group(f)
        return [ff for ff in self.active_fighters if ff not in own_group]


class AutoGroupFreeForAll(BaseGroupFreeForAll, AutoFight):
    pass


class NormalGroupFreeForAll(BaseGroupFreeForAll, NormalFight):
    pass
