class FightActionsUser:
    def apply_dfs_penalty(self):
        self.dfs_penalty_mult -= self.dfs_penalty_step
        if self.dfs_penalty_mult < 0:
            self.dfs_penalty_mult = 0

    def attack(self):
        n1 = self.current_fight.get_f_name_string(self)
        n2 = self.current_fight.get_f_name_string(self.target)
        s = f'{n1}: {self.action.name} @ {n2}'
        self.current_fight.display(s)
        if self.guard_while_attacking:
            self.current_fight.display(f' (guarding while attacking)')
            self.dfs_bonus += self.guard_dfs_bonus * self.guard_while_attacking
        self.current_fight.display('=' * len(s))
        # print(n2, 'dfs_bonus', self.target.dfs_bonus)
        self.try_strike()
        self.target.try_counter()

    def calc_atk(self, action):
        """Calculate attack numbers w.r.t. some action (not necessarily action chosen)."""
        strike_mult = 1.0
        strike_mult *= getattr(self, f'dist{action.distance}_bonus', 1.0)
        for feature in action.features:
            # low-prio todo reimplement computing strike_mult without getattr, use dict
            strike_mult *= getattr(self, f'{feature}_strike_mult', 1.0)
        self.atk_bonus = self.atk_mult * strike_mult
        if self.check_status('off-balance'):
            self.atk_bonus *= self.off_balance_atk_mult
        self.atk_pwr = (
            self.strength_full * action.power * self.atk_bonus * self.stamina_factor / DAM_DIVISOR
        )
        self.to_hit = self.agility_full * action.accuracy * self.atk_bonus * self.stamina_factor

    # todo how is it used? why not relative to attacker?
    def calc_dfs(self):
        """Calculate defense numbers."""
        if self.check_status('shocked'):
            self.to_dodge = 0
            self.to_block = 0
        else:
            attacker = self.target
            atk_action = attacker.action
            rep_actions_factor = attacker.get_rep_actions_factor(atk_action)
            # todo recalc as a value in (0.0, 1.0)?
            # * 10 because of new system:
            x = self.dfs_penalty_mult * self.agility_full * self.dodge_mult * 10
            x *= self.stamina_factor * rep_actions_factor
            x *= self.dfs_bonus
            # print('x after dfs_bonus', x)
            if self.check_status('off-balance'):
                x *= self.off_balance_dfs_mult
            if self.check_status('lying'):
                x *= self.lying_dfs_mult
            self.to_dodge = x / DODGE_DIVISOR
            self.to_block = x / BLOCK_DIVISOR
            self.to_block *= self.wp_dfs_bonus  # no weapon bonus to dodging!
            # print('to dodge, to block', self.to_dodge, self.to_block)
            self.dfs_pwr = self.dfs_penalty_mult * self.block_power * self.strength_full
            self.dfs_pwr *= self.stamina_factor * self.wp_dfs_bonus  # todo divide by sth?

    def calc_stamina_factor(self):
        # todo docstring calc_stamina_factor
        self.stamina_factor = self.stamina / self.stamina_max / 2 + STAMINA_FACTOR_BIAS

    def check_move_failed(self):
        compl = self.action.complexity
        f_ch = self.get_move_fail_chance(self.action)
        if rnd() <= f_ch:
            if self.action.power:
                self.to_hit = 0
                if compl >= 1:
                    self.current_fight.display('Miss!')
                    self.cause_off_balance()
            if self.action.dist_change:
                self.current_fight.display('Fail!')
                if compl >= 3:
                    self.cause_fall()
                else:
                    self.cause_off_balance()
            return True
        else:
            return False

    def choose_move(self):
        self.av_moves = self.get_av_moves()  # this depends on target
        self.action = self.fight_ai.choose_move()

    def choose_target(self):
        if len(self.act_targets) == 1:
            self.set_target(self.act_targets[0])
        else:
            self.set_target(self.fight_ai.choose_target())

    def defend(self):
        atkr = self.target
        atkr.dam = atkr.atk_pwr
        dodge_chance = self.to_dodge / atkr.to_hit
        block_chance = self.to_block / atkr.to_hit
        roll = rnd()
        prefix = 'Lying ' if self.check_status('lying') else ''
        self.defended = False
        if roll <= dodge_chance:
            atkr.dam = 0
            self.change_qp(self.qp_gain)
            self.current_fight.display(
                '{} {}dodges!'.format(self.name, get_adverb(dodge_chance, 'barely', 'easily'))
            )
            self.set_ascii(prefix + 'Dodge')
            self.defended = True
        elif roll <= block_chance:
            atkr.dam = max(atkr.dam - self.dfs_pwr, 0)
            self.change_qp(self.qp_gain // 2)
            self.current_fight.display(
                '{} {}blocks!'.format(self.name, get_adverb(block_chance, 'barely', 'easily'))
            )
            self.set_ascii(prefix + 'Block')
            self.try_block_disarm()
            self.defended = True
        else:
            self.set_ascii(prefix + 'Hit')
        # todo handle the no defense case
        atkr.dam = round(atkr.dam)

    def do_counter(self):
        cand_moves = self.get_av_moves(attack_moves_only=True)
        if cand_moves:
            self.current_fight.display('COUNTER!')
            new_action = random.choice(cand_moves)
            self.action = new_action
            s = f'{self.name}: {self.action.name} @ {self.target.name}'
            self.current_fight.display(s)
            self.do_strike()

    def do_strike(self):
        m = self.action
        self.calc_atk(m)
        self.try_environment('attack')
        self.try_critical()
        self.target.calc_dfs()
        self.try_unblockable()
        self.target.try_environment('defense')
        self.target.defend()
        self.hit_or_miss()
        self.target.apply_dfs_penalty()
        if m.dist_change:
            self.change_distance(m.dist_change, self.target)
        self.previous_actions = self.previous_actions[1:] + [m.name]
        self.change_stamina(-m.stam_cost)
        self.change_qp(-m.qi_cost)

    def exec_move(self):
        m = self.action
        self.current_fight.cls()
        if m.power:
            self.attack()  # changing distance is included
        else:
            self.maneuver()
        self.current_fight.show(self.visualize_fight_state())
        self.show_ascii()

    def get_av_moves(self, attack_moves_only=False):
        av_moves = []
        lying_op = self.target.check_status('lying')
        for m in self.moves + (self.weapon.moves if self.weapon else []):
            enough_stamina = self.stamina >= m.stam_cost
            enough_qi = self.qp >= m.qi_cost
            if enough_stamina and enough_qi:
                if m.distance:
                    right_distance = m.distance == self.distances[self.target]
                    if right_distance:
                        anti_ground = (
                                              'antiground only' in m.features or 'also antiground' in m.features
                                      ) and lying_op
                        anti_standing = 'antiground only' not in m.features and not lying_op
                        if anti_ground or anti_standing:
                            av_moves.append(m)
                else:
                    av_moves.append(m)
        if attack_moves_only:
            av_moves = [m for m in av_moves if m.power]
        return av_moves

    # todo reimplement this as a multiplier, not an addition of guard_dfs_bonus to dfs_bonus,
    #  but careful with wp_dfs_bonus
    def guard(self):
        """This is called with eval as a function of the Guard move."""
        # print('giving guard dfs bonus:', self.dfs_bonus, '+', self.guard_dfs_bonus)
        self.dfs_bonus += self.guard_dfs_bonus

    def hit_or_miss(self):
        tgt = self.target
        if self.dam > 0:
            self.dam = max(self.dam - tgt.dam_reduc, 0)
            tgt.take_damage(self.dam)
            self.current_fight.display(f'hit: -{self.dam} HP ({tgt.hp})')
            self.try_hit_disarm()
            self.do_move_functions(self.action)
            self.try_stun()
            self.try_knockback()
            self.try_knockdown()
            self.try_ko()

    def start_fight_turn(self):
        cur_fight = self.current_fight
        self.act_targets = (
            cur_fight.active_side_b if self in cur_fight.active_side_a else cur_fight.active_side_a
        )
        self.act_allies = (
            cur_fight.active_side_b if self in cur_fight.active_side_b else cur_fight.active_side_a
        )
        self.action = None
        self.dfs_bonus = 1.0
        self.dfs_penalty_mult = 1.0
        self.target = None
        # breathing techs and other automatic actions
        self.change_hp(self.hp_gain)
        self.change_qp(self.qp_gain)
        self.change_stamina(self.stamina_gain)
        self.try_in_fight_impro_wp()  # before get_av_atk_actions! or won't get weapon moves
        self.calc_stamina_factor()

    def try_strike(self):
        if not self.check_move_failed():
            self.do_strike()

    def try_block_disarm(self):
        atkr = self.target
        if atkr.weapon and self.block_disarm and rnd() <= self.block_disarm:
            atkr.disarm()
            self.current_fight.display(f'{self.name} disarms {atkr.name} while blocking')

    def try_counter(self):
        if self.defended and self.hp > 0 and rnd() <= self.counter_chance:
            self.do_counter()

    def try_in_fight_impro_wp(self):
        if (
            self.in_fight_impro_wp_chance
            and not self.weapon
            and self.current_fight.environment_allowed
            and rnd() <= self.in_fight_impro_wp_chance
        ):
            self.arm_improv()
            s = self.current_fight.get_f_name_string(self)
            self.current_fight.display(f'{s} grabs an improvised weapon!')
            self.current_fight.pak()
