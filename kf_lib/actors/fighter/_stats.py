from abc import ABC

from kf_lib.actors.fighter._abc import FighterAPI


class FighterStats(FighterAPI, ABC):
    def change_stat(self, *args, **kwargs) -> None:
        pass
