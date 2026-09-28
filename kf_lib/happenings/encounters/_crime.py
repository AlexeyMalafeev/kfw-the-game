import random

from kf_lib.actors import fighter_factory
from kf_lib.fighting import fight
from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name
from kf_lib.things import items
from kf_lib.utils import add_article, rnd, rndint
from ._base_encounter import BaseEncounter, Guaranteed
from ._utils import check_feeling_greedy, check_scary_fight, get_escape_chance, \
    try_enemy, try_escape


# constants
# encounter chances
ENC_CH_CRIMINAL = 0.03

# misc chances
CH_CONVICT_ARMED = 0.35
CH_POLICE_CHAOS = 0.25
CH_ROBBER_ARMED = 0.35
CH_ROBBER_ENEMY = 0.1
CH_ROBBERS_SQUABBLE = 0.25
CH_THIEF_ARMED = 0.3
CH_THIEF_ESCAPES = 0.3
CH_THIEF_TOUGH = 0.1
CH_THUG_ENEMY = 0.1

# lines
LINES_ROBBER = (
    _('Hey, I really need {} coins. Do you think you can help me out?'),
    _("If you don't give me {} coins, you'll need a doctor, and a good one!"),
    _('Hey you! This is my territory. Entering is free, but leaving in one piece costs {} coins.'),
    _('You know, I need {} coins to buy medicine for my sick grandma. Wanna share?'),
    _('It is important to share what you have with others. Pay {} coins and you are free to go.'),
)

# money
MONEY_CONVICT_REWARD_MULT = (10, 15, 20, 25, 30, 40)
MONEY_GIVE_ROBBERS = (40, 50, 60, 80, 100, 120, 130, 150, 180)
MONEY_SHOP_BREAKAGES = (30, 50, 70)
MONEY_THIEF_STEALS = (25, 50, 75, 100, 200)

# numbers
NUM_EXTORTERS = (2, 6)
NUM_GANG_WAR = (2, 3)
NUM_POLICE_CHAOS_GANG = (2, 3)
NUM_POLICE_VS_THUGS = (2, 4)
NUM_THUGS_VS_POLICE = (+1, +4)  # always more than the police
NUM_ROBBERS_CROWD = (5, 8)
NUM_ROBBERS_GROUP = (2, 4)

# reputation
REP_PEN_BREAK_NOT_PAY = -1


