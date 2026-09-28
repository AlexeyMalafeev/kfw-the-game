import random

from kf_lib.actors import fighter_factory
from kf_lib.i18n import _, ngettext, tr_fighter_name
from kf_lib.utils import rnd, rndint
from ._base_encounter import BaseEncounter, Guaranteed


# constants
# encounter chances
ENC_CH_GAMBLER = 0.05
ENC_CH_PRIZE_FIGHTING = 0.02

# misc chances
CH_GAMBLER_ARMED = 0.3
CH_GAMBLER_ENEMY = 0.5
CH_GAMBLER_FIGHT = 0.25

# levels
LV_PRIZE_FIGHTERS = (2, 4, 7, 10, 15)

# money
MONEY_GAMBLING_BETS = (20, 25, 30, 40, 50)
MONEY_PRIZE_FIGHTING_FEE = 50
MONEY_PRIZE_FIGHTING_WIN = (25, 50, 100, 150, 250)

# reputation
REP_PEN_GAMBLE = -3
REP_PEN_PRIZE_FIGHTING = -5


class Gambler(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.bet = 0
        self.won = 0
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= ENC_CH_GAMBLER

    def run(self):
        p = self.player
        self.bet = random.choice(MONEY_GAMBLING_BETS)
        t = ngettext(
            'Gambler: "Hey, do you want to play? You could make some serious money!"\n'
            'One bet is {} coin.',
            'Gambler: "Hey, do you want to play? You could make some serious money!"\n'
            'One bet is {} coins.',
            self.bet,
        ).format(self.bet)
        p.show(t)
        p.log(_("Meets a gambler."))
        if p.gamble_or_not() or rnd() < p.gamble_with_gambler:
            p.show(_("{} can't resist the temptation.").format(tr_fighter_name(p.name)))
            p.log(_("Gambles."))
            p.gain_rep(REP_PEN_GAMBLE)
            money = p.money
            p.pak()
            self.play()
            self.won = p.money - money
            p.refresh_screen()
            if self.won <= 0:
                p.msg(_('Gambler: "Better luck next time!"'))
                p.record_gamble_lost(-self.won)
            else:
                p.record_gamble_win(self.won)
                if self.won >= 100 and rnd() <= CH_GAMBLER_FIGHT:
                    self.do_fight()
        else:
            p.show(_("{} refuses to gamble.").format(tr_fighter_name(p.name)))
            p.log(_("Refuses to gamble."))
            p.pak()

    def play(self):
        p = self.player
        RPS_TR = {'Rock': _('Rock'), 'Paper': _('Paper'), 'Scissors': _('Scissors')}
        skewed = random.choice((1, 0))
        if skewed:
            weights = [rndint(1, 3) for _ in range(3)]
            gambler_options = (
                ["Rock"] * weights[0] + ["Paper"] * weights[1] + ["Scissors"] * weights[2]
            )
        else:
            gambler_options = ["Rock", "Paper", "Scissors"]
        i = 0
        while True:
            i += 1
            if p.check_money(self.bet):
                if i <= 5:
                    p.pay(self.bet)
                    while True:
                        p.refresh_screen()
                        yc = p.rock_paper_or_scissors()
                        gc = random.choice(gambler_options)
                        p.show(
                            _("{p_name}: {yc}\nGambler: {gc}").format(
                                p_name=tr_fighter_name(p.name),
                                yc=RPS_TR[yc],
                                gc=RPS_TR[gc],
                            )
                        )
                        if yc == gc:
                            p.show(_("Tie!"))
                            p.pak()
                            continue
                        if (
                            (yc == "Rock" and gc == "Scissors")
                            or (yc == "Paper" and gc == "Rock")
                            or (yc == "Scissors" and gc == "Paper")
                        ):
                            p.money += self.bet * 2
                            p.show(_("{} wins!").format(tr_fighter_name(p.name)))
                            p.pak()
                            break
                        else:
                            p.show(_("Gambler wins!"))
                            p.pak()
                            break
                    p.refresh_screen()
                else:
                    if not rnd() < p.gamble_continue:
                        p.show(
                            _("{} decides to stop gambling.").format(
                                tr_fighter_name(p.name)
                            )
                        )
                        p.pak()
                        return
                    else:
                        i = 0
            else:
                break

    def do_fight(self):
        p = self.player
        g = fighter_factory.new_gambler()
        g.name = p.game.get_new_name("Gambler")
        if rnd() <= CH_GAMBLER_ARMED:
            g.arm_improv()
        p.show(_('Gambler: "You think you can get away with that?"'))
        p.log(_("The gambler attacks {}.").format(tr_fighter_name(p.name)))
        p.pak()
        if p.fight(g):
            if rnd() <= CH_GAMBLER_ENEMY:
                p.show(_('Gambler: "I\'m telling you, this is not over yet!"'))
                p.add_enemy(g)
                p.pak()
            p.add_accompl("Gambler Beaten")
        else:
            p.money -= self.won
            p.show(_("Gambler: I'm just taking back what's mine!"))
            p.pak()



class PrizeFighting(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_PRIZE_FIGHTING

    def run(self):
        p = self.player
        t = ngettext(
            "{} meets a shady character who offers to participate in an underground prize fighting contest. "
            "\"It's simple. You pay {} coin to enter. There are five stages in the contest. The more opponents you "
            'beat, the more money you win. How does that sound?"',
            "{} meets a shady character who offers to participate in an underground prize fighting contest. "
            "\"It's simple. You pay {} coins to enter. There are five stages in the contest. The more opponents you "
            'beat, the more money you win. How does that sound?"',
            MONEY_PRIZE_FIGHTING_FEE,
        ).format(tr_fighter_name(p.name), MONEY_PRIZE_FIGHTING_FEE)
        p.show(t)
        p.log(_("Offered to take part in an underground prize fighting contest."))
        if not p.check_money(MONEY_PRIZE_FIGHTING_FEE):
            p.show(
                _("{} doesn't have enough money.").format(tr_fighter_name(p.name))
            )
            p.pak()
        elif p.tourn_or_not():
            p.gain_rep(REP_PEN_PRIZE_FIGHTING)
            p.pay(MONEY_PRIZE_FIGHTING_FEE)
            self.do_fight()
        else:
            p.log(_("Chooses to ignore the offer."))

    def do_fight(self):
        p = self.p
        prize = 0
        for i, lv in enumerate(LV_PRIZE_FIGHTERS):
            p.cls()
            p.show(_("Stage {}").format(i + 1))
            c = fighter_factory.new_prize_fighter(lv)
            opp_strength = p.get_rel_strength(c)
            if (i and p.fight_or_not(opp_strength)) or not i:
                win = p.fight(c, items_allowed=False)
                if win:
                    prize = MONEY_PRIZE_FIGHTING_WIN[i]
                else:
                    prize = 0
                    break
            else:
                break
        if prize:
            p.earn_prize(prize)
            p.pak()



class GGambler(Guaranteed, Gambler):
    pass



