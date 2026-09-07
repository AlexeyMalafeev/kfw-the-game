import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.things import items
from kf_lib.utils import rndint
from ._base_story import BaseStory


class WrongPouchStory(BaseStory):
    """A pickpocket steals from the hero — and turns out to have stolen from two
    gangs' fences on the same day. The den erupts into a free-for-all over the
    loot pile. Comedy required."""

    min_level = 4
    max_level = 8

    money_stolen = (30, 150)
    num_thugs = (2, 3)

    def __init__(self, g, state=None, player=None, boss=None):
        # not saved mid-story; 0 is a safe fallback after loading
        self.stolen = 0
        super().__init__(g, state=state, player=player, boss=boss)

    def intro(self):
        g, p = self.game, self.player
        g.cls()
        self.stolen = 0
        if p.money:
            self.stolen = min(rndint(*self.money_stolen), p.money)
            p.money -= self.stolen
        t = (
            f'A nimble figure bumps into {p.name}, apologizes profusely, and disappears '
            f'into the crowd. A moment later {p.name} realizes the money pouch is gone. '
            f'"{self.stolen} coins! My {self.stolen} coins!"'
        )
        g.show(t)
        g.pak()
        p.log(f'Is pickpocketed of {self.stolen} coins.')

    def scene1(self):
        p = self.player
        thief = fighter_factory.new_thief()
        fences = fighter_factory.new_gambler(), fighter_factory.new_gambler()
        thugs = fighter_factory.new_thug(n=rndint(*self.num_thugs))
        if not isinstance(thugs, list):
            thugs = [thugs]
        f1, f2 = fences
        t = (
            f'{p.name} chases the pickpocket into a shady den... and freezes in the '
            f'doorway. The thief has had a busy day: he also stole from TWO gang fences, '
            f'and both gangs are already here. A pile of pouches lies on the table.\n'
            f'{f1.name}: "That one\'s mine! I know my own pouch!"\n'
            f'{f2.name}: "Yours? YOURS?! You couldn\'t tell a pouch from a potato!"\n'
            f'Thief: "Gentlemen, gentlemen, let\'s be civilized about this—"\n'
            f'{p.name}: "Hey! One of those is MINE!"\n'
            f'Everyone looks at everyone. Someone grabs the whole pile. Bad idea.'
        )
        p.show(t)
        p.log('Finds the pickpocket... and two angry fences... and their thugs.')
        p.pak()
        crowd = [thief, f1, f2] + thugs
        if fight.free_for_all([p] + crowd):
            item = items.get_random_item()
            p.show(
                f'{p.name} climbs out of the pile of bodies, pockets {self.stolen} coins '
                f'("EXACTLY mine, I counted"), and also grabs {item} from the table. '
                f'Finders keepers!'
            )
            p.log('Wins the den brawl and recovers the stolen money.')
            p.earn_money(self.stolen)
            p.obtain_item(item)
            p.add_accompl('Pouch Justice')
        else:
            p.show(
                f'{p.name} wakes up in the alley behind the den. The pouches are gone. '
                f'So is everyone. Even the table is gone.'
            )
            p.log('Is knocked out in the den brawl. The money is gone for good.')
        p.pak()
        self.end()
