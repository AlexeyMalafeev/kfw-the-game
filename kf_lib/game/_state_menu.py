from kf_lib.ui import cls, menu, pak
from ._base_game import BaseGame


class StateMenu(BaseGame):
    def state_menu(self):
        p = self.current_player
        cls()
        print(p.get_p_info_verbose())
        print()
        options = ['Items', 'Accomplishments', 'Moves', 'Techniques']
        keys = 'iamt'
        if p.is_master:
            options.append('Students')
            keys += 's'
        options.append('Back')
        keys += 'b'
        if self.play_indefinitely:
            options.append('Finish Game')
            keys += 'F'
        options += ['Save', 'Load', 'Quit', 'Save and Quit', 'Debug Menu']
        keys += 'SlQXd'
        choice = menu(options, keys=keys, new_line=False)
        if choice == 'Items':
            cls()
            print(p.get_inventory_info())
            pak()
        elif choice == 'Accomplishments':
            cls()
            print(p.get_accompl_info())
            pak()
        elif choice == 'Moves':
            cls()
            p.show(p.get_moves_string())
            pak()
        elif choice == 'Techniques':
            cls()
            p.show(p.get_techs_string())
            pak()
        elif choice == 'Students':
            cls()
            print(p.get_students_info())
            pak()
        elif choice == 'Finish Game':
            self.finish_game()
        elif choice == 'Save':
            self.save_game('save.txt')
        elif choice == 'Load':
            self.load_game('save.txt')
            self.prepare_for_playing()  # otherwise loading fails
            self.chosen_load = True
        elif choice == 'Quit':
            self.chosen_quit = True
        elif choice == 'Save and Quit':
            self.save_game('save.txt')
            self.chosen_quit = True
        elif choice == 'Debug Menu':
            self.debug_menu()

    def finish_game(self):
        """Voluntarily end the game after winning and continuing: rerun the
        victory routine (message, stats, bio) and quit."""
        p = self.current_player
        wins = [f'{p.name} becomes {v}!' for v in self.check_victory_conditions(p)]
        self.show_victory(wins, [p])
        self.chosen_quit = True
