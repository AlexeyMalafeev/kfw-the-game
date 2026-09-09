import random

from kf_lib.fighting import fight
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
            f'Tension is brewing in {p.new_school_name}: two students keep arguing about '
            f'who is {p.name}\'s best. Yesterday\'s shouting match ended with a broken bench.'
        )
        g.show(t)
        g.pak()

    @staticmethod
    def _duel(p, s1, s2):
        p.show(f'{s1.name} and {s2.name} bow to each other — and explode into motion!')
        if fight.fight(s1, s2):
            winner, loser = s1, s2
        else:
            winner, loser = s2, s1
        p.show(f'{winner.name} wins the duel. {loser.name} bows, gritting his teeth.')
        p.log(f'{winner.name} defeats {loser.name} in a students\' duel.')
        if rnd() <= CH_DUEL_WINNER_LV_UP:
            winner.level_up()
            p.show(f'The victory does {winner.name} good — he visibly improves!')
        return winner

    def scene1(self):
        g, p = self.game, self.player
        s1, s2 = random.sample(g.schools[p.new_school_name], 2)
        t = (
            f'{s1.name} and {s2.name} stand before {p.name}, fists clenched. Each demands '
            f'to be recognized as the master\'s best student. The whole school holds its '
            f'breath, waiting for the master\'s word.'
        )
        p.show(t)
        p.log('Has to settle a rivalry between two students.')
        if p.is_human:
            choice = menu(
                [
                    ('Let them duel — may the better fighter win', DUEL),
                    ('"Enough! You will both spar ME."', SPAR),
                    ('Forbid the duel and send them back to training', FORBID),
                ],
                title=f'{p.name}\'s decision:',
            )
        else:
            choice = random.choice((DUEL, SPAR, FORBID))
        if choice == DUEL:
            self._duel(p, s1, s2)
            p.gain_rep(DUEL_REP)
        elif choice == SPAR:
            if p.spar(s1, en_allies=[s2], hide_stats=False):
                p.show(
                    f'{s1.name} and {s2.name} lie on the ground, groaning and grinning. '
                    f'{s1.name}: "The master is the master!"'
                )
                p.log('Beats both quarreling students in a spar.')
                p.gain_rep(SPAR_WIN_REP)
            else:
                p.show(
                    f'{p.name} wipes the blood off his lip. The students look impressed... '
                    f'and a little too pleased.'
                )
                p.log('Loses a spar to his own students.')
                p.gain_rep(SPAR_LOSS_REP)
        else:  # FORBID
            if rnd() <= CH_DUEL_ANYWAY:
                p.show('That night, the two sneak out to the backyard and duel anyway...')
                self._duel(p, s1, s2)
                p.gain_rep(DISOBEYED_REP)
            else:
                p.show('The students bow and disperse. Order is kept — for now.')
                p.log('Forbids the students\' duel.')
        p.pak()
        self.end()
