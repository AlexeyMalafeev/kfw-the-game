"""Fight engine characterization: crowd fights, weapons, sparring, exp, stats."""
import random

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib.actors import fighter_factory
from kf_lib.actors.fighter import Fighter
from kf_lib.actors.player import SmartAIP
from kf_lib.fighting.fight import AutoFight, free_for_all, group_free_for_all
from kf_lib.fighting.fight._base_fight import (
    ENVIRONMENT_BONUSES,
    LOSER_EXP_DIVISOR,
    BaseFight,
)
from kf_lib.fighting.fight._free_for_all import BaseFreeForAll, BaseGroupFreeForAll
from kf_lib.constants.experience import BASE_FIGHT_EXP, LOSER_EXP


def lv1_fighter(name):
    return Fighter(name, 'Long Fist', level=1, tech_names=[], move_names=[])


def make_game(seed=0):
    random.seed(seed)
    g = game.Game()
    g.new_game(
        num_players=2,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=True,
        silent_ending=True,
        forced_aip_class=SmartAIP,
    )
    return g


class TestCheckFightOver:
    """Unit-pin the win/draw state machine without running the fight loop."""

    def make_fight(self):
        random.seed(0)  # environment bonus is drawn at construction
        fa, fb = lv1_fighter('A'), lv1_fighter('B')
        fight = BaseFight([fa], [fb])
        fa.hp = fb.hp = 10
        return fight, fa, fb

    def test_ongoing_fight_is_not_over(self):
        fight, fa, fb = self.make_fight()
        assert not fight.check_fight_over()
        assert fight.winners == [] and fight.win is None

    def test_side_b_wins_when_side_a_is_down(self):
        fight, fa, fb = self.make_fight()
        fa.hp = 0
        assert fight.check_fight_over()
        assert fight.winners == [fb]
        assert fight.losers == [fa]
        assert fight.win is False  # win means "side A won"

    def test_side_a_wins_when_side_b_is_down(self):
        fight, fa, fb = self.make_fight()
        fb.hp = 0
        assert fight.check_fight_over()
        assert fight.winners == [fa]
        assert fight.win is True

    def test_everybody_down_is_a_draw(self):
        fight, fa, fb = self.make_fight()
        fa.hp = fb.hp = 0
        assert fight.check_fight_over()
        assert fight.winners == []
        assert fight.losers == [fa, fb]
        assert fight.win is False

    def test_fresh_fighter_has_zero_hp_until_prepared(self):
        # hp is only set to hp_max by prepare_for_fight; a bare Fighter is "down"
        f = lv1_fighter('Fresh')
        assert f.hp == 0
        assert f.hp_max > 0


class TestFightSettings:
    def test_environment_bonus_disabled_is_zero(self):
        # BUG?: environment_bonus = environment_allowed * random.choice(...) means
        # a disallowed environment gives a 0 multiplier, not 1.0; pinned as-is
        random.seed(0)
        fight = BaseFight([lv1_fighter('A')], [lv1_fighter('B')], environment_allowed=False)
        assert fight.environment_bonus == 0

    def test_environment_bonus_allowed(self):
        random.seed(0)
        fight = BaseFight([lv1_fighter('A')], [lv1_fighter('B')], environment_allowed=True)
        assert fight.environment_bonus in ENVIRONMENT_BONUSES

    def test_get_time_and_seconds(self):
        random.seed(0)
        fight = BaseFight([lv1_fighter('A')], [lv1_fighter('B')])
        fight.timer = 250
        assert fight.get_seconds() == 125
        assert fight.get_time() == (2, 5)


class TestCrowdFights:
    def test_one_vs_many_terminates(self):
        for seed in range(5):
            random.seed(seed)
            one = fighter_factory.new_fighter(5)
            crowd = fighter_factory.new_fighter(3, n=3)
            f = AutoFight([one], crowd)
            assert f.winners is not None
            assert len(f.all_fighters) == 4

    def test_winners_come_from_one_side(self):
        random.seed(0)
        one = fighter_factory.new_fighter(5)
        crowd = fighter_factory.new_fighter(3, n=3)
        f = AutoFight([one], crowd)
        if f.winners:
            assert all(w in f.side_a for w in f.winners) or all(
                w in f.side_b for w in f.winners
            )

    def test_strong_crowd_beats_lone_fighter(self):
        wins = 0
        n = 10
        for seed in range(n):
            random.seed(500 + seed)
            crowd = fighter_factory.new_fighter(10, n=3)
            one = fighter_factory.new_fighter(3)
            f = AutoFight([one], crowd)
            if f.winners and f.winners[0] in f.side_b:
                wins += 1
        assert wins >= n - 2

    def test_lone_warrior_accomplishment(self):
        # single winner against 5+ losers earns 'Lone Warrior'
        g = make_game()
        p = g.players[0]
        p.level_up(19)
        won = False
        for seed in range(50):
            random.seed(seed)
            thugs = fighter_factory.new_thug(n=5)
            f = AutoFight([p], thugs)
            if f.winners == [p]:
                won = True
                break
            p.hp = p.hp_max  # revive for the next attempt
        assert won, 'lv-20 player should beat five thugs within 50 seeds'
        assert 'Lone Warrior' in p.accompl


