from abc import ABC

from kf_lib.actors.fighter._abc import FighterAPI


class BlankFighterIO(FighterAPI, ABC):
    def cls(self):
        pass

    def log(self, text: str) -> None:
        pass

    def msg(self, *args, **kwargs):
        pass

    def pak(self):
        pass

    def show(self, text, align=False):
        pass

    def write(self, *args, **kwargs):
        pass
