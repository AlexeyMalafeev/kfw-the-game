class BaseEncounter(object):
    """Base encounter class."""

    def __init__(self, player, check_if_happens=True):
        self.p = self.player = player
        if (check_if_happens and self.check_if_happens()) or not check_if_happens:
            enc_name = self.__class__.__name__
            enc_dict = self.p.game.enc_count_dict
            if enc_name in enc_dict:
                enc_dict[enc_name] += 1
            else:
                enc_dict[enc_name] = 1
            self.p.refresh_screen()
            self.run()

    def check_if_happens(self):
        return True

    def run(self):
        pass


class Guaranteed(object):
    @staticmethod
    def check_if_happens():
        return True
