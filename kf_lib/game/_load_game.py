import json
from pathlib import Path

# used with exec by the legacy loader, do not delete
from kf_lib.actors.player import ALL_AI_PLAYERS, HumanPlayer, SmartAIP, SmartAIPVisible
from kf_lib.actors.fighter import Challenger, Fighter, Master, Thug
from kf_lib.happenings import story
from kf_lib.utils import SAVE_FOLDER
from ._base_game import BaseGame
from . import game_stats


FIGHTER_CLASSES = {
    cls.__name__: cls
    for cls in (
        *ALL_AI_PLAYERS,
        HumanPlayer,
        SmartAIP,
        SmartAIPVisible,
        Challenger,
        Fighter,
        Master,
        Thug,
    )
}

# stats_dict values that are tuples in the legacy format (JSON stores them as lists)
TUPLE_STATS = ('aston_victory', 'humil_defeat')


class LoadGame(BaseGame):
    def load_game(self, file_name):
        """Load a saved game; auto-detects JSON vs the legacy exec-based format."""
        with open(Path(SAVE_FOLDER, file_name), 'r') as f:
            text = f.read()
        if text.lstrip().startswith('{'):
            self._load_json(text)
        else:
            self._load_legacy(text)
        # loading clears logs
        for player in self.players:
            player.plog = []
            # initialize player statistics that aren't in the save file
            for sname, sval in game_stats.DEFAULT_STATS:
                if sname not in player.stats_dict:
                    player.stats_dict[sname] = sval

    def _load_legacy(self, text):
        """Load a save in the legacy format: executable Python lines, exec()ed
        in a shared namespace. Kept so that old save files still load."""
        # Shared namespace: names bound by one exec'd line (fsd, md, school, p)
        # must persist to the next, so do NOT use bare exec() in function scope.
        namespace = {'g': self, 'story': story}
        for cls in FIGHTER_CLASSES.values():
            namespace[cls.__name__] = cls
        for line in text.splitlines():
            # print(line)
            exec(line, namespace)

    @staticmethod
    def _fighter_from_data(fdata):
        cls = FIGHTER_CLASSES[fdata['class']]
        args = list(fdata['args'])
        args[3] = tuple(args[3])  # atts_tuple: JSON stores it as a list
        return cls(*args)

    def _load_json(self, text):
        data = json.loads(text)
        self.fighters_list = [self._fighter_from_data(fd) for fd in data['fighters']]
        self.fighters_dict = fsd = {f.name: f for f in self.fighters_list}
        self.masters = {sn: fsd[name] for sn, name in data['masters'].items()}
        self.schools = {
            sn: [fsd[name] for name in names] for sn, names in data['schools'].items()
        }
        self.beggar = fsd.get(data['beggar'])
        self.drunkard = fsd.get(data['drunkard'])
        self.thief = fsd.get(data['thief'])
        self.criminals = [fsd[name] for name in data['criminals']]
        self.fat_girl = fsd.get(data['fat_girl'])
        self.stories = {}
        for sname, sdata in data['stories'].items():
            story_cls = getattr(story, sname)
            # player/boss are stored by name; re-link them to the loaded fighters
            self.stories[sname] = story_cls(
                self,
                state=sdata['state'],
                player=fsd.get(sdata['player']),
                boss=fsd.get(sdata['boss']),
            )
        for att, val in data['game_atts'].items():
            setattr(self, att, val)
        self.players = []
        for pdata in data['players']:
            p = fsd[pdata['name']]
            self.players.append(p)
            for att, val in pdata['atts'].items():
                if att == 'stats_dict':
                    val = self._restore_stats_dict(val)
                setattr(p, att, val)
            if pdata['current_story'] is not None:
                p.current_story = self.stories[pdata['current_story']]
            p.friends = [fsd[name] for name in pdata['friends']]
            p.enemies = [fsd[name] for name in pdata['enemies']]
            p.students = pdata['students']
            if pdata['best_student'] is not None:
                p.best_student = self._fighter_from_data(pdata['best_student'])

    @staticmethod
    def _restore_stats_dict(stats_dict):
        for sname in TUPLE_STATS:
            val = stats_dict.get(sname)
            if isinstance(val, list):
                stats_dict[sname] = tuple(val)
        return stats_dict
