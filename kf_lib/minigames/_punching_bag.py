"""Punching Bag: one minute of fight time to hit a bag as hard as you can.

The bag never fights back, dodges or blocks, so the round is about choosing
strong, affordable moves, managing stamina and qi, and staying in range (heavy
pushes swing the bag away). The fighter has a fixed level, so records compare
like with like; the best damage is kept as a record.
"""
from kf_lib.actors import fighter_factory
from kf_lib.actors.fighter import Fighter
from kf_lib.fighting.fight._base_fight import TIME_TO_SEC_DIVISOR
from kf_lib.fighting.fight._normal_fight import NormalFight
from kf_lib.i18n import _, tr_name, tr_style_name
from kf_lib.kung_fu import styles
from kf_lib.ui import (
    MUSIC,
    cls,
    fight_music,
    pak,
    play_music,
    play_sound,
    rprint,
    style,
    yn,
)
from . import _records


BAG_NAME = 'Punching Bag'
BAG_HP = 9999  # far more than a round can take: the bag is never knocked out
FIGHTER_LEVEL = 10
ROUND_SECONDS = 60
RECORDS = 'bag'


class PunchingBag(Fighter):
    """Takes every hit: no turns (the fight never queues it), no dodging or
    blocking, no statuses, no bleeding or gasping, no knock-out."""

    is_living = False

    def __init__(self):
        super().__init__(
            BAG_NAME, styles.NO_STYLE.name, 1, atts_tuple=(1, 1, 1, 1),
            tech_names=[], move_names=[],
        )

    def prepare_for_fight(self):
        super().prepare_for_fight()
        self.hp_max = self.hp = BAG_HP
        self.toughness = 0
        self.dam_reduc = 0.0

    def calc_dfs(self):
        self.to_dodge = self.to_block = 0
        self.dfs_pwr = 0

    def take_damage(self, dam):
        # only an instant knock-out takes all of a bag's HP; a bag just swings
        super().take_damage(min(dam, self.hp - 1))

    # a bag doesn't fall, lose balance, get stunned, shocked or slowed down
    def cause_fall(self):
        pass

    def cause_off_balance(self, brief=False):
        pass

    def cause_shock(self):
        pass

    def cause_slow_down(self):
        pass

    def cause_stun(self):
        pass

    def try_counter(self):
        pass

    def say_prefight_quote(self):
        return False

    def say_win_quote(self):
        pass


class BagRound(NormalFight):
    """A timed NormalFight against the bag; the score is the HP it lost."""

    TIME_LIMIT = ROUND_SECONDS * TIME_TO_SEC_DIVISOR

    def __init__(self, fighter, bag):
        self.bag = bag
        super().__init__(
            [fighter], [bag], environment_allowed=False, items_allowed=False
        )

    @property
    def damage(self):
        return BAG_HP - self.bag.hp

    def queue(self, f, i):
        if f is not self.bag:  # the bag never takes a turn
            super().queue(f, i)

    def handle_prefight_quote(self):
        pass

    def handle_time_limit_exceeded(self):
        pass  # the round just ends; nobody is knocked out

    def get_turn_note(self):
        seconds = max(0, round((self.time_limit - self.timer) / TIME_TO_SEC_DIVISOR))
        clock = f'{seconds // 60}:{seconds % 60:02}'
        return '   ' + _('time left: {t}').format(t=clock)

    def play_end_jingle(self):
        play_music(None)
        play_sound('gong_clash')

    def show_win_message(self, who_shows_ascii=None, alternative_printing_fn=None):
        self.cls()
        fs = self.main_player.fight_stats
        lines = [
            style(_('Time!'), 'bold yellow'),
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


def play_round(fighter):
    """One round; return the damage dealt."""
    with fight_music(MUSIC['practice']):
        return BagRound(fighter, PunchingBag()).damage


def _record_text(record):
    return _('{dam} damage ({name}, {style})').format(
        dam=_records.get_score(record, 'damage'),
        name=record.get('name', '?'),
        style=tr_style_name(str(record.get('style', '?'))),
    )


def update_record(fighter, damage):
    old = _records.get_records(RECORDS).get('best')
    if damage > _records.get_score(old, 'damage'):
        _records.save_record(
            RECORDS,
            'best',
            {
                'damage': damage,
                'name': fighter.name,
                'style': fighter.style.public_name,
            },
        )
        rprint(style(_(' New record!'), 'bold green'))
    elif old:
        rprint(_(' Record: {record}').format(record=_record_text(old)))


def play_punching_bag():
    play_music(MUSIC['practice'])
    cls()
    rprint(_(' ***Welcome to the [bold]Punching Bag[/bold]***'))
    rprint(
        _(' Hit the bag as hard as you can in {sec} seconds of fight time.').format(
            sec=ROUND_SECONDS
        )
    )
    rprint(
        _(' The bag never fights back. Your fighter is level {lv}.').format(
            lv=FIGHTER_LEVEL
        )
    )
    old = _records.get_records(RECORDS).get('best')
    if old:
        rprint(_(' Record: {record}').format(record=_record_text(old)))
    pak()
    fighter = fighter_factory.new_custom_hcf(level=FIGHTER_LEVEL)
    while True:
        damage = play_round(fighter)
        update_record(fighter, damage)
        if not yn(_('Another round?')):
            break
