"""Fights against the punching bag (kf_lib/actors/punching_bag.py).

BagFight is a NormalFight that never gives the bag a turn and ends with a
summary screen instead of a win message. TimedBagRound (the Punching Bag
mini-game) lasts a minute of fight time; BagPractice (the main game's State >
Moves > Punching Bag) lasts a number of moves and records nothing: no exp,
stats, move usage, injuries, gossip or accomplishments.
"""
from kf_lib.i18n import _, tr_name
from kf_lib.ui import MUSIC, fight_music, play_music, play_sound, style
from ._base_fight import TIME_TO_SEC_DIVISOR
from ._normal_fight import NormalFight


class BagFight(NormalFight):
    def __init__(self, fighter, bag):
        self.bag = bag
        super().__init__(
            [fighter], [bag], environment_allowed=False, items_allowed=False
        )

    @property
    def damage(self):
        """The HP the bag lost: the round's score."""
        return self.bag.hp_max - self.bag.hp

    def queue(self, f, i):
        if f is not self.bag:  # the bag never takes a turn
            super().queue(f, i)

    def handle_prefight_quote(self):
        pass

    def handle_time_limit_exceeded(self):
        pass  # the round just ends; nobody is knocked out

    def play_end_jingle(self):
        play_music(None)
        play_sound('gong_clash')

    def summary_title(self):
        raise NotImplementedError

    def show_win_message(self, who_shows_ascii=None, alternative_printing_fn=None):
        self.cls()
        fs = self.main_player.fight_stats
        lines = [
            style(self.summary_title(), 'bold yellow'),
            _('Damage: {dam}').format(dam=style(str(self.damage), 'bold red')),
            _('Strikes landed: {landed} of {thrown}').format(
                landed=fs['landed'], thrown=fs['thrown']
            ),
        ]
        if fs['max_blow']:
            lines.append(
                _('Hardest blow: {dam} ({move})').format(
                    dam=fs['max_blow'], move=tr_name(fs['max_blow_move'])
                )
            )
        lines.append(
            _('Criticals: {crits}, epics: {epics}').format(
                crits=fs['criticals'], epics=fs['epics']
            )
        )
        self.main_player.show('\n'.join(lines), align=False)

    # a bag fight is not a fight for the record (these act on players only)
    def give_exp(self):
        pass

    def handle_accompl(self):
        pass

    def handle_gossip(self):
        pass

    def handle_injuries(self):
        pass


class TimedBagRound(BagFight):
    """The Punching Bag mini-game's round: one minute of fight time."""

    ROUND_SECONDS = 60
    TIME_LIMIT = ROUND_SECONDS * TIME_TO_SEC_DIVISOR

    def get_turn_note(self):
        seconds = max(0, round((self.time_limit - self.timer) / TIME_TO_SEC_DIVISOR))
        clock = f'{seconds // 60}:{seconds % 60:02}'
        return '   ' + _('time left: {t}').format(t=clock)

    def summary_title(self):
        return _('Time!')


class BagPractice(BagFight):
    """A practice session of a set number of the fighter's moves."""

    def __init__(self, fighter, bag, moves):
        self.moves_total = moves
        self.moves_made = 0
        super().__init__(fighter, bag)

    def handle_move_done(self, f):
        self.moves_made += 1
        if self.moves_made >= self.moves_total:
            # the next turn starts later than now, so the session ends before it
            self.time_limit = self.timer + 1

    def get_turn_note(self):
        left = self.moves_total - self.moves_made
        return '   ' + _('moves left: {n}').format(n=left)

    def summary_title(self):
        return _('Practice over!')


def _new_bag():
    # imported here: kf_lib.actors.fighter imports this package at load time
    from kf_lib.actors.punching_bag import PunchingBag

    return PunchingBag()


def play_timed_bag_round(fighter):
    """One mini-game round; return the damage dealt."""
    with fight_music(MUSIC['practice']):
        return TimedBagRound(fighter, _new_bag()).damage


def practice_on_bag(fighter, moves):
    """A practice session; return the damage dealt."""
    with fight_music(MUSIC['practice']):
        return BagPractice(fighter, _new_bag(), moves).damage
