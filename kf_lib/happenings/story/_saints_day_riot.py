import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.i18n import _, ngettext, tr_fighter_name
from kf_lib.utils import rnd, rndint
from ._base_story import BaseStory


class SaintsDayRiotStory(BaseStory):
    """A town festival spirals into a huge free-for-all riot, and then the town
    looks for someone to blame."""

    min_level = 5
    max_level = 9

    fine_amount = 100
    num_brawlers = (2, 4)
    rep_pen_drunk = -3
    rep_pen_responsibility = -5
    rep_reward_blame = 3
    rep_reward_riot = 10

    def intro(self):
        g = self.game
        g.cls()
        t = (
            _('{town} is preparing for the Saint\'s Day festival — the one day of the '
              'year when all work stops, wine flows like water, and the town\'s kung-fu '
              'schools show off their students. The air smells of roast duck and '
              'trouble...')
        ).format(town=g.town_name)
        g.show(t)
        g.pak()

    def scene1(self):
        p = self.player
        p.show(
            _('The Saint\'s Day festival is in full swing. Lanterns, drums, wine... '
              'Students of rival schools are already measuring each other with long '
              'looks.')
        )
        p.log(_('Enjoys the Saint\'s Day festival.'))
        if rnd() < p.drink_with_drunkard:
            p.show(
                _('{name} cannot resist the free wine. It would be rude not to, '
                  'right?').format(name=tr_fighter_name(p.name))
            )
            p.drink()
            p.gain_rep(self.rep_pen_drunk)
        else:
            p.show(
                _('{name} decides to stay sober. Just in case.').format(
                    name=tr_fighter_name(p.name)
                )
            )
        p.pak()

    def scene2(self):
        # the riot
        g, p = self.game, self.player
        rioters = []
        schools = [s for s in g.schools.values() if s]
        random.shuffle(schools)
        for school in schools[:2]:
            members = [f for f in school if not f.is_player]
            rioters += random.sample(members, min(len(members), 2))
        rioters += [
            fighter_factory.new_brawler() for _ in range(rndint(*self.num_brawlers))
        ]
        t = (
            _('It starts with a spilled jar of wine and an old grudge. A punch is '
              'thrown, then another — and suddenly the whole festival square is one '
              'giant brawl! {name} is right in the middle of it.')
        ).format(name=tr_fighter_name(p.name))
        p.show(t)
        p.log(_('Gets caught in the Saint\'s Day riot.'))
        p.pak()
        if fight.free_for_all([p] + rioters):
            p.show(
                _('When the dust settles, {name} is the only one still standing in the '
                  'square. Somebody in the crowd starts a slow clap...').format(
                    name=tr_fighter_name(p.name)
                )
            )
            p.gain_rep(self.rep_reward_riot)
            p.add_accompl('Riot Survivor')
            p.log(_('Wins the Saint\'s Day riot.'))
        else:
            p.log(_('Is knocked out in the Saint\'s Day riot.'))
        p.pak()

    def scene3(self):
        # the aftermath: somebody must be blamed
        g, p = self.game, self.player
        p.show(
            _('The morning after, {town} counts the broken stalls and broken noses. '
              'The elders demand that someone answer for the riot. All eyes turn to '
              '{name}...').format(town=g.town_name, name=tr_fighter_name(p.name))
        )
        p.log(_('Is blamed for the Saint\'s Day riot.'))
        if not p.is_human or g.yn(_('Take responsibility for the riot?')):
            if p.check_money(self.fine_amount):
                p.pay(self.fine_amount)
                p.show(
                    ngettext(
                        '{name} pays {} coin for the damages. Honor is kept, if not '
                        'the money.',
                        '{name} pays {} coins for the damages. Honor is kept, if not '
                        'the money.',
                        self.fine_amount,
                    ).format(self.fine_amount, name=tr_fighter_name(p.name))
                )
                p.log(
                    ngettext(
                        'Pays {} coin for the riot damages.',
                        'Pays {} coins for the riot damages.',
                        self.fine_amount,
                    ).format(self.fine_amount)
                )
            else:
                p.show(
                    _('{name} has no money for the damages and has to endure a public '
                      'scolding by the elders.').format(name=tr_fighter_name(p.name))
                )
                p.log(_('Is publicly scolded by the elders.'))
            p.gain_rep(self.rep_pen_responsibility)
        else:
            masters = [m for m in g.masters.values() if m.style.name != p.style.name]
            if masters:
                scapegoat = random.choice(masters)
                p.show(
                    _('{name}: "It was the {style} school! Their students started it!" '
                      'The elders nod — they never liked those guys anyway.').format(
                        name=tr_fighter_name(p.name),
                        style=scapegoat.style.display_public_name,
                    )
                )
                p.log(
                    _('Pins the blame for the riot on the {style} school.').format(
                        style=scapegoat.style.display_public_name
                    )
                )
                p.gain_rep(self.rep_reward_blame)
                p.enemies.append(scapegoat)  # masters are already registered fighters
                p.log(
                    _('{master} is now {name}\' enemy.').format(
                        master=tr_fighter_name(scapegoat.name),
                        name=tr_fighter_name(p.name),
                    )
                )
                p.show(
                    _('{master} hears about this and vows to make {name} pay for '
                      'the slander.').format(
                        master=tr_fighter_name(scapegoat.name),
                        name=tr_fighter_name(p.name),
                    )
                )
            else:
                p.gain_rep(self.rep_pen_responsibility)
        p.pak()
        self.end()
