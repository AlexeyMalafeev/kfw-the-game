class FighterOutput:
    def log(self, text):
        """Empty method for convenience."""
        pass

    def msg(self, *args, **kwargs):
        pass

    def pak(self):
        pass

    def show(self, text, align=False):
        pass

    def cls(self):
        """Empty method for convenience"""
        pass

    def get_f_info(self, short=False, show_st_emph=False):
        s = self
        if s.weapon:
            w_info = f', {s.weapon.name}'
        else:
            w_info = ''
        if short:
            info = f'{s.name}, lv.{s.level} {s.style.name}{w_info}'
        else:
            info = '{}, lv.{} {}{}\n{}'.format(
                s.name, s.level, s.get_style_string(show_st_emph), w_info, s.get_all_atts_str()
            )
        return info

    def get_prefight_info(self, side_a, side_b=None, hide_enemy_stats=False, basic_info_only=False):
        fs = side_a[:]
        if side_b:
            fs.extend(side_b)
        s = ''
        size1 = max([len(s) for s in ['NAME '] + [f.name + '  ' for f in fs]])
        size2 = max([len(s) for s in ['LEV '] + [str(f.level) + ' ' for f in fs]])
        size3 = max([len(s) for s in ['STYLE '] + [f.style.name + ' ' for f in fs]])
        att_names = ' '.join(self.att_names_short) if not basic_info_only else ''
        s += 'NAME'.ljust(size1) + 'LEV'.ljust(size2) + 'STYLE'.ljust(size3) + att_names
        if any([f.weapon for f in fs]) and not basic_info_only:
            s += ' WEAPON'
        for f in fs:
            if side_b and f == side_b[0]:
                s += '\n-vs-'
            s += '\n{:<{}}{:<{}}{:<{}}'.format(
                f.name,
                size1,
                f.level,
                size2,
                f.style.name,
                size3,
            )
            if basic_info_only:
                continue
            if (
                (not hide_enemy_stats)
                or f.is_human
                or (f in side_a and any([ff.is_human for ff in side_a]))
                or (side_b and f in side_b and any([ff.is_human for ff in side_b]))
            ):
                atts_wb = (f.get_att_str_prefight(att) for att in self.att_names)
            else:
                atts_wb = (f.get_att_str_prefight(att, hide=True) for att in self.att_names)
            s += '{:<4}{:<4}{:<4}{:<4}'.format(*atts_wb)
            if f.weapon:
                s += f'{f.weapon.name} {f.weapon.descr_short}'
            s += f"\n{' ' * (size1 + size2)}{f.style.descr_short}"
        return s

    def see_fight_info(self, *args, **kwargs):
        pass

    def visualize_fight_state(self):
        try:
            ft = self.current_fight
            side_a, side_b = ft.active_side_a, ft.active_side_b
            n_a, n_b = len(side_a), len(side_b)
            hp_a, hp_b = sum((f.hp for f in side_a)), sum((f.hp for f in side_b))
            bar = get_bar(hp_a, hp_a + hp_b, '/', '\\', 20)
            s = f'\n{n_a} {bar} {n_b}\n'
            return s
        except ZeroDivisionError:
            from pprint import pprint
            import traceback
            traceback.print_exc()
            pprint(vars())
            pprint(vars(self))
            pprint(self.current_fight.timeline)
            pak()

    def write(self, *args, **kwargs):
        pass