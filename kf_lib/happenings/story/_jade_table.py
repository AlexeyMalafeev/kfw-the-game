import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.i18n import _, tr_fighter_name
from kf_lib.utils import rndint
from ._base_story import BaseStory


class JadeTableStory(BaseStory):
    """A sit-down between crime bosses at the Jade Table restaurant explodes into
    a group free-for-all: the hero alone vs each boss with his bodyguards."""

    min_level = 9
    max_level = 13

    num_bosses = 3
    num_bodyguards = (1, 2)
    reputation_reward = 30

    def intro(self):
        g = self.game
        g.cls()
        t = _(
            'Lately, the streets of {town} whisper about the underworld: the old '
            'balance between the crime bosses is breaking, and a bloody war seems '
            'inevitable. To prevent it, the elders of the underworld call for a sit-down '
            'at the Jade Table restaurant...'
        ).format(town=g.town_name)
        g.show(t)
        g.pak()
        name = g.get_new_name('Uncle')
        self.boss = b = fighter_factory.new_master_challenger(self._boss_base_lv(), name)
        g.register_fighter(b)

    def _boss_base_lv(self):
        # bosses are slightly below the hero's level: the melee is chaotic and
        # winnable (~20%), but only just
        return max(self.player.level - 2, 1)

    def scene1(self):
        p, b = self.player, self.boss
        t = (
            _(
                '{p_name} is approached by a polite gentleman with a scar: "{b_name} '
                'sends his regards. The sit-down at the Jade Table needs... outside '
                'muscle. Someone neutral, to keep things honest. The pay is good." '
                '{p_name} has heard the rumors — every boss coming to that table plans '
                'treachery. But the pay IS good.'
            ).format(p_name=tr_fighter_name(p.name), b_name=tr_fighter_name(b.name))
        )
        p.show(t)
        p.log(
            _('Is hired by {b_name} as muscle for the Jade Table sit-down.').format(
                b_name=tr_fighter_name(b.name)
            )
        )
        p.pak()

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            _(
                'The Jade Table restaurant, private room. Silk robes, gold teeth, cold '
                'smiles. {b_name} raises a cup: "To peace!" Everyone drinks. Nobody '
                'believes a word. {p_name} notices a bodyguard slowly reaching under '
                'the table...'
            ).format(b_name=tr_fighter_name(b.name), p_name=tr_fighter_name(p.name))
        )
        p.show(t)
        p.log(_('Attends the Jade Table sit-down.'))
        p.pak()

    def scene3(self):
        # the sit-down explodes into a group free-for-all
        g, p, b = self.game, self.player, self.boss
        t = _(
            'A knife flashes. A table is flipped. "TREACHERY!" — and in a heartbeat the '
            'private room turns into a battlefield, every boss for himself!'
        )
        p.show(t)
        p.log(_('The Jade Table sit-down explodes into a brawl.'))
        p.pak()
        groups = [[p]]
        bosses = [b] + [
            fighter_factory.new_master_challenger(
                self._boss_base_lv(), g.get_new_name(random.choice(('Boss', 'Madame')))
            )
            for _ in range(self.num_bosses - 1)
        ]
        for boss in bosses:
            guards = fighter_factory.new_bodyguard(n=rndint(*self.num_bodyguards))
            if not isinstance(guards, list):
                guards = [guards]
            groups.append([boss] + guards)
        if fight.group_free_for_all(groups):
            t = (
                _(
                    'When the dust settles, {p_name} stands alone among the broken '
                    'tables. The underworld of {town} has been decapitated in a single '
                    'evening. The town breathes a sigh of relief — and looks at '
                    '{p_name} with new respect.'
                ).format(p_name=tr_fighter_name(p.name), town=g.town_name)
            )
            p.show(t)
            p.log(_('Is the last one standing at the Jade Table.'))
            p.gain_rep(self.reputation_reward)
            p.add_accompl('Jade Table')
            g.crime_down()
            g.crime_down()
        else:
            p.show(
                _(
                    '{p_name} wakes up under a pile of broken furniture. The sit-down '
                    'is over, and so is the peace. {b_name} survives — and he remembers '
                    'who was supposed to "keep things honest"...'
                ).format(p_name=tr_fighter_name(p.name), b_name=tr_fighter_name(b.name))
            )
            p.log(_('Is knocked out at the Jade Table.'))
            p.enemies.append(b)  # the boss is already a registered fighter
            p.log(
                _('{b_name} is now {p_name}\' enemy.').format(
                    b_name=tr_fighter_name(b.name), p_name=tr_fighter_name(p.name)
                )
            )
            self.boss = None  # keep him registered as a persistent enemy
        p.pak()
        self.end()