class TestWeaponFights:
    def test_weapon_fight_terminates(self):
        for seed in range(5):
            random.seed(seed)
            fa = fighter_factory.new_fighter(5)
            fb = fighter_factory.new_fighter(5)
            fa.arm()
            fb.arm()
            f = AutoFight([fa], [fb])
            assert f.winners is not None

    def test_fighters_are_disarmed_after_fight(self):
        random.seed(0)
        fa = fighter_factory.new_fighter(5)
        fb = fighter_factory.new_fighter(5)
        fa.arm()
        fb.arm()
        assert fa.weapon is not None and fb.weapon is not None
        AutoFight([fa], [fb])
        assert fa.weapon is None and fb.weapon is None


class TestSparring:
    def test_spar_returns_bool(self):
        random.seed(0)
        fa = fighter_factory.new_fighter(5)
        fb = fighter_factory.new_fighter(5)
        result = fa.spar(fb)
        assert isinstance(result, bool)

    def test_spar_between_players_gives_no_injuries(self):
        g = make_game()
        pa, pb = g.players
        for seed in range(5):
            random.seed(seed)
            pa.hp, pb.hp = pa.hp_max, pb.hp_max
            pa.spar(pb)
            assert pa.inact_status == '' and pb.inact_status == ''


class TestExpAndStats:
    def test_fight_gives_exp_and_counts_stats(self):
        g = make_game()
        p = g.players[0]
        exp_before = p.exp
        random.seed(1)
        thug = fighter_factory.new_thug()
        AutoFight([p], [thug])
        assert p.stats_dict['num_fights'] == 1
        assert g.fights_total == 1
        # losers get LOSER_EXP, winners more; either way exp grows
        assert p.exp >= exp_before + LOSER_EXP

    def test_winner_and_loser_stats(self):
        g = make_game()
        p = g.players[0]
        p.level_up(19)
        random.seed(0)
        thug = fighter_factory.new_thug()
        f = AutoFight([p], [thug])
        assert f.winners == [p]  # sanity for the seed
        assert p.stats_dict['fights_won'] == 1
        assert p.stats_dict['times_koed'] == 0

    def test_loser_gets_koed_stat_and_injury(self):
        g = make_game()
        p = g.players[0]
        random.seed(0)  # lv-1 player loses to the thug with this seed
        thug = fighter_factory.new_thug()
        f = AutoFight([p], [thug])
        assert f.winners == [thug]
        assert p.stats_dict['times_koed'] == 1
        # knocked-out players get injured (inactive for some days)
        assert p.inact_status == 'injured'
        assert 1 <= p.inactive <= p.max_days_to_recover


class TestBlocking:
    """Pins for the BLOCK_POWER shadowing fix: the per-fighter hook
    (BLOCK_DEFAULT_POWER) and the global constant (BLOCK_POWER) must not
    collapse into one name, or MRO makes blocks absorb ~nothing."""

    def test_block_constants_resolve_correctly(self):
        f = lv1_fighter('A')
        assert f.BLOCK_POWER == 20  # global, StrikeMechanics
        assert f.BLOCK_DEFAULT_POWER == 1.0  # per-fighter hook, FightActions

    def test_dfs_pwr_is_meaningful(self):
        random.seed(0)
        fa, fb = lv1_fighter('A'), lv1_fighter('B')
        fight = BaseFight([fa], [fb])
        fight.prepare_fighters()
        fa.calc_stamina_factor()
        fa.dfs_bonus = fa.dfs_penalty_mult = 1.0
        fa.target = fb
        fb.action = next(m for m in fb.moves if m.name == 'Punch')
        fa.calc_dfs()
        # pre-fix the shadowed formula gave dfs_pwr ~= 80/400 = 0.2; a working
        # block must absorb a meaningful share of a punch (Punch power = 26)
        assert fa.dfs_pwr >= 20


