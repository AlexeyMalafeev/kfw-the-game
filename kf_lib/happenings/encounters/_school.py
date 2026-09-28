import random

from kf_lib.actors import fighter_factory, quotes
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.ui import yn
from kf_lib.utils import rnd, rndint
from ._base_encounter import BaseEncounter
from ._utils import get_escape_chance, try_escape


# constants
# encounter chances
ENC_CH_MASTER_TRIAL = 0.05
# ENC_CH_SCHOOL_CHALL = 0.05
ENC_CH_SCHOOL_BULLYING = 0.03
ENC_CH_STUDENT = 0.07

# misc chances
CH_SCHOOL_CHALLENGER_ARMED = 0.3
CH_STUDENT_CHALLENGE = 0.25
BASE_STUDENT_CH = 0.01  # even a completely unknown master attracts some applicants

# levels
LV_STUD_CHALLENGERS = (1, 3)
REQ_LV_MASTER_TRIAL = fighter_factory.MASTER_LV[0]

# money
MONEY_OPEN_SCHOOL = 1000

# numbers
NUM_STUD_CHALLENGERS = (2, 5)

# rewards for reaching school rank 1
RANK1_EXP = 25
RANK1_REP = 2


class MasterTrial(BaseEncounter):
    def check_if_happens(self):
        p = self.player
        return (
            not p.is_master
            and p.school_rank == 1
            and p.check_lv(REQ_LV_MASTER_TRIAL)
            and rnd() <= ENC_CH_MASTER_TRIAL
        )

    def run(self):
        p = self.player
        m = p.get_master()
        t = (
            _('{p_name} meets his master. \n{m_name}: "{p_name}, you are one of my best students. '
              'You have made a lot of progress in {style}. But you might be ready to found your own '
              'kung-fu school... '
              "Let's find that out!\"")
        ).format(
            p_name=tr_fighter_name(p.name),
            m_name=tr_fighter_name(m.name),
            style=p.get_displayed_style_name(),
        )
        p.show(t)
        p.log(_('Is offered a trial to become a master.'))
        opp_strength = p.get_rel_strength(m)
        if p.fight_or_not(opp_strength):
            if p.spar(m, hide_stats=False):
                p.show(_('{name}: "Yes, you ARE ready!"').format(name=tr_fighter_name(m.name)))
                p.add_friend(m)
                outlay = MONEY_OPEN_SCHOOL
                p.show(
                    _('To open a martial arts school, {} needs to make the initial outlay of {} '
                      'coins.').format(tr_fighter_name(p.name), outlay)
                )
                p.pay(outlay)
                # grab the old school before is_master flips get_school()
                school = p.game.schools[p.style.name]
                school.remove(p)
                p.is_master = True
                p.log(_('Becomes a master and founds his own school.'))
                p.set_stat("became_master", p.game.get_date())
                p.set_stat("became_master_at_lv", p.level)
                for a_player in p.game.players:
                    a_player.refresh_school_rank()  # in case there are other players in the same school
                school_name = p.choose_school_name()
                p.game.schools[school_name] = []
                p.game.masters[school_name] = p
                p.new_school_name = school_name
                p.custom_style_name = school_name
                p.show(
                    _("From now on, {name}'s kung-fu style will be known as {school}.").format(
                        name=tr_fighter_name(p.name), school=school_name
                    )
                )
                p.log(_('Founds the {} school and style.').format(school_name))
                p.choose_school_techs()
            else:
                p.show(
                    _('{name}: "No, you are not ready yet. Practice some more."').format(
                        name=tr_fighter_name(m.name)
                    )
                )
            p.pak()



class SchoolBullying(BaseEncounter):
    def check_if_happens(self):
        p = self.p
        return not p.is_master and p.school_rank > 1 and rnd() <= ENC_CH_SCHOOL_BULLYING

    def run(self):
        p = self.player
        m = self.player.get_master()
        t = _('{p_name} is bullied at his school while {m_name} is away.').format(
            p_name=tr_fighter_name(p.name), m_name=tr_fighter_name(m.name)
        )
        p.show(t)
        p.log(_('Is bullied at his school.'))
        school = p.get_school()
        opp = random.choice(
            school[: p.school_rank - 1]
        )  # adjusts for Python indexing and skips self
        opp_strength = p.get_rel_strength(opp)
        esc_chance = get_escape_chance(p)
        if p.fight_or_run(opp_strength, esc_chance):
            p.fight(opp, hide_stats=False)
        else:
            try_escape(p, esc_chance)



