import random
from typing import Any, Optional


from ..actors.fighter import Fighter
from ..actors.human_controlled_fighter import HumanControlledFighter
from ..actors.player import Player
from ..fighting import fight


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
    ):
        self.g = self.game = game  # todo decouple tournament from game
        self.num_participants = num_participants
        self.min_lv = min_lv
        self.max_lv = max_lv
        self.tourn_type = tourn_type
        self.fee = fee
        self.prize = prize if prize != 'auto' else self._calc_prize()
        self.participants: Optional[list] = None
        self.spectator: Optional[HumanControlledFighter] = None
        self.last_draw_winner: Optional[Fighter] = None
        self.winner: Any[Fighter, Player] = None
        self.current_round = 0
        self.run()

    def _calc_prize(self):
        return int(round(self.fee * self.num_participants / 2, -1))

    def _do_fight(self, f1, f2):
        f1.fight(f2, af_option=True, environment_allowed=False, items_allowed=False)
        if f1.hp <= 0 and f2.hp <= 0:
            self.last_draw_winner = wnr = random.choice((f1, f2))
            if f1.is_player or f2.is_player:
                self.g.msg(f'Draw! The judges rule the winner to be {wnr.name}.')

    def _do_rounds(self):
        participants = self.participants
        while (remaining_participants := len(participants)) > 1:
            self.current_round += 1
            self.spectator.cls()
            self.spectator.msg(
                f'Round {self.current_round}\n'
                f'tournament participants left: {remaining_participants}'
            )
            random.shuffle(participants)
            for i in range(0, remaining_participants - 1, 2):
                # if odd, one random fighter is left out, but that's ok
                f1, f2 = participants[i:i + 2]
                self._do_fight(f1, f2)
            participants[:] = [f for f in participants if f.hp > 0]
        if participants:
            self.winner = participants[0]
        else:  # in case of a draw
            self.winner = self.last_draw_winner

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
            # print('warning: invalid k in Tournament._gather_participants')
            # print(f'{participants = }, {self.participants = }, {len(av_fighters) = }, {k = }')
            # input('setting k to len(av_fighters), press Enter to continue')
            k = len(av_fighters)
        add = random.sample(av_fighters, k)
        participants += add

    def _give_prize(self):
        winner = self.winner
        self.g.msg(f'{winner.name} wins the tournament!')
        if winner.is_player:
            winner.win_tourn(self.prize)

    def run(self):
        self.g.cls()
        tourn_type_str = f'({self.tourn_type} level)' if self.tourn_type else ''
        self.g.msg(
            f'A kung-fu tournament {tourn_type_str} is organized in {self.g.town_name}. '
            f'The participation fee is {self.fee}.'
        )

        self._gather_participants()
        self.spectator = self.participants[0]
        self._show_participants()
        self._do_rounds()
        self._give_prize()

    def _show_participants(self):
        participants = self.participants
        self.g.cls()
        self.g.show('The participants are:\n')
        self.g.show(fight.get_prefight_info(participants, basic_info_only=True))
        self.g.pak()
