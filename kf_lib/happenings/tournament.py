import random
from typing import Any, Dict, Optional

from kf_lib.actors.fighter import Fighter
from kf_lib.actors.human_controlled_fighter import HumanControlledFighter
from kf_lib.actors.player import AIPlayer, HumanPlayer
from kf_lib.fighting import fight


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
            f'All {len(self.participants)} participants fight at once — last man standing wins!'
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
                f'Round {self.current_round}\n'
                f'tournament participants left: {n_remaining_participants}'
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
        else:
            raise NotImplementedError('The no-winner case in tournaments is not implemented')

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
            self.g.msg('The tournament ends with no winner!')
            return
        self.g.msg(f'{winner.name} wins the tournament!')
        if winner.is_player:
            winner.win_tourn(self.prize)
            if self.ffa:
                winner.add_accompl('Battle Royale Champion')

    def _place_bets(self):
        for p in self.g.get_act_players():
            if p.bet_on_tourn_or_not():
                bet_on, bet_amount = p.place_bet_on_tourn(self)
                self.bets[p] = bet_on, bet_amount
                self.g.msg(f'{p.name}: {bet_amount} coins says {bet_on.name} wins!')
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
                    p.log(f'{f.name} represents the school at the tournament.')
            winner = self.winner
            if winner is not None and not winner.is_player and winner in school:
                p.write(f'{p.name}\'s student {winner.name} wins the tournament!')
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
                self.g.msg(f'{p.name} wins {money_won} coins with his bet!')
                p.record_gamble_win(money_won)
            else:
                p.record_gamble_lost(bet_amount)

    def run(self):
        self.g.cls()
        tourn_type_str = f'({self.tourn_type} level)' if self.tourn_type else ''
        format_str = (
            ' It is a battle royale: all participants fight at once, last man standing wins!'
            if self.ffa else ''
        )
        self.g.msg(
            f'A kung-fu tournament {tourn_type_str} is organized in {self.g.town_name}.{format_str} '
            f'The participation fee is {self.fee}.'
        )

        self._gather_participants()
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
        self.g.show('The participants are:\n')
        self.g.show(fight.get_prefight_info(participants, basic_info_only=True))
        self.g.pak()