class SchoolChallenge(BaseEncounter):
    def check_if_happens(self):
        p = self.p
        return (
            not p.is_master
            and p.school_rank > 1
            and self._get_target() is not None
            and rnd() <= ((len(p.get_school()) - 1) / 100)
        )

    def _get_target(self):
        """The nearest active schoolmate above the player; inactive (KO'd)
        schoolmates can't be challenged and are skipped."""
        p = self.p
        for f in reversed(p.get_school()[: p.school_rank - 1]):
            if not (f.is_player and f.inactive):
                return f
        return None

    def run(self):
        p = self.player
        opp = self._get_target()
        if opp is None:
            return
        m = self.player.get_master()
        t = _('''{p_name} meets his master.
{m_name}: "{p_name}, you have been practicing hard. It is now time to test your kung-fu!"''').format(
            p_name=tr_fighter_name(p.name), m_name=tr_fighter_name(m.name)
        )
        p.show(t)
        p.log(_('Is offered a trial at his school.'))
        school = p.get_school()
        opp_strength = p.get_rel_strength(opp)
        if p.fight_or_not(opp_strength):
            if rnd() < CH_SCHOOL_CHALLENGER_ARMED:
                p.arm_normal()
                opp.arm_normal()
            if p.spar(opp, hide_stats=False):
                # take the defeated opponent's slot, leapfrogging any skipped
                # inactive schoolmates: everyone passed shifts one rank down
                opp_idx = school.index(opp)
                school.remove(p)
                school.insert(opp_idx, p)
                for a_player in p.game.players:
                    a_player.refresh_school_rank()  # other players' ranks may have shifted
                if p.school_rank > 1:
                    t = (
                        _('{m_name}: "{p_name}, I can see that you have mastered some aspects of '
                          '{style}. However, you must keep practicing as you still have a long way '
                          'to go."')
                    ).format(
                        m_name=tr_fighter_name(m.name),
                        p_name=tr_fighter_name(p.name),
                        style=p.get_displayed_style_name(),
                    )
                    p.show(t)
                else:
                    t = (
                        _('{m_name}: "Well done, {p_name}. You are now the best student of '
                          'our school. You make me proud — but remember, there is always '
                          'more to learn."')
                    ).format(m_name=tr_fighter_name(m.name), p_name=tr_fighter_name(p.name))
                    p.show(t)
                    p.log(_('Becomes the best student of his school.'))
                    p.gain_exp(RANK1_EXP)
                    p.gain_rep(RANK1_REP)
            else:
                react = random.choice(quotes.MASTER_CRITICISM)
                p.show(_('{name}: {react}').format(name=tr_fighter_name(m.name), react=react))
            p.pak()



class Students(BaseEncounter):
    def check_if_happens(self):
        return (
            self.p.is_master
            and self.p.students < self.p.game.MAX_NUM_STUDENTS
            and rnd() <= min(BASE_STUDENT_CH + self.p.get_fame(), ENC_CH_STUDENT)
        )

    def run(self):
        p = self.player
        n_can_join = p.game.MAX_NUM_STUDENTS - p.students
        if n_can_join >= NUM_STUD_CHALLENGERS[0] and rnd() <= CH_STUDENT_CHALLENGE:
            num_st = rndint(NUM_STUD_CHALLENGERS[0], min(NUM_STUD_CHALLENGERS[1], n_can_join))
            t = _('Young men: "Master {}! We want to learn kung-fu. Please show us your '
                  'skill!"').format(tr_fighter_name(p.name.split()[0]))
            p.show(t)
            p.log(_('Is approached by a group of potential students.'))
            p.pak()
            students = fighter_factory.new_opponent(
                lv=rndint(*LV_STUD_CHALLENGERS), n=num_st, rand_atts_mode=0
            )
            if p.fight(students[0], en_allies=students[1:], hide_stats=False, items_allowed=False):
                t = _("Young men: \"Thank you Master, now we see that you're very strong! Please "
                      'teach us to be strong too!"')
                p.show(t)
                p.add_students(num_st)
            else:
                p.show(_('Young men: "Sorry, Master, we\'ll learn kung-fu elsewhere."'))
            p.pak()
        else:
            p.show(
                _('Young man: "Master {}! Please accept me as your student!"').format(
                    tr_fighter_name(p.name.split()[0])
                )
            )
            p.log(_('Is approached by a potential student.'))
            if p.is_human:
                choice = yn(_('Accept the young man?'))
            else:
                choice = True
            if choice:
                p.add_students(1)



