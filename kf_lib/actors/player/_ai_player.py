import random


from ._base_player import BasePlayer
from ...ui._interactive import pak
from ...ui import cls
from ...utils._random import rnd


class AIPlayer(BasePlayer):
    is_human = False

    acceptable_fight_threshold = 1.2
    acceptable_escape_risk = 0.6
    brawl_chance = 0.25
    buy_item_chance = 0.5
    donate_chance = 0.5
    gamble_chance = 0.5
    master_practice_chance = 0.6
    min_days_use_med = 2
    min_non_master_money = 175
    min_master_money = 150
    min_students_to_teach = 5
    non_master_practice_chance = 0.9

    def bet_on_tourn_or_not(self):
        return rnd() <= self.gamble_chance

    def brawl_or_not(self, opp_info):
        return rnd() <= self.brawl_chance and opp_info[0] <= self.acceptable_fight_threshold

    def buy_item_or_not(self):
        return rnd() <= self.buy_item_chance

    def choose_day_action(self):
        if not self.is_master:
            if self.money < self.min_non_master_money:
                return self.go_work
            else:
                if rnd() <= self.non_master_practice_chance:
                    return self.practice_school
                else:
                    return self.go_walk
        else:
            if self.money < self.min_master_money:
                if self.students >= self.min_students_to_teach:
                    return self.teach_students
                else:
                    return self.go_work
            else:
                if rnd() <= self.master_practice_chance:
                    return self.practice_master
                else:
                    return self.go_walk

    def choose_school_name(self):
        return '{}\'s school'.format(self.name)

    def cls(self):
        pass

    def donate_or_not(self, amount):
        """Return an amount or 0"""
        if rnd() <= self.donate_chance:
            return amount
        else:
            return 0

    def fight_or_not(self, opp_info):
        """Return True if fight is chosen"""
        return opp_info[0] <= self.acceptable_fight_threshold

    def fight_or_run(self, opp_info, esc_chance):
        """Return True if fight is chosen"""
        return opp_info[0] <= self.acceptable_fight_threshold or esc_chance < 0.5

    def fight_run_or_pay(self, opp_info, esc_chance, money):
        """Return 'f', 'r' or 'p'"""
        if not self.check_money(money):
            return 'f' if self.fight_or_run(opp_info, esc_chance) else 'r'
        else:
            if self.fight_or_not(opp_info):
                return 'f'
            elif self.run_or_not(esc_chance):
                return 'r'
            else:
                return 'p'

    def gamble_or_not(self):
        return rnd() <= self.gamble_chance

    @staticmethod
    def hear_rumors_or_not():
        return False

    def msg(self, text, align=False):
        self.write(text, align=align)

    @staticmethod
    def p_match_or_not():
        return True

    def pak(self):
        pass

    def place_bet_on_tourn(self, tourn_obj):
        max_lv = max(f.level for f in tourn_obj.participants)
        choose_from = [f for f in tourn_obj.participants if f.level == max_lv]
        bet_on = random.choice(choose_from)
        bet_amount = random.choice(self.possible_tournament_bets)
        self.pay(bet_amount)
        return bet_on, bet_amount

    def refresh_screen(self):
        pass

    @staticmethod
    def rock_paper_or_scissors():
        return random.choice(('Rock', 'Paper', 'Scissors'))

    def run_or_not(self, esc_chance):
        """Return True if run is chosen"""
        return esc_chance >= self.acceptable_escape_risk

    def see_day_info(self):
        pass

    @staticmethod
    def talk_wise_or_not():
        return True  # always talk to wise men

    @staticmethod
    def tourn_or_not():
        return True

    def use_fight_item_or_not(self):
        own_side_pwr = self.get_allies_power()
        other_side_pwr = self.get_opponents_power()
        if other_side_pwr > own_side_pwr:
            av_items = self.get_items()
            choice = random.choice(av_items)
            return choice

    def use_med_or_not(self):
        if self.inactive >= self.min_days_use_med:
            return True
        else:
            return False

    def write(self, text, align=False):
        self.log(text)


class BaselineAIP(AIPlayer):
    def choose_day_action(self):
        actions = [a[1] for a in self.get_day_actions()]
        return random.choice(actions)


class LazyAIP(AIPlayer):
    non_master_practice_chance = 0.3
    master_practice_chance = 0.2
    gamble_chance = 0.7


class SmartAIP(AIPlayer):
    acceptable_fight_threshold = 1.1
    acceptable_escape_risk = 0.7
    brawl_chance = 0
    buy_med_chance = 100
    continue_gambling_chance = 0
    drink_chance = 0
    gamble_chance = 0.2
    master_practice_chance = 0.5
    min_days_use_med = 3
    min_non_master_money = 175
    min_master_money = 150
    min_students_to_teach = 5
    non_master_practice_chance = 0.8


class SmartAIPVisible(SmartAIP):
    def cls(self):
        cls()

    def end_turn(self):
        print(f'\n---{self.name} ends his turn---')
        pak()

    def log(self, text):
        self.plog.append(text)
        print(text)
        pak()

    def log_new_day(self):
        self.plog.append('\n\n*NEW DAY*')
        self.plog.append(self.game.get_date())
        self.plog.append(self.get_p_info())

    def see_day_info(self):
        cls()
        print(f'---{self.name}\'s turn---\n')
        print(
            f'{self.style.name} lv.{self.level} exp:{self.exp}/{self.next_level}\n'
            f'money:{self.money}\n'
        )


class VanillaAIP(AIPlayer):
    pass


ALL_AI_PLAYERS = (LazyAIP, SmartAIP, VanillaAIP, BaselineAIP)
