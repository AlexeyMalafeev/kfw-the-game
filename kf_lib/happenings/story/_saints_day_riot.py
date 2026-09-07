import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
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
            f'{g.town_name} is preparing for the Saint\'s Day festival — the one day of the '
            f'year when all work stops, wine flows like water, and the town\'s kung-fu '
            f'schools show off their students. The air smells of roast duck and trouble...'
        )
        g.show(t)
        g.pak()

    def scene1(self):
        p = self.player
        p.show(
            f'The Saint\'s Day festival is in full swing. Lanterns, drums, wine... '
            f'Students of rival schools are already measuring each other with long looks.'
        )
        p.log('Enjoys the Saint\'s Day festival.')
        if rnd() < p.drink_with_drunkard:
            p.show(f'{p.name} cannot resist the free wine. It would be rude not to, right?')
            p.drink()
            p.gain_rep(self.rep_pen_drunk)
        else:
            p.show(f'{p.name} decides to stay sober. Just in case.')
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
            f'It starts with a spilled jar of wine and an old grudge. A punch is thrown, '
            f'then another — and suddenly the whole festival square is one giant brawl! '
            f'{p.name} is right in the middle of it.'
        )
        p.show(t)
        p.log('Gets caught in the Saint\'s Day riot.')
        p.pak()
        if fight.free_for_all([p] + rioters):
            p.show(
                f'When the dust settles, {p.name} is the only one still standing in the '
                f'square. Somebody in the crowd starts a slow clap...'
            )
            p.gain_rep(self.rep_reward_riot)
            p.add_accompl('Riot Survivor')
            p.log('Wins the Saint\'s Day riot.')
        else:
            p.log('Is knocked out in the Saint\'s Day riot.')
        p.pak()

    def scene3(self):
        # the aftermath: somebody must be blamed
        g, p = self.game, self.player
        p.show(
            f'The morning after, {g.town_name} counts the broken stalls and broken noses. '
            f'The elders demand that someone answer for the riot. All eyes turn to '
            f'{p.name}...'
        )
        p.log('Is blamed for the Saint\'s Day riot.')
        if not p.is_human or g.yn('Take responsibility for the riot?'):
            if p.check_money(self.fine_amount):
                p.pay(self.fine_amount)
                p.show(
                    f'{p.name} pays {self.fine_amount} coins for the damages. Honor is '
                    f'kept, if not the money.'
                )
                p.log(f'Pays {self.fine_amount} coins for the riot damages.')
            else:
                p.show(
                    f'{p.name} has no money for the damages and has to endure a public '
                    f'scolding by the elders.'
                )
                p.log('Is publicly scolded by the elders.')
            p.gain_rep(self.rep_pen_responsibility)
        else:
            masters = [m for m in g.masters.values() if m.style.name != p.style.name]
            if masters:
                scapegoat = random.choice(masters)
                p.show(
                    f'{p.name}: "It was the {scapegoat.style.public_name} school! Their '
                    f'students started it!" The elders nod — they never liked those guys '
                    f'anyway.'
                )
                p.log(f'Pins the blame for the riot on the {scapegoat.style.public_name} school.')
                p.gain_rep(self.rep_reward_blame)
                p.enemies.append(scapegoat)  # masters are already registered fighters
                p.log(f'{scapegoat.name} is now {p.name}\' enemy.')
                p.show(
                    f'{scapegoat.name} hears about this and vows to make {p.name} pay for '
                    f'the slander.'
                )
            else:
                p.gain_rep(self.rep_pen_responsibility)
        p.pak()
        self.end()
