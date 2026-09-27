from kf_lib.i18n import _, tr_fighter_name, tr_name
from kf_lib.ui import cls, get_key, pak
from ._base_game import BaseGame


class StateMenu(BaseGame):
    def state_menu(self):
        p = self.current_player
        while True:
            cls()
            print(p.get_p_info_verbose())
            print()
            # (display label, English value) pairs: the values are compared below
            options = [
                (_('Items'), 'Items'),
                (_('Accomplishments'), 'Accomplishments'),
                (_('Moves'), 'Moves'),
                (_('Techniques'), 'Techniques'),
            ]
            keys = 'iamt'
            if p.is_master:
                options.append((_('Students'), 'Students'))
                keys += 's'
            options.append((_('Back'), 'Back'))
            keys += 'b'
            print(' ' + '  '.join(f'{k} - {opt[0]}' for k, opt in zip(keys, options)))
            sys_options = [
                (_('Save'), 'Save'),
                (_('Load'), 'Load'),
                (_('Quit'), 'Quit'),
                (_('Save and Quit'), 'Save and Quit'),
                (_('Debug Menu'), 'Debug Menu'),
            ]
            sys_keys = 'SLQXD'
            if self.play_indefinitely:
                sys_options.append((_('Finish Game'), 'Finish Game'))
                sys_keys += 'F'
            print(' ' + '  '.join(f'{k} - {opt[0]}' for k, opt in zip(sys_keys, sys_options)))
            options += sys_options
            keys += sys_keys
            while True:
                key = get_key()
                if key in keys:
                    choice = options[keys.index(key)][1]
                    break
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
                return
            elif choice == 'Save':
                self.save_game('save.txt')
            elif choice == 'Load':
                self.load_game('save.txt')
                self.prepare_for_playing()  # otherwise loading fails
                self.chosen_load = True
                return
            elif choice == 'Quit':
                self.chosen_quit = True
                return
            elif choice == 'Save and Quit':
                self.save_game('save.txt')
                self.chosen_quit = True
                return
            elif choice == 'Debug Menu':
                self.debug_menu()
            else:  # Back
                return

    def finish_game(self):
        """Voluntarily end the game after winning and continuing: rerun the
        victory routine (message, stats, bio) and quit."""
        p = self.current_player
        wins = [
            _('{name} becomes {victory}!').format(
                name=tr_fighter_name(p.name), victory=tr_name(v)
            )
            for v in self.check_victory_conditions(p)
        ]
        self.show_victory(wins, [p])
        self.chosen_quit = True
