from ._base_fighter import BaseFighter
from ...utils.utilities import get_bar, pak


class FighterUI(BaseFighter):
    def msg(self, *args, **kwargs):
        pass

    def pak(self):
        pass

    def show(self, text, align=False):
        pass

    def cls(self):
        pass

    def see_fight_info(self, *args, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass
