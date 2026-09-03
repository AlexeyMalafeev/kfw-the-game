import random

from kf_lib.actors import fighter_factory, quotes
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

# levels
LV_STUD_CHALLENGERS = (1, 3)
REQ_LV_MASTER_TRIAL = fighter_factory.MASTER_LV[0]

# money
MONEY_OPEN_SCHOOL = 1000

# numbers
NUM_STUD_CHALLENGERS = (2, 5)


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
            '{0} meets his master. \n{1}: "{0}, you are one of my best students. '
            "You have made a lot of progress in {2}. But you might be ready to found your own "
            "kung-fu school... "
            "Let's find that out!\"".format(p.name, m.name, p.style.name)
        )
        p.show(t)
        p.log("Is offered a trial to become a master.")
        opp_strength = p.get_rel_strength(m)
        if p.fight_or_not(opp_strength):
            if p.spar(m, hide_stats=False):
                p.show(f'{m.name}: "Yes, you ARE ready!"')
                p.add_friend(m)
                outlay = MONEY_OPEN_SCHOOL
                p.show(
                    "To open a martial arts school, {} needs to make the initial outlay of {} coins.".format(
                        p.name, outlay
                    )
                )
                p.pay(outlay)
                p.is_master = True
                p.log("Becomes a master and founds his own school.")
                p.set_stat("became_master", p.game.get_date())
                p.set_stat("became_master_at_lv", p.level)
                school = p.get_school()
                school.remove(p)
                for a_player in p.game.players:
                    a_player.refresh_school_rank()  # in case there are other players in the same school
                school_name = p.choose_school_name()
                p.game.schools[school_name] = []
                p.game.masters[school_name] = p
                p.new_school_name = school_name
            else:
                p.show(f'{m.name}: "No, you are not ready yet. Practice some more."')
            p.pak()



class SchoolBullying(BaseEncounter):
    def check_if_happens(self):
        p = self.p
        return not p.is_master and p.school_rank > 1 and rnd() <= ENC_CH_SCHOOL_BULLYING

    def run(self):
        p = self.player
        m = self.player.get_master()
        t = f"""{p.name} is bullied at his school while {m.name} is away."""
        p.show(t)
        p.log("Is bullied at his school.")
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
        return not p.is_master and p.school_rank > 1 and rnd() <= ((len(p.get_school()) - 1) / 100)

    def run(self):
        p = self.player
        m = self.player.get_master()
        t = '''{0} meets his master.
{1}: "{0}, you have been practicing hard. It is now time to test your kung-fu!"'''.format(
            p.name, m.name
        )
        p.show(t)
        p.log("Is offered a trial at his school.")
        school = p.get_school()
        opp = school[p.school_rank - 2]  # adjusts for Python indexing and skips self
        opp_strength = p.get_rel_strength(opp)
        if p.fight_or_not(opp_strength):
            if rnd() < CH_SCHOOL_CHALLENGER_ARMED:
                p.arm_normal()
                opp.arm_normal()
            if p.spar(opp, hide_stats=False):
                school.remove(p)
                school.insert(
                    p.school_rank - 2, p
                )  # adjusts for Python indexing and skips defeated fighter
                p.refresh_school_rank()
                if p.school_rank > 1:
                    t = (
                        '{}: "{}, I can see that you have mastered some aspects of {}. However, you must keep '
                        'practicing as you still have a long way to go."'.format(
                            m.name, p.name, p.style.name
                        )
                    )
                    p.show(t)
                else:
                    # t = ('{}: "Well done, {}. Now it is time you learned the secret technique of our school, '
                    #      '"{}".'.format(m.name, p.name, m.style.tech.name))
                    t = f'{m.name}: "Well done, {p.name}."'
                    p.show(t)
                    # p.learn_tech(m.style.tech.name)
            else:
                react = random.choice(quotes.MASTER_CRITICISM)
                p.show(f"{m.name}: {react}")
            p.pak()



class Students(BaseEncounter):
    def check_if_happens(self):
        return (
            self.p.is_master
            and self.p.students < self.p.game.MAX_NUM_STUDENTS
            and rnd() <= min(self.p.get_fame(), ENC_CH_STUDENT)
        )

    def run(self):
        p = self.player
        n_can_join = p.game.MAX_NUM_STUDENTS - p.students
        if n_can_join >= NUM_STUD_CHALLENGERS[0] and rnd() <= CH_STUDENT_CHALLENGE:
            num_st = rndint(NUM_STUD_CHALLENGERS[0], min(NUM_STUD_CHALLENGERS[1], n_can_join))
            t = '''Young men: "Master {}! We want to learn kung-fu. Please show us your skill!"'''.format(
                p.name.split()[0]
            )
            p.show(t)
            p.log("Is approached by a group of potential students.")
            p.pak()
            students = fighter_factory.new_opponent(
                lv=rndint(*LV_STUD_CHALLENGERS), n=num_st, rand_atts_mode=0
            )
            if p.fight(students[0], en_allies=students[1:], hide_stats=False, items_allowed=False):
                t = ("Young men: \"Thank you Master, now we see that you're very strong! Please "
                     'teach us to be strong too!"')
                p.show(t)
                p.add_students(num_st)
            else:
                p.show('Young men: "Sorry, Master, we\'ll learn kung-fu elsewhere."')
            p.pak()
        else:
            p.show(
                'Young man: "Master {}! Please accept me as your student!"'.format(
                    p.name.split()[0]
                )
            )
            p.log("Is approached by a potential student.")
            if p.is_human:
                choice = yn("Accept the young man?")
            else:
                choice = True
            if choice:
                p.add_students(1)



