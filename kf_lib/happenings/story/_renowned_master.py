from ._base_story import BaseStory
from kf_lib.actors import fighter_factory


class RenownedMasterStory(BaseStory):
    min_level = 14
    max_level = 16

    def intro(self):
        g, p = self.game, self.player
        g.cls()
        name = g.get_new_name(prefix='Master')
        b = self.boss = fighter_factory.new_master_challenger(p.level, name)
        g.register_fighter(b)
        t = (
            f'{b.name}, a renowned master of {b.style.name} kung-fu from a remote province, '
            f'comes to {g.town_name} and stays at a local tavern.'
        )
        g.show(t)
        g.pak()

    def reward(self):
        p = self.player
        p.add_accompl('Renowned Master')
        t = (
            f'Having defeated such a strong opponent, {p.name} gained an important insight into '
            f'his own fighting technique.'
        )
        p.show(t)
        p.choose_tech_to_upgrade()

    def scene1(self):
        g, p, b = self.game, self.player, self.boss
        t = (
            f'{p.name} meets {b.name}. '
            f'\n{b.name}: "I feel that I have reached perfection in my kung-fu, {b.style.name}. '
            f'I have been looking for a worthy opponent for a very, very long time. I will be '
            f'honored to test your famous {p.style.name} kung-fu."'
        )
        g.show(t)
        p.log(f'Challenged by {b.name}.')
        g.pak()
        if p.fight(b, environment_allowed=False, items_allowed=False):
            t = (
                f'{b.name}: "Indeed remarkable! What excellent skill. I thank you for showing me '
                f'that I still have something to learn."'
            )
            g.show(t)
            self.reward()
        else:
            g.show(f'{b.name}: "I am disappointed - yet again."')
        self.end()
        g.pak()
