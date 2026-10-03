import random

from kf_lib.actors import quotes
from kf_lib.actors import traits
from kf_lib.actors.fighter import Fighter
# todo refactor importing get_rand_traits
# have to import separately or .set_rand_traits doesn't work
from kf_lib.actors.traits import get_rand_traits
from kf_lib.constants import experience
from kf_lib.constants.experience import EXP_PER_LEVEL
from kf_lib.game import game_stats
from kf_lib.happenings import encounters
from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name
from kf_lib.kung_fu import techniques
from kf_lib.things import items
from kf_lib.ui import bold, green, strip_tags, yellow, yn
from kf_lib.utils import add_sign, enum_words, Integer, rnd, rndint


# todo refactor _base_player into specific modules

EXTREMELY_GOOD_LUCK = 20
EXTREMELY_BAD_LUCK = 1
LUCK_ACCOMPLISHMENT_THRESHOLD = 10
MASTER_GREETING_CHANCE = 0.1
TUITION_FEE = 20
WAGE = 50

# banned from school (Grand Melee story)
CH_MASTER_FORGIVES = 0.25
CH_BEG_BULLIED = 0.2

# teaching students
CH_STUDENT_LV_UP_WHEN_TAUGHT = 0.2
TAUGHT_STUDENT_LV_GAP = 2  # a master can't teach students beyond (own level - gap)
NUM_SCHOOL_TECHS = 3  # how many techs a school teaches its students
CH_STUDENT_LEARN_TECH = 0.25  # per lesson, per student missing a school tech

# uniting the schools (kung-fu federation)
UNITED_SCHOOL_REP = 5
PERSUADE_REP_DIVISOR = 150  # persuade chance = reputation / this
MAX_PERSUADE_CH = 0.75

# romance
ROMANCE_PROPOSE_THRESHOLD = 10  # romance_progress needed for a proposal
ROMANCE_GIFT_COST = 10
CH_PROPOSAL_ACCEPT = 0.5  # + reputation / 500, capped at 0.9
CH_SPOUSE_GIFT = 0.1  # daily chance the spouse brings home some money

# family
MAX_CHILDREN = 3
CHILD_GROWN_AGE = 12  # months; a grown child can practice kung-fu with the player
CHILD_EXP = 10  # exp for practicing kung-fu with a grown child
CHILD_PRACTICE_CHANCE = 0.3  # on the 'Visit spouse' day action
CH_CHILD_BORN = 0.2  # monthly chance for a married player
CH_CHILD_COST = 0.05  # daily per-child chance of a small expense


# todo Epic Gambler accomplishment


