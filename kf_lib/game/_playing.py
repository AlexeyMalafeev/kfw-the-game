from ._base_game import BaseGame


class Playing(BaseGame):
    def game_loop(self):
        self.chosen_quit = False
        self.chosen_load = False
        while True:
            for p in self.players:
                if p.ended_turn:
                    continue
                self.current_player = p
                while True:
                    # output info if human player
                    p.see_day_info()
                    # inactivity check
                    if self.check_inactive_player(p):
                        choice = p.rest
                        break

                    # make a decision about what to do
                    choice = p.choose_day_action()

                    # do it
                    brk = choice()

                    # break out of loop if actually did something
                    if brk:
                        break

                    # check for load_game or quit
                    if self.chosen_load:
                        return True
                    elif self.chosen_quit:
                        return False

                # enc chance
                if choice not in (p.rest,):
                    self.enc.rand_enc()
                # extra enc chance for walks
                if choice == p.go_walk:
                    for i in range(WALK_EXTRA_ENC):
                        self.enc.rand_enc()

                # end turn
                p.end_turn()
                p.ended_turn = True

            if self.check_victory():
                return
            self.next_day()

    def play(self):
        """Play the (previously initialized or loaded) game."""
        self.prepare_for_playing()
        play = True
        while play:
            play = self.game_loop()
        else:
            if self.play_indefinitely and not self.chosen_quit:
                self.play()

    def prepare_for_playing(self):
        """Prepare for playing a new or previously saved game."""
        for p in self.players:
            if p.is_human:
                self.spectator = p
                break
        # the default for self.spectator is None (in __init__)
        self.hook_up_players()
        self.collect_used_names()