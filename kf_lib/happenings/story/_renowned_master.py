from ._base_story import BaseStory
from kf_lib.actors import fighter_factory
from kf_lib.i18n import _, tr_fighter_name, tr_style_name


class RenownedMasterStory(BaseStory):
    min_level = 14
    max_level = 16

    def intro(self):
        g, p = self.game, self.player
        g.cls()
        name = g.get_new_name(prefix='Master')
        b = self.boss = fighter_factory.new_master_challenger(p.level, name)
        g.register_fighter(b)
        t = _(
            '{name}, a renowned master of {style} kung-fu from a remote province, '
            'comes to {town} and stays at a local tavern.'
        ).format(
            name=tr_fighter_name(b.name),
            style=tr_style_name(b.style.public_name),
            town=g.town_name,
        )
        g.show(t)
        g.pak()

    def reward(self):
        p = self.player
        p.add_accompl('Renowned Master')
        t = _(
            'Having defeated such a strong opponent, {name} gained an important insight into '
            'his own fighting technique.'
        ).format(name=tr_fighter_name(p.name))
        p.show(t)
        p.choose_tech_to_upgrade()

    def scene1(self):
        g, p, b = self.game, self.player, self.boss
        t = _(
            '{p_name} meets {b_name}. '
            '\n{b_name}: "I feel that I have reached perfection in my kung-fu, {style}. '
            'I have been looking for a worthy opponent for a very, very long time. I will be '
            'honored to test your famous {p_style} kung-fu."'
        ).format(
            p_name=tr_fighter_name(p.name),
            b_name=tr_fighter_name(b.name),
            style=tr_style_name(b.style.public_name),
            p_style=p.get_displayed_style_name(),
        )
        p.show(t)
        p.log(_('Challenged by {}.').format(tr_fighter_name(b.name)))
        p.pak()
        if p.fight(b, environment_allowed=False, items_allowed=False):
            t = _(
                '{name}: "Indeed remarkable! What excellent skill. I thank you for showing me '
                'that I still have something to learn."'
            ).format(name=tr_fighter_name(b.name))
            p.show(t)
            self.reward()
        else:
            p.show(_('{name}: "I am disappointed - yet again."').format(
                name=tr_fighter_name(b.name)
            ))
        self.end()
        p.pak()
