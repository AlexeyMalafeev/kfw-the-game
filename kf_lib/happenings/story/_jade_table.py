import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
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
        t = (
            f'Lately, the streets of {g.town_name} whisper about the underworld: the old '
            f'balance between the crime bosses is breaking, and a bloody war seems '
            f'inevitable. To prevent it, the elders of the underworld call for a sit-down '
            f'at the Jade Table restaurant...'
        )
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
            f'{p.name} is approached by a polite gentleman with a scar: "{b.name} sends his '
            f'regards. The sit-down at the Jade Table needs... outside muscle. Someone '
            f'neutral, to keep things honest. The pay is good." '
            f'{p.name} has heard the rumors — every boss coming to that table plans '
            f'treachery. But the pay IS good.'
        )
        p.show(t)
        p.log(f'Is hired by {b.name} as muscle for the Jade Table sit-down.')
        p.pak()

    def scene2(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            f'The Jade Table restaurant, private room. Silk robes, gold teeth, cold smiles. '
            f'{b.name} raises a cup: "To peace!" Everyone drinks. Nobody believes a word. '
            f'{p.name} notices a bodyguard slowly reaching under the table...'
        )
        p.show(t)
        p.log('Attends the Jade Table sit-down.')
        p.pak()

    def scene3(self):
        # the sit-down explodes into a group free-for-all
        g, p, b = self.game, self.player, self.boss
        t = (
            f'A knife flashes. A table is flipped. "TREACHERY!" — and in a heartbeat the '
            f'private room turns into a battlefield, every boss for himself!'
        )
        p.show(t)
        p.log('The Jade Table sit-down explodes into a brawl.')
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
                f'When the dust settles, {p.name} stands alone among the broken tables. '
                f'The underworld of {g.town_name} has been decapitated in a single evening. '
                f'The town breathes a sigh of relief — and looks at {p.name} with new respect.'
            )
            p.show(t)
            p.log('Is the last one standing at the Jade Table.')
            p.gain_rep(self.reputation_reward)
            p.add_accompl('Jade Table')
            g.crime_down()
            g.crime_down()
        else:
            p.show(
                f'{p.name} wakes up under a pile of broken furniture. The sit-down is over, '
                f'and so is the peace. {b.name} survives — and he remembers who was '
                f'supposed to "keep things honest"...'
            )
            p.log('Is knocked out at the Jade Table.')
            p.enemies.append(b)  # the boss is already a registered fighter
            p.log(f'{b.name} is now {p.name}\' enemy.')
            self.boss = None  # keep him registered as a persistent enemy
        p.pak()
        self.end()
