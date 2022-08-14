import random

from kf_lib.actors import quotes
from kf_lib.actors import traits
from kf_lib.actors.fighter import Fighter
# todo refactor importing get_rand_traits
# have to import separately or .set_rand_traits doesn't work
from kf_lib.actors.traits import get_rand_traits
from kf_lib.constants.experience import (
    ACCOMPL_EXP,
    EXP_PER_LEVEL,
    HOME_TRAINING_EXP,
    MASTER_TRAINING_EXP,
    SCHOOL_TRAINING_EXP,
)
from kf_lib.game import game_stats
from kf_lib.happenings import encounters
from kf_lib.things import items
from kf_lib.utils import add_sign, enum_words, Integer, rnd, rndint


# todo refactor _base_player into specific modules

EXTREMELY_GOOD_LUCK = 20
EXTREMELY_BAD_LUCK = 1
LUCK_ACCOMPLISHMENT_THRESHOLD = 10
MASTER_GREETING_CHANCE = 0.1
TUITION_FEE = 20
WAGE = 50


# todo Epic Gambler accomplishment


class BasePlayer(Fighter):
    is_player = True
    savable_atts = '''exp home_training_exp_mult is_master new_school_name money reputation 
    inactive inact_status inventory ended_turn accompl accompl_dates stats_dict'''.split()
    possible_tournament_bets = (10, 25, 50, 100)
    quotes = 'hero'

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
        super().__init__(
            name=name,
            style=style,
            level=level,
            atts_tuple=atts_tuple,
            tech_names=tech_names,
            move_names=move_names,
            rand_atts_mode=rand_atts_mode,
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
        self.home_training_exp_mult = 1.0
        self.item_is_found = 0.01
        self.item_is_lost = 0.01
        self.master_joins_fight = 0.5
        self.max_days_to_recover = 7
        self.max_num_friends = 8
        self.next_lv_exp_mult = 1.0
        self.traits = []
        self.school_training_exp_mult = 1.0
        self.schoolmates_help = 0.5
        self.thief_steals = 0.3
        self.training_injury = 0.05
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
        self.accompl = []
        self.accompl_dates = []
        self.is_master = False
        self.new_school_name = ''
        self.school_rank = None
        self.max_school_rank = None
        self.students = 0
        self.best_student = None
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
            self.write(f'Accomplishment: {label}')
            self.gain_exp(ACCOMPL_EXP)
            self.pak()

    def add_enemy(self, enemy):
        self.enemies.append(enemy)
        self.game.register_fighter(enemy)
        self.log('{} is now {}\' enemy.'.format(enemy.name, self.name))

    def add_friend(self, obj):
        if len(self.friends) < self.max_num_friends:
            self.friends.append(obj)
            self.log('{} is now {}\' friend.'.format(obj.name, self.name))

    def add_students(self, num_stud):
        self.students += num_stud
        new_students = []
        school = self.game.schools[self.new_school_name]
        for i in range(num_stud):
            new_student = self.game.get_new_student(self.style.name)
            new_students.append(new_student)
            school.append(new_student)
            self.game.register_fighter(new_student)
        if num_stud > 1:
            self.log('{} students join {}\'s school.'.format(num_stud, self.name))
        else:
            self.log('A new student joins {}\'s school.'.format(self.name))
        self.log('\n'.join((str(s) for s in new_students)))

    def add_trait(self, trait):
        """NB: differs from the activate_trait method.
        Should be used only for adding NEW traits in-game."""
        opp_trait = traits.get_opposite_trait(trait)
        if trait not in self.traits and opp_trait not in self.traits:
            self.traits.append(trait)
            self.activate_trait(trait)
            self.write(f'{self.name} becomes {trait}.')
        else:
            raise Exception(
                'Cannot add trait "{}" to player {}\'s traits: {}'.format(
                    trait, self.name, self.traits
                )
            )

    def buy_item(self, item, price):
        self.pay(price)
        self.log(f'Buys {item} for {price}.')
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
        self.msg('{}: {}'.format(att, add_sign(amount)))

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
                if len(allies) > 1:
                    s = ''
                else:
                    s = 's'
                a_str = enum_words([a.name for a in allies])
                self.msg('{} join{} the fight on {}\'s side.'.format(a_str, s, self.name))
            return allies

    def check_fight_items(self):
        """Return True if player has any items usable in fights"""
        for k, v in self.inventory.items():
            if k in items.FIGHT_ITEMS and v > 0:
                return True

    def check_help(self, allies=True, master=True, impr_wp=True, school=True):
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
        x = random.choice(hlp)
        if x == 'a':
            p.allies = p.check_allies()
        elif x == 'm':
            if rnd() <= self.master_joins_fight:
                m = p.get_master()
                p.show('{}: "What\'s going on here?"'.format(m.name))
                p.log(f"{m.name} joins the fight on {p.name}'s side.")
                p.allies = [m]
                p.pak()
        elif x == 'w':
            if rnd() <= self.grab_improvised_weapon:
                p.arm_improv()
                p.show(f'{p.name} grabs an improvised weapon!')
                p.log('Grabs an improvised weapon.')
                p.pak()
        elif x == 's':
            if rnd() <= self.schoolmates_help:
                n = random.choice((2, 3))
                av_mates = [f for f in self.get_school() if not f.is_player]
                mates = random.sample(av_mates, n)
                a_str = enum_words([f.name for f in mates])
                p.allies = mates
                self.msg(
                    '{}, who were passing by, join the fight on {}\'s side.'.format(
                        a_str, self.name
                    )
                )

    def check_injured(self):
        return self.inact_status == 'injured'

    def check_item(self, item_name):
        return self.inventory.get(item_name, 0)

    def check_luck(self, silent=False):
        outcome = random.randint(EXTREMELY_BAD_LUCK, EXTREMELY_GOOD_LUCK)
        if outcome == EXTREMELY_BAD_LUCK:
            if not silent:
                self.show('BAD LUCK!')
            self.change_stat('bad_luck', 1)
            if self.get_stat('bad_luck') >= LUCK_ACCOMPLISHMENT_THRESHOLD:
                self.add_accompl('Unlucky Devil')
            return -1
        elif outcome == EXTREMELY_GOOD_LUCK:
            if not silent:
                self.show('LUCKY!')
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
                if len(partners) > 1:
                    s = ''
                else:
                    s = 's'
                p_str = enum_words([p.name for p in partners])
                self.write('{} join{} {}\'s training session.'.format(p_str, s, self.name))
            return partners

    def check_training_injury(self):
        if rnd() <= self.training_injury:
            q = random.choice(quotes.TRAINING_INJURY)
            self.show(f'{self.name}: "{q}"')
            self.msg(f'{self.name} gets injured during training.')
            self.injure(1)

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
            self.log('Doesn\'t give anything.')
        else:
            self.log(f'Donates {amount} c.')
            self.money -= amount
            self.change_stat('donated', amount)
            self.gain_rep(round(amount * 0.2))

    def drink(self):
        self.log('Drinks wine.')
        self.inactive += 1
        self.inact_status = 'sick'
        self.change_stat('got_drunk', 1)

    def earn_money(self, amount, silent=False):
        self.money += amount
        if not silent:
            self.change_stat('money_earned', amount)
            self.log(f'Earns {amount} c.')

    def earn_prize(self, amount):
        self.money += amount
        self.change_stat('prize_money_earned', amount)
        self.write(f'{self.name} earns a {amount}-coin prize.')

    def earn_reward(self, amount):
        self.money += amount
        self.change_stat('rew_money_earned', amount)
        self.write(f'{self.name} earns a {amount}-coin reward.')

    def end_turn(self):
        pass

    def enter_tourn(self, fee):
        self.log('Takes part in a kung-fu tournament.')
        self.pay(fee)
        self.change_stat('num_tourn', 1)

    def fight_crime(self):
        self.log('Intends to fight crime.')
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
            self.show(f'{self.name} gains {amount} exp.')
            self.log(f'Gains {amount} exp.')
        self.exp += amount
        while self.exp >= self.next_level:
            self.level_up()

    def gain_rep(self, amount):
        self.reputation += amount
        self.log('Reputation: {} ({})'.format(add_sign(amount), self.reputation))

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
            ('Practice at school', self.practice_school)
            if not self.is_master
            else ('Practice', self.practice_master),
            ('Go to work', self.go_work),
            ('Buy items', self.buy_items),
            ('Fight crime', self.fight_crime),
            ('Help the poor', self.help_poor),
            ('Pick fights', self.pick_fights)
            if not self.is_master
            else ('Teach students', self.teach_students),
            ('Go to seedy places', self.go_seedy),
            ('Go for a walk', self.go_walk),
            # ('Dummy', self.fight_dummy)
        ]
        return ops

    def get_fame(self):
        return (
            self.get_stat('tourn_won') + len(self.accompl) + (self.get_stat('fights_won') // 10)
        ) * 0.01

    def get_fight_statistics(self):
        return 'Fights/Wins/KOs: {}/{}/{}'.format(
            self.get_stat('num_fights'), self.get_stat('fights_won'), self.get_stat('num_kos')
        )

    def get_inact_info(self):
        s = '{} is {} and needs {} day{} to recover.'.format(
            self.name, self.inact_status, self.inactive, 's' if self.inactive > 1 else ''
        )
        self.log(s)
        return s

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
                lines.append(f'{k}: {v}')
        lines = ['{}\'s items:'.format(self.name)] + sorted(lines)
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
        return f'{s.name} lv.{s.level} exp:{s.exp}/{s.next_level}\nmoney:{s.money}\n'

    def get_p_info_verbose(self):
        lines = [
            self.get_f_info(),
            f'exp:{self.exp}/{self.next_level} money:{self.money}',
            f'traits: {enum_words(self.traits)}',
            f'rank in school: {self.school_rank}/{self.max_school_rank}',
        ]
        fr_info = 'friends:{}'.format(len(self.friends)) if self.friends else ''
        en_info = 'enemies:{}'.format(len(self.enemies)) if self.enemies else ''
        stud_info = f'students:{self.students}' if self.students else ''
        lines.append(' '.join(w for w in (fr_info, en_info, stud_info) if w))
        lines.append(self.get_fight_statistics())
        return '\n'.join([line for line in lines if line])

    def get_random_other_school(self):
        # avoid empty schools
        schools = [
            (s_name, members) for s_name, members in self.get_other_schools().items() if members
        ]
        return random.choice(schools)  # returns a tuple!

    def get_school(self):
        return self.game.schools[self.style.name]

    def get_stat(self, stat_name):
        return self.stats_dict[stat_name]

    def go_seedy(self):
        self.log(f'Goes to the seedy places of {self.game.town_name}.')
        encs = encounters.SEEDY_PLACES_ENCS
        encounters.random_encounters(self, encs)
        return True  # to end turn

    def go_walk(self):
        self.log('Goes for a walk.')
        encs = encounters.WALK_ENCS
        encounters.random_encounters(self, encs)
        if self.is_master and rnd() <= MASTER_GREETING_CHANCE:
            self.refresh_screen()
            self.show(f'Woman: Good day, Master {self.name.split()[0]}!')
            self.pak()
        return True  # to end turn

    def go_work(self):
        self.log('Goes to work.')
        if self.is_master:
            self.refresh_screen()
            self.show(f'Man: Master {self.name.split()[0]}! Why are you here?')
            self.pak()
        self.earn_money(round(WAGE * self.wage_mult))
        return True  # to end turn

    def help_poor(self):
        self.log('Intends to help the poor.')
        encs = encounters.HELP_POOR_ENCS
        encounters.random_encounters(self, encs)
        return True  # to end turn

    def injure(self, extent=0):
        if not extent:
            extent = rndint(1, self.max_days_to_recover)
        self.inactive += extent
        self.inact_status = 'injured'
        self.log('Is injured.')

    def level_up(self, times=1):
        # do not replace with super() for now; can cause bugs; todo investigate this
        Fighter.level_up(self, times)
        self.log(f'Reaches level {self.level}.')
        self.next_level = self.get_next_lv_exp()

    def log(self, text):
        self.plog.append(text)

    def log_new_day(self):
        self.log('\n\n*NEW DAY*')
        self.log(self.game.get_date())
        self.log(self.get_p_info())

    def lose_item(self, item_name, quantity=1):
        self.inventory[item_name] -= quantity
        total = self.inventory[item_name]
        self.log(f'{item_name}: {-quantity}({total})')

    def obtain_item(self, item_name, quantity=1):
        if self.check_item(item_name):
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
        total = self.inventory[item_name]
        self.log(f'{item_name}: {quantity}({total})')
        self.change_stat('items_obtained', quantity)

    def pak(self):
        raise Exception('Not implemented.')

    def pay(self, amount):
        self.money -= amount
        self.log(f'Pays {amount} c.')

    def pick_fights(self):
        self.log('Intends to pick fights.')
        encs = encounters.PICK_FIGHTS_ENCS
        encounters.random_encounters(self, encs)
        return True  # to end turn

    def practice_home(self, suppress_log=False):
        if not suppress_log:
            self.log('Practices at home.')
        exp = round(HOME_TRAINING_EXP * self.home_training_exp_mult)
        self.gain_exp(exp, silent=True)

    def practice_master(self):
        self.log('Practices at his school.')
        base_exp = MASTER_TRAINING_EXP
        base_exp = round(base_exp * self.school_training_exp_mult)
        min_exp = round(base_exp * 0.8)
        max_exp = round(base_exp * 1.2)
        exp = rndint(min_exp, max_exp)
        self.gain_exp(exp, silent=True)
        return True  # to end turn

    def practice_school(self):
        self.log('Practices at school.')
        if self.check_money(TUITION_FEE):
            self.pay(TUITION_FEE)
            self.change_stat('spent_on_training', TUITION_FEE)
            base_exp = SCHOOL_TRAINING_EXP
            base_exp = round(base_exp * self.school_training_exp_mult)
            min_exp = round(base_exp * 0.8)
            max_exp = round(base_exp * 1.2)
            self.gain_exp(rndint(min_exp, max_exp), silent=True)
            encs = encounters.PRACTICE_SCHOOL_ENCS
            encounters.random_encounters(self, encs)
            self.check_training_injury()
            return True  # to end turn
        else:
            self.show('Not enough money!')
            self.pak()

    def prepare_for_fight(self):
        super().prepare_for_fight()
        self.exp_bonuses = 0
        self.log('Fight:')
        for ff in self.current_fight.side_a + self.current_fight.side_b:
            if ff == self.current_fight.side_b[0]:
                self.log('vs')
            self.log(ff.get_f_info())

    def record_gamble_lost(self, money):
        self.log(f"Loses {money}.")
        self.change_stat("gamb_lost", money)

    def record_gamble_win(self, money):
        self.log(f"Wins {money}.")
        self.change_stat("gamb_won", money)

    def recover(self):
        self.inactive = 0
        self.inact_status = ''

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
        self.log('{} is no longer {}\' enemy.'.format(enemy.name, self.name))
        self.game.unregister_fighter(enemy)

    def remove_trait(self, trait):
        self.traits.remove(trait)
        self.deactivate_trait(trait)
        self.write(f'{self.name} is no longer {trait}.')

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
            self.msg('You don\'t have any students yet.')
        else:
            self.log('Teaches his students.')
            self.earn_money(TUITION_FEE * self.students // 2)
            return True  # to end turn

    def use_med(self):
        self.log('Uses medicine to recover.')
        self.inventory[items.MEDICINE] -= 1
        self.change_stat('healers_used', 1)
        self.recover()

    def use_item(self, item):
        self.log(f'Uses {item}.')
        self.lose_item(item)
        items.use_item(item, self)
        if item in items.FIGHT_ITEMS:
            self.change_stat('fight_items_used', 1)

    def win_tourn(self, prize):
        self.earn_prize(prize)
        self.change_stat('tourn_won', 1)
        self.log('Wins the tournament')
        self.pak()
        if self.get_stat('tourn_won') >= 3:
            self.add_accompl('Tournament Champion')

    def write_stat(self, stat_name, value):
        """Write new stat value"""
        self.stats_dict[stat_name] = value