class Criminal(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.c = None
        self.allies = None
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= ENC_CH_CRIMINAL and self.p.game.criminals

    def run(self):
        p = self.player
        self.c = c = random.choice(p.game.criminals)
        p.show(
            _('{name} accidentally bumps into a wanted criminal, {c_name}.').format(
                name=tr_fighter_name(p.name), c_name=tr_fighter_name(c.name)
            )
        )
        p.log(_('Encounters a wanted criminal.'))
        opp_strength = p.get_rel_strength(c)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
            if c.check_lv(p.level + 1):
                self.allies = p.check_allies(1)
            if rnd() <= CH_CONVICT_ARMED:
                c.arm_robber()
                p.msg(_('The criminal pulls out a weapon!'))
            win = p.fight(c, self.allies)
            if win:
                self.reward()
                p.game.criminals.remove(c)
                p.game.unregister_fighter(c)
        else:
            p.log(_("Doesn't try to stop the criminal."))

    def reward(self):
        p = self.player
        c = self.c
        rew_mult = random.choice(MONEY_CONVICT_REWARD_MULT)
        reward = c.level * rew_mult
        rep_gain = c.level
        p.show(_('{} takes the criminal to the police.').format(tr_fighter_name(p.name)))
        # split the reward
        if self.allies:
            ally = self.allies[0]
            reward = round(reward / 2)
            rep_gain = round(rep_gain / 2)
            if ally.is_player:
                ally.gain_rep(rep_gain)
                ally.earn_reward(reward)
                ally.pak()
        p.gain_rep(c.level)
        p.earn_reward(reward)
        p.pak()



class Extorters(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.p.game.crime / 4

    def run(self):
        p = self.player
        num_en = rndint(*NUM_EXTORTERS)
        p.show(
            ngettext(
                "{name} sees {} man in a shop demanding 'protection' money.",
                "{name} sees {} men in a shop demanding 'protection' money.",
                num_en,
            ).format(num_en, name=tr_fighter_name(p.name))
        )
        p.log(
            ngettext(
                'Sees {} extorter in a shop.',
                'Sees {} extorters in a shop.',
                num_en,
            ).format(num_en)
        )
        en = fighter_factory.new_thug(n=num_en)
        for e in en:
            if random.choice((True, False, False)):
                e.arm_robber()
        opp_strength = p.get_rel_strength(*en)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
            p.check_help()
            p.gain_rep(num_en * 2)
            if p.fight(en[0], p.allies, en[1:]):
                p.game.crime_down()
                try_enemy(p, en[0], CH_THUG_ENEMY)
                if random.choice([True, True, False]):
                    item = items.get_random_item()
                    p.show(_('Shop owner: "Thank you, thank you young man!"'))
                    for pp in [p] + (p.allies if p.allies is not None else []):
                        if pp.is_player:
                            pp.show(
                                _(
                                    '{name} gets {item} from the grateful shop owner.'
                                ).format(
                                    name=tr_fighter_name(p.name), item=tr_name(item)
                                )
                            )
                            pp.obtain_item(item)
                else:
                    t = _(
                        'Shop owner: "Oh boy... You martial artists only know how to fight and break things! '
                        "Look what you've done to my shop! Who's gonna pay for the breakages?.."
                    )
                    p.show(t)
                    cost = random.choice(MONEY_SHOP_BREAKAGES)
                    if p.check_money(cost) and not check_feeling_greedy(p):
                        p.pay(cost)
                        p.show(
                            _('{name} pays {cost} c.').format(
                                name=tr_fighter_name(p.name), cost=cost
                            )
                        )
                    else:
                        p.gain_rep(REP_PEN_BREAK_NOT_PAY)
            else:
                p.show(_('Shop owner: "Are you hurt? I\'ll find a doctor..."'))
            p.pak()
        else:
            p.log(_('Looks the other way.'))



class GangWar(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 8

    def run(self):
        p = self.player
        num_a = rndint(*NUM_GANG_WAR)
        num_b = rndint(*NUM_GANG_WAR)
        p.show(
            _(
                '{name} walks right into a street war between two gangs, '
                '{num_a} against {num_b} — and both sides think {name} is with '
                'the enemy!'
            ).format(name=tr_fighter_name(p.name), num_a=num_a, num_b=num_b)
        )
        p.log(_('Gets caught in a gang war.'))
        gang_a = fighter_factory.new_thug(n=num_a)
        gang_b = fighter_factory.new_thug(n=num_b)
        for e in gang_a + gang_b:
            if random.choice((True, False)):
                e.arm_robber()
        opp = gang_a + gang_b
        opp_strength = p.get_rel_strength(groups=[gang_a, gang_b])
        esc_chance = get_escape_chance(p)
        if p.fight_or_run(opp_strength, esc_chance) and not check_scary_fight(
                p, opp_to_self_pwr_ratio=opp_strength[0]):
            if fight.group_free_for_all([[p], gang_a, gang_b]):
                p.show(_('{} is the last one standing!').format(tr_fighter_name(p.name)))
                p.gain_rep(len(opp))
                p.game.crime_down()
                try_enemy(p, opp[0], CH_THUG_ENEMY)
        else:
            try_escape(p, esc_chance)
        p.pak()



class HelpPolice(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 4

    def run(self):
        p = self.player
        num_al = rndint(*NUM_POLICE_VS_THUGS)
        num_en = num_al + rndint(*NUM_THUGS_VS_POLICE)
        p.show(
            _('{name} sees {num_al} police officers fighting {num_en} thugs!').format(
                name=tr_fighter_name(p.name), num_al=num_al, num_en=num_en
            )
        )
        p.log(
            _('Sees {num_al} police officers fighting {num_en} thugs.').format(
                num_al=num_al, num_en=num_en
            )
        )
        al = fighter_factory.new_police(n=num_al)
        for a in al:
            if random.choice((True, False)):
                a.arm_police()
        en = fighter_factory.new_thug(n=num_en)
        for e in en:
            if random.choice((True, False)):
                e.arm_robber()
        opp_strength = p.get_rel_strength(*en, allies=al)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
            if rnd() <= CH_POLICE_CHAOS:
                self.do_chaos(al, en)
                return
            p.gain_rep(num_en - num_al)
            p.check_help(allies=False, master=False, school=False)
            if p.fight(en[0], al, en[1:]):
                p.show(_('Police Officer: "Thank you very much for your help!"'))
                p.pak()
        else:
            p.log(_('Does not help the police.'))

    def do_chaos(self, al, en):
        p = self.player
        newcomers = fighter_factory.new_thug(n=rndint(*NUM_POLICE_CHAOS_GANG))
        for e in newcomers:
            if random.choice((True, False)):
                e.arm_robber()
        p.show(
            ngettext(
                'Suddenly, {} more thug arrives to rob both sides — '
                'the fight turns into a total free-for-all!',
                'Suddenly, {} more thugs arrive to rob both sides — '
                'the fight turns into a total free-for-all!',
                len(newcomers),
            ).format(len(newcomers))
        )
        p.log(_('The fight turns into a free-for-all.'))
        if fight.free_for_all([p] + al + en + newcomers):
            p.show(_('Police Officer: "Thank you very much for your help!"'))
            p.gain_rep(len(en) + len(newcomers) - len(al))
            p.pak()



class Robbers(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.num_r = 0
        self.r = None
        self.rs = []
        self.escape_chance = 0
        self.squabble = False
        self.money = random.choice(MONEY_GIVE_ROBBERS)
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 2

    def run(self):
        self.set_up()
        if self.num_r > 1:
            self.start_many()
        else:
            self.start_one()
        self.pre_fight()

    def set_up(self):
        self.num_r = random.choice((1, 1, rndint(*NUM_ROBBERS_GROUP), rndint(*NUM_ROBBERS_CROWD)))
        self.r = fighter_factory.new_robber()
        self.escape_chance = get_escape_chance(self.p)
        self.squabble = self.num_r >= NUM_ROBBERS_CROWD[0] and rnd() <= CH_ROBBERS_SQUABBLE

    def start_one(self):
        self.p.show(_('{} encounters a robber.').format(tr_fighter_name(self.p.name)))
        self.p.log(_('Encounters a robber.'))
        if rnd() <= CH_ROBBER_ARMED:
            self.r.arm_robber()
            self.p.show(
                _('He is armed with {}.').format(
                    add_article(tr_name(self.r.weapon.name))
                )
            )
        self.rs = []

    def start_many(self):
        self.p.show(
            ngettext(
                '{} encounters {} robber.', '{} encounters {} robbers.', self.num_r
            ).format(tr_fighter_name(self.p.name), self.num_r)
        )
        self.p.log(
            ngettext(
                'Encounters {} robber.', 'Encounters {} robbers.', self.num_r
            ).format(self.num_r)
        )
        self.rs = fighter_factory.new_robber(n=self.num_r)
        self.r, self.rs = self.rs[0], self.rs[1:]

    def pre_fight(self):
        p = self.player
        r_words = random.choice(LINES_ROBBER).format(self.money)
        r_line = _('Robber: "{}"').format(r_words)
        p.show(r_line)
        opp = [self.r] + self.rs
        opp_strength = p.get_rel_strength(*opp)
        choice = p.fight_run_or_pay(opp_strength, self.escape_chance, self.money)
        if choice == "f" and not check_scary_fight(p, opp_strength[0]):
            self.do_fight()
        elif choice == "p":
            if check_feeling_greedy(p):
                try_escape(p, self.escape_chance)
            else:
                self.pay()
        else:
            try_escape(p, self.escape_chance)

    def do_fight(self):
        p = self.p
        if self.squabble:
            p.show(
                _(
                    'The robbers start arguing over how to split the loot... '
                    "In the chaos, it's everyone for themselves!"
                )
            )
            p.log(_('The robbers squabble over the loot.'))
            if fight.free_for_all([p, self.r] + self.rs):
                p.game.crime_down()
                p.gain_rep(self.num_r)
                try_enemy(p, self.r, CH_ROBBER_ENEMY)
            return
        if self.num_r > 1:
            p.check_help()
            allies = p.allies
        else:
            if self.r.weapon and self.r.check_lv(p.level + 1):
                p.check_help(allies=False, master=False, school=False)
            allies = None
        if p.fight(self.r, allies, self.rs):
            if self.num_r >= NUM_ROBBERS_GROUP[0]:
                p.game.crime_down()
            p.gain_rep(self.num_r)
            try_enemy(p, self.r, CH_ROBBER_ENEMY)

    def pay(self):
        self.p.pay(self.money)
        self.p.change_stat("money_robbed", self.money)
        self.p.msg(
            ngettext(
                'The robber decides to let {name} go.',
                'The robbers decide to let {name} go.',
                self.num_r,
            ).format(name=tr_fighter_name(self.p.name))
        )



class RobbingSomeone(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 4

    def run(self):
        p = self.player
        num_en = rndint(*NUM_EXTORTERS)
        p.show(
            ngettext(
                '{} sees {} man robbing someone.',
                '{} sees {} men robbing someone.',
                num_en,
            ).format(tr_fighter_name(p.name), num_en)
        )
        p.log(
            ngettext(
                'Sees {} man robbing someone.', 'Sees {} men robbing someone.', num_en
            ).format(num_en)
        )
        en = fighter_factory.new_thug(n=num_en)
        opp_strength = p.get_rel_strength(*en)
        if p.fight_or_not(opp_strength) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_strength[0]):
            p.check_help()
            p.gain_rep(num_en * 2)
            if p.fight(en[0], p.allies, en[1:]):
                p.game.crime_down()
                try_enemy(p, en[0], CH_ROBBER_ENEMY)
                victim = random.choice((_('Man'), _('Woman')))
                p.show(_('{}: "Thank you very much!!!"').format(victim))
                p.pak()
        else:
            p.log(_('Looks the other way.'))



class Thief(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.players_items = None
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        return rnd() <= self.player.game.crime / 3

    def run(self):
        p = self.player
        _items = self.players_items = p.get_items(incl_healer=True)
        if p.money <= 0 and not _items:
            self.nothing_to_steal()
        else:
            if rnd() <= p.thief_steals:
                self.steal()
            else:
                self.fail()
        p.pak()

    def nothing_to_steal(self):
        p = self.p
        t = _(
            '''A thief tries to steal something from {name} but fails to find anything!
Thief: "What\'s with that? Are you poor or something?"'''
        ).format(name=tr_fighter_name(p.name))
        p.show(t)
        p.log(
            _('A thief fails to find anything to steal from {}.').format(
                tr_fighter_name(p.name)
            )
        )
        p.pak()

    def steal(self):
        p = self.player
        steal_item = random.choice((1, 0))
        if (steal_item or p.money <= 0) and self.players_items:
            item = random.choice(self.players_items)
            p.lose_item(item)
            p.show(
                _('A thief steals {item} from {name}.').format(
                    item=tr_name(item), name=tr_fighter_name(p.name)
                )
            )
            p.log(_('{} is stolen by a thief.').format(tr_name(item)))
            p.change_stat("items_stolen_from", 1)
        else:
            amount = random.choice(MONEY_THIEF_STEALS)
            if amount >= p.money:
                amount = p.money
                p.show(
                    _(
                        "A thief steals all {name}'s money! {name} loses {amount} c."
                    ).format(name=tr_fighter_name(p.name), amount=amount)
                )
                p.log(
                    _("All {name}'s money ({amount}) is stolen by a thief.").format(
                        name=tr_fighter_name(p.name), amount=amount
                    )
                )
            else:
                p.write(
                    ngettext(
                        'A thief steals {} coin from {name}!',
                        'A thief steals {} coins from {name}!',
                        amount,
                    ).format(amount, name=tr_fighter_name(p.name))
                )
                p.log(_('{} c. is stolen by a thief.').format(amount))
            self.p.steal_from(amount)
            p.show(
                _('The pickpocket had escaped before {} noticed anything.').format(
                    tr_fighter_name(p.name)
                )
            )

    def fail(self):
        p = self.player
        p.show(
            _('A thief tries to steal from {}, but fails.').format(
                tr_fighter_name(p.name)
            )
        )
        p.log(_('A thief fails to steal from {}.').format(tr_fighter_name(p.name)))
        if rnd() <= CH_THIEF_ESCAPES:
            t = _(
                '{} tries to stop him, but the pickpocket quickly disappears '
                'in the crowd.'
            ).format(tr_fighter_name(p.name))
            p.show(t)
            p.log(_('The thief escapes.'))
        else:
            p.show(
                _('{} grabs the thief by the arm, but the thief fights back.').format(
                    tr_fighter_name(p.name)
                )
            )
            p.log(_('The thief attacks {}.').format(tr_fighter_name(p.name)))
            self.do_fight()

    def do_fight(self):
        p = self.p
        if rnd() <= CH_THIEF_TOUGH and p.game.thief is not None:
            tough_thief = True
            thief = p.game.thief
            p.show(
                _('Thief: "Can you stop the infamous {}?"').format(
                    tr_fighter_name(thief.name)
                )
            )
        else:
            tough_thief = False
            thief = fighter_factory.new_thief(tough=False)
        p.pak()
        if rnd() <= CH_THIEF_ARMED:
            thief.arm("knife")
        if self.p.fight(thief):
            p.show(
                _('{}: "Now let\'s go to the police..."').format(
                    tr_fighter_name(self.p.name)
                )
            )
            if tough_thief:
                p.add_accompl("Beat Tough Thief")
                p.game.thief = None
                p.game.unregister_fighter(thief)
        else:
            p.show(
                _('{}: "Can\'t stop me, can you? Ha-ha-ha!"').format(
                    tr_fighter_name(thief.name)
                )
            )



class GRobbers(Guaranteed, Robbers):
    pass



