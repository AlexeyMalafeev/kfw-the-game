from abc import ABC

from kf_lib.actors.fighter._abc import FighterAPI


class BlankFighterIO(FighterAPI, ABC):
    def cls(self):
        pass

    def log(self, text: str) -> None:
        pass

    def msg(self, *args, **kwargs) -> None:
        pass

    def pak(self) -> None:
        pass

    def show(self, text: str, align: bool = False) -> None:
        pass

    def write(self, *args, **kwargs) -> None:
        pass
