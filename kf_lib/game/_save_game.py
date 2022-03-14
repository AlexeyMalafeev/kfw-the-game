from ._base_game import BaseGame


class SaveGame(BaseGame):
    def save_game(self, file_name):
        def _save_all():
            _save_fighters()
            _save_masters()
            _save_schools()
            _save_special_npcs()
            _save_stories()
            _save_game_atts()
            _save_players()

        def _save_fighters():
            self.refresh_roster()  # this is only to order the fighters
            f.write('g.fighters_dict = fsd = {}')
            for ftr in self.fighters_list:
                f.write(f'\n\nfsd[{ftr.name!r}] = {ftr.get_init_string()}')
            f.write('\n\ng.fighters_list = list(fsd.values())')

        def _save_game_atts():
            f.write('\n')
            for att in self.savable_atts:
                f.write('\ng.{} = {!r}'.format(att, getattr(self, att)))

        def _save_masters():
            f.write('\n\ng.masters = md = {}')
            for sn in sorted(self.masters):
                m = self.masters[sn]
                f.write(f'\nmd[{sn!r}] = {self.get_fighter_ref(m)}')

        def _save_players():
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

        def _save_schools():
            f.write('\n\ng.schools = {}')
            for sn in sorted(self.schools):
                f.write(f'\n\ng.schools[{sn!r}] = school = []')
                for student in self.schools[sn]:
                    f.write(f'\nschool.append({self.get_fighter_ref(student)})')

        def _save_special_npcs():
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

        def _save_stories():
            f.write(f'\n\ng.stories = {self.stories!r}')

        with open(Path(SAVE_FOLDER, file_name), 'w') as f:
            _save_all()