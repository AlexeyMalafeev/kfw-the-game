from abc import ABC, abstractmethod


class FighterABC(ABC):
    fight_ai = None

    @abstractmethod
    def set_fight_ai(self, *args, **kwargs):
        pass
