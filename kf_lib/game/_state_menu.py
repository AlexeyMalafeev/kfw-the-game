from kf_lib.ui import cls, menu, pak
from ._base_game import BaseGame


class StateMenu(BaseGame):
    def state_menu(self):
        p = self.current_player
        cls()
        print(p.get_p_info_verbose())
        print()
        p.show(p.get_techs_string())
        print()
        p.show('Moves:')
        print(', '.join([str(m) for m in p.moves if not m.is_basic]))
        print()
        # add move screen with more detailed descriptions
        choice = menu(
            ('Items', 'Back', 'Save', 'Load', 'Quit', 'Save and Quit', 'Debug Menu'),
            keys='ibslqxd',
            new_line=False,
        )
        if choice == 'Items':
            cls()
            print(p.get_inventory_info())
            pak()
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
