from pathlib import Path

# used with exec, do not delete
from kf_lib.actors.player import ALL_AI_PLAYERS, HumanPlayer, SmartAIP, SmartAIPVisible
from kf_lib.actors.fighter import Challenger, Fighter, Master, Thug
from kf_lib.happenings import story
from kf_lib.utils import SAVE_FOLDER
from ._base_game import BaseGame
from . import game_stats


class LoadGame(BaseGame):
    def load_game(self, file_name):
        """Read and execute the save file."""
        # todo reimplement game loading to avoid using exec
        # do not delete the below line; needed for loading
        g = self  # noqa
        with open(Path(SAVE_FOLDER, file_name), 'r') as f:
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
