import random

from kf_lib.i18n import _, tr_fighter_name, tr_style_name
from kf_lib.utils import rnd
from ._base_encounter import BaseEncounter, Guaranteed
from ._utils import check_scary_fight, set_up_weapon_fight


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
            _('a lot '),
            _('hands-down '),
            _('much '),
            _('simply '),
            _('undoubtedly '),
            _('way '),
        ))
        school_name, school_members = p.get_random_other_school()
        c = self.c = random.choice(school_members)
        self.c_master = p.game.masters[school_name]

        rank = school_members.index(c) + 1
        t = _(
            '{name}, number {rank} in the {school} school, stops {pname} in the street '
            'and yells: "My kung-fu is {color}better than yours!!"'
        ).format(
            name=tr_fighter_name(c.name),
            rank=rank,
            school=tr_style_name(c.style.public_name),
            pname=tr_fighter_name(p.name),
            color=color,
        )
        p.show(t)
        p.log(
            _('Challenged by {name}, number {rank} in the {school} school.').format(
                name=tr_fighter_name(c.name),
                rank=rank,
                school=tr_style_name(c.style.public_name),
            )
        )
        opp_strength = p.get_rel_strength(c)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
            if rnd() <= CH_CHALLENGER_ARMED:
                set_up_weapon_fight(p, c)
            self.do_fight()
        else:
            p.log(_("Chooses to ignore the challenge."))

    def do_fight(self):
        p, c = self.p, self.c
        win = p.fight(c, items_allowed=False)
        if rnd() <= CH_CHALLENGER_FRIEND * p.challenger_friend_mult and c not in p.friends:
            p.show(
                _('{}: "That was a good fight!\nLet\'s be friends!"').format(
                    tr_fighter_name(c.name)
                )
            )
            p.add_friend(self.c)
            p.pak()
        if win:
            luck = p.check_luck()
            if luck == 1:
                p.show(_('{name}: "I can learn something from this fight."').format(
                    name=tr_fighter_name(p.name)
                ))
                p.pak()
                p.learn_move_from(c)
            elif luck == -1:
                master = self.c_master
                p.show(
                    _('Suddenly, {name}\'s master appears!').format(
                        name=tr_fighter_name(c.name)
                    )
                )
                p.show(
                    _('{name}: "How dare you belittle the kung-fu I teach? '
                      'You will pay for this!"').format(name=tr_fighter_name(master.name))
                )
                p.pak()
                p.fight(master, items_allowed=False)


class GChallenger(Guaranteed, Challenger):
    pass
