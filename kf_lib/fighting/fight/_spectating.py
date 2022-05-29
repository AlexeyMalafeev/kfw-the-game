from ._base_fight import BaseFight
from ._helpers import get_prefight_info, get_sides
from ._normal_fight import NormalFight
from kf_lib.ui import cls, pak


def spectate(f1, f2, f1_allies=None, f2_allies=None, environment_allowed=True, win_messages=None):
    side_a, side_b = get_sides(f1, f2, f1_allies, f2_allies)
    SpectateFight(
        side_a, side_b, environment_allowed=environment_allowed, win_messages=win_messages
    )


class SpectateFight(NormalFight):
    def __init__(
        self, side_a, side_b, environment_allowed=True, win_messages=None, school_display=False
    ):
        BaseFight.__init__(
            self, side_a=side_a, side_b=side_b, environment_allowed=environment_allowed
        )
        self.win_messages = win_messages
        self.school_display = school_display
        self.cls()
        self.show(get_prefight_info(side_a, side_b, hide_enemy_stats=False))
        self.pak()
        # cls()
        self.players = []
        self.prepare_fighters()
        self.fight_loop()
        self.show_win_message()
        self.disarm_all()

    def cls(self):
        cls()

    def show(self, text, **kwargs):
        print(text)

    def show_win_message(self, who_shows_ascii=None, alternative_printing_fn=None):
        super().show_win_message(who_shows_ascii=self.side_a[0], alternative_printing_fn=print)

    def pak(self):
        pak()
