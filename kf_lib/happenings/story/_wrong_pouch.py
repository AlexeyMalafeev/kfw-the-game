import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name
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
    savable_atts = ('stolen',)

    def __init__(self, g, state=None, player=None, boss=None):
        # default for saves from before story atts were persisted
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
            _('A nimble figure bumps into {name}, apologizes profusely, and disappears '
              'into the crowd. A moment later {name} realizes the money pouch is gone. ')
            .format(name=tr_fighter_name(p.name))
            + ngettext('"{n} coin! My {n} coin!"', '"{n} coins! My {n} coins!"', self.stolen)
            .format(n=self.stolen)
        )
        g.show(t)
        g.pak()
        p.log(
            ngettext(
                'Is pickpocketed of {} coin.', 'Is pickpocketed of {} coins.', self.stolen
            ).format(self.stolen)
        )

    def scene1(self):
        p = self.player
        thief = fighter_factory.new_thief()
        fences = fighter_factory.new_gambler(), fighter_factory.new_gambler()
        thugs = fighter_factory.new_thug(n=rndint(*self.num_thugs))
        if not isinstance(thugs, list):
            thugs = [thugs]
        f1, f2 = fences
        t = _(
            '{p_name} chases the pickpocket into a shady den... and freezes in the '
            'doorway. The thief has had a busy day: he also stole from TWO gang fences, '
            'and both gangs are already here. A pile of pouches lies on the table.\n'
            '{f1_name}: "That one\'s mine! I know my own pouch!"\n'
            '{f2_name}: "Yours? YOURS?! You couldn\'t tell a pouch from a potato!"\n'
            'Thief: "Gentlemen, gentlemen, let\'s be civilized about this—"\n'
            '{p_name}: "Hey! One of those is MINE!"\n'
            'Everyone looks at everyone. Someone grabs the whole pile. Bad idea.'
        ).format(
            p_name=tr_fighter_name(p.name),
            f1_name=tr_fighter_name(f1.name),
            f2_name=tr_fighter_name(f2.name),
        )
        p.show(t)
        p.log(_('Finds the pickpocket... and two angry fences... and their thugs.'))
        p.pak()
        crowd = [thief, f1, f2] + thugs
        if fight.free_for_all([p] + crowd):
            item = items.get_random_item()
            p.show(
                ngettext(
                    '{name} climbs out of the pile of bodies, pockets {n} coin '
                    '("EXACTLY mine, I counted"), and also grabs {item} from the table. '
                    'Finders keepers!',
                    '{name} climbs out of the pile of bodies, pockets {n} coins '
                    '("EXACTLY mine, I counted"), and also grabs {item} from the table. '
                    'Finders keepers!',
                    self.stolen,
                ).format(
                    name=tr_fighter_name(p.name), n=self.stolen, item=tr_name(item)
                )
            )
            p.log(_('Wins the den brawl and recovers the stolen money.'))
            p.earn_money(self.stolen)
            p.obtain_item(item)
            p.add_accompl('Pouch Justice')
        else:
            p.show(
                _('{name} wakes up in the alley behind the den. The pouches are gone. '
                  'So is everyone. Even the table is gone.')
                .format(name=tr_fighter_name(p.name))
            )
            p.log(_('Is knocked out in the den brawl. The money is gone for good.'))
        p.pak()
        self.end()
