from kf_lib.ui import cls, yn


class GameIO:
    def __init__(self):
        self.spectator = None

    def cls(self):
        if self.spectator:
            cls()

    def msg(self, text, align=True):
        if self.spectator:
            self.spectator.show(text, align=align)
            self.spectator.pak()

    def pak(self):
        if self.spectator:
            self.spectator.pak()

    def show(self, text, align=True):
        if self.spectator:
            self.spectator.show(text, align)

    def yn(self, text):
        if self.spectator:
            return yn(text)
        else:
            return True
