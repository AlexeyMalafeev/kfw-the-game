from ._base_fight import BaseFight
from ._auto_fight import AutoFight


class NormalFight(AutoFight):
    """Does not only have fight mechanics, but also outputs what happens during the fight."""

    def cls(self):
        self.main_player.cls()

    def display(self, text, **kwargs):
        BaseFight.display(self, text, **kwargs)
        self.show(text, **kwargs)

    def pak(self):
        self.main_player.pak()

    def prepare_fighters(self):
        AutoFight.prepare_fighters(self)
        for f in self.all_fighters:
            if f.is_human:
                f.is_auto_fighting = False

    def show(self, text, **kwargs):
        self.main_player.show(text, **kwargs)
