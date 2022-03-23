from pathlib import Path

from kf_lib.utils import SAVE_FOLDER
from ._base_game import BaseGame


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
        with open(Path(SAVE_FOLDER, file_name), 'w') as f:
            self._save_all(f)

    def _save_all(self, f):
        self._save_fighters(f)
        self._save_masters(f)
        self._save_schools(f)
        self._save_special_npcs(f)
        self._save_stories(f)
        self._save_game_atts(f)
        self._save_players(f)

    def _save_fighters(self, f):
        self._refresh_roster()  # this is only to order the fighters
        f.write('g.fighters_dict = fsd = {}')
        for ftr in self.fighters_list:
            f.write(f'\n\nfsd[{ftr.name!r}] = {ftr.get_init_string()}')
        f.write('\n\ng.fighters_list = list(fsd.values())')

    def _save_game_atts(self, f):
        f.write('\n')
        for att in self.savable_atts:
            f.write('\ng.{} = {!r}'.format(att, getattr(self, att)))

    def _save_masters(self, f):
        f.write('\n\ng.masters = md = {}')
        for sn in sorted(self.masters):
            m = self.masters[sn]
            f.write(f'\nmd[{sn!r}] = {self.get_fighter_ref(m)}')

    def _save_players(self, f):
        f.write('\n\ng.players = []')
        for p in self.players:
            f.write('\n\n' + '#' * 80)
            f.write(f'\n\ng.players.append({self.get_fighter_ref(p)})\n')
            f.write('p = g.players[-1]\n')

            # save player attributes
            for att in p.savable_atts:
                f.write('p.{} = {!r}\n'.format(att, getattr(p, att)))

            # save current story
            if p.current_story:
                f.write(
                    'p.current_story = g.stories[{!r}]\n'.format(
                        p.current_story.__class__.__name__
                    )
                )

            # friends
            f.write('\np.friends = [')
            for friend in p.friends:
                f.write(f'{self.get_fighter_ref(friend)}, ')
            f.write(']\n')

            # enemies
            f.write('\np.enemies = [')
            for en in p.enemies:
                f.write(f'{self.get_fighter_ref(en)}, ')
            f.write(']\n')

            # students
            f.write(f'\np.students = {p.students!r}\n')
            best = p.best_student.get_init_string() if p.best_student else 'None'
            f.write(f'\np.best_student = {best}')

            # dump log
            path = Path(SAVE_FOLDER, f'{p.name}\'s log.txt')
            with open(path, 'a') as log_file:
                log_file.write('\n'.join(p.plog))
                p.plog = []

    def _save_schools(self, f):
        f.write('\n\ng.schools = {}')
        for sn in sorted(self.schools):
            f.write(f'\n\ng.schools[{sn!r}] = school = []')
            for student in self.schools[sn]:
                f.write(f'\nschool.append({self.get_fighter_ref(student)})')

    def _save_special_npcs(self, f):
        bgr = self.beggar
        drkd = self.drunkard
        thf = self.thief
        crmls = self.criminals
        fg = self.fat_girl
        f.write(
            f"\n\ng.beggar = {self.get_fighter_ref(bgr) if bgr is not None else 'None'}"
        )
        f.write(
            '\ng.drunkard = {}'.format(
                self.get_fighter_ref(drkd) if drkd is not None else 'None'
            )
        )
        f.write(
            f"\ng.thief = {self.get_fighter_ref(thf) if thf is not None else 'None'}"
        )
        f.write('\ng.criminals = []')
        for c in crmls:
            f.write(f'\ng.criminals.append({self.get_fighter_ref(c)})')
        f.write(
            f"\ng.fat_girl = {self.get_fighter_ref(fg) if fg is not None else 'None'}"
        )

    def _save_stories(self, f):
        f.write(f'\n\ng.stories = {self.stories!r}')
