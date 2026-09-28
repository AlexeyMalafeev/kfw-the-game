from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.i18n import _, ngettext, tr_fighter_name
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
            _('A flashy stranger arrives in {town} and starts putting up posters: '
              '"THE GRAND MELEE! Eight fighters enter, one fighter leaves with a fat '
              'purse! No rules, no teams, no honor!" The local masters shake their '
              'heads in disapproval...')
        ).format(town=g.town_name)
        g.show(t)
        g.pak()
        self.boss = b = fighter_factory.new_official(g.get_new_name('Promoter'))
        g.register_fighter(b)

    def scene1(self):
        p, b = self.player, self.boss
        t = (
            ngettext(
                '{name} sees a crowd reading the Grand Melee posters. '
                '{boss} is boasting to anyone who will listen: '
                '"Real fighting, no masters wagging their fingers! '
                'Entry fee {fee} coin, the purse is {purse}! '
                'What do you say, friend? You look like you can throw a punch!"',
                '{name} sees a crowd reading the Grand Melee posters. '
                '{boss} is boasting to anyone who will listen: '
                '"Real fighting, no masters wagging their fingers! '
                'Entry fee {fee} coins, the purse is {purse}! '
                'What do you say, friend? You look like you can throw a punch!"',
                self.entry_fee,
            )
        ).format(
            name=tr_fighter_name(p.name),
            boss=tr_fighter_name(b.name),
            fee=self.entry_fee,
            purse=self.day_purse,
        )
        p.show(t)
        p.log(
            _('Meets {boss}, the Grand Melee promoter.').format(
                boss=tr_fighter_name(b.name)
            )
        )
        p.pak()

    def scene2(self):
        # the day melee
        p, b = self.player, self.boss
        p.show(
            ngettext(
                'The Grand Melee begins! {boss} waves at {name}: '
                '"Last chance! {fee} coin to enter, {purse} to the '
                'last man standing!"',
                'The Grand Melee begins! {boss} waves at {name}: '
                '"Last chance! {fee} coins to enter, {purse} to the '
                'last man standing!"',
                self.entry_fee,
            ).format(
                boss=tr_fighter_name(b.name),
                name=tr_fighter_name(p.name),
                fee=self.entry_fee,
                purse=self.day_purse,
            )
        )
        if not p.check_money(self.entry_fee):
            p.show(
                _('{name} doesn\'t have enough money to enter.').format(
                    name=tr_fighter_name(p.name)
                )
            )
            p.log(_('Misses the Grand Melee, being broke.'))
            self.end()
            return
        if not p.tourn_or_not():
            p.log(_('Decides not to participate in the disgraceful Grand Melee.'))
            self.end()
            return
        p.pay(self.entry_fee)
        p.gain_rep(self.rep_pen_participate)
        p.log(_('Participates in the Grand Melee.'))
        opponents = [
            fighter_factory.new_brawler()
            for _ in range(rndint(*self.day_melee_opponents))
        ]
        if fight.free_for_all([p] + opponents):
            p.show(
                _('{name} is the last one standing! The crowd goes wild!').format(
                    name=tr_fighter_name(p.name)
                )
            )
            p.earn_prize(self.day_purse)
            p.add_accompl('Grand Melee Champion')
            p.log(_('Wins the Grand Melee.'))
            # winning leads to the night melee (scene3)
        else:
            p.log(_('Loses the Grand Melee.'))
            self.state += 1  # skip the night melee scene, go straight to the reprimand
        p.pak()

    def scene3(self):
        # the night melee, only reached after winning the day melee
        p, b = self.player, self.boss
        p.show(
            ngettext(
                '{boss} finds {name} after the fight: "The crowd LOVED you! How about '
                'the Night Melee? Armed fighters, no questions asked, and the purse '
                'is {purse} coin! But let\'s keep it quiet — if your master finds '
                'out..."',
                '{boss} finds {name} after the fight: "The crowd LOVED you! How about '
                'the Night Melee? Armed fighters, no questions asked, and the purse '
                'is {purse} coins! But let\'s keep it quiet — if your master finds '
                'out..."',
                self.night_purse,
            ).format(
                boss=tr_fighter_name(b.name),
                name=tr_fighter_name(p.name),
                purse=self.night_purse,
            )
        )
        p.log(_('Is invited to the Night Melee.'))
        if p.tourn_or_not():
            p.gain_rep(self.rep_pen_night_melee)
            p.log(_('Participates in the Night Melee.'))
            opponents = [
                fighter_factory.new_prize_fighter(
                    max(rndint(p.level - 1, p.level + 2), 1)
                )
                for _ in range(rndint(*self.night_melee_opponents))
            ]
            for e in opponents:
                e.arm_robber()
            if fight.free_for_all([p] + opponents):
                p.show(
                    _('{name} is the last one standing again! Easy money!').format(
                        name=tr_fighter_name(p.name)
                    )
                )
                p.earn_prize(self.night_purse)
                p.add_accompl('King of the Night Ring')
                p.log(_('Wins the Night Melee.'))
            else:
                p.log(_('Loses the Night Melee.'))
        else:
            p.log(_('Declines the Night Melee.'))
        p.pak()

    def scene4(self):
        # the master's reprimand, after the final bout (win or lose)
        g, p = self.game, self.player
        m = g.masters.get(p.style.name)
        if m is None or p.is_master:
            self.end()
            return
        p.show(
            _('{master} summons {name}.\n'
              '{master}: "So. The WHOLE town is talking about how my student rolled '
              'in the dirt for coins like a common wrestler! A hundred horse '
              'stances! NOW!"\n'
              '{name} spends the whole evening holding the horse stance, sweating '
              'and repenting.').format(
                master=tr_fighter_name(m.name), name=tr_fighter_name(p.name)
            )
        )
        p.log(
            _(
                'Is reprimanded and disciplined by {master} for fighting for money.'
            ).format(master=tr_fighter_name(m.name))
        )
        if rnd() <= self.ch_master_bans:
            p.banned_from_school = True
            p.show(
                _('{master}: "And that is not all! You are BANNED from this school '
                  'until you learn some humility. Do not show your face '
                  'here!"').format(master=tr_fighter_name(m.name))
            )
            p.log(
                _('Is banned from school by {master}.').format(
                    master=tr_fighter_name(m.name)
                )
            )
        p.pak()
        self.end()