class TestDraw:
    def test_draw_gives_exp_without_crash(self):
        # draw: no winners; give_exp must not divide by zero
        g = make_game()
        p1, p2 = g.players
        fight = BaseFight([p1], [p2])
        fight.prepare_fighters()
        fight.main_player = p1
        fight.winners = []
        fight.losers = [p1, p2]
        exp1, exp2 = p1.exp, p2.exp
        fight.give_exp()
        draw_exp = round(BASE_FIGHT_EXP / 2)  # DRAW_EXP_DIVISOR = 2
        assert p1.exp == exp1 + draw_exp
        assert p2.exp == exp2 + draw_exp


class TestInFightStats:
    """Per-fight strike stats: collected in Fighter.fight_stats during the
    fight, shown post-fight via BaseFight.show_stats, accumulated into player
    stats_dict/move_usage in handle_player_stats."""

    def fight_with_player(self, seed=1):
        g = make_game()
        p = g.players[0]
        random.seed(seed)
        thug = fighter_factory.new_thug()
        f = AutoFight([p], [thug])
        return g, p, thug, f

    def test_fight_stats_collected_for_all_fighters(self):
        _, p, thug, _ = self.fight_with_player()
        for ftr in (p, thug):
            fs = ftr.fight_stats
            assert fs['thrown'] >= 0
            assert 0 <= fs['landed'] <= fs['thrown']
            assert fs['dam_dealt'] >= 0
            assert fs['moves_used']  # everyone at least guards/steps
        # somebody won, so somebody dealt damage
        assert p.fight_stats['dam_dealt'] + thug.fight_stats['dam_dealt'] > 0

    def test_thrown_counts_only_strikes(self):
        _, p, _, _ = self.fight_with_player()
        from kf_lib.kung_fu.moves import ALL_MOVES_DICT
        strikes = sum(
            cnt
            for name, cnt in p.fight_stats['moves_used'].items()
            if name in ALL_MOVES_DICT and ALL_MOVES_DICT[name].power
        )
        assert strikes == p.fight_stats['thrown']

    def test_stats_accumulate_into_player_stats(self):
        _, p, _, _ = self.fight_with_player()
        fs = p.fight_stats
        assert p.get_stat('strikes_thrown') == fs['thrown']
        assert p.get_stat('strikes_landed') == fs['landed']
        assert p.get_stat('dam_dealt') == fs['dam_dealt']
        assert p.move_usage == fs['moves_used']

    def test_show_stats_prints_per_fighter_lines(self, capsys):
        _, p, thug, f = self.fight_with_player()
        f.show_stats()
        out = capsys.readouterr().out
        assert p.name in out and thug.name in out
        assert 'landed' in out and 'damage dealt' in out

    def test_favorite_move_and_biography(self):
        _, p, _, _ = self.fight_with_player()
        fav = p.get_favorite_move()
        assert fav == max(p.move_usage.items(), key=lambda kv: kv[1])[0]
        from kf_lib.game.biographies import generate_bio
        fav_strike = p.get_favorite_move(attack_only=True)
        if fav_strike:  # the player threw at least one strike
            assert f'signature move was the {fav_strike}' in generate_bio(p)

    def test_stats_report_fav_move_is_attack_only(self):
        # the "Fav. move" row must match the biography's signature move:
        # Guard/maneuvers are recorded but never shown as the favorite
        _, p, _, _ = self.fight_with_player()
        p.move_usage = {'Guard': 100, 'Punch': 5}
        from kf_lib.game.game_stats import get_player_data
        rows = dict(get_player_data(p))
        assert rows['Fav. move'] == 'Punch'


class TestExpMath:
    def test_loser_exp_constant(self):
        # exp math pinned from constants: losers always get LOSER_EXP
        assert LOSER_EXP == round(BASE_FIGHT_EXP * 0.1)
        assert LOSER_EXP_DIVISOR == 4


