import random
import re

from kf_lib.actors import fighter_factory, traits
from kf_lib.fighting import fight
from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name
from kf_lib.utils import enum_words, rnd, rndint
from ._base_encounter import BaseEncounter, Guaranteed
from ._utils import check_feeling_greedy, check_scary_fight, get_escape_chance, try_escape


# constants
# encounter chances
ENC_CH_BRAWLER = 0.03
ENC_CH_DRUNKARD = 0.05
ENC_CH_FAT_GIRL = 0.02
ENC_CH_GOSSIP = 0.03
ENC_CH_OVERHEAR_CONVERSATION = 0.03
ENC_CH_PLAYER_MATCH = 0.01
ENC_CH_STREET_BRAWL = 0.015
ENC_CH_WISE_MAN = 0.02

# misc chances
_NUMBERED_NAME = re.compile(r'^(.*\S)\s+\d+$')


def group_same_fighters(opp_strs):
    """Condense 'Thug 1, lv.1 Dirty Fighting' x5 into '5 Thugs'; singles keep full info."""
    groups = {}
    order = []
    for s in opp_strs:
        name = s.split(', lv.', 1)[0]
        m = _NUMBERED_NAME.match(name)
        # only numbered names group; an unnumbered name stays unique to its string
        base = m.group(1) if m else s
        if base not in groups:
            groups[base] = []
            order.append(base)
        groups[base].append(s)
    parts = []
    for base in order:
        group = groups[base]
        if len(group) > 1:
            parts.append(f'{len(group)} {base}s')
        else:
            parts.append(group[0])
    return parts
CH_BRAWLER_ATTACKS = 0.2
CH_BRAWL_SPREADS = 0.125
CH_CHANGE_TRAIT = 0.15
CH_DRUNKARD_FIGHT_STRONG = 0.1
CH_DRUNKARD_FIGHT_WEAK = 0.1

# levels
REQ_LV_DRUNKARD_FIGHT_STRONG = (5, 10)
REQ_LV_DRUNKARD_FIGHT_WEAK = (1, 5)

# money
MONEY_GOSSIP_COST = (15, 20, 25, 30, 35)
MONEY_WISE_MAN = 10

# moves
DRUNKARD_LOSE_MOVE_TIERS = (2, 4)
# DRUNKARD_WIN_MOVE_TIERS = (4, 6)  # decided not to implement

# numbers
NUM_BRAWL_BYSTANDERS = (2, 4)
NUM_STREET_BRAWLERS = (3, 5)

# reputation
REP_PEN_BRAWL = -3
REP_PEN_DRINK = -3
REP_NOT_BRAWL = 1
REP_WIN_BRAWL = 2


class Brawler(BaseEncounter):
    def check_if_happens(self):
        return not self.player.is_master and rnd() <= ENC_CH_BRAWLER

    def run(self):
        p = self.player
        t = _('''A man bumps into {name} in the street.
Man: "Hey you! Apologize or I'll beat you up!\"''').format(
            name=tr_fighter_name(p.name)
        )
        p.show(t)
        p.log(_('Encounters a brawler.'))
        b = fighter_factory.new_brawler()
        opp_info = p.get_rel_strength(b)
        if p.brawl_or_not(opp_info):
            p.log(_('Is provoked.'))
            p.gain_rep(REP_PEN_BRAWL)
            self.do_fight(b)
            p.show(
                _('{}: "I shouldn\'t have been provoked so easily..."').format(
                    tr_fighter_name(p.name)
                )
            )
            p.pak()
        else:
            p.log(_('Apologizes.'))
            p.gain_rep(REP_NOT_BRAWL)
            if rnd() <= CH_BRAWLER_ATTACKS:
                p.log(_("The brawler won't let go."))
                p.show(_('Brawler: "That\'s not good enough!"'))
                p.pak()
                self.do_fight(b)

    def do_fight(self, b):
        p = self.player
        if rnd() <= CH_BRAWL_SPREADS:
            bystanders = [
                fighter_factory.new_brawler() for _ in range(rndint(*NUM_BRAWL_BYSTANDERS))
            ]
            p.show(
                _(
                    'The commotion draws in {} more people — '
                    'it turns into a full-blown street brawl!'
                ).format(len(bystanders))
            )
            p.log(_('The brawl spreads to bystanders.'))
            fight.free_for_all([p, b] + bystanders)
        else:
            p.fight(b)



class Drunkard(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_DRUNKARD

    def run(self):
        p = self.player
        t = _('{} meets a drunkard. "Hey, pal, come drink with me!" he slurs.').format(
            tr_fighter_name(p.name)
        )
        p.show(t)
        p.log(_('Meets a drunkard.'))
        if rnd() < p.drink_with_drunkard:
            p.show(_("{} can't resist the temptation.").format(tr_fighter_name(p.name)))
            p.drink()
            p.gain_rep(REP_PEN_DRINK)
        else:
            p.show(_('{} refuses to drink.').format(tr_fighter_name(p.name)))
            p.log(_('Refuses to drink.'))
            roll = rnd()
            if (
                p.check_lv(*REQ_LV_DRUNKARD_FIGHT_STRONG)
                and roll <= CH_DRUNKARD_FIGHT_STRONG
                and p.game.drunkard is not None
            ):
                self.do_fight(strong=True)
            elif not p.is_master and roll <= CH_DRUNKARD_FIGHT_WEAK:
                self.do_fight()
        p.pak()

    def do_fight(self, strong=False):
        p = self.player
        if strong:
            d = p.game.drunkard
            t = _('''Drunkard: "What? Just ignoring Legendary {}? \
            Let me teach you some manners!"''').format(
                tr_fighter_name(d.name.replace("Drunkard ", ""))
            )
        else:
            t = _('''Drunkard: "You think you're too good for drinkin' with me?"''')
            d = fighter_factory.new_drunkard(strong=False)
        p.show(t)
        p.log(_('The drunkard attacks {}.').format(tr_fighter_name(p.name)))
        p.pak()
        if p.fight(d, items_allowed=False):
            if strong:
                t = _('''{}: "Whoa, you are good! I was just as good and just as arrogant in my day... \
                I\'m sure we\'ll meet again."''').format(
                    tr_fighter_name(d.name)
                )
                p.show(t)
                p.add_friend(d)
                p.add_accompl("Drunkard's Friend")
                p.show(
                    _(
                        '{}: "What amazing kung-fu! I feel that my technique has improved"'
                    ).format(tr_fighter_name(p.name))
                )
                p.pak()
                p.learn_move_from(d)
                p.game.drunkard = None
        else:
            p.show(
                _(
                    '{}: "When I\'m one-tenth drunk I can use only one-tenth of my skill, '
                    'but when I\'m ten-tenths drunk I\'m at the top of my form."'
                ).format(tr_fighter_name(d.name))
            )
            p.pak()
            if strong:
                p.show(
                    _(
                        '{}: "What amazing kung-fu! Even though I lost, I feel that my '
                        'technique has improved"'
                    ).format(tr_fighter_name(p.name))
                )
                p.pak()
                p.learn_move_from(d)



class FatGirl(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.g = player.game.fat_girl
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        p = self.p
        return p.game.fat_girl is not None and not p.is_master and rnd() <= ENC_CH_FAT_GIRL

    def run(self):
        p = self.player
        p.show(_('{} is ambushed by a strange fat girl.').format(tr_fighter_name(p.name)))
        p.log(_('Is ambushed by a fat girl.'))
        self.g = p.game.fat_girl
        opp_strength = p.get_rel_strength(self.g)
        esc_chance = get_escape_chance(p)
        p.show(
            _(
                'Fat Girl: "You look like a martial artist! '
                "Surely you'll make a fine husband. MARRY ME NOW OR I'LL BEAT THE CRAP OUT OF YOU!"
            )
        )
        if p.fight_or_run(opp_strength, esc_chance) and not check_scary_fight(p, opp_strength[0]):
            self.do_fight()
        else:
            try_escape(p, esc_chance)

    def do_fight(self):
        p = self.player
        if p.fight(self.g):
            p.msg(_('{} runs away in fear.').format(tr_fighter_name(self.p.name)))
            p.game.fat_girl = None
            p.add_accompl("Fat Girl Defeated")
        else:
            p.msg(
                _(
                    'Fat Girl: "Now that I think about it, you are too weak to be my husband '
                    'anyway!"'
                )
            )



class FriendMatch(BaseEncounter):
    def __init__(self, player, check_if_happens=True):
        self.av_fr = []
        BaseEncounter.__init__(self, player, check_if_happens)

    def check_if_happens(self):
        self.av_fr = [
            f for f in self.player.get_nonhuman_friends()
            if not (f.is_player and (f.inactive or f.inact_status))
        ]
        return rnd() <= len(self.av_fr) * 0.01

    def run(self):
        p = self.player
        opp = random.choice(self.av_fr)
        t1 = _('''{opp}: "{player}, I've learned some new moves. Let's practice!\"''').format(
            opp=tr_fighter_name(opp.name), player=tr_fighter_name(p.name)
        )
        t2 = _("{player}'s friend {opp} challenges him to a friendly match.").format(
            player=tr_fighter_name(p.name), opp=tr_fighter_name(opp.name)
        )
        p.show(t1)
        p.log(t2)
        p.show(_('Accept?'))
        if p.p_match_or_not():
            p.spar(opp)
            p.show(
                _('{}: "That was a good match! Let\'s do it again some time."').format(
                    tr_fighter_name(opp.name)
                )
            )
            p.pak()
        else:
            p.log(_('Refuses.'))



class Gossip(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_GOSSIP

    def run(self):
        p = self.player
        cost = random.choice(MONEY_GOSSIP_COST)
        t = ngettext(
            '{name} meets a local gossipmonger. Pay {n} coin to hear the latest rumors?',
            '{name} meets a local gossipmonger. Pay {n} coins to hear the latest rumors?',
            cost,
        ).format(name=tr_fighter_name(p.name), n=cost)
        p.show(t)
        p.log(_('Meets a gossipmonger.'))
        if p.hear_rumors_or_not() and p.check_money(cost):
            p.pay(cost)
            p.log(_('Hears the rumors.'))
            p.game.show_stats()




class OverhearConversation(BaseEncounter):
    """Hear interesting facts about players."""

    def __init__(self, player, check_if_happens=True):
        self.facts = []
        BaseEncounter.__init__(self, player, check_if_happens)

    def collect_facts(self):
        g = self.player.game
        for p in g.players:
            for stat in ("aston_victory", "humil_defeat"):
                result = p.get_stat(stat)  # tuple: (date, p.level, [enemies strings], big opp_to_self_pwr_ratio)
                if result is not None:
                    self.facts.append((p, stat, result))

    def check_if_happens(self):
        return rnd() <= ENC_CH_OVERHEAR_CONVERSATION

    def run(self):
        p = self.player
        t = _(
            '{} accidentally overhears a conversation of two young kung-fu practitioners.'
        ).format(tr_fighter_name(p.name))
        p.log(_('Overhears a conversation.'))
        p.show(t)
        self.collect_facts()
        if not self.facts:
            p.show(
                _(
                    '"They talk about such silly things instead of practicing!" - {} thinks.'
                ).format(tr_fighter_name(p.name))
            )
            p.log(_('Nothing interesting.'))
        else:
            random.shuffle(self.facts)
            person, fact, result = self.facts[0]
            date, lv, opps, ratio = result
            opp_str = enum_words(group_same_fighters(opps))
            if fact == "humil_defeat":
                t = _('''One of them says: "Haven't you heard? {} at lv.{} shamefully lost to {}. What a disgrace to \
kung-fu!"''').format(
                    tr_fighter_name(person.name), lv, tr_name(opp_str)
                )
                p.show(t)
                p.log(
                    _("Something about {}'s humiliating defeat.").format(
                        tr_fighter_name(person.name)
                    )
                )
            elif fact == "aston_victory":
                t = _('''One of them says: "Haven't you heard? {} at lv.{} beat {}. What an astonishing \
victory!"''').format(
                    tr_fighter_name(person.name), lv, tr_name(opp_str)
                )
                p.show(t)
                p.log(
                    _("Something about {}'s astonishing victory.").format(
                        tr_fighter_name(person.name)
                    )
                )
        p.pak()



class PlayerMatch(BaseEncounter):
    """Works with computer players as opponents only (for both human and computer players)."""

    def __init__(self, player, check_if_happens=True):
        self.av_p = []
        BaseEncounter.__init__(self, player, check_if_happens)

    def set_available_players(self):
        p, g = self.player, self.player.game
        self.av_p = [
            pp for pp in g.get_act_players()
            if not pp.is_human and not pp == p and not pp.inact_status
        ]

    def check_if_happens(self):
        self.set_available_players()
        return self.av_p and rnd() <= ENC_CH_PLAYER_MATCH

    def run(self):
        p = self.player
        opp = random.choice(self.av_p)
        t = _('''{player} meets {opp} (lv.{lv}).
{opp}: "Let\'s have a friendly match!"''').format(
            player=tr_fighter_name(p.name), opp=tr_fighter_name(opp.name), lv=opp.level
        )
        p.show(t)
        p.log(_('Meets {}').format(tr_fighter_name(opp.name)))
        if p.p_match_or_not():
            p.spar(opp)
            p.show(
                _('{}: "That was a good match! Let\'s do it again some time."').format(
                    tr_fighter_name(opp.name)
                )
            )
            p.pak()
        else:
            p.log(_('Refuses.'))



class StreetBrawl(BaseEncounter):
    def check_if_happens(self):
        return not self.player.is_master and rnd() <= ENC_CH_STREET_BRAWL

    def run(self):
        p = self.player
        num_b = rndint(*NUM_STREET_BRAWLERS)
        if random.choice((True, False)):
            p.show(
                ngettext(
                    '{name} stumbles upon a street brawl — {n} man is fighting each other!',
                    '{name} stumbles upon a street brawl — {n} men are fighting each other!',
                    num_b,
                ).format(name=tr_fighter_name(p.name), n=num_b)
            )
            p.log(_('Sees a street brawl.'))
        else:
            p.show(
                ngettext(
                    '{name} stumbles into a tavern brawl — {n} drunkard is fighting each other!',
                    '{name} stumbles into a tavern brawl — {n} drunkards are fighting each other!',
                    num_b,
                ).format(name=tr_fighter_name(p.name), n=num_b)
            )
            p.log(_('Sees a tavern brawl.'))
        brawlers = [fighter_factory.new_brawler() for _ in range(num_b)]
        opp_info = p.get_rel_strength(*brawlers, mean=True)
        if p.brawl_or_not(opp_info) and not check_scary_fight(p, opp_to_self_pwr_ratio=opp_info[0]):
            p.log(_('Joins the brawl.'))
            p.gain_rep(REP_PEN_BRAWL)
            if fight.free_for_all([p] + brawlers):
                p.show(_('{} is the last one standing!').format(tr_fighter_name(p.name)))
                p.gain_rep(num_b * REP_WIN_BRAWL)
            p.pak()
        else:
            p.log(_('Walks away from the brawl.'))



class WiseMan(BaseEncounter):
    def check_if_happens(self):
        return rnd() <= ENC_CH_WISE_MAN

    def run(self):
        p = self.player
        t = _('{} meets a wise man.').format(tr_fighter_name(p.name))
        p.show(t)
        p.log(_('Meets a wise man.'))
        if p.check_money(MONEY_WISE_MAN):
            if p.talk_wise_or_not() and not check_feeling_greedy(p):
                p.pay(MONEY_WISE_MAN)
                trait = traits.get_rand_traits(negative=False)
                p.show(
                    _(
                        "{} and the wise man have a long conversation in a nearby tavern. The wise man talks about "
                        "the importance of being {}."
                    ).format(tr_fighter_name(p.name), tr_name(trait))
                )
                p.log(
                    _('The wise man talks about the importance of being {}.').format(
                        tr_name(trait)
                    )
                )
                if rnd() <= CH_CHANGE_TRAIT and trait not in p.traits:
                    p.show(
                        _("This conversation changes {}'s life.").format(
                            tr_fighter_name(p.name)
                        )
                    )
                    opp_trait = traits.get_opposite_trait(trait)
                    if opp_trait in p.traits:
                        p.remove_trait(opp_trait)
                    else:
                        p.add_trait(trait)
                    p.add_accompl("Personality Change")
            else:
                return
        else:
            p.show(
                _(
                    "Too bad {} doesn't have enough money to treat the wise man to lunch and talk to him."
                ).format(tr_fighter_name(p.name))
            )
        p.pak()



class GDrunkard(Guaranteed, Drunkard):
    pass


