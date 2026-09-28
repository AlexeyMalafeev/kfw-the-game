import random
from typing import Any, Dict, Optional

from kf_lib.actors.fighter import Fighter
from kf_lib.actors.human_controlled_fighter import HumanControlledFighter
from kf_lib.actors.player import AIPlayer, HumanPlayer
from kf_lib.fighting import fight
from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name


BET_REPUTATION_PENALTY = -3
STUDENT_TOURN_WIN_REP = 3
STUDENT_TOURN_WINS_ACCOMPL = 3


class Tournament(object):
    def __init__(
            self,
            game,
            num_participants: int = 8,
            min_lv: int = 1,
            max_lv: int = 5,
            tourn_type: str = '',
            fee: int = 100,
            prize: str = 'auto',
            ffa: bool = False,
    ):
        self.g = self.game = game  # todo decouple tournament from game
        self.num_participants = num_participants
        self.min_lv = min_lv
        self.max_lv = max_lv
        self.tourn_type = tourn_type
        self.fee = fee
        self.prize = prize if prize != 'auto' else self._calc_prize()
        self.ffa = ffa
        self.participants: list = []
        self.spectator: Optional[HumanControlledFighter] = None
        # player_obj: (who_will_win, money_bet)
        self.bets: Dict[Optional[AIPlayer, HumanPlayer], tuple] = {}
        self.winner: Any[Fighter, Optional[AIPlayer, HumanPlayer]] = None
        self.current_round = 0
        self.run()

    def _calc_prize(self):
        return int(round(self.fee * self.num_participants / 2, -1))

    def _do_battle_royale(self):
        self.current_round = 1
        if len(self.participants) < 2:
            # no melee makes sense; the only participant (if any) wins by default
            self.winner = self.participants[0] if self.participants else None
            return
        self.spectator.cls()
        self.spectator.msg(
            ngettext(
                'All {} participants fight at once — last man standing wins!',
                'All {} participants fight at once — last man standing wins!',
                len(self.participants),
            ).format(len(self.participants))
        )
        fight_obj = fight.free_for_all(
            self.participants,
            environment_allowed=False,
            items_allowed=False,
            return_fight_obj=True,
        )
        if fight_obj.winners:
            self.winner = fight_obj.winners[0]

    def _do_rounds(self):
        if self.ffa:
            self._do_battle_royale()
            return
        remaining_participants = self.participants[:]
        n_remaining_participants = len(remaining_participants)
        while n_remaining_participants > 1:
            self.current_round += 1
            self.spectator.cls()
            self.spectator.msg(
                ngettext(
                    'Round {round}\ntournament participants left: {left}',
                    'Round {round}\ntournament participants left: {left}',
                    n_remaining_participants,
                ).format(
                    round=self.current_round, left=n_remaining_participants
                )
            )
            random.shuffle(remaining_participants)
            winners_list = []
            for i in range(0, n_remaining_participants, 2):
                # if odd, one random fighter automatically joins next round
                f1 = remaining_participants[i]
                try:
                    f2 = remaining_participants[i + 1]
                except IndexError:
                    winners_list.append(f1)
                    break
                fight_obj = fight.fight(f1, f2,
                                        environment_allowed=False,
                                        items_allowed=False,
                                        return_fight_obj=True,
                                        )
                winners_list.extend(fight_obj.winners)
            remaining_participants = winners_list
            n_remaining_participants = len(remaining_participants)
        if remaining_participants:
            self.winner = remaining_participants[0]
        # else: a drawn final (mutual KO) — no winner, like a battle-royale draw

    def _gather_participants(self):
        # player participants
        self.participants = participants = []
        for p in self.g.get_act_players():
            if not p.check_lv(self.min_lv, self.max_lv):
                continue
            if p.tourn_or_not():
                p.enter_tourn(self.fee)
                participants.append(p)
            if len(participants) == self.num_participants:  # for crowds of players
                break

        # known fighters
        pool = list(self.g.masters.values())
        pool += [f for s in self.g.schools.values() for f in s]
        av_fighters = [f for f in pool if
                       f.check_lv(self.min_lv, self.max_lv) and not f.is_player]
        k = self.num_participants - len(participants)
        if k > len(av_fighters) or k < 0:
            k = len(av_fighters)
        add = random.sample(av_fighters, k)
        participants += add

    def _give_prize(self):
        winner = self.winner
        if winner is None:
            self.g.msg(_('The tournament ends with no winner!'))
            return
        self.g.msg(_('{} wins the tournament!').format(tr_fighter_name(winner.name)))
        if winner.is_player:
            winner.win_tourn(self.prize)
            if self.ffa:
                winner.add_accompl('Battle Royale Champion')

    def _place_bets(self):
        for p in self.g.get_act_players():
            if p.bet_on_tourn_or_not():
                bet_on, bet_amount = p.place_bet_on_tourn(self)
                self.bets[p] = bet_on, bet_amount
                self.g.msg(
                    ngettext(
                        '{name}: {bet} coin says {opponent} wins!',
                        '{name}: {bet} coins says {opponent} wins!',
                        bet_amount,
                    ).format(
                        name=tr_fighter_name(p.name),
                        bet=bet_amount,
                        opponent=tr_fighter_name(bet_on.name),
                    )
                )
                # gambling is not honorable (wuxia morals) — win or lose
                p.gain_rep(BET_REPUTATION_PENALTY)
            else:
                pass
                # if not p.is_human:
                #     print(f'DEBUG: {p.name} doesn\'t bet')

    def _reward_masters(self):
        """A player-master shares the glory when his students fight in the tournament."""
        for p in self.g.players:
            if not p.is_master:
                continue
            school = self.g.schools.get(p.new_school_name, [])
            for f in self.participants:
                if not f.is_player and f in school:
                    p.log(
                        _('{} represents the school at the tournament.').format(
                            tr_fighter_name(f.name)
                        )
                    )
            winner = self.winner
            if winner is not None and not winner.is_player and winner in school:
                p.write(
                    _("{name}'s student {student} wins the tournament!").format(
                        name=tr_fighter_name(p.name),
                        student=tr_fighter_name(winner.name),
                    )
                )
                p.gain_rep(STUDENT_TOURN_WIN_REP)
                p.change_stat('students_tourn_won', 1)
                if p.get_stat('students_tourn_won') >= STUDENT_TOURN_WINS_ACCOMPL:
                    p.add_accompl('Master of Champions')

    def _resolve_bets(self):
        for p in sorted(self.bets, key=self.g.players.index):
            bet_on, bet_amount = self.bets[p]
            if self.winner is bet_on:
                win_mult = max((self.current_round, 1.5))  # 1.5 is for the 1 round edge case
                money_won = int(bet_amount * win_mult)
                p.money += money_won
                self.g.msg(
                    ngettext(
                        '{name} wins {money} coin with his bet!',
                        '{name} wins {money} coins with his bet!',
                        money_won,
                    ).format(name=tr_fighter_name(p.name), money=money_won)
                )
                p.record_gamble_win(money_won)
            else:
                p.record_gamble_lost(bet_amount)

    def run(self):
        self.g.cls()
        if self.tourn_type:
            tourn_type_str = _('({} level)').format(tr_name(self.tourn_type))
        else:
            tourn_type_str = ''
        format_str = (
            _(' It is a battle royale: all participants fight at once, last man standing wins!')
            if self.ffa
            else ''
        )
        self.g.msg(
            _(
                'A kung-fu tournament {type_str} is organized in {town}.{format_str} '
                'The participation fee is {fee}.'
            ).format(
                type_str=tourn_type_str,
                town=self.g.town_name,
                format_str=format_str,
                fee=self.fee,
            )
        )

        self._gather_participants()
        if not self.participants:
            self.g.msg(_('...but nobody shows up, so the tournament is canceled.'))
            return
        self.spectator = self.participants[0]
        self._show_participants()
        self._place_bets()
        self._do_rounds()
        self._give_prize()
        self._reward_masters()
        self._resolve_bets()

    def _show_participants(self):
        participants = self.participants
        self.g.cls()
        self.g.show(_('The participants are:\n'))
        self.g.show(fight.get_prefight_info(participants, basic_info_only=True))
        self.g.pak()