class TestRelStrength:
    """Relative-strength estimation used by AI decisions."""

    def test_equal_opponent_is_fair_fight(self):
        random.seed(0)
        fa = fighter_factory.new_fighter(5)
        fb = fighter_factory.copy_fighter(fa)
        ratio, legend = fa.get_rel_strength(fb)
        assert ratio == 1.0
        assert legend == 'fair fight'

    def test_two_equal_opponents_are_extremely_risky(self):
        random.seed(0)
        fa = fighter_factory.new_fighter(5)
        fb = fighter_factory.copy_fighter(fa)
        fc = fighter_factory.copy_fighter(fa)
        ratio, legend = fa.get_rel_strength(fb, fc)
        assert ratio == 2.0
        assert legend == 'impossible'

    def test_weak_opponent_is_no_risk(self):
        random.seed(0)
        strong = fighter_factory.new_fighter(20)
        weak = fighter_factory.new_fighter(1)
        ratio, legend = strong.get_rel_strength(weak)
        assert ratio < 0.5
        assert legend in ('no risk', 'very low risk')

    def test_allies_lower_the_ratio(self):
        random.seed(0)
        fa = fighter_factory.new_fighter(5)
        fb = fighter_factory.copy_fighter(fa)
        alone, _ = fa.get_rel_strength(fb)
        with_ally, _ = fa.get_rel_strength(fb, allies=[fighter_factory.copy_fighter(fa)])
        assert with_ally < alone

    def test_mean_flag_averages_multiple_opponents(self):
        # free-for-all estimate: average opponent power, not the sum
        random.seed(0)
        fa = fighter_factory.new_fighter(5)
        fb = fighter_factory.copy_fighter(fa)
        fc = fighter_factory.copy_fighter(fa)
        ratio, legend = fa.get_rel_strength(fb, fc, mean=True)
        assert ratio == 1.0
        assert legend == 'fair fight'

    def test_copy_fighter_preserves_combat_relevant_atts(self):
        random.seed(0)
        f = fighter_factory.new_fighter(8)
        f.arm('knife')
        c = fighter_factory.copy_fighter(f)
        assert c.get_exp_worth() == f.get_exp_worth()
        assert c.weapon is not None and c.weapon.name == 'knife'
        assert [m.name for m in c.moves] == [m.name for m in f.moves]


class TestFreeForAll:
    """Free-for-all fights: everyone fights everyone, last man standing wins."""

    def run_ffa(self, fighters, seed=0):
        random.seed(seed)
        return free_for_all(fighters, return_fight_obj=True)

    def test_three_way_ffa_ends_with_at_most_one_winner(self):
        fs = [lv1_fighter(name) for name in 'ABC']
        f = self.run_ffa(fs)
        assert len(f.winners) <= 1
        assert sorted(f.winners + f.losers, key=id) == sorted(fs, key=id)
        assert f.win == bool(f.winners and f.winners[0] is fs[0])

    def test_eight_way_ffa_terminates(self):
        fs = [fighter_factory.new_thug() for _ in range(8)]
        f = self.run_ffa(fs)
        assert len(f.winners) <= 1
        assert len(f.winners) + len(f.losers) == len(fs)

    def test_seeded_ffa_variants(self):
        for seed in range(10):
            fs = [fighter_factory.new_thug() for _ in range(4)]
            f = self.run_ffa(fs, seed=seed)
            assert len(f.winners) <= 1
            assert f.win == bool(f.winners and f.winners[0] is fs[0])

    def test_strongest_fighter_wins(self):
        strong = fighter_factory.new_fighter(20)
        weak1 = fighter_factory.new_fighter(1)
        weak2 = fighter_factory.new_fighter(1)
        f = self.run_ffa([strong, weak1, weak2])
        assert f.winners == [strong]
        assert f.win is True

    def test_everybody_down_is_a_draw(self):
        random.seed(0)
        fs = [lv1_fighter(name) for name in 'ABC']
        f = BaseFreeForAll(fs, [])
        for ff in fs:
            ff.hp = 0
        assert f.check_fight_over()
        assert f.winners == []
        assert f.losers == fs
        assert f.win is False

    def test_ffa_targeting_excludes_self(self):
        random.seed(0)
        fs = [lv1_fighter(name) for name in 'ABC']
        f = BaseFreeForAll(fs, [])
        for ff in fs:
            ff.hp = 10
        assert not f.check_fight_over()
        for ff in fs:
            assert f.get_act_targets(ff) == [x for x in fs if x is not ff]
            assert f.get_act_allies(ff) == [ff]

    def run_player_ffa(self, n_enemies, player_wins, lv_up=0):
        g = make_game()
        p = g.players[0]
        if lv_up:
            p.level_up(lv_up)
        for seed in range(50):
            random.seed(seed)
            enemies = fighter_factory.new_thug(n=n_enemies)
            f = free_for_all([p] + enemies, return_fight_obj=True)
            if bool(f.winners) and (f.winners[0] is p) == player_wins:
                return f, p
            p.hp = p.hp_max  # revive for the next attempt
        raise AssertionError(f'no suitable FFA outcome within 50 seeds')

    def test_ffa_winner_exp_uses_average_not_sum(self):
        # an FFA win pays per-capita exp: the losers were fighting each other too
        f, p = self.run_player_ffa(n_enemies=5, player_wins=True, lv_up=19)
        exp_gains = []
        p.gain_exp = lambda n, **kw: exp_gains.append(n)
        f.give_exp()
        exp_gained = exp_gains[-1]
        losers_yield = sum(e.exp_yield for e in f.losers)
        mean_based = round((losers_yield / len(f.losers) / p.exp_yield) ** 1.5 * BASE_FIGHT_EXP)
        sum_based = round((losers_yield / p.exp_yield) ** 1.5 * BASE_FIGHT_EXP)
        assert exp_gained <= round(mean_based * 1.75)  # up to three +25% exp bonuses
        assert exp_gained < sum_based  # the old, sum-based behavior

    def test_ffa_win_grants_no_crowd_accomplishments(self):
        # beating five separate enemies in an FFA is not beating a united group
        f, p = self.run_player_ffa(n_enemies=5, player_wins=True, lv_up=19)
        assert len(f.losers) >= 5  # sanity: would be 'Lone Warrior' in a normal fight
        assert 'Lone Warrior' not in p.accompl
        assert 'Against All Odds' not in p.accompl

    def test_win_message_shows_actual_winner_to_losing_viewer(self):
        f, p = self.run_player_ffa(n_enemies=3, player_wins=False)
        p.target = f.losers[-1]  # stale last target, not the winner
        f.show_win_message()
        assert p.target is f.winners[0]
        assert f.winners[0].ascii_name == 'Win'


