from abc import ABC, abstractmethod

from kf_lib.ui import MUSIC, music


all_random_encounter_classes = []


class BaseEncounter(ABC):
    guaranteed = False
    thematic_only = False  # True: only in a day action's own list, not the daily pool
    music = None  # a ui.MUSIC key: the scene's tune while it runs (see docs/audio.md)

    def __init__(
            self,
            player,
            check_if_happens: bool = True
    ):
        self.p = self.player = player
        if (check_if_happens and self.check_if_happens()) or not check_if_happens:
            enc_name = self.__class__.__name__
            enc_dict = self.p.game.enc_count_dict
            if enc_name in enc_dict:
                enc_dict[enc_name] += 1
            else:
                enc_dict[enc_name] = 1
            self.p.refresh_screen()
            tune = MUSIC.get(self.music)
            with music(tune, enabled=bool(tune) and self.p.shows_output):
                self.run()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.guaranteed and not cls.thematic_only:
            all_random_encounter_classes.append(cls)

    @abstractmethod
    def check_if_happens(self) -> bool:
        pass

    @abstractmethod
    def run(self) -> None:
        pass


class Guaranteed:
    guaranteed = True

    @staticmethod
    def check_if_happens():
        return True
