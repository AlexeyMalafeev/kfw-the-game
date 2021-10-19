from ._base_fighter import BaseFighter
from ...kung_fu import ascii_art


class FighterWithASCII(BaseFighter):
    ascii_l = ''
    ascii_r = ''
    ascii_name = ''

    def refresh_ascii(self):
        self.ascii_l, self.ascii_r = self.action.ascii_l, self.action.ascii_r
        targ = self.target
        if targ.check_status('lying'):
            targ.set_ascii('Lying')
        else:
            targ.set_ascii('Stance')

    def set_ascii(self, ascii_name):
        self.ascii_l, self.ascii_r = ascii_art.get_ascii(ascii_name)
        self.ascii_name = ascii_name

    def show_ascii(self):
        if self in self.current_fight.side_a:
            a = self.ascii_l
            b = self.target.ascii_r
        else:
            b = self.ascii_r
            a = self.target.ascii_l
        pic = ascii_art.concat(a, b)
        self.current_fight.show(pic, align=False)
        self.current_fight.cartoon.append(pic)
