from ._base_fight import BaseFight


class AutoFight(BaseFight):
    """Has all fight constants but no output of what happens during the fight."""

    def __init__(
        self,
        side_a,
        side_b,
        environment_allowed=True,
        items_allowed=True,
        win_messages=None,
        school_display=False,
    ):
        super().__init__(side_a, side_b, environment_allowed=environment_allowed)
        self.items_allowed = items_allowed
        self.win_messages = win_messages
        self.school_display = school_display
        self.players = [f for f in self.all_fighters if f.is_player]
        humans = [f for f in self.all_fighters if f.is_human]
        if humans:
            self.main_player = humans[0]
        elif self.players:
            self.main_player = self.players[0]
        else:
            self.main_player = self.side_a[0]
        self.handle_items()
        self.prepare_fighters()
        self.handle_prefight_quote()
        self.fight_loop()
        self.disarm_all()
        self.cancel_items_for_all()
        if self.main_player.is_human:
            self.show_win_message()
            self.post_fight_menu()
        if self.main_player.is_player:
            self.handle_injuries()
            self.handle_gossip()
            self.give_exp()
            self.handle_accompl()