class TestGroupFreeForAll:
    """Group free-for-all: groups fight each other, no infighting."""

    def run_gffa(self, groups, seed=0):
        random.seed(seed)
        return group_free_for_all(groups, return_fight_obj=True)

    def make_groups(self):
        return [
            [lv1_fighter('Hero')],
            [lv1_fighter('Boss1'), lv1_fighter('Guard1')],
            [lv1_fighter('Boss2'), lv1_fighter('Guard2')],
        ]

    def test_three_groups_end_with_at_most_one_winning_group(self):
        groups = self.make_groups()
        f = self.run_gffa(groups)
        assert f.win in (True, False)
        all_fs = [ff for grp in groups for ff in grp]
        assert sorted(f.winners + f.losers, key=id) == sorted(all_fs, key=id)
        # winners, if any, form exactly one whole group
        if f.winners:
            assert any(sorted(f.winners, key=id) == sorted(grp, key=id) for grp in groups)

    def test_win_is_true_iff_protagonist_group_wins(self):
        for seed in range(10):
            groups = self.make_groups()
            f = self.run_gffa(groups, seed=seed)
            assert f.win == bool(f.winners and groups[0][0] in f.winners)

    def test_no_infighting(self):
        random.seed(0)
        groups = self.make_groups()
        f = BaseGroupFreeForAll(groups)
        for grp in groups:
            for ff in grp:
                ff.hp = 10
        assert not f.check_fight_over()
        hero, boss1, guard1 = groups[0][0], groups[1][0], groups[1][1]
        assert f.get_act_targets(boss1) == [hero] + groups[2]
        assert f.get_act_allies(boss1) == [boss1, guard1]

    def test_group_with_survivors_beats_stronger_half_dead_group(self):
        random.seed(0)
        groups = self.make_groups()
        f = BaseGroupFreeForAll(groups)
        groups[0][0].hp = 0  # protagonist down
        groups[1][0].hp = 10  # boss1 standing
        groups[1][1].hp = 0  # guard1 down
        for ff in groups[2]:
            ff.hp = 0
        assert f.check_fight_over()
        assert f.winners == groups[1]  # whole group, incl. the downed guard
        assert f.win is False

    def test_seeded_group_ffa_variants_terminate(self):
        for seed in range(10):
            random.seed(seed)
            groups = [
                [fighter_factory.new_thug()],
                [fighter_factory.new_thug() for _ in range(2)],
                [fighter_factory.new_thug() for _ in range(2)],
            ]
            f = self.run_gffa(groups, seed=seed)
            assert len(f.winners) + len(f.losers) == 5
