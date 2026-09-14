import random

from kf_lib.actors import fighter_factory
from kf_lib.utils import rnd, rndint
from ._base_encounter import BaseEncounter


# encounter chances
ENC_CH_NEW_ROMANCE = 0.03
ENC_CH_ROMANTIC_DATE = 0.05

SWEETHEART_LV_MOD = (-2, 2)  # sweetheart level = player level + this


class NewRomance(BaseEncounter):
    """Meet a potential love interest (only while not courting or married)."""

    def check_if_happens(self):
        p = self.p
        return p.sweetheart is None and rnd() <= ENC_CH_NEW_ROMANCE

    def run(self):
        p = self.player
        g = p.game
        gender = random.choice(('f', 'm'))
        name = g.get_new_name(gender=gender)
        who = 'a young woman' if gender == 'f' else 'a young man'
        p.show(
            f'While walking around town, {p.name} bumps into {who} — quite literally. '
            f'After a moment of confusion, they get to talking. What a charming person! '
            f'Turns out, {name} is also a martial artist.'
        )
        p.log(f'Meets {name}.')
        p.show('Pursue the relationship?')
        if not p.pursue_romance_or_not():
            p.show(f'{p.name} politely says goodbye and walks away.')
            p.log(f'Decides not to pursue the relationship with {name}.')
            p.pak()
            return
        level = max(1, p.level + rndint(*SWEETHEART_LV_MOD))
        sw = fighter_factory.new_sweetheart(name, gender, level)
        g.register_fighter(sw)
        p.sweetheart = sw
        p.romance_progress = 1
        p.show(f'{p.name} and {name} agree to meet again.')
        p.log(f'A romance begins between {p.name} and {name}.')
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
            f'{p.name} and {sw.name} go on a date. They talk about kung-fu, life '
            f'and dreams for the future.'
        )
        p.log(f'Goes on a date with {sw.name}.')
        p.romance_progress += rndint(1, 3)
        p.pak()
