from kf_lib.i18n import _, tr_fighter_name
from kf_lib.ui import (
    align_text,
    bold,
    cls,
    get_bar,
    green,
    magenta,
    menu,
    pak,
    pretty_table,
    red,
    render,
    visible_len,
    yellow,
)
from kf_lib.utils import roman
from .fighter import Fighter

ALIGN = 60
INDENT = 0


def format_move_distance(m):
    if m.dist_change:
        return f'{m.distance}->{m.distance + m.dist_change}'
    return str(m.distance)


# todo break HCF into submodules like Fighter
class HumanControlledFighter(Fighter):
    is_human = True

    def upgrade_att(self):
        self.show('')
        self.show(self.get_f_info(show_st_emph=True))
        options = self.get_atts_to_choose()
        labels = {
            'strength': _('Strength'),
            'agility': _('Agility'),
            'speed': _('Speed'),
            'health': _('Health'),
        }
        options = [(labels[att], att) for att in options]
        att = menu(options, _('Improve:'))
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
                f'{m.display_name}{self.get_move_stars(m)}{self.get_move_tier_string(m)}'
                for m in self.av_moves
            ]
            max_len = max((visible_len(m_name) for m_name in m_names))
            m_hints = [self.get_move_hints(m) for m in self.av_moves]
            options = [
                (
                    m_names[i] + ' ' * (max_len - visible_len(m_names[i])) + ' ' + m_hints[i],
                    m,
                )
                for i, m in enumerate(self.av_moves)
            ]
            options.sort(key=lambda x: not x[1].power)
            # print(self.current_fight.order)
            d = self.get_vis_distance(self.distances[self.target])
            self.action = menu(options, title=f' {d}')

    def choose_new_move(self, sample):
        first_line = (
            _('Move'),
            _('Tier'),
            _('Dist'),
            _('Pwr'),
            _('Acc'),
            _('Cmpl'),
            _('Sta'),
            _('Time'),
            _('Qi'),
            _('Func'),
        )
        options = [
            (
                f'{m.display_name}{self.get_move_stars(m)}',
                roman(m.tier),
                format_move_distance(m),
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
        options = list(zip(options, [m for m in sample]))
        mn = menu(
            options,
            title=_('Choose a move to learn:') + '\n     ' + first_line,
        )
        self.learn_move(mn)

    def choose_new_tech(self):
        sample = self.get_techs_to_choose(annotated=True)
        if not sample:
            return
        choice = self.menu(sample, _('Choose a technique to learn:'))
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
                        wp_info = f' {f.weapon.display_name}'
                    else:
                        wp_info = ''
                    marks = f.get_status_marks(right=True)
                    options.append(
                        (
                            f'{dist}',
                            f'{tr_fighter_name(n)}{marks}',
                            '(' + _('lv.{}').format(lev),
                            _('HP:{}').format(hp),
                            _('SP:{}').format(stam),
                            _('QP:{}').format(qi) + wp_info + ')',
                        )
                    )
                options = pretty_table(options, sep='  ', as_list=True)
                options = list(zip(options, self.act_targets))
                tgt = self.menu(options, title=_('Choose target:'))
                self.set_target(tgt)

    def choose_tech_to_upgrade(self):
        av_techs = self.get_techs_to_choose(annotated=True, for_upgrade=True)
        if not av_techs:
            return
        t = self.menu(av_techs, _('Choose a technique to improve:'))
        self.upgrade_tech(t)

    def choose_style_tech_to_upgrade(self):
        av_techs = sorted(
            (t for t in self.techs if t in self.style.techs.values()),
            key=lambda t: t.name,
        )
        if not av_techs:
            return
        self.show(
            _(
                'As {name} trains hard, delving deeper into the art of {style}, he '
                "discovers a way to improve one of the style's techniques..."
            ).format(
                name=tr_fighter_name(self.name),
                style=self.get_displayed_style_name(),
            )
        )
        self.pak()
        options = [(f'{t.display_name} ({t.descr})', t) for t in av_techs]
        t = self.menu(sorted(options), _('Choose a technique to improve:'))
        self.upgrade_style_tech(t)

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
            val = getattr(self, feature + '_strike_mult', 1.0)
            if val > 1.0:
                n += 1
        return yellow('*' * n) if n else ''

    def level_up(self, times=1):
        self.msg(_('{name}: *LEVEL UP*').format(name=tr_fighter_name(self.name)))
        self.cls()
        self.show(_('*LEVEL UP*'))
        Fighter.level_up(self, times)

    def learn_secret_style_tech(self, tech):
        style = self.style
        master = None
        get_master = getattr(self, 'get_master', None)
        if get_master is not None:
            try:
                master = get_master()
            except KeyError:
                master = None
        if master is not None and master is not self:
            if style.public_name != style.name:
                t = _(
                    "{name} is practicing in the school's courtyard when {master} "
                    'calls him to the main hall.\n'
                    '{master}: "{name}, you have been most diligent. Few students '
                    'go as far as you have, so today I can trust you with the inner '
                    'teaching of our school. The style the outside world knows as '
                    '{public_style} has a true name, whispered only to the most '
                    'trusted disciples: {style}! And with it comes the secret '
                    'technique — {tech}. Guard this knowledge, and never speak of '
                    'it outside these walls."'
                ).format(
                    name=tr_fighter_name(self.name),
                    master=tr_fighter_name(master.name),
                    public_style=style.display_public_name,
                    style=style.display_name,
                    tech=tech.display_name,
                )
            else:
                t = _(
                    "{name} is practicing in the school's courtyard when {master} "
                    'calls him to the main hall.\n'
                    '{master}: "{name}, you have been most diligent. Few students '
                    'go as far as you have. It is time you learned the secret '
                    'technique of {style} — {tech}. Guard this knowledge, and '
                    'never speak of it outside these walls."'
                ).format(
                    name=tr_fighter_name(self.name),
                    master=tr_fighter_name(master.name),
                    style=style.display_name,
                    tech=tech.display_name,
                )
        else:
            t = _(
                'Through countless hours of training, {name} finally grasps the '
                'deepest secret of {style} — {tech}.'
            ).format(
                name=tr_fighter_name(self.name),
                style=style.display_public_name,
                tech=tech.display_name,
            )
        self.show(t)
        self.log(f'Learns the secret technique of {style.name}.')
        self.pak()
        Fighter.learn_tech(self, tech)

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
                line_len = max([visible_len(a) + visible_len(b) for a, b in lines_a])
                min_len = 26
                if line_len < min_len:
                    line_len = min_len
                for i, line in enumerate(lines_a):
                    a, b = line
                    pad = line_len - (visible_len(a) + visible_len(b)) + 1
                    lines_a[i] = f"{a}{' ' * pad}{b}"
                return lines_a

        def fill_lines(lines_to_be_filled, f, right=False):
            lines_f = lines_to_be_filled
            marks = f.get_status_marks(right=right)
            lines_f[0].append(bold(tr_fighter_name(f.name)) + marks)

            health_bar = get_bar(f.hp, f.hp_max, '%', '.', 10, mirror=right)
            hp_ratio = f.hp / f.hp_max if f.hp_max else 0
            hp_color = green if hp_ratio > 0.5 else (yellow if hp_ratio > 0.25 else red)
            elt1, elt2, elt3 = _('HP'), hp_color(health_bar), f.hp
            if right:
                elt1, elt3 = elt3, elt1
            lines_f[1].append(f'{elt1} {elt2} {elt3}')

            stamina_bar = get_bar(f.stamina, f.stamina_max, '#', '-', 10, mirror=right)
            elt1, elt2, elt3 = _('SP'), yellow(stamina_bar), f.stamina
            if right:
                elt1, elt3 = elt3, elt1
            lines_f[2].append(f'{elt1} {elt2} {elt3}')

            qi_bar = get_bar(f.qp, f.qp_max, '@', '~', 10, mirror=right)
            elt1, elt2, elt3 = _('QP'), magenta(qi_bar), f.qp
            if right:
                elt1, elt3 = elt3, elt1
            lines_f[3].append(f'{elt1} {elt2} {elt3}')

            if f.weapon:
                lines_f[4].append(f'({f.weapon.display_name})')
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
        """Print aligned text in paragraphs (markup tags resolved to colors)."""
        if align:
            pars = [align_text(t, INDENT, ALIGN) for t in text.split('\n')]
            for p in pars:
                print(render(p))
        else:
            print(render(text))

    @staticmethod
    def spectate(side_a, side_b, environment_allowed=True):
        from kf_lib.fighting.fight import SpectateFight

        SpectateFight(side_a, side_b, environment_allowed)

    def write(self, text, align=False):
        self.show(text, align=align)
        self.log(text)
