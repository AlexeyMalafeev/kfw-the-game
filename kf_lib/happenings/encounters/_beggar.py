from ._base_encounter import BaseEncounter, Guaranteed
from ._utils import check_feeling_greedy
from ...utils._random import rnd

CH_BEGGAR_FIGHT = 0.1
MONEY_GIVE_BEGGAR = 10
REQ_LV_BEGGAR_FIGHT = (5, 10)


class Beggar(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.p.game.poverty / 2

    def run(self):
        p = self.player
        p.show(f"{p.name} meets a beggar.")
        p.log("Meets a beggar.")
        amount = p.donate_or_not(MONEY_GIVE_BEGGAR)
        if amount and not check_feeling_greedy(p):
            p.donate(amount)
            if p.check_lv(*REQ_LV_BEGGAR_FIGHT) and rnd() <= CH_BEGGAR_FIGHT:
                self.do_fight()

    def do_fight(self):
        p = self.player
        b = p.game.beggar
        if b is None:
            return
        t = (
            f'As {p.name} turns to leave however, the beggar stops him.\n'
            'Beggar: "In thanks for your kindness, young man, let me teach you some special '
            f'kung-fu from {b.name}!'
        )
        p.show(t)
        p.log(f"{b.name} gives {p.name} a free kung-fu lesson.")
        p.pak()
        if p.spar(b):
            p.show(f'{b.name}: "Your skill is very impressive! Let\'s practice again some time."')
            p.add_friend(b)
            p.add_accompl("Beggar's Friend")
            p.show(f'{p.name}: "What amazing kung-fu! I feel that my technique has improved"')
            p.pak()
            p.learn_move_from(b)
            luck = p.check_luck()
            if luck == 1:
                p.show(f'{b.name}: "Within the four seas, all men are brothers. '
                       'Let me also teach you this secret technique..."')
                p.pak()
                p.learn_random_new_tech()
            elif luck == -1:
                p.show(f'{p.name}: "What great good fortune that I could meet this fine man today. '
                       'However, I spent too much energy in this friendly sparring. Now I need '
                       'some good rest."')
                p.injure()
                p.pak()
            p.game.beggar = None
        else:
            p.show(f'{b.name}: "Still got a lot to learn, huh..."')
            p.show(
                f'{p.name}: "What amazing kung-fu! Even though I lost, I feel that my technique '
                'has improved."'
            )
            p.pak()
            p.learn_move_from(b)


class GBeggar(Guaranteed, Beggar):
    pass
