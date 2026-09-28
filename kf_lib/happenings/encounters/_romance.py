import random

from kf_lib.actors import fighter_factory
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.utils import rnd, rndint
from ._base_encounter import BaseEncounter
from ._utils import check_scary_fight, get_escape_chance, try_escape


# encounter chances
ENC_CH_NEW_ROMANCE = 0.03
ENC_CH_ROMANTIC_DATE = 0.05
ENC_CH_JEALOUS_RIVAL = 0.02

SWEETHEART_LV_MOD = (-2, 2)  # sweetheart level = player level + this
RIVAL_LV_MOD = (0, 2)  # the jealous rival is at least the player's level
CH_RIVAL_BECOMES_ENEMY = 0.3
RIVAL_WIN_PROGRESS = 2
RIVAL_LOSS_PROGRESS = 3


class NewRomance(BaseEncounter):
    """Meet a potential love interest (only while not courting or married)."""

    def check_if_happens(self):
        p = self.p
        return p.sweetheart is None and rnd() <= ENC_CH_NEW_ROMANCE

    def run(self):
        p = self.player
        g = p.game
        # opposite-sex love interests only; p.gender is None in pre-gender saves
        gender = (
            random.choice(('f', 'm')) if p.gender is None
            else 'f' if p.gender == 'm' else 'm'
        )
        name = g.get_new_name(gender=gender)
        who = _('a young woman') if gender == 'f' else _('a young man')
        p.show(
            _(
                'While walking around town, {p_name} bumps into {who} — quite literally. '
                'After a moment of confusion, they get to talking. What a charming person! '
                'Turns out, {name} is also a martial artist.'
            ).format(
                p_name=tr_fighter_name(p.name), who=who, name=tr_fighter_name(name)
            )
        )
        p.log(_('Meets {name}.').format(name=tr_fighter_name(name)))
        p.show(_('Pursue the relationship?'))
        if not p.pursue_romance_or_not():
            p.show(
                _('{} politely says goodbye and walks away.').format(
                    tr_fighter_name(p.name)
                )
            )
            p.log(
                _('Decides not to pursue the relationship with {name}.').format(
                    name=tr_fighter_name(name)
                )
            )
            p.pak()
            return
        level = max(1, p.level + rndint(*SWEETHEART_LV_MOD))
        sw = fighter_factory.new_sweetheart(name, gender, level)
        g.register_fighter(sw)
        p.sweetheart = sw
        p.romance_progress = 1
        p.show(
            _('{p_name} and {name} agree to meet again.').format(
                p_name=tr_fighter_name(p.name), name=tr_fighter_name(name)
            )
        )
        p.log(
            _('A romance begins between {p_name} and {name}.').format(
                p_name=tr_fighter_name(p.name), name=tr_fighter_name(name)
            )
        )
        p.pak()


class RomanticDate(BaseEncounter):
    """A date while courting; raises the player's romance_progress."""

    def check_if_happens(self):
        p = self.p
        return (
            p.sweetheart is not None
            and not p.is_married
            and rnd() <= ENC_CH_ROMANTIC_DATE
        )

    def run(self):
        p = self.player
        sw = p.sweetheart
        p.show(
            _('{p_name} and {sw_name} go on a date. They talk about kung-fu, life '
              'and dreams for the future.').format(
                p_name=tr_fighter_name(p.name), sw_name=tr_fighter_name(sw.name)
            )
        )
        p.log(
            _('Goes on a date with {name}.').format(name=tr_fighter_name(sw.name))
        )
        p.romance_progress += rndint(1, 3)
        p.pak()


class JealousRival(BaseEncounter):
    """A rival suitor challenges the player to a duel while courting."""

    def check_if_happens(self):
        p = self.p
        return (
            p.sweetheart is not None
            and not p.is_married
            and rnd() <= ENC_CH_JEALOUS_RIVAL
        )

    def run(self):
        p = self.player
        g = p.game
        sw = p.sweetheart
        rival_gender = 'm' if sw.gender == 'f' else 'f'
        name = g.get_new_name(gender=rival_gender)
        level = max(1, p.level + rndint(*RIVAL_LV_MOD))
        r = fighter_factory.new_love_rival(name, rival_gender, level)
        p.show(
            _('{r_name} blocks {p_name}\'s way.'
              '\n{r_name}: "Stay away from {sw_name}! {sw_name} is mine! '
              'Let\'s settle this like martial artists!"').format(
                r_name=tr_fighter_name(r.name),
                p_name=tr_fighter_name(p.name),
                sw_name=tr_fighter_name(sw.name),
            )
        )
        p.log(
            _('Is challenged by a jealous rival, {name}.').format(
                name=tr_fighter_name(r.name)
            )
        )
        opp_strength = p.get_rel_strength(r)
        esc_chance = get_escape_chance(p)
        if p.fight_or_run(opp_strength, esc_chance) and not check_scary_fight(
            p, opp_strength[0]
        ):
            self.do_fight(r)
        else:
            try_escape(p, esc_chance)

    def do_fight(self, r):
        p = self.player
        sw = p.sweetheart
        if p.fight(r):
            p.show(
                _('{name}: "Curses! You are stronger than I thought..."').format(
                    name=tr_fighter_name(r.name)
                )
            )
            p.log(
                _('Defeats the jealous rival {r_name}; {sw_name} is impressed.').format(
                    r_name=tr_fighter_name(r.name), sw_name=tr_fighter_name(sw.name)
                )
            )
            p.romance_progress += RIVAL_WIN_PROGRESS
            if rnd() <= CH_RIVAL_BECOMES_ENEMY:
                p.show(
                    _('{name}: "You haven\'t seen the last of me!"').format(
                        name=tr_fighter_name(r.name)
                    )
                )
                p.add_enemy(r)
            p.pak()
        else:
            p.show(
                _('{r_name}: "Ha! And you call yourself a martial artist? '
                  'Stay away from {sw_name}!"').format(
                    r_name=tr_fighter_name(r.name), sw_name=tr_fighter_name(sw.name)
                )
            )
            p.log(
                _('Is beaten by the jealous rival {name}.').format(
                    name=tr_fighter_name(r.name)
                )
            )
            p.romance_progress -= RIVAL_LOSS_PROGRESS
            p.check_romance_breakup()
            p.pak()
