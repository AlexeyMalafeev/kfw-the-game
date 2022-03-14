from pathlib import Path


from kf_lib.actors.player import (
    HumanPlayer,
    ALL_AI_PLAYERS,  # used in load/new_game
)
from kf_lib.happenings import events, encounters, story
from kf_lib.ui import cls, get_int_from_user, menu, pak, yn
from kf_lib.utils import rnd, rndint, SAVE_FOLDER
from . import game_stats


# todo refactor game.py into submodules


class Game:
    def crime_down(self):
        events.crime_down(self)

    def get_act_players(self):
        return [p for p in self.players if not p.inactive]

    # noinspection PyUnresolvedReferences
    def load_game(self, file_name):
        """Read and execute the save file."""
        # todo reimplement game loading to avoid using exec
        # do not delete the below line; needed for loading
        g = self  # noqa
        with open(Path(SAVE_FOLDER, file_name), 'r') as f:
            from ..actors.fighter import (
                Fighter,
                Challenger,
                Master,
                Thug,
            )  # this is used for loading, do not delete
            from ..actors.player import (
                LazyAIP,
                SmartAIP,
                VanillaAIP,
                BaselineAIP,
            )  # this is used for loading, do not delete

            for line in f:
                # print(line)
                exec(line)
        # loading clears logs
        # (do not use 'p' as variable here as it breaks exec code)
        for player in self.players:
            player.plog = []
            # initialize player statistics that aren't in the save file
            for sname, sval in game_stats.DEFAULT_STATS:
                if sname not in player.stats_dict:
                    player.stats_dict[sname] = sval

    @staticmethod
    def quit():
        import sys
        sys.exit()

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

    def unregister_fighter(self, f):
        self.fighters_list.remove(f)
        del self.fighters_dict[f.name]
