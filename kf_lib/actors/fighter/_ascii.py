from ._base_fighter import BaseFighter
from kf_lib.kung_fu import ascii_art


class FighterWithASCII(BaseFighter):
    def refresh_ascii(self):
        self.ascii_l, self.ascii_r = self.action.ascii_l, self.action.ascii_r
        targ = self.target
        self.ascii_buffer = targ.ascii_buffer = 0
        if targ.check_status('lying'):
            targ.set_ascii('Lying')
        else:
            targ.set_ascii('Stance')

    def set_ascii(self, ascii_name):
        self.ascii_l, self.ascii_r = ascii_art.get_ascii(ascii_name)
        self.ascii_name = ascii_name

    def show_ascii(self):
        try:
            if self in self.current_fight.side_a:
                a = self.ascii_l
                b = self.target.ascii_r
            else:
                b = self.ascii_r
                a = self.target.ascii_l
        except AttributeError:
            import pprint
            print(self)
            print('**********\n'*3)
            pprint.pprint(vars(self))
            print('**********\n'*3)
            pprint.pprint(vars(self.current_fight))
            print('**********\n'*3)
            pprint.pprint(vars(self.current_fight.side_b[0]))
            print('**********\n'*3)
            raise
        buffer = max((self.ascii_buffer, self.target.ascii_buffer))
        pic = ascii_art.concat(a, b, buffer)
        self.current_fight.show(pic, align=False)
        self.current_fight.cartoon.append(pic)
