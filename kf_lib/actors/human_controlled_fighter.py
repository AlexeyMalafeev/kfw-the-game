from .fighter import Fighter
from ..utils.utilities import menu, roman, pretty_table, cls, pak, get_bar, align_text


ALIGN = 60
INDENT = 0


# todo break HCF into submodules like Fighter
class HumanControlledFighter(Fighter):
    is_human = True

    def upgrade_att(self):
        self.show('')
        self.show(self.get_f_info(show_st_emph=True))
        options = self.get_atts_to_choose()
        att = self.menu(options, 'Improve:')
        self.change_att(att, 1)

    # def choose_best_norm_wp(self):
    #     wpts = techniques.get_weapon_techs(self)
    #     line = 'Pick a weapon:'
    #     if wpts:
    #         line += f"\n({self.name}'s weapon techniques: {', '.join(wpts)})"
    #     options = [(f'{wp.name} {wp.descr}', wp) for wp in weapons.NORMAL_WEAPONS]
    #     wn = self.menu(sorted(options), line)
    #     self.arm(wn)

    def choose_move(self):
        if self.is_auto_fighting:
            Fighter.choose_move(self)
        else:
            self.av_moves = self.get_av_moves()  # this depends on target
            self.see_fight_info(show_opp=True)
            # print('status', self.status)
            # print('opp status', self.target.status)
            # print(self.dfs_bonus)
            m_names = [
                f'{m.name}{self.get_move_stars(m)}{self.get_move_tier_string(m)}'
                for m in self.av_moves
            ]
            max_len = max((len(m_name) for m_name in m_names))
            m_hints = [self.get_move_hints(m) for m in self.av_moves]
            options = [
                ('{:<{}} {}'.format(m_names[i], max_len, m_hints[i]), m)
                for i, m in enumerate(self.av_moves)
            ]
            options.sort(key=lambda x: not x[1].power)
            # print(self.current_fight.order)
            d = self.get_vis_distance(self.distances[self.target])
            self.action = menu(options, title=f' {d}')

    def choose_new_move(self, sample):
        first_line = ('Move', 'Tier', 'Dist', 'Pwr', 'Acc', 'Cmpl', 'Sta', 'Time', 'Qi', 'Func')
        options = [
            (
                f'{m.name}{self.get_move_stars(m)}',
                roman(m.tier),
                f'{m.distance}({m.dist_change})' if m.dist_change else str(m.distance),
                str(m.power),
                str(m.accuracy),
                str(m.complexity),
                str(m.stam_cost),
                str(m.time_cost),
                str(m.qi_cost),
                ', '.join(m.functions),
            )
            for m in sample
        ]
        options = [first_line] + options
        options = pretty_table(options, sep=' ', as_list=True)
        first_line = options[0]
        options = options[1:]
        options = list(zip(options, [m.name for m in sample]))
        mn = menu(
            options,
            title='Choose a move to learn:\n     ' + first_line,
        )
        self.learn_move(mn)

    def choose_new_tech(self):
        sample = self.get_techs_to_choose(annotated=True)
        if not sample:
            return
        choice = self.menu(sample, 'Choose a technique to learn:')
        self.learn_tech(choice)

    def choose_target(self):
        if self.is_auto_fighting:
            Fighter.choose_target(self)
        else:
            if len(self.act_targets) == 1:
                self.set_target(self.act_targets[0])
            else:
                self.see_fight_info(show_opp=False)
                # self.show(self.visualize_fight_state())
                options = []
                for f in self.act_targets:
                    dist = self.get_vis_distance(self.distances[f])
                    n, lev, hp, stam, qi = f.name, f.level, f.hp, f.stamina, f.qp
                    if f.weapon:
                        wp_info = f' {f.weapon.name}'
                    else:
                        wp_info = ''
                    marks = f.get_status_marks(right=True)
                    options.append(
                        (
                            f'{dist}',
                            f'{n}{marks}',
                            f'(lv.{lev}',
                            f'HP:{hp}',
                            f'SP:{stam}',
                            f'QP:{qi}{wp_info})',
                        )
                    )
                options = pretty_table(options, sep='  ', as_list=True)
                options = list(zip(options, self.act_targets))
                tgt = self.menu(options, title='Choose target:')
                self.set_target(tgt)

    def choose_tech_to_upgrade(self):
        av_techs = self.get_techs_to_choose(annotated=True, for_upgrade=True)
        if not av_techs:
            return
        t = self.menu(av_techs, 'Choose a technique to improve:')
        self.upgrade_tech(t)

    def cls(self):
        cls()

    def get_move_hints(self, move_obj):
        targ = self.target
        t_cost = self.get_move_time_cost(move_obj)
        fail_warning = ''
        fail_chance = self.get_move_fail_chance(move_obj)
        if fail_chance >= 0.6:
            fail_warning = '~~~'
        elif fail_chance >= 0.25:
            fail_warning = '~~'
        elif fail_chance >= 0.1:
            fail_warning = '~'
        likely_hit = ''
        if move_obj.power:
            self.action = move_obj  # this is needed to calc dfs correctly
            self.calc_atk(self.action)
            targ.calc_dfs()
            defend_chance = max(targ.to_dodge / self.to_hit, targ.to_block / self.to_hit)
            if defend_chance <= 0.1:
                likely_hit = '%%%'
            elif defend_chance <= 0.25:
                likely_hit = '%%'
            elif defend_chance <= 0.4:
                likely_hit = '%'
        init = self.current_fight.check_initiative(t_cost, targ)
        have_time = '+' if not init else ''
        most_powerful = ''
        most_accurate = ''
        least_stamina = ''
        effects = ''
        if move_obj.power:
            moves_pool = [m for m in self.get_av_moves() if m.power]
            max_p = max(m.power for m in moves_pool)
            max_a = max(m.accuracy for m in moves_pool)
            min_s = min(m.stam_cost for m in moves_pool)
            if move_obj.power == max_p:
                most_powerful = 'P'
            if move_obj.accuracy == max_a:
                most_accurate = 'A'
            if move_obj.stam_cost == min_s:
                least_stamina = 's'
            effects = '!' * len(move_obj.functions)
        mh = '{}{}{}{}{}{}{}'.format(
            fail_warning,
            likely_hit,
            have_time,
            most_powerful,
            most_accurate,
            least_stamina,
            effects,
        )
        return mh

    def get_move_stars(self, move_obj):
        n = 0
        for feature in move_obj.features:
            if isinstance(feature, str):  # todo reimplement this
                val_a = getattr(self, feature + '_strike_mult', 1.0)
                val_b = getattr(self, feature + '_mult', 1.0)
                if max(val_a, val_b) > 1.0:
                    n += 1
        if (
            hasattr(move_obj, 'distance')
            and getattr(self, f'dist{move_obj.distance}_bonus', 1.0) > 1.0
        ):
            n += 1
        return '*' * n

    def level_up(self, times=1):
        self.msg(f'{self.name}: *LEVEL UP*')
        self.cls()
        self.show('*LEVEL UP*')
        Fighter.level_up(self, times)

    @staticmethod
    def menu(opt_list, *args, **kw_args):
        return menu(opt_list, *args, **kw_args)

    def msg(self, text, align=True):
        self.write(text, align=align)
        self.pak()

    def pak(self):
        pak()

    def refresh_screen(self):
        cls()
        self.show(self.get_f_info())

    def see_fight_info(self, show_opp=True):
        def align_lines(lines_to_be_aligned):
            lines_a = lines_to_be_aligned[:]
            if len(lines_a[0]) == 1:
                return [line[0] for line in lines_a]
            else:
                line_len = max([len(a) + len(b) for a, b in lines_a])
                min_len = 26
                if line_len < min_len:
                    line_len = min_len
                for i, line in enumerate(lines_a):
                    a, b = line
                    pad = line_len - (len(a) + len(b)) + 1
                    lines_a[i] = f"{a}{' ' * pad}{b}"
                return lines_a

        def fill_lines(lines_to_be_filled, f, right=False):
            lines_f = lines_to_be_filled
            marks = f.get_status_marks(right=right)
            lines_f[0].append(f.name + marks)

            health_bar = get_bar(f.hp, f.hp_max, '%', '.', 10, mirror=right)
            elt1, elt2, elt3 = 'HP', health_bar, f.hp
            if right:
                elt1, elt3 = elt3, elt1
            lines_f[1].append(f'{elt1} {elt2} {elt3}')

            stamina_bar = get_bar(f.stamina, f.stamina_max, '#', '-', 10, mirror=right)
            elt1, elt2, elt3 = 'SP', stamina_bar, f.stamina
            if right:
                elt1, elt3 = elt3, elt1
            lines_f[2].append(f'{elt1} {elt2} {elt3}')

            qi_bar = get_bar(f.qp, f.qp_max, '@', '~', 10, mirror=right)
            elt1, elt2, elt3 = 'QP', qi_bar, f.qp
            if right:
                elt1, elt3 = elt3, elt1
            lines_f[3].append(f'{elt1} {elt2} {elt3}')

            if f.weapon:
                lines_f[4].append(f'({f.weapon.name})')
            else:
                lines_f[4].append('')

        lines = [[], [], [], [], []]
        fill_lines(lines, self)
        if show_opp:
            fill_lines(lines, self.target, right=True)

        lines = align_lines(lines)
        lines.append(self.visualize_fight_state())

        self.cls()
        output = '\n'.join(lines)
        self.show(output, align=False)
        # todo show standing fighters with distance?

    def show(self, text, align=True):
        """Print aligned text in paragraphs."""
        from rich import print
        if align:
            pars = [align_text(t, INDENT, ALIGN) for t in text.split('\n')]
            for p in pars:
                print(p)
        else:
            print(text)

    @staticmethod
    def spectate(side_a, side_b, environment_allowed=True):
        from kf_lib.fighting.fight import SpectateFight

        SpectateFight(side_a, side_b, environment_allowed)

    def write(self, text, align=False):
        self.show(text, align=align)
        self.log(text)
