from ...utils.utilities import rnd


class StrikeEffectUser:
    def cause_fall(self):
        lying_dur = rndint_2d(DUR_LYING_MIN, DUR_LYING_MAX) // self.speed_full
        self.add_status('lying', lying_dur)
        self.add_status('skip', lying_dur)
        fall_dam = rndint(*FALL_DAMAGE)
        self.change_hp(-fall_dam)
        self.set_ascii('Falling')
        self.current_fight.display(f' falls to the ground! -{fall_dam} HP ({self.hp})', align=False)
        # print('$$$', self.status)

    def cause_knockback(self, dist):
        opp = self.target
        self.change_distance(dist, opp)
        s = 's' if dist > 1 else ''
        self.set_ascii('Knockback')
        # self.current_fight.display('{} is knocked back {} step{}!'.format(self.name, dist, s))
        self.current_fight.display(f' knocked back {dist} step{s}!', align=False)

    def cause_off_balance(self):
        ob_dur = rndint_2d(DUR_OFF_BAL_MIN, DUR_OFF_BAL_MAX) // self.speed_full
        self.add_status('off-balance', ob_dur)
        # self.current_fight.display('{} is off-balance!'.format(self.name))
        self.current_fight.display(' off-balance!', align=False)
        # print('$$$', self.status)

    def cause_shock(self):
        """Shock is worse than stun."""
        shock_dur = rndint_2d(DUR_SHOCK_MIN, DUR_SHOCK_MAX) // self.speed_full
        self.add_status('shocked', shock_dur)
        self.add_status('skip', shock_dur)
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        # self.current_fight.display('{} is shocked!'.format(self.name))
        self.current_fight.display(' shocked!', align=False)
        # print('$$$', self.status)

    def cause_slow_down(self):
        slow_dur = rndint_2d(DUR_SLOW_MIN, DUR_SLOW_MAX) // self.speed_full
        self.add_status('slowed down', slow_dur)
        # todo do not repeat this line in all functions, use helper
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        # self.current_fight.display('{} is slowed down!'.format(self.name))
        self.current_fight.display(' slowed down!', align=False)

    def cause_stun(self):
        """Stun is not as bad as shock."""
        stun_dur = rndint_2d(DUR_STUN_MIN, DUR_STUN_MAX) // self.speed_full
        self.add_status('stunned', stun_dur)
        self.add_status('skip', stun_dur)
        prefix = 'Lying ' if self.ascii_name.startswith('lying') else ''
        self.set_ascii(prefix + 'Hit Effect')
        # self.current_fight.display('{} is stunned!'.format(self.name))
        self.current_fight.display(' stunned!', align=False)
        # print('$$$', self.status)

    def do_agility_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.agility_full * STAT_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' agility-based -{dam} HP ({targ.hp})', align=False)

    def do_knockback(self):
        dist = random.choice(KNOCKBACK_DIST_FORCED)
        self.target.cause_knockback(dist)

    def do_level_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.level * LEVEL_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' level-based -{dam} HP ({targ.hp})', align=False)

    def do_mob_dam(self):
        self.target.cause_slow_down()

    def do_move_functions(self, m):
        if m.functions:
            for fun_s in m.functions:
                fun = getattr(self, fun_s)
                fun()

    def do_qi_based_dam(self):
        targ = self.target
        dam = rndint_2d(self.qp, self.qp * QI_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' qi-based -{dam} HP ({targ.hp})', align=False)

    def do_shock_move(self):
        self.target.cause_shock()

    def do_speed_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.speed_full * STAT_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' speed-based -{dam} HP ({targ.hp})', align=False)

    def do_stam_dam(self):
        targ = self.target
        dam = round(targ.stamina_max * STAMINA_DAMAGE)
        targ.change_stamina(-dam)
        prefix = 'lying ' if targ.check_status('lying') else ''
        targ.set_ascii(prefix + 'Hit Effect')
        self.current_fight.display(' gasps for breath!', align=False)

    def do_strength_based_dam(self):
        targ = self.target
        dam = rndint_2d(1, self.strength_full * STAT_BASED_DAM_UPPER_MULT)
        targ.take_damage(dam)
        self.current_fight.display(f' strength-based -{dam} HP ({targ.hp})', align=False)

    def do_takedown(self):
        targ = self.target
        targ.cause_fall()

    def try_critical(self):
        if rnd() <= self.critical_chance:
            self.atk_pwr *= self.critical_mult
            self.current_fight.display('CRITICAL!')

    def try_environment(self, mode):
        if (
            self.environment_chance
            and self.current_fight.environment_allowed
            and rnd() <= self.environment_chance
        ):
            if mode == 'attack':
                self.atk_pwr *= self.current_fight.environment_bonus
                self.to_hit *= self.current_fight.environment_bonus
            elif mode == 'defense':
                self.dfs_pwr *= self.current_fight.environment_bonus
                self.to_block *= self.current_fight.environment_bonus
                self.to_dodge *= self.current_fight.environment_bonus
            self.current_fight.display(f'{self.name} uses the environment!')

    def try_hit_disarm(self):
        tgt = self.target
        if tgt.weapon and self.hit_disarm and rnd() <= self.hit_disarm:
            tgt.disarm()
            self.current_fight.display(f'{self.name} disarms {tgt.name} while attacking')

    def try_insta_ko(self):
        targ = self.target
        if rnd() <= INSTA_KO_CHANCE:
            dam = targ.hp
            self.current_fight.display('INSTANT KNOCK-OUT!!!')
            targ.take_damage(dam)

    def try_knockback(self):
        targ = self.target
        kb = 0
        if not targ.check_status('lying'):
            dam_ratio = self.dam / targ.hp_max
            for thresh in KNOCKBACK_HP_THRESHOLDS:
                if dam_ratio > thresh:
                    kb += 1
        if kb > 0:
            targ.cause_knockback(kb)

    def try_knockdown(self):
        targ = self.target
        if not targ.check_status('lying'):
            if self.dam >= targ.hp_max / KNOCKDOWN_HP_DIVISOR:
                targ.cause_fall()
            elif self.dam >= targ.hp_max / OFF_BALANCE_HP_DIVISOR:
                targ.cause_off_balance()

    def try_ko(self):
        tgt = self.target
        if not tgt.hp:
            if tgt.resist_ko and rnd() <= tgt.resist_ko:
                tgt.hp = 1
                self.log(f'{tgt.name} resists being knocked out.')
                tgt.log('Resists being knocked out.')
                self.current_fight.display(f'{tgt.name} resists being knocked out!')
            else:
                self.kos_this_fight += 1
                self.log(f'Knocks out {tgt.name}.')
                tgt.log(f'Knocked out by {self.name}.')
                if not tgt.ascii_name.startswith('lying'):
                    tgt.set_ascii('Falling')
                self.current_fight.display(' KNOCK-OUT!'.format(tgt.name), align=False)

    def try_shock_move(self):
        targ = self.target
        if rnd() <= SHOCK_CHANCE:
            targ.cause_shock()

    def try_stun(self):
        targ = self.target
        if (self.dam >= targ.hp_max / STUN_HP_DIVISOR) or (
            self.stun_chance and rnd() <= self.stun_chance
        ):
            targ.cause_stun()

    def try_unblockable(self):
        if self.unblock_chance and rnd() <= self.unblock_chance:
            self.target.to_block = 0
            self.current_fight.display('UNBLOCKABLE!')
