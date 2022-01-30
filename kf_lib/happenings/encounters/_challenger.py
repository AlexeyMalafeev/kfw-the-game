import random


from . import BaseEncounter, Guaranteed
from ._utils import check_scary_fight, set_up_weapon_fight
from ...utils.utilities import rnd


CH_CHALLENGER_ARMED = 0.3
CH_CHALLENGER_FRIEND = 0.1
ENC_CH_CHALLENGER = 0.07


class Challenger(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.c = None
        self.c_master = None
        super().__init__(player, check_if_happens)

    def check_if_happens(self):
        return not self.p.is_master and rnd() <= ENC_CH_CHALLENGER

    def run(self):
        p = self.player
        color = random.choice((
            '',
            'a lot ',
            'hands-down ',
            'much ',
            'simply ',
            'undoubtedly ',
            'way ',
        ))
        school_name, school_members = p.get_random_other_school()
        c = self.c = random.choice(school_members)
        self.c_master = p.game.masters[school_name]

        rank = school_members.index(c) + 1
        t = f'{c.name}, number {rank} in the {school_name} school, stops {p.name} in the street ' \
            f'and yells: "My kung-fu is {color}better than yours!!"'
        p.show(t)
        p.log(f"Challenged by {c.name}, number {rank} in the {c.style.name} school.")
        opp_strength = p.get_rel_strength(c)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, ratio=opp_strength[0]):
            if rnd() <= CH_CHALLENGER_ARMED:
                set_up_weapon_fight(p, c)
            self.do_fight()
        else:
            p.log("Chooses to ignore the challenge.")

    def do_fight(self):
        p, c = self.p, self.c
        p.fight(c, items_allowed=False)
        if rnd() <= CH_CHALLENGER_FRIEND * p.challenger_friend_mult and c not in p.friends:
            p.show('{}: "That was a good fight!\nLet\'s be friends!"'.format(c.name))
            p.add_friend(self.c)
            p.pak()
        luck = p.check_luck()
        if luck == 1:
            p.show(f'{p.name}: "I can learn something from this fight.')
            p.learn_move_from(c)
        elif luck == -1:
            master = self.c_master
            p.show(f'Suddenly, {c.name}\'s master appears!')
            p.show(f'{master.name}: "How dare you belittle the kung-fu I teach? '
                   'You will pay for this!"')
            p.fight(master, items_allowed=False)


class GChallenger(Guaranteed, Challenger):
    pass
