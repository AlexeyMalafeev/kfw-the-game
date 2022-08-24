from abc import ABC, abstractmethod


class FighterAPI(ABC):
    action = None
    ascii_buffer = None
    ascii_l = None
    ascii_name = None
    ascii_r = None
    current_fight = None
    fight_ai = None
    target = None

    @abstractmethod
    def set_ascii(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_fight_ai(self, *args, **kwargs):
        pass

    @abstractmethod
    def show_ascii(self, *args, **kwargs):
        pass
