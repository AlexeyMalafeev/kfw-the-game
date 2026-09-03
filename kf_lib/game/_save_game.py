import json
from pathlib import Path

from kf_lib.utils import SAVE_FOLDER
from ._base_game import BaseGame


SAVE_FORMAT = 'kfw-save'
SAVE_VERSION = 1


class SaveGame(BaseGame):
    def _refresh_roster(self):
        """Only for fighter ordering when saving"""
        bosses = []
        for s in self.stories.values():
            if s.boss:
                bosses.append(s.boss)
        students = [s for school in self.schools.values() for s in school if not s.is_player]
        special_npcs = [
            f for f in (self.beggar, self.drunkard, self.thief, self.fat_girl) if f is not None
        ]
        self.fighters_list = (
            self.players
            + [m for m in self.masters.values() if not m.is_player]  # to avoid duplicating players
            + bosses
            + students
            + special_npcs
            + self.criminals
            + [en for p in self.players for en in p.enemies]
        )
        for p in self.players:
            for fr in p.friends:
                if fr not in self.fighters_list:
                    self.fighters_list.append(fr)
        self.fighters_dict = {f.name: f for f in self.fighters_list}

    def save_game(self, file_name):
        """Save the game as JSON (see get_save_data for the schema)."""
        data = self.get_save_data()
        with open(Path(SAVE_FOLDER, file_name), 'w') as f:
            json.dump(data, f, indent=1)
        self._dump_player_logs()

    @staticmethod
    def _fighter_to_data(ftr):
        """Serialize a fighter via the same constructor contract as get_init_string()."""
        return {'class': ftr.__class__.__name__, 'args': list(ftr.get_init_atts())}

    @staticmethod
    def _name_or_none(ftr):
        return ftr.name if ftr is not None else None

    def _player_to_data(self, p):
        return {
            'name': p.name,
            'atts': {att: getattr(p, att) for att in p.savable_atts},
            'current_story': p.current_story.name if p.current_story else None,
            'friends': [f.name for f in p.friends],
            'enemies': [en.name for en in p.enemies],
            'students': p.students,
            'best_student': self._fighter_to_data(p.best_student) if p.best_student else None,
        }

    def _story_to_data(self, s):
        return {
            'state': s.state,
            'player': self._name_or_none(s.player),
            'boss': self._name_or_none(s.boss),
        }

    def get_save_data(self):
        self._refresh_roster()  # this is only to order the fighters
        return {
            'format': SAVE_FORMAT,
            'version': SAVE_VERSION,
            'fighters': [self._fighter_to_data(f) for f in self.fighters_list],
            'masters': {sn: self.masters[sn].name for sn in sorted(self.masters)},
            'schools': {
                sn: [f.name for f in self.schools[sn]] for sn in sorted(self.schools)
            },
            'beggar': self._name_or_none(self.beggar),
            'drunkard': self._name_or_none(self.drunkard),
            'thief': self._name_or_none(self.thief),
            'criminals': [c.name for c in self.criminals],
            'fat_girl': self._name_or_none(self.fat_girl),
            'stories': {name: self._story_to_data(s) for name, s in self.stories.items()},
            # silent_ending is not in savable_atts for backward compat with the legacy format
            'game_atts': dict(
                {att: getattr(self, att) for att in self.savable_atts},
                silent_ending=self.silent_ending,
            ),
            'players': [self._player_to_data(p) for p in self.players],
        }

    def _dump_player_logs(self):
        for p in self.players:
            # dump log
            path = Path(SAVE_FOLDER, f'{p.name}\'s log.txt')
            with open(path, 'a') as log_file:
                log_file.write('\n'.join(p.plog))
                p.plog = []
