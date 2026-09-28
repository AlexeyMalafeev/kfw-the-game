from ._base_encounter import BaseEncounter, Guaranteed
from ._utils import check_feeling_greedy
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.utils import rnd


CH_BEGGAR_FIGHT = 0.1
MONEY_GIVE_BEGGAR = 10
REQ_LV_BEGGAR_FIGHT = (5, 10)

# moves
BEGGAR_LOSE_MOVE_TIERS = (2, 4)
# BEGGAR_WIN_MOVE_TIERS = (4, 6)  # decided not to implement


class Beggar(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.p.game.poverty / 2

    def run(self):
        p = self.player
        p.show(_('{} meets a beggar.').format(tr_fighter_name(p.name)))
        p.log(_("Meets a beggar."))
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
        t = _(
            'As {name} turns to leave however, the beggar stops him.\n'
            'Beggar: "In thanks for your kindness, young man, let me teach you some special '
            'kung-fu from {bname}!'
        ).format(name=tr_fighter_name(p.name), bname=tr_fighter_name(b.name))
        p.show(t)
        p.log(
            _('{bname} gives {name} a free kung-fu lesson.').format(
                bname=tr_fighter_name(b.name), name=tr_fighter_name(p.name)
            )
        )
        p.pak()
        if p.spar(b):
            p.show(
                _('{bname}: "Your skill is very impressive! Let\'s practice again some '
                  'time."').format(bname=tr_fighter_name(b.name))
            )
            p.add_friend(b)
            p.add_accompl("Beggar's Friend")
            p.show(
                _('{name}: "What amazing kung-fu! I feel that my technique has '
                  'improved"').format(name=tr_fighter_name(p.name))
            )
            p.pak()
            p.learn_move_from(b)
            luck = p.check_luck()
            if luck == 1:
                p.show(
                    _('{bname}: "Within the four seas, all men are brothers. '
                      'Let me also teach you this secret technique..."').format(
                        bname=tr_fighter_name(b.name)
                    )
                )
                p.pak()
                p.learn_random_new_tech()
            elif luck == -1:
                p.show(
                    _('{name}: "What great good fortune that I could meet this fine man today. '
                      'However, I spent too much energy in this friendly sparring. Now I need '
                      'some good rest."').format(name=tr_fighter_name(p.name))
                )
                p.injure()
                p.pak()
            p.game.beggar = None
        else:
            p.show(_('{bname}: "Still got a lot to learn, huh..."').format(
                bname=tr_fighter_name(b.name)
            ))
            p.show(
                _('{name}: "What amazing kung-fu! Even though I lost, I feel that my technique '
                  'has improved."').format(name=tr_fighter_name(p.name))
            )
            p.pak()
            p.learn_move_from(b)


class GBeggar(Guaranteed, Beggar):
    pass