class BasePlayer(Fighter):
    is_player = True
    savable_atts = '''exp is_master new_school_name money reputation 
    inactive inact_status inventory ended_turn accompl accompl_dates stats_dict
    move_usage banned_from_school schools_allied school_techs
    romance_progress is_married children_ages'''.split()
    possible_tournament_bets = (10, 25, 50, 100)

    exp = Integer(minvalue=0, action='raise')

    # the order of arguments should not be changed, or saving will break
    def __init__(
        self,
        name='',
        style=None,
        level=1,
        atts_tuple=None,
        tech_names=None,
        move_names=None,
        rand_atts_mode=2,
        traits_list=None,
    ):
        self.plog = []
        self.traits = []  # initialized early so repr() works during super().__init__()
        super().__init__(
            name=name,
            style=style,
            level=level,
            atts_tuple=atts_tuple,
            tech_names=tech_names,
            move_names=move_names,
            rand_atts_mode=rand_atts_mode,
            occupation='hero',
        )
        self.allies = []
        self.ended_turn = False
        self.challenger_friend_mult = 1.0
        self.coop_joins_fight = 0.5
        self.coop_joins_training = 0.25
        self.drink_with_drunkard = 0.25
        self.escape_bonus = 0.0
        self.feel_too_greedy = 0.3
        self.feel_too_scared = 0.3
        self.friend_joins_fight = 0.3
        self.friend_joins_training = 0.25
        self.gamble_continue = 0.4
        self.gamble_with_gambler = 0.3
        self.grab_improvised_weapon = 0.5
        self.home_training_exp_bonus = 0
        self.item_is_found = 0.01
        self.item_is_lost = 0.01
        self.master_joins_fight = 0.5
        self.max_days_to_recover = 7
        self.max_num_friends = 8
        self.next_lv_exp_mult = 1.0
        self.romance_pursuit_chance = 0.5
        self.school_training_exp_mult = 1.0
        self.schoolmates_help = 0.5
        self.spouse_joins_fight = 0.6
        self.thief_steals = 0.3
        self.training_injury = 0.05
        self.visit_sweetheart_chance = 0.2
        self.wage_mult = 1.0
        if traits_list is None:
            self.set_rand_traits()
        else:
            self.traits = traits_list  # directly add traits not to write log and on screen
        for trait in self.traits:
            self.activate_trait(trait)

        # default player attributes
        self.game = None
        self.friends = []
        self.enemies = []
        self.sweetheart = None  # love interest / spouse (a Fighter)
        self.romance_progress = 0
        self.is_married = False
        self.children_ages = []  # months old, one entry per child
        self.accompl = []
        self.accompl_dates = []
        self.banned_from_school = False
        self.move_usage = {}  # move name -> times used, accumulated over all fights
        self.is_master = False
        self.new_school_name = ''
        self.school_rank = None
        self.max_school_rank = None
        self.students = 0
        self.best_student = None
        self.schools_allied = []  # school names whose masters joined the federation
        self.school_techs = []  # names of the techs the player's school teaches
        self.current_story = None
        self.exp = 0
        self.next_level = self.get_next_lv_exp()
        self.money = 10
        self.reputation = 0
        self.inactive = 0
        self.inact_status = ''
        self.inventory = {}
        self.used_item = ''
        self.exp_bonuses = 0  # for every fight

        self.stats_dict = game_stats.get_blank_stats_dict()

    def activate_trait(self, trait):
        eff_dict = traits.get_trait_eff_dict(trait)
        for att, change in eff_dict.items():
            val = getattr(self, att)
            new_val = val + change
            setattr(self, att, new_val)

    def add_accompl(self, label):
        # todo refactor accomplishemnts as dict {accompl: date}, otherwise inefficient
        if label not in self.accompl:
            self.accompl.append(label)
            self.accompl_dates.append(self.game.get_date())
            self.write(_('Accomplishment: {label}').format(label=tr_name(label)))
            self.gain_exp(experience.ACCOMPL_EXP)
            self.pak()

    def add_enemy(self, enemy):
        self.enemies.append(enemy)
        self.game.register_fighter(enemy)
        self.log(
            _('{enemy} is now {name}\' enemy.').format(
                enemy=tr_fighter_name(enemy.name), name=tr_fighter_name(self.name)
            )
        )

    def get_accompl_info(self):
        if not self.accompl:
            return _('{name} has no accomplishments yet.').format(
                name=tr_fighter_name(self.name)
            )
        lines = [_('{name}\'s accomplishments:').format(name=tr_fighter_name(self.name))]
        lines += [
            '{}. {} ({})'.format(i, tr_name(label), date)
            for i, (label, date) in enumerate(zip(self.accompl, self.accompl_dates), 1)
        ]
        return '\n'.join(lines)

    def add_friend(self, obj):
        if len(self.friends) < self.max_num_friends:
            self.friends.append(obj)
            self.log(
                _('{obj} is now {name}\' friend.').format(
                    obj=tr_fighter_name(obj.name), name=tr_fighter_name(self.name)
                )
            )
        else:
            self.show(
                _(
                    '{name} already has {max_num} friends — too many to '
                    'keep up with. {obj} remains a friendly acquaintance.'
                ).format(
                    name=tr_fighter_name(self.name),
                    max_num=self.max_num_friends,
                    obj=tr_fighter_name(obj.name),
                )
            )
            self.log(
                _('Has too many friends already; {obj} stays an acquaintance.').format(
                    obj=tr_fighter_name(obj.name)
                )
            )

    def choose_school_techs(self):
        """Pick the techs the player's school will teach (AI default: random known
        non-weapon techs). HumanPlayer overrides this with a menu."""
        av = sorted((t for t in self.techs if not t.is_weapon_tech), key=lambda t: t.name)
        self.school_techs = [
            t.name for t in random.sample(av, min(NUM_SCHOOL_TECHS, len(av)))
        ]
        if self.school_techs:
            self.log(
                _('Decides to teach {}.').format(
                    enum_words([tr_name(t) for t in self.school_techs])
                )
            )

    def add_students(self, num_stud):
        self.students += num_stud
        new_students = []
        school = self.game.schools[self.new_school_name]
        for i in range(num_stud):
            new_student = self.game.get_new_student(self.style.name)
            new_student.custom_style_name = self.custom_style_name
            new_students.append(new_student)
            school.append(new_student)
            self.game.register_fighter(new_student)
        if num_stud > 1:
            self.log(
                _('{num} students join {name}\'s school.').format(
                    num=num_stud, name=tr_fighter_name(self.name)
                )
            )
        else:
            self.log(
                _('A new student joins {name}\'s school.').format(
                    name=tr_fighter_name(self.name)
                )
            )
        self.log('\n'.join((str(s) for s in new_students)))
        self.refresh_best_student()

    def ally_school(self, school_name, master):
        """A master agrees to join the player's kung-fu federation."""
        self.schools_allied.append(school_name)
        self.add_friend(master)
        self.gain_rep(UNITED_SCHOOL_REP)
        # the school key is the style's secret true name — a master wouldn't
        # reveal it, so announce/log the displayed (public) name instead
        displayed_school = master.get_displayed_style_name()
        self.show(
            _('{master}: "From this day, {school} stands with you!"').format(
                master=tr_fighter_name(master.name), school=displayed_school
            )
        )
        self.log(
            _('{master} of {school} joins the federation.').format(
                master=tr_fighter_name(master.name), school=displayed_school
            )
        )
        self.pak()
        if not self.get_unallied_masters():
            self.show(
                _(
                    'All the schools of {town} are now united under '
                    '{name}\'s kung-fu federation!'
                ).format(town=self.game.town_name, name=tr_fighter_name(self.name))
            )
            self.log(_('Founds the kung-fu federation.'))
            self.add_accompl('Founder of the Federation')

    def add_trait(self, trait):
        """NB: differs from the activate_trait method.
        Should be used only for adding NEW traits in-game."""
        opp_trait = traits.get_opposite_trait(trait)
        if trait not in self.traits and opp_trait not in self.traits:
            self.traits.append(trait)
            self.activate_trait(trait)
            self.write(
                _('{name} becomes {trait}.').format(
                    name=tr_fighter_name(self.name), trait=tr_name(trait)
                )
            )
        else:
            raise Exception(
                'Cannot add trait "{}" to player {}\'s traits: {}'.format(
                    trait, self.name, self.traits
                )
            )

    def beg_master_for_mercy(self):
        """Banned from school (Grand Melee story): a practice visit becomes a begging
        scene — no tuition, no exp, a chance of forgiveness and of being bullied."""
        m = self.game.masters.get(self.style.name)
        if m is None or self.is_master:
            self.banned_from_school = False
            return
        self.show(
            _('{name} comes to school to beg {master} for forgiveness.').format(
                name=tr_fighter_name(self.name), master=tr_fighter_name(m.name)
            )
        )
        if rnd() <= CH_MASTER_FORGIVES:
            self.banned_from_school = False
            self.show(
                _(
                    '{master}: "Hmm... You do look sincere. Very well, I forgive you. '
                    'But if I EVER hear about you fighting for money again...!"'
                ).format(master=tr_fighter_name(m.name))
            )
            self.log(
                _('{master} forgives {name} and lifts the ban.').format(
                    master=tr_fighter_name(m.name), name=tr_fighter_name(self.name)
                )
            )
        else:
            self.show(
                _(
                    '{master}: "You still don\'t get it, do you? Come back when you have '
                    'learned some humility!"'
                ).format(master=tr_fighter_name(m.name))
            )
            self.log(_('Begs the master for forgiveness, in vain.'))
            if self.school_rank > 1 and rnd() <= CH_BEG_BULLIED:
                encounters.SchoolBullying(self, check_if_happens=False)
        self.pak()

    def buy_item(self, item, price):
        self.pay(price)
        self.log(_('Buys {item} for {price}.').format(item=tr_name(item), price=price))
        self.change_stat('items_bought', 1)
        self.obtain_item(item)

    def buy_items(self):
        from . import _day_actions
        _day_actions.buy_items(self)
        return True  # to end turn

    def cancel_item(self, item):
        """Convenience wrapper"""
        items.cancel_item(item, self)

    def change_att(self, att, amount):
        Fighter.change_att(self, att, amount)
        self.msg(_('{}: {}').format(tr_name(att), add_sign(amount)))

    def change_stat(self, stat_name, value):
        """Modify stat by adding value"""
        self.stats_dict[stat_name] += value

    def check_allies(self, max_num_allies=-1):
        if not self.friends:
            return None
        else:
            if max_num_allies == -1:
                max_num_allies = self.max_num_friends
            allies = []
            for a in self.friends:
                if a.is_player:
                    if not a.inactive and rnd() <= self.coop_joins_fight:
                        allies.append(a)
                else:
                    if rnd() <= self.friend_joins_fight:
                        allies.append(a)
                if len(allies) == max_num_allies:
                    break
            if allies:
                a_str = enum_words([tr_fighter_name(a.name) for a in allies])
                self.msg(
                    ngettext(
                        '{} joins the fight on {}\'s side.',
                        '{} join the fight on {}\'s side.',
                        len(allies),
                    ).format(a_str, tr_fighter_name(self.name))
                )
            return allies

    def check_fight_items(self):
        """Return True if player has any items usable in fights"""
        for k, v in self.inventory.items():
            if k in items.FIGHT_ITEMS and v > 0:
                return True

    def check_help(
        self, allies=True, master=True, impr_wp=True, school=True, spouse=True
    ):
        p = self
        p.allies = []
        hlp = []
        if allies:
            hlp.append('a')
        if master:
            hlp.append('m')
        if impr_wp:
            hlp.append('w')
        if school:
            hlp.append('s')
        if spouse and self.is_married and self.sweetheart is not None:
            hlp.append('sp')
        x = random.choice(hlp)
        if x == 'a':
            p.allies = p.check_allies()
        elif x == 'm':
            if rnd() <= self.master_joins_fight:
                if p.is_master:
                    # a master is helped by his best student, not his old master
                    school = p.get_school()
                    if not school:
                        return
                    helper = max(school, key=lambda f: f.get_exp_worth())
                    p.show(
                        _('{name}: "Let me help, Master!"').format(
                            name=tr_fighter_name(helper.name)
                        )
                    )
                    p.log(
                        _('{helper} joins the fight on {name}\'s side.').format(
                            helper=tr_fighter_name(helper.name),
                            name=tr_fighter_name(p.name),
                        )
                    )
                    p.allies = [helper]
                    p.pak()
                else:
                    m = p.get_master()
                    p.show(_('{}: "What\'s going on here?"').format(tr_fighter_name(m.name)))
                    p.log(
                        _('{master} joins the fight on {name}\'s side.').format(
                            master=tr_fighter_name(m.name), name=tr_fighter_name(p.name)
                        )
                    )
                    p.allies = [m]
                    p.pak()
        elif x == 'w':
            if rnd() <= self.grab_improvised_weapon:
                p.arm_improv()
                p.show(
                    _('{name} grabs an improvised weapon!').format(
                        name=tr_fighter_name(p.name)
                    )
                )
                p.log(_('Grabs an improvised weapon.'))
                p.pak()
        elif x == 's':
            if rnd() <= self.schoolmates_help:
                av_mates = [f for f in self.get_school() if not f.is_player]
                if av_mates:
                    n = min(random.choice((2, 3)), len(av_mates))
                    mates = random.sample(av_mates, n)
                    a_str = enum_words([tr_fighter_name(f.name) for f in mates])
                    p.allies = mates
                    self.msg(
                        _(
                            '{mates}, who were passing by, join the fight on '
                            '{name}\'s side.'
                        ).format(mates=a_str, name=tr_fighter_name(self.name))
                    )
        elif x == 'sp':
            if p.sweetheart is not None and rnd() <= self.spouse_joins_fight:
                sw = p.sweetheart
                p.show(
                    _('{name}: "Let me help you, dear!"').format(
                        name=tr_fighter_name(sw.name)
                    )
                )
                p.log(
                    _('{sw} joins the fight on {name}\'s side.').format(
                        sw=tr_fighter_name(sw.name), name=tr_fighter_name(p.name)
                    )
                )
                p.allies = [sw]
                p.pak()

    def check_injured(self):
        return self.inact_status == 'injured'

    def check_item(self, item_name):
        return self.inventory.get(item_name, 0)

    def check_luck(self, silent=False):
        outcome = random.randint(EXTREMELY_BAD_LUCK, EXTREMELY_GOOD_LUCK)
        if outcome == EXTREMELY_BAD_LUCK:
            if not silent:
                self.show(_('BAD LUCK!'))
            self.change_stat('bad_luck', 1)
            if self.get_stat('bad_luck') >= LUCK_ACCOMPLISHMENT_THRESHOLD:
                self.add_accompl('Unlucky Devil')
            return -1
        elif outcome == EXTREMELY_GOOD_LUCK:
            if not silent:
                self.show(_('LUCKY!'))
            self.change_stat('good_luck', 1)
            if self.get_stat('good_luck') >= LUCK_ACCOMPLISHMENT_THRESHOLD:
                self.add_accompl('Lucky Devil')
            return 1
        else:
            return 0

    def check_money(self, amount):
        """Return True if player has at least _amount_ money."""
        return self.money >= amount

    def check_partners(self):
        if not self.friends:
            return None
        else:
            partners = []
            for a in self.friends:
                if (a.is_player and not a.inactive and rnd() <= self.coop_joins_training) or (
                    not a.is_player and rnd() <= self.friend_joins_training
                ):
                    partners.append(a)
            if partners:
                p_str = enum_words([tr_fighter_name(p.name) for p in partners])
                self.write(
                    ngettext(
                        '{} joins {}\'s training session.',
                        '{} join {}\'s training session.',
                        len(partners),
                    ).format(p_str, tr_fighter_name(self.name))
                )
            return partners

    def check_training_injury(self):
        if rnd() <= self.training_injury:
            q = random.choice(quotes.TRAINING_INJURY)
            self.show(_('{name}: "{q}"').format(name=tr_fighter_name(self.name), q=q))
            self.msg(
                _('{name} gets injured during training.').format(
                    name=tr_fighter_name(self.name)
                )
            )
            self.injure(1)

    def check_spouse_daily(self):
        """Married life: the spouse contributes to the household, the children cost."""
        if not (self.is_married and self.sweetheart is not None):
            return
        if rnd() <= CH_SPOUSE_GIFT:
            amount = rndint(5, 20)
            self.show(
                _('{name} brings home some money. (+{amount} coins)').format(
                    name=tr_fighter_name(self.sweetheart.name), amount=amount
                )
            )
            self.earn_money(amount)
        if self.children_ages and self.money > 0:
            if rnd() <= CH_CHILD_COST * len(self.children_ages):
                amount = min(self.money, rndint(1, 5))
                self.pay(amount)
                self.show(
                    _('Children grow so fast — new clothes. (-{amount} coins)').format(
                        amount=amount
                    )
                )

    def check_family_monthly(self):
        """Monthly family events: children grow; a new child may be born."""
        if not (self.is_married and self.sweetheart is not None):
            return
        self.children_ages = [age + 1 for age in self.children_ages]
        if len(self.children_ages) < MAX_CHILDREN and rnd() <= CH_CHILD_BORN:
            self.children_ages.append(0)
            if rnd() < 0.5:
                self.show(
                    _('{name} and {sw} welcome a baby son!').format(
                        name=tr_fighter_name(self.name),
                        sw=tr_fighter_name(self.sweetheart.name),
                    )
                )
                self.log(_('A baby son is born.'))
            else:
                self.show(
                    _('{name} and {sw} welcome a baby daughter!').format(
                        name=tr_fighter_name(self.name),
                        sw=tr_fighter_name(self.sweetheart.name),
                    )
                )
                self.log(_('A baby daughter is born.'))
            if len(self.children_ages) == 1:
                self.add_accompl('Proud Parent')

    def get_grown_children(self):
        return [age for age in self.children_ages if age >= CHILD_GROWN_AGE]

    def cls(self):
        raise Exception('Not implemented.')

    def deactivate_trait(self, trait):
        eff_dict = traits.get_trait_eff_dict(trait)
        for att, change in eff_dict.items():
            val = getattr(self, att)
            new_val = val - change
            setattr(self, att, new_val)

    def donate(self, amount):
        if not amount:
            self.log(_('Doesn\'t give anything.'))
        else:
            self.log(_('Donates {} c.').format(amount))
            self.money -= amount
            self.change_stat('donated', amount)
            self.gain_rep(round(amount * 0.2))

    def drink(self):
        self.log(_('Drinks wine.'))
        self.inactive += 1
        self.inact_status = 'sick'
        self.change_stat('got_drunk', 1)

    def earn_money(self, amount, silent=False):
        self.money += amount
        if not silent:
            self.change_stat('money_earned', amount)
            self.log(_('Earns {} c.').format(amount))

    def earn_prize(self, amount):
        self.money += amount
        self.change_stat('prize_money_earned', amount)
        self.write(
            _('{name} earns a {prize} prize.').format(
                name=tr_fighter_name(self.name), prize=yellow(f'{amount}-coin')
            )
        )

    def earn_reward(self, amount):
        self.money += amount
        self.change_stat('rew_money_earned', amount)
        self.write(
            _('{name} earns a {reward} reward.').format(
                name=tr_fighter_name(self.name), reward=yellow(f'{amount}-coin')
            )
        )

    def end_turn(self):
        pass

    def enter_tourn(self, fee):
        self.log(_('Takes part in a kung-fu tournament.'))
        self.pay(fee)
        self.change_stat('num_tourn', 1)

    def fight_crime(self):
        self.log(_('Intends to fight crime.'))
        encs = encounters.FIGHT_CRIME_ENCS
        encounters.random_encounters(self, encs)
        return True  # to end turn

    def fight_dummy(self):
        dummy = Fighter('Dummy', style='No Style', atts_tuple=(1, 1, 1, 5))
        dummy.moves = []
        dummy.learn_move('Do Nothing')
        self.spar(dummy, hide_stats=True)

    def gain_exp(self, amount, silent=False):
        if not silent:
            self.show(
                _('{name} {exp_msg}').format(
                    name=tr_fighter_name(self.name),
                    exp_msg=green(_('gains {} exp.').format(amount)),
                )
            )
            self.log(_('Gains {} exp.').format(amount))
        self.exp += amount
        while self.exp >= self.next_level:
            self.level_up()

    def gain_rep(self, amount):
        self.reputation += amount
        self.log(_('Reputation: {} ({})').format(add_sign(amount), self.reputation))

    def get_items(self, incl_healer=False, incl_mock=False, as_dict=False):
        item_strings = items.FIGHT_ITEMS[:]
        if incl_healer:
            item_strings += [items.MEDICINE]
        if incl_mock:
            item_strings += items.MOCK_ITEMS
        if as_dict:
            return {k: v for k, v in self.inventory.items() if k in item_strings and v > 0}
        else:
            return [k for k, v in self.inventory.items() for _ in range(v) if k in item_strings]

    def get_day_actions(self):
        """Return list of available options"""
        ops = [
            (_('Practice at school'), self.practice_school)
            if not self.is_master
            else (_('Practice'), self.practice_master),
            (_('Go to work'), self.go_work),
            (_('Buy items'), self.buy_items),
            (_('Fight crime'), self.fight_crime),
            (_('Help the poor'), self.help_poor),
            (_('Pick fights'), self.pick_fights)
            if not self.is_master
            else (_('Teach students'), self.teach_students),
            (_('Go to seedy places'), self.go_seedy),
            (_('Go for a walk'), self.go_walk),
            # ('Dummy', self.fight_dummy)
        ]
        if self.is_master:
            ops.append((_('Visit other masters'), self.visit_masters))
        if self.sweetheart is not None:
            label = _('Visit spouse') if self.is_married else _('Visit sweetheart')
            ops.append((label, self.visit_sweetheart))
        return ops

    def get_fame(self):
        return (
            self.get_stat('tourn_won') + len(self.accompl) + (self.get_stat('fights_won') // 10)
        ) * 0.01

    def get_fight_statistics(self):
        return _('Fights/Wins/KOs: {}/{}/{}').format(
            self.get_stat('num_fights'), self.get_stat('fights_won'), self.get_stat('num_kos')
        )

    def get_inact_info(self):
        s = ngettext(
            '{name} is {status} and needs {days} day to recover.',
            '{name} is {status} and needs {days} days to recover.',
            self.inactive,
        ).format(
            name=tr_fighter_name(self.name),
            status=self.inact_status,
            days=self.inactive,
        )
        self.log(s)
        return s

    def get_unallied_masters(self):
        """NPC masters whose schools haven't joined the player's federation yet."""
        return [
            (school_name, m)
            for school_name, m in self.game.masters.items()
            if not m.is_player and school_name not in self.schools_allied
        ]

    def get_init_atts(self):
        """Return tuple of attributes used by __init__"""
        return Fighter.get_init_atts(self) + (
            self.rand_atts_mode,
            self.traits,
        )

    def get_inventory_info(self):
        lines = []
        for k, v in self.inventory.items():
            if v > 0:
                lines.append('{}: {}'.format(tr_name(k), v))
        lines = [_('{name}\'s items:').format(name=tr_fighter_name(self.name))] + sorted(
            lines
        )
        return '\n'.join(lines)

    def get_master(self):
        return self.game.masters[self.style.name]

    def get_next_lv_exp(self):
        return round(EXP_PER_LEVEL * self.next_lv_exp_mult * self.level)

    def get_nonhuman_friends(self):
        return [f for f in self.friends if not f.is_human]

    def get_other_schools(self):
        schools = self.game.schools.copy()
        del schools[self.style.name]
        return schools

    def get_p_info(self):
        s = self
        return _('{name} lv.{lv} exp:{exp}/{next_lv}\nmoney:{money}\n').format(
            name=bold(tr_fighter_name(s.name)),
            lv=s.level,
            exp=green(s.exp),
            next_lv=green(s.next_level),
            money=yellow(s.money),
        )

    def get_p_info_verbose(self):
        lines = [
            self.get_f_info(),
            _('exp:{exp}/{next_lv} money:{money}').format(
                exp=self.exp, next_lv=self.next_level, money=self.money
            ),
            _('traits: {}').format(enum_words([tr_name(t) for t in self.traits])),
        ]
        fr_info = _('friends:{}').format(len(self.friends)) if self.friends else ''
        en_info = _('enemies:{}').format(len(self.enemies)) if self.enemies else ''
        love_info = ''
        if self.sweetheart is not None:
            rel = _('spouse') if self.is_married else _('sweetheart')
            love_info = _('{rel}:{name}').format(
                rel=rel, name=tr_fighter_name(self.sweetheart.name)
            )
            if self.children_ages:
                love_info += _(' children:{}').format(len(self.children_ages))
        stud_info = _('students:{}').format(self.students) if self.students else ''
        if self.is_master and self.best_student is not None:
            stud_info += _(' (best: {name})').format(
                name=tr_fighter_name(self.best_student.name)
            )
        if self.is_master:
            lines.append(stud_info)
            lines.append(' '.join(w for w in (fr_info, en_info, love_info) if w))
        else:
            lines.append(
                _('rank in school: {}/{}').format(self.school_rank, self.max_school_rank)
            )
            lines.append(' '.join(w for w in (fr_info, en_info, love_info, stud_info) if w))
        lines.append(self.get_fight_statistics())
        return '\n'.join([line for line in lines if line])

    def get_students_info(self):
        school = self.get_school()
        students = sorted(
            (f for f in school if f is not self), key=lambda f: f.level, reverse=True
        )
        lines = [
            _('{name}\'s students ({num}):').format(
                name=tr_fighter_name(self.name), num=len(students)
            )
        ]
        for s in students:
            line = s.get_f_info(short=True)
            if s is self.best_student:
                line += _(' (best student)')
            lines.append(line)
        return '\n'.join(lines)

    def get_random_other_school(self):
        # avoid empty schools
        schools = [
            (s_name, members) for s_name, members in self.get_other_schools().items() if members
        ]
        return random.choice(schools)  # returns a tuple!

    def get_school(self):
        if self.is_master:
            return self.game.schools[self.new_school_name]
        return self.game.schools[self.style.name]

    def get_favorite_move(self, attack_only=False):
        """Most-used move across all fights ('' if none). With attack_only,
        consider strikes only (defensive moves like Guard otherwise dominate)."""
        usage = self.move_usage
        if attack_only:
            from kf_lib.kung_fu.moves import ALL_MOVES_DICT
            usage = {
                name: cnt
                for name, cnt in usage.items()
                if name in ALL_MOVES_DICT and ALL_MOVES_DICT[name].power
            }
        if usage:
            return max(usage.items(), key=lambda kv: kv[1])[0]
        return ''

    def get_most_feared_move(self, exclude=''):
        """Highest-tier attack move the player has; ties (same tier) are broken
        by times used across all fights. `exclude` skips a move name (e.g. the
        signature move) so the bio can name a distinct feared move. '' if the
        player has no attack moves (other than the excluded one)."""
        strikes = [m for m in self.moves if m.power and m.name != exclude]
        if not strikes:
            return ''
        max_tier = max(m.tier for m in strikes)
        top = [m for m in strikes if m.tier == max_tier]
        return max(top, key=lambda m: self.move_usage.get(m.name, 0)).name

    def get_stat(self, stat_name):
        return self.stats_dict[stat_name]

    def go_seedy(self):
        self.log(_('Goes to the seedy places of {}.').format(self.game.town_name))
        encs = encounters.SEEDY_PLACES_ENCS
        encounters.random_encounters(self, encs)
        return True  # to end turn

    def go_walk(self):
        self.log(_('Goes for a walk.'))
        encs = encounters.WALK_ENCS
        encounters.random_encounters(self, encs)
        if self.is_master and rnd() <= MASTER_GREETING_CHANCE:
            self.refresh_screen()
            self.show(
                _('Woman: Good day, Master {name}!').format(
                    name=tr_fighter_name(self.name.split()[0])
                )
            )
            self.pak()
        return True  # to end turn

    def go_work(self):
        self.log(_('Goes to work.'))
        if self.is_master:
            self.refresh_screen()
            self.show(
                _('Man: Master {name}! Why are you here?').format(
                    name=tr_fighter_name(self.name.split()[0])
                )
            )
            self.pak()
        self.earn_money(round(WAGE * self.wage_mult))
        return True  # to end turn

    def help_poor(self):
        self.log(_('Intends to help the poor.'))
        encs = encounters.HELP_POOR_ENCS
        encounters.random_encounters(self, encs)
        return True  # to end turn

    def injure(self, extent=0):
        if not extent:
            extent = rndint(1, self.max_days_to_recover)
        self.inactive += extent
        self.inact_status = 'injured'
        self.log(_('Is injured.'))

    def level_up(self, times=1):
        # do not replace with super() for now; can cause bugs; todo investigate this
        Fighter.level_up(self, times)
        self.log(_('Reaches level {}.').format(self.level))
        self.next_level = self.get_next_lv_exp()

    def log(self, text):
        self.plog.append(strip_tags(text))

    def log_new_day(self):
        self.log(_('\n\n*NEW DAY*'))
        self.log(self.game.get_date())
        self.log(self.get_p_info())

    def lose_item(self, item_name, quantity=1):
        self.inventory[item_name] -= quantity
        total = self.inventory[item_name]
        self.log(
            _('{item}: {delta}({total})').format(
                item=tr_name(item_name), delta=-quantity, total=total
            )
        )

    def obtain_item(self, item_name, quantity=1):
        if self.check_item(item_name):
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
        total = self.inventory[item_name]
        self.log(
            _('{item}: {delta}({total})').format(
                item=tr_name(item_name), delta=quantity, total=total
            )
        )
        self.change_stat('items_obtained', quantity)

    def pak(self):
        raise Exception('Not implemented.')

    def pay(self, amount):
        self.money -= amount
        self.log(_('Pays {} c.').format(amount))

    def pick_fights(self):
        self.log(_('Intends to pick fights.'))
        encs = encounters.PICK_FIGHTS_ENCS
        encounters.random_encounters(self, encs)
        return True  # to end turn

    def practice_home(self, suppress_log=False):
        if not suppress_log:
            self.log(_('Practices at home.'))
        exp = experience.HOME_TRAINING_EXP + self.home_training_exp_bonus
        self.gain_exp(max(exp, 0), silent=True)

    def practice_master(self):
        self.log(_('Practices at his school.'))
        base_exp = experience.MASTER_TRAINING_EXP
        base_exp = round(base_exp * self.school_training_exp_mult)
        min_exp = round(base_exp * 0.8)
        max_exp = round(base_exp * 1.2)
        exp = rndint(min_exp, max_exp)
        self.gain_exp(exp, silent=True)
        return True  # to end turn

    def practice_school(self):
        self.log(_('Practices at school.'))
        if self.banned_from_school:
            self.beg_master_for_mercy()
            return True  # to end turn
        if self.check_money(TUITION_FEE):
            self.pay(TUITION_FEE)
            self.change_stat('spent_on_training', TUITION_FEE)
            base_exp = experience.SCHOOL_TRAINING_EXP
            base_exp = round(base_exp * self.school_training_exp_mult)
            min_exp = round(base_exp * 0.8)
            max_exp = round(base_exp * 1.2)
            self.gain_exp(rndint(min_exp, max_exp), silent=True)
            encs = encounters.PRACTICE_SCHOOL_ENCS
            encounters.random_encounters(self, encs)
            self.check_training_injury()
            return True  # to end turn
        else:
            self.show(_('Not enough money!'))
            self.pak()

    def prepare_for_fight(self):
        super().prepare_for_fight()
        self.exp_bonuses = 0
        self.log(_('Fight:'))
        side_b = self.current_fight.side_b
        for ff in self.current_fight.side_a + side_b:
            if side_b and ff == side_b[0]:
                self.log(_('vs'))
            self.log(ff.get_f_info())

    def record_gamble_lost(self, money):
        self.log(_('Loses {}.').format(money))
        self.change_stat("gamb_lost", money)

    def record_gamble_win(self, money):
        self.log(_('Wins {}.').format(money))
        self.change_stat("gamb_won", money)

    def recover(self):
        self.inactive = 0
        self.inact_status = ''

    def refresh_best_student(self):
        school = self.game.schools.get(self.new_school_name, [])
        if school:
            self.best_student = max(school, key=lambda s: s.get_exp_worth())

    def refresh_school_rank(self):
        if self.is_master:
            self.school_rank = 'n'
            self.max_school_rank = 'a'
            return
        school = self.get_school()
        self.school_rank = school.index(self) + 1  # +1 to possibly match max_school_rank
        self.max_school_rank = len(school)

    def refresh_screen(self):
        raise Exception('Not implemented.')

    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)
        self.log(
            _('{enemy} is no longer {name}\' enemy.').format(
                enemy=tr_fighter_name(enemy.name), name=tr_fighter_name(self.name)
            )
        )
        self.game.unregister_fighter(enemy)

    def remove_trait(self, trait):
        self.traits.remove(trait)
        self.deactivate_trait(trait)
        self.write(
            _('{name} is no longer {trait}.').format(
                name=tr_fighter_name(self.name), trait=tr_name(trait)
            )
        )

    @staticmethod
    def rest():
        # don't log anything because rest gets called somewhere unexpectedly
        # self.log('{} has a rest.'.format(self.name))
        return True  # to end turn

    def set_rand_traits(self):
        self.traits = [
            get_rand_traits(1, player=self, positive=False)
        ]  # have to add traits one by one
        self.traits += [get_rand_traits(1, player=self, negative=False)]  # to avoid clashes

    def set_stat(self, stat_name, value):
        self.stats_dict[stat_name] = value

    def spectate(self, side_a, side_b):
        pass

    def steal_from(self, amount):
        self.money -= amount
        self.change_stat('stolen_from', amount)

    def teach_students(self):
        if not self.students:
            self.msg(_('You don\'t have any students yet.'))
        else:
            self.log(_('Teaches his students.'))
            self.earn_money(TUITION_FEE * self.students // 2)
            school = self.game.schools.get(self.new_school_name, [])
            max_student_lv = self.level - TAUGHT_STUDENT_LV_GAP
            improved = []
            for student in school:
                if student.level < max_student_lv and rnd() <= CH_STUDENT_LV_UP_WHEN_TAUGHT:
                    student.level_up()
                    improved.append(student)
                    self.log(
                        _('{name} reaches lv.{lv}.').format(
                            name=tr_fighter_name(student.name), lv=student.level
                        )
                    )
            self.refresh_best_student()
            if improved:
                self.write(
                    _('{} made great progress!').format(
                        enum_words([tr_fighter_name(s.name) for s in improved])
                    )
                )
            school_techs = [techniques.get_tech_obj(name) for name in self.school_techs]
            learned = []
            if school_techs:
                for student in school:
                    missing = [t for t in school_techs if t not in student.techs]
                    if missing and rnd() <= CH_STUDENT_LEARN_TECH:
                        tech = random.choice(missing)
                        student.learn_tech(tech)  # silent for NPC students
                        learned.append(
                            _('{name} learns {tech}.').format(
                                name=tr_fighter_name(student.name), tech=tr_name(tech.name)
                            )
                        )
                if learned:
                    self.write('\n'.join(learned))
            if improved or learned:
                self.pak()
            return True  # to end turn

    def use_med(self):
        self.log(_('Uses medicine to recover.'))
        self.inventory[items.MEDICINE] -= 1
        self.change_stat('healers_used', 1)
        self.recover()

    def use_item(self, item):
        self.log(_('Uses {item}.').format(item=tr_name(item)))
        self.lose_item(item)
        items.use_item(item, self)
        if item in items.FIGHT_ITEMS:
            self.change_stat('fight_items_used', 1)

    def visit_masters(self):
        """Master-only day action: convince another school's master to join the
        kung-fu federation — by persuasion (reputation) or in a spar."""
        g = self.game
        av = self.get_unallied_masters()
        if not av:
            self.msg(
                _('All the masters of {town} already acknowledge {name}.').format(
                    town=g.town_name, name=tr_fighter_name(self.name)
                )
            )
            return  # the turn is not consumed
        self.log(_('Visits other masters to promote the idea of a kung-fu federation.'))
        school_name, m = random.choice(av)
        self.show(
            _(
                '{name} visits {master}, the master of {school}, '
                'to discuss uniting the schools of {town}.'
            ).format(
                name=tr_fighter_name(self.name),
                master=tr_fighter_name(m.name),
                school=m.get_displayed_style_name(),
                town=g.town_name,
            )
        )
        persuade_chance = min(self.reputation / PERSUADE_REP_DIVISOR, MAX_PERSUADE_CH)
        if self.is_human:
            challenge = yn(
                _(
                    'Challenge {name} to a spar? ("No" = try to persuade him; '
                    'persuasion chance: {chance:.0%})'
                ).format(name=tr_fighter_name(m.name), chance=persuade_chance)
            )
        else:
            challenge = self.fight_or_not(self.get_rel_strength(m))
        if challenge:
            self.show(
                _('{name}: "Words are wind. Show me your kung-fu!"').format(
                    name=tr_fighter_name(m.name)
                )
            )
            if self.spar(m, hide_stats=False):
                self.ally_school(school_name, m)
            else:
                self.show(
                    _('{name}: "Come back when you are stronger."').format(
                        name=tr_fighter_name(m.name)
                    )
                )
                self.pak()
        elif rnd() <= persuade_chance:
            self.show(
                _(
                    '{name}: "Your reputation precedes you... Let the schools unite."'
                ).format(name=tr_fighter_name(m.name))
            )
            self.ally_school(school_name, m)
        else:
            self.show(
                _(
                    '{name}: "Why should the schools follow you? Prove yourself first."'
                ).format(name=tr_fighter_name(m.name))
            )
            self.pak()
        return True  # to end turn

    def visit_sweetheart(self):
        """Day action: court the sweetheart / spend time with the spouse."""
        p = self
        sw = p.sweetheart
        if p.is_married:
            if p.get_grown_children() and rnd() <= CHILD_PRACTICE_CHANCE:
                p.show(
                    _('{name} spends the day practicing kung-fu with the child.').format(
                        name=tr_fighter_name(p.name)
                    )
                )
                p.log(_('Practices kung-fu with the child.'))
                p.gain_exp(CHILD_EXP)
            else:
                p.show(
                    _('{name} spends a quiet day at home with {sw}.').format(
                        name=tr_fighter_name(p.name), sw=tr_fighter_name(sw.name)
                    )
                )
                p.log(
                    _('Spends the day with {sw}.').format(sw=tr_fighter_name(sw.name))
                )
        else:
            p.show(
                _('{name} spends the day with {sw}.').format(
                    name=tr_fighter_name(p.name), sw=tr_fighter_name(sw.name)
                )
            )
            p.log(_('Goes on a date with {sw}.').format(sw=tr_fighter_name(sw.name)))
            progress = rndint(1, 2)
            if p.check_money(ROMANCE_GIFT_COST) and rnd() <= 0.5:
                p.pay(ROMANCE_GIFT_COST)
                progress += 2
                p.show(
                    _('{name} brings a small gift. {sw} is delighted!').format(
                        name=tr_fighter_name(p.name), sw=tr_fighter_name(sw.name)
                    )
                )
            p.romance_progress += progress
            if p.romance_progress >= ROMANCE_PROPOSE_THRESHOLD:
                p.propose_marriage()
        p.pak()
        return True  # to end turn

    def check_romance_breakup(self):
        """Courting only: at romance_progress <= 0 the sweetheart leaves."""
        if (
            self.sweetheart is not None
            and not self.is_married
            and self.romance_progress <= 0
        ):
            sw = self.sweetheart
            self.show(
                _('{sw} is not impressed and decides to see {name} no more.').format(
                    sw=tr_fighter_name(sw.name), name=tr_fighter_name(self.name)
                )
            )
            self.log(
                _('{sw} breaks up with {name}.').format(
                    sw=tr_fighter_name(sw.name), name=tr_fighter_name(self.name)
                )
            )
            self.sweetheart = None
            self.romance_progress = 0

    def propose_marriage(self):
        p = self
        sw = p.sweetheart
        p.show(_('Propose to {sw}?').format(sw=tr_fighter_name(sw.name)))
        if not p.pursue_romance_or_not():
            p.show(
                _('{name} decides to wait a little longer.').format(
                    name=tr_fighter_name(p.name)
                )
            )
            p.log(
                _('Is about to propose to {sw}, but gets cold feet.').format(
                    sw=tr_fighter_name(sw.name)
                )
            )
            return
        p.show(
            _('{name}: "{sw}, will you marry me?"').format(
                name=tr_fighter_name(p.name), sw=tr_fighter_name(sw.name)
            )
        )
        accept_chance = min(0.9, CH_PROPOSAL_ACCEPT + p.reputation / 500)
        if rnd() <= accept_chance:
            p.is_married = True
            p.show(
                _('{sw}: "Yes! Yes, a thousand times yes!"').format(
                    sw=tr_fighter_name(sw.name)
                )
            )
            p.log(_('Marries {sw}.').format(sw=tr_fighter_name(sw.name)))
            p.add_accompl('Got Married')
        else:
            p.show(
                _('{sw}: "I... I am not ready yet. Give me some more time."').format(
                    sw=tr_fighter_name(sw.name)
                )
            )
            p.log(
                _('{sw} turns down the proposal, for now.').format(
                    sw=tr_fighter_name(sw.name)
                )
            )
            p.romance_progress = ROMANCE_PROPOSE_THRESHOLD - 4

    def win_tourn(self, prize):
        self.earn_prize(prize)
        self.change_stat('tourn_won', 1)
        self.log(_('Wins the tournament'))
        self.pak()
        if self.get_stat('tourn_won') >= 3:
            self.add_accompl('Tournament Champion')

    def write_stat(self, stat_name, value):
        """Write new stat value"""
        self.stats_dict[stat_name] = value
