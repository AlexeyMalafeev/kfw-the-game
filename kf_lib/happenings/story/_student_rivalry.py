import random

from kf_lib.fighting import fight
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.ui import menu
from kf_lib.utils import rnd
from ._base_story import BaseStory


# constants
MIN_STUDENTS_FOR_RIVALRY = 2
CH_DUEL_ANYWAY = 0.25
CH_DUEL_WINNER_LV_UP = 0.5
DUEL_REP = 2
SPAR_WIN_REP = 3
SPAR_LOSS_REP = -2
DISOBEYED_REP = -1

DUEL, SPAR, FORBID = 'duel', 'spar', 'forbid'


class StudentRivalryStory(BaseStory):
    """Two students quarrel over who is the master's best. The master decides:
    let them duel, spar them both, or forbid the whole thing."""

    min_level = 11
    max_level = 20

    def test(self, player):
        p = player
        return (
            super().test(p)
            and p.is_master
            and p.students >= MIN_STUDENTS_FOR_RIVALRY
        )

    def intro(self):
        g, p = self.game, self.player
        g.cls()
        t = (
            _(
                'Tension is brewing in {school}: two students keep arguing about '
                'who is {p_name}\'s best. Yesterday\'s shouting match ended with a '
                'broken bench.'
            ).format(school=p.new_school_name, p_name=tr_fighter_name(p.name))
        )
        g.show(t)
        g.pak()

    @staticmethod
    def _duel(p, s1, s2):
        p.show(
            _(
                '{s1_name} and {s2_name} bow to each other — and explode into motion!'
            ).format(s1_name=tr_fighter_name(s1.name), s2_name=tr_fighter_name(s2.name))
        )
        if fight.fight(s1, s2):
            winner, loser = s1, s2
        else:
            winner, loser = s2, s1
        p.show(
            _(
                '{winner} wins the duel. {loser} bows, gritting his teeth.'
            ).format(
                winner=tr_fighter_name(winner.name), loser=tr_fighter_name(loser.name)
            )
        )
        p.log(
            _('{winner} defeats {loser} in a students\' duel.').format(
                winner=tr_fighter_name(winner.name), loser=tr_fighter_name(loser.name)
            )
        )
        if rnd() <= CH_DUEL_WINNER_LV_UP:
            winner.level_up()
            p.show(
                _('The victory does {winner} good — he visibly improves!').format(
                    winner=tr_fighter_name(winner.name)
                )
            )
        return winner

    def scene1(self):
        g, p = self.game, self.player
        s1, s2 = random.sample(g.schools[p.new_school_name], 2)
        t = (
            _(
                '{s1_name} and {s2_name} stand before {p_name}, fists clenched. Each '
                'demands to be recognized as the master\'s best student. The whole '
                'school holds its breath, waiting for the master\'s word.'
            ).format(
                s1_name=tr_fighter_name(s1.name),
                s2_name=tr_fighter_name(s2.name),
                p_name=tr_fighter_name(p.name),
            )
        )
        p.show(t)
        p.log(_('Has to settle a rivalry between two students.'))
        if p.is_human:
            choice = menu(
                [
                    (_('Let them duel — may the better fighter win'), DUEL),
                    (_('"Enough! You will both spar ME."'), SPAR),
                    (_('Forbid the duel and send them back to training'), FORBID),
                ],
                title=_('{p_name}\'s decision:').format(p_name=tr_fighter_name(p.name)),
            )
        else:
            choice = random.choice((DUEL, SPAR, FORBID))
        if choice == DUEL:
            self._duel(p, s1, s2)
            p.gain_rep(DUEL_REP)
        elif choice == SPAR:
            if p.spar(s1, en_allies=[s2], hide_stats=False):
                p.show(
                    _(
                        '{s1_name} and {s2_name} lie on the ground, groaning and '
                        'grinning. {s1_name}: "The master is the master!"'
                    ).format(
                        s1_name=tr_fighter_name(s1.name),
                        s2_name=tr_fighter_name(s2.name),
                    )
                )
                p.log(_('Beats both quarreling students in a spar.'))
                p.gain_rep(SPAR_WIN_REP)
            else:
                p.show(
                    _(
                        '{p_name} wipes the blood off his lip. The students look '
                        'impressed... and a little too pleased.'
                    ).format(p_name=tr_fighter_name(p.name))
                )
                p.log(_('Loses a spar to his own students.'))
                p.gain_rep(SPAR_LOSS_REP)
        else:  # FORBID
            if rnd() <= CH_DUEL_ANYWAY:
                p.show(
                    _('That night, the two sneak out to the backyard and duel anyway...')
                )
                self._duel(p, s1, s2)
                p.gain_rep(DISOBEYED_REP)
            else:
                p.show(_('The students bow and disperse. Order is kept — for now.'))
                p.log(_('Forbids the students\' duel.'))
        p.pak()
        self.end()
