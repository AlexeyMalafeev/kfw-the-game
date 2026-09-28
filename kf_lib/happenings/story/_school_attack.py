from kf_lib.actors import fighter_factory
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.utils import rndint
from ._base_story import BaseStory


# constants
MIN_STUDENTS_FOR_ATTACK = 2
ATTACK_THUGS = (2, 4)
SCHOOL_DEFENSE_WIN_REP = 8
SCHOOL_DEFENSE_LOSE_REP = -5
RANSACK_MONEY = (100, 300)


class SchoolAttackStory(BaseStory):
    """Thugs hired by a rival school attack the player's school at night;
    the master and the students defend it together."""

    min_level = 11
    max_level = 20

    def test(self, player):
        p = player
        return (
            super().test(p)
            and p.is_master
            and p.students >= MIN_STUDENTS_FOR_ATTACK
        )

    def intro(self):
        g, p = self.game, self.player
        g.cls()
        t = _(
            'Lately, rough-looking strangers have been seen watching {school}. '
            '{name}\'s students whisper that someone has hired thugs to "teach the new '
            'master a lesson".'
        ).format(school=p.new_school_name, name=tr_fighter_name(p.name))
        g.show(t)
        g.pak()

    def scene1(self):
        g, p = self.game, self.player
        school = g.schools[p.new_school_name]
        thugs = fighter_factory.new_thug(n=rndint(*ATTACK_THUGS))
        if not isinstance(thugs, list):
            thugs = [thugs]
        t = _(
            'Night. A crash of breaking wood — masked men burst into {school} '
            'with torches and clubs! {name} and the students rush out to defend the school.'
        ).format(school=p.new_school_name, name=tr_fighter_name(p.name))
        p.show(t)
        p.log(_('Defends the school against a night attack.'))
        p.pak()
        if p.fight(thugs[0], allies=school, en_allies=thugs[1:], hide_stats=False):
            p.show(
                _('The last thug crawls away into the night. The school stands! '
                  'The neighbors saw everything — word spreads through {town}.')
                .format(town=g.town_name)
            )
            p.log(_('Repels the attack on the school!'))
            p.gain_rep(SCHOOL_DEFENSE_WIN_REP)
            p.add_accompl('School Defender')
        else:
            loss = min(p.money, rndint(*RANSACK_MONEY))
            p.show(
                _('The school is ransacked and half-burned before the thugs retreat '
                  'into the night. It will take time to live this down...')
            )
            p.log(_('Fails to defend the school; it is ransacked.'))
            if loss > 0:
                p.pay(loss)
            p.gain_rep(SCHOOL_DEFENSE_LOSE_REP)
        p.pak()
        self.end()
