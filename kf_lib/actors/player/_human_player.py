from kf_lib.actors.human_controlled_fighter import HumanControlledFighter
from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name
from kf_lib.things.items import get_item_descr, MEDICINE
from kf_lib.ui import cls, menu, style, yn
from kf_lib.utils import enum_words, float_to_pcnt
from ._base_player import BasePlayer, NUM_SCHOOL_TECHS


class HumanPlayer(HumanControlledFighter, BasePlayer):
    is_human = True

    def bet_on_tourn_or_not(self):
        return yn(_('{}: Bet on the tournament?').format(tr_fighter_name(self.name)))

    def brawl_or_not(self, opp_info):
        return self.menu(
            (
                (_('"What? I\'ll teach you a lesson! ({})"').format(opp_info[1]), True),
                (_('"I\'m sorry."'), False),
            ),
            title=_('{}:').format(tr_fighter_name(self.name)),
        )

    @staticmethod
    def buy_item_or_not():
        return yn('')

    def choose_day_action(self):
        # what player can do (option lists)
        options = self.get_day_actions()
        n = len(options)
        keys = '1234567890'[:n]
        options.extend(
            [(_('Rest'), self.rest), (_('State'), self.game.state_menu)]
        )
        keys += 'rs'
        # choose what to do; choice is a function
        return self.menu(options, keys=keys, options_per_page=15)

    def choose_school_name(self):
        while True:
            school_name = input(
                _(" What is the name of {}'s school? >").format(
                    tr_fighter_name(self.name)
                )
            )
            if school_name not in self.game.schools:
                return school_name
            else:
                self.show(
                    _(' A school with the name "{}" already exists.').format(school_name)
                )

    def choose_school_techs(self):
        av = sorted((t for t in self.techs if not t.is_weapon_tech), key=lambda t: t.name)
        chosen = []
        while av and len(chosen) < NUM_SCHOOL_TECHS:
            options = [(f'{t.display_name} ({t.descr})', t) for t in av]
            options.append((_('(nothing else)'), None))
            t = self.menu(
                options, title=_('Choose the techniques your school will teach:')
            )
            if t is None:
                break
            chosen.append(t.name)
            av.remove(t)
        self.school_techs = chosen
        if chosen:
            self.write(
                _('Your school will teach {}.').format(
                    enum_words([tr_name(c) for c in chosen])
                )
            )

    def donate_or_not(self, amount):
        """Return an amount or 0"""
        options = []
        if self.check_money(amount):
            options.append(
                (
                    ngettext('Give {} coin', 'Give {} coins', amount).format(amount),
                    amount,
                )
            )
        options.append((_('Ignore'), 0))
        return self.menu(options)

    @staticmethod
    def fight_or_not(opp_info):
        """Return True if fight is chosen"""
        return menu([(_('Fight! ({})').format(opp_info[1]), True), (_('Ignore'), False)])

    @staticmethod
    def fight_or_run(opp_info, esc_chance):
        """Return True if fight is chosen"""
        return menu(
            [
                (_('Fight! ({})').format(opp_info[1]), True),
                (_('Run! ({})').format(float_to_pcnt(esc_chance)), False),
            ]
        )

    def fight_run_or_pay(self, opp_info, esc_chance, money):
        """Return 'f', 'r' or 'p'"""
        options = [
            (_('Fight! ({})').format(opp_info[1]), 'f'),
            (_('Run away ({})').format(float_to_pcnt(esc_chance)), 'r'),
        ]
        if self.check_money(money):
            options.append(
                (ngettext('Give {} coin', 'Give {} coins', money).format(money), 'p')
            )
        return menu(options)

    @staticmethod
    def gamble_or_not():
        return yn(_('Gamble?'))

    @staticmethod
    def hear_rumors_or_not():
        return yn('')

    def level_up(self, times=1):
        banner = style(_('*LEVEL UP*'), 'bold green')
        self.msg(
            _('{name}: {banner}').format(
                name=tr_fighter_name(self.name), banner=banner
            )
        )
        cls()
        self.show(banner)
        # do not change BasePlayer to super(), will cause bugs; todo investigate this
        BasePlayer.level_up(self, times)

    def place_bet_on_tourn(self, tourn_obj):
        bet_on = menu(
            [(f.get_f_info(short=True), f) for f in tourn_obj.participants],
            title=_('Who wins?'),
        )
        bet_amount = menu(
            [(str(amount), amount) for amount in self.possible_tournament_bets],
            title=_('How much to bet?'),
        )
        self.pay(bet_amount)
        return bet_on, bet_amount

    @staticmethod
    def p_match_or_not():
        return yn('')

    @staticmethod
    def pursue_romance_or_not():
        return yn('')

    def refresh_screen(self):
        cls()
        self.show(self.get_p_info())

    def rock_paper_or_scissors(self):
        return self.menu(
            [(_('Rock'), 'Rock'), (_('Paper'), 'Paper'), (_('Scissors'), 'Scissors')]
        )

    def see_day_info(self):
        cls()
        self.show(style(self.game.get_date(), 'bold'))
        self.show(self.get_p_info())

    @staticmethod
    def talk_wise_or_not():
        return yn(_('Treat the wise man to lunch and talk to him?'))

    def tourn_or_not(self):
        return yn(_('{}: Participate?').format(tr_fighter_name(self.name)))

    def use_fight_item_or_not(self):
        av_items = self.get_items(as_dict=True)
        options = ((_('Do not use items'), False),)
        options += tuple(
            (
                _('{item} ({descr}) ({count})').format(
                    item=tr_name(k), descr=get_item_descr(k), count=av_items[k]
                ),
                k,
            )
            for k in sorted(av_items.keys())
        )
        choice = menu(options, _('{} - use an item?').format(tr_fighter_name(self.name)))
        return choice

    @staticmethod
    def use_med_or_not():
        return yn(_('Use the {} medicine?').format(tr_name(MEDICINE)))
