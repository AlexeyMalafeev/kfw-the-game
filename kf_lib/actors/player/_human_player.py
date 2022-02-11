from ._base_player import BasePlayer
from ..human_controlled_fighter import HumanControlledFighter
from ...things.items import get_item_descr, MEDICINE
from ...utils.utilities import cls, float_to_pcnt, menu, yn


class HumanPlayer(HumanControlledFighter, BasePlayer):
    is_human = True

    def bet_on_tourn_or_not(self):
        return yn(f'{self.name}: Bet on the tournament?')

    def brawl_or_not(self, opp_info):
        return self.menu(
            (
                ('"What? I\'ll teach you a lesson! ({})"'.format(opp_info[1]), True),
                ('"I\'m sorry."', False),
            ),
            title=f'{self.name}:',
        )

    @staticmethod
    def buy_item_or_not():
        return yn('')

    def choose_day_action(self):
        # what player can do (option lists)
        options = self.get_day_actions()
        n = len(options)
        keys = ''.join([str(x) for x in list(range(1, n + 1))])
        options.extend(
            [('Rest', self.rest), ('State', self.game.state_menu), ('Test', self.game.test)]
        )
        keys += 'rst'
        # choose what to do; choice is a function
        return self.menu(options, keys=keys, options_per_page=15)

    def choose_school_name(self):
        while True:
            school_name = input(' What is the name of {}\'s school? >'.format(self.name))
            if school_name not in self.game.schools:
                return school_name
            else:
                self.show(f' A school with the name "{school_name}" already exists.')

    def donate_or_not(self, amount):
        """Return an amount or 0"""
        options = []
        if self.check_money(amount):
            options.append((f'Give {amount} coins', amount))
        options.append(('Ignore', 0))
        return self.menu(options)

    @staticmethod
    def fight_or_not(opp_info):
        """Return True if fight is chosen"""
        return menu([(f'Fight! ({opp_info[1]})', True), ('Ignore', False)])

    @staticmethod
    def fight_or_run(opp_info, esc_chance):
        """Return True if fight is chosen"""
        return menu(
            [
                (f'Fight! ({opp_info[1]})', True),
                ('Run! ({})'.format(float_to_pcnt(esc_chance)), False),
            ]
        )

    def fight_run_or_pay(self, opp_info, esc_chance, money):
        """Return 'f', 'r' or 'p'"""
        options = [
            (f'Fight! ({opp_info[1]})', 'f'),
            ('Run away ({})'.format(float_to_pcnt(esc_chance)), 'r'),
        ]
        if self.check_money(money):
            options.append((f'Give {money} coins', 'p'))
        return menu(options)

    @staticmethod
    def gamble_or_not():
        return yn("Gamble?")

    @staticmethod
    def hear_rumors_or_not():
        return yn('')

    def level_up(self, times=1):
        self.msg(f'{self.name}: *LEVEL UP*')
        self.cls()
        self.show('*LEVEL UP*')
        super().level_up(times)

    def place_bet_on_tourn(self, tourn_obj):
        bet_on = menu(
            [(f.get_f_info(short=True), f) for f in tourn_obj.participants],
            title='Who wins?',
        )
        bet_amount = menu([(str(amount), amount) for amount in self.possible_tournament_bets],
                          title='How much to bet?')
        self.pay(bet_amount)
        return bet_on, bet_amount

    @staticmethod
    def p_match_or_not():
        return yn('')

    def refresh_screen(self):
        cls()
        self.show(self.get_p_info())

    def rock_paper_or_scissors(self):
        return self.menu(('Rock', 'Paper', 'Scissors'))

    def see_day_info(self):
        cls()
        self.show(self.game.get_date())
        self.show(self.get_p_info())

    @staticmethod
    def talk_wise_or_not():
        return yn('Treat the wise man to lunch and talk to him?')

    def tourn_or_not(self):
        return yn(f'{self.name}: Participate?')

    def use_fight_item_or_not(self):
        av_items = self.get_items(as_dict=True)
        options = (('Do not use items', False),)
        options += tuple(
            (f'{k} ({get_item_descr(k)}) ({av_items[k]})', k)
            for k in sorted(av_items.keys())
        )
        choice = menu(options, f'{self.name} - use an item?')
        return choice

    @staticmethod
    def use_med_or_not():
        return yn(f'Use the {MEDICINE} medicine?')
