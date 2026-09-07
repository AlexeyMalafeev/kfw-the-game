from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.utils import rnd, rndint
from ._base_story import BaseStory


class GrandMeleeStory(BaseStory):
    """A shady promoter stages a free-for-all prize melee. Fighting for money is
    against the wushu code: rep penalties, a reprimand from the hero's master,
    and possibly a ban from school (see BasePlayer.beg_master_for_mercy)."""

    min_level = 3
    max_level = 6

    ch_master_bans = 0.2
    day_melee_opponents = (5, 7)
    entry_fee = 25
    day_purse = 150
    night_melee_opponents = (4, 6)
    night_purse = 400
    rep_pen_participate = -3
    rep_pen_night_melee = -5

    def intro(self):
        g = self.game
        g.cls()
        t = (
            f'A flashy stranger arrives in {g.town_name} and starts putting up posters: '
            '"THE GRAND MELEE! Eight fighters enter, one fighter leaves with a fat purse! '
            'No rules, no teams, no honor!" The local masters shake their heads in '
            'disapproval...'
        )
        g.show(t)
        g.pak()
        self.boss = b = fighter_factory.new_official(g.get_new_name('Promoter'))
        g.register_fighter(b)

    def scene1(self):
        p, b = self.player, self.boss
        t = (
            f'{p.name} sees a crowd reading the Grand Melee posters. '
            f'{b.name} is boasting to anyone who will listen: '
            f'"Real fighting, no masters wagging their fingers! '
            f'Entry fee {self.entry_fee} coins, the purse is {self.day_purse}! '
            f'What do you say, friend? You look like you can throw a punch!"'
        )
        p.show(t)
        p.log(f'Meets {b.name}, the Grand Melee promoter.')
        p.pak()

    def scene2(self):
        # the day melee
        p, b = self.player, self.boss
        p.show(
            f'The Grand Melee begins! {b.name} waves at {p.name}: '
            f'"Last chance! {self.entry_fee} coins to enter, {self.day_purse} to the '
            f'last man standing!"'
        )
        if not p.check_money(self.entry_fee):
            p.show(f'{p.name} doesn\'t have enough money to enter.')
            p.log('Misses the Grand Melee, being broke.')
            self.end()
            return
        if not p.tourn_or_not():
            p.log('Decides not to participate in the disgraceful Grand Melee.')
            self.end()
            return
        p.pay(self.entry_fee)
        p.gain_rep(self.rep_pen_participate)
        p.log('Participates in the Grand Melee.')
        opponents = [
            fighter_factory.new_brawler()
            for _ in range(rndint(*self.day_melee_opponents))
        ]
        if fight.free_for_all([p] + opponents):
            p.show(f'{p.name} is the last one standing! The crowd goes wild!')
            p.earn_prize(self.day_purse)
            p.add_accompl('Grand Melee Champion')
            p.log('Wins the Grand Melee.')
            # winning leads to the night melee (scene3)
        else:
            p.log('Loses the Grand Melee.')
            self.state += 1  # skip the night melee scene, go straight to the reprimand
        p.pak()

    def scene3(self):
        # the night melee, only reached after winning the day melee
        p, b = self.player, self.boss
        p.show(
            f'{b.name} finds {p.name} after the fight: "The crowd LOVED you! How about the '
            f'Night Melee? Armed fighters, no questions asked, and the purse is '
            f'{self.night_purse} coins! But let\'s keep it quiet — if your master finds out..."'
        )
        p.log('Is invited to the Night Melee.')
        if p.tourn_or_not():
            p.gain_rep(self.rep_pen_night_melee)
            p.log('Participates in the Night Melee.')
            opponents = [
                fighter_factory.new_prize_fighter(
                    max(rndint(p.level - 1, p.level + 2), 1)
                )
                for _ in range(rndint(*self.night_melee_opponents))
            ]
            for e in opponents:
                e.arm_robber()
            if fight.free_for_all([p] + opponents):
                p.show(f'{p.name} is the last one standing again! Easy money!')
                p.earn_prize(self.night_purse)
                p.add_accompl('King of the Night Ring')
                p.log('Wins the Night Melee.')
            else:
                p.log('Loses the Night Melee.')
        else:
            p.log('Declines the Night Melee.')
        p.pak()

    def scene4(self):
        # the master's reprimand, after the final bout (win or lose)
        g, p = self.game, self.player
        m = g.masters.get(p.style.name)
        if m is None or p.is_master:
            self.end()
            return
        p.show(
            f'{m.name} summons {p.name}.\n'
            f'{m.name}: "So. The WHOLE town is talking about how my student rolled in the '
            f'dirt for coins like a common wrestler! A hundred horse stances! NOW!"\n'
            f'{p.name} spends the whole evening holding the horse stance, sweating and '
            f'repenting.'
        )
        p.log(f'Is reprimanded and disciplined by {m.name} for fighting for money.')
        if rnd() <= self.ch_master_bans:
            p.banned_from_school = True
            p.show(
                f'{m.name}: "And that is not all! You are BANNED from this school until you '
                f'learn some humility. Do not show your face here!"'
            )
            p.log(f'Is banned from school by {m.name}.')
        p.pak()
        self.end()
