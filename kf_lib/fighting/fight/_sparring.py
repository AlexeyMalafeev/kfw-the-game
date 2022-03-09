from ._auto_fight import AutoFight
from ._base_fight import BaseFight
from ._helpers import get_prefight_info, get_sides
from ._normal_fight import NormalFight
from kf_lib.ui import cls, pak, yn


def spar(
    f1,
    f2,
    f1_allies=None,
    f2_allies=None,
    auto_fight=False,
    af_option=True,
    hide_stats=False,
    environment_allowed=True,
):
    """Return True if f1 wins, False otherwise (including draw).
    A sparring is different from a fight in that there are no injuries and items are not allowed.
    Everything else is the same."""
    side_a, side_b = get_sides(f1, f2, f1_allies, f2_allies)
    if any((f.is_human for f in side_a + side_b)):
        cls()
        print(get_prefight_info(side_a, side_b, hide_stats))
        if af_option:
            auto_fight = yn('\nAuto fight?')
        else:
            pak()
            cls()
    else:
        auto_fight = True
    if auto_fight:
        f = AutoSparring(side_a, side_b, environment_allowed)
    else:
        f = NormalSparring(side_a, side_b, environment_allowed)
    return f.win


class BaseSparring(BaseFight):
    """Doesn't have items, accomplishments, injuries, stats, quotes or gossip."""

    def handle_accompl(self):
        pass

    def handle_injuries(self):
        pass

    def handle_items(self):
        pass

    def handle_player_stats(self):
        pass

    def handle_prefight_quote(self):
        pass

    def handle_win_quote(self):
        pass

    def handle_gossip(self):
        pass


class AutoSparring(BaseSparring, AutoFight):
    pass


class NormalSparring(BaseSparring, NormalFight):
    pass
