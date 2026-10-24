"""The master's teachings stay true: each saying is pinned to the values and
rules it paraphrases (kf_lib/happenings/teachings.py). A failure here means a
fight rule changed: reword the saying (and its Russian translation), then
update the pinned value."""
import ast
import inspect
import os
import random
import re
from types import SimpleNamespace

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib import i18n
from kf_lib.actors.fighter import Fighter
from kf_lib.actors.player import SmartAIP
import kf_lib.actors.fighter._fight_actions as fight_actions_mod
import kf_lib.actors.fighter._strike_mechanics as strike_mod
from kf_lib.fighting.fight._base_fight import BaseFight
from kf_lib.fighting.fight._sparring import BaseSparring
from kf_lib.happenings import encounters
from kf_lib.happenings.encounters import _school as school_mod
from kf_lib.happenings.teachings import get_teachings
from kf_lib.kung_fu.moves import ALL_MOVES_DICT

TEACHINGS = get_teachings()
BY_ID = {t.id: t for t in TEACHINGS}


def lv1_fighter(name):
    return Fighter(name, 'Long Fist', level=1, tech_names=[], move_names=[])


def duel():
    random.seed(0)
    fa, fb = lv1_fighter('A'), lv1_fighter('B')
    fight = BaseFight([fa], [fb])
    fight.prepare_fighters()
    fa.target, fb.target = fb, fa
    fb.action = ALL_MOVES_DICT['Punch']
    return fa, fb


def base_dfs():
    fa, fb = duel()
    fa.calc_stamina_factor()
    fa.dfs_bonus = fa.dfs_penalty_mult = 1.0
    fa.calc_dfs()
    return fa, fb, (fa.to_dodge, fa.to_block, fa.dfs_pwr)


def moves_named(word):
    return [m for n, m in ALL_MOVES_DICT.items() if word in n.split()]


# --- behaviour checks for teachings whose fact is a formula or a rule ---

def check_block_from_health():
    fa, _, (dodge, block, pwr) = base_dfs()
    fa.strength_full += 3
    fa.calc_dfs()
    assert fa.dfs_pwr == pytest.approx(pwr)
    fa.health_full += 3
    fa.calc_dfs()
    assert fa.dfs_pwr > pwr


def check_weapon_blocks():
    fa, _, (dodge, block, pwr) = base_dfs()
    fa.wp_dfs_bonus = 1.5
    fa.calc_dfs()
    assert fa.to_dodge == pytest.approx(dodge)
    assert fa.to_block == pytest.approx(block * 1.5)
    assert fa.dfs_pwr == pytest.approx(pwr * 1.5)


def check_repetition():
    fa, fb, (dodge, block, _) = base_dfs()
    punch = fb.action
    factors = []
    for n in range(4):
        fb.previous_actions.clear()
        fb.previous_actions.extend([punch] * n)
        factors.append(fb.get_rep_actions_factor(punch))
    assert factors == sorted(factors) and factors[0] == 1.0
    assert factors[-1] == pytest.approx(2.0, abs=0.02)  # 'about twice as easy'
    fa.calc_dfs()
    assert fa.to_dodge == pytest.approx(dodge * factors[-1])


def check_dodge_feeds_qi(monkeypatch):
    for rolls, gain in (([0.1], 10), ([0.5, 0.2], 5)):  # dodge, block
        fa, fb = duel()
        fb.atk_pwr, fb.to_hit = 30, 1.0
        fa.to_dodge, fa.to_block, fa.dfs_pwr = 0.30, 0.25, 10
        fa.qp_max, fa.qp, fa.qp_gain = 100, 0, 10
        it = iter(rolls + [0.99] * 10)
        monkeypatch.setattr(fight_actions_mod, 'rnd', lambda: next(it))
        fa.defend()
        assert fa.qp == gain


def check_complex_forms():
    f = lv1_fighter('A')
    simple, intricate = SimpleNamespace(complexity=1), SimpleNamespace(complexity=3)
    assert f.get_move_fail_chance(intricate) > f.get_move_fail_chance(simple)
    before = f.get_move_fail_chance(intricate)
    f.agility_full += 3
    assert f.get_move_fail_chance(intricate) < before


def check_cost_on_miss(monkeypatch):
    fa, fb = duel()
    monkeypatch.setattr(fb, 'get_move_fail_chance', lambda move: 1.0)
    stamina = fb.stamina
    fb.exec_move()
    assert fb.stamina == stamina - fb.action.stam_cost


def check_momentum_knockback():
    def knockback(momentum):
        fa, fb = duel()
        fa.distances[fb] = fb.distances[fa] = 1
        fa.momentum = momentum
        fb.dam = fa.hp_max // 2
        fb.try_knockback()
        return fa.distances[fb] - 1

    assert knockback(0) > knockback(2)


def check_distance():
    attacks = [m for m in ALL_MOVES_DICT.values() if m.power]
    assert {m.distance for m in attacks} == {1, 2, 3, 4}


def check_antiground():
    assert any('antiground only' in m.features for m in ALL_MOVES_DICT.values())


def check_shock():
    fa, fb = duel()
    fb.do_shock_move()
    assert fa.check_status('shocked') and fa.check_status('skip')
    fa.calc_dfs()
    assert fa.to_dodge == fa.to_block == 0
    assert all('do_shock_move' in m.functions for m in moves_named('Shocking'))


def check_nerve_slow():
    ms = moves_named('Nerve')
    assert ms and all('do_mob_dam' in m.functions for m in ms)
    f = lv1_fighter('A')
    base = f.get_move_time_cost(ALL_MOVES_DICT['Punch'])
    f.status['slowed down'] = 100
    # 'about 40% longer': 1 / (1 - 0.3) = 1.43, with rounding to whole time units
    assert f.get_move_time_cost(ALL_MOVES_DICT['Punch']) / base == pytest.approx(1.4, abs=0.1)


def check_solar_breath():
    ms = moves_named('Solar')
    assert ms and all('do_stam_dam' in m.functions for m in ms)


def check_debilitating():
    ms = moves_named('Debilitating')
    assert ms and all(
        {'do_shock_move', 'do_mob_dam', 'do_stam_dam'} <= set(m.functions) for m in ms
    )


def check_claws_bleed():
    claws = [m for m in moves_named('Claw') if m.name != 'Dragon Claw']
    assert claws and all('cause_bleeding' in m.functions for m in claws)
    assert 'cause_bleeding' not in ALL_MOVES_DICT['Dragon Claw'].functions
    assert all('cause_bleeding' in m.functions for m in moves_named('Slashing'))
    fa, fb = duel()
    fb.dam = 20
    fb.cause_bleeding()
    hp = fa.hp
    fa.apply_bleeding()
    fa.apply_bleeding()  # bleeding doesn't stop by itself
    assert fa.hp == hp - 2 * fa.bleeding > 0 and fa.bleeding == 3


def check_statuses_speed(monkeypatch):
    monkeypatch.setattr(strike_mod, 'rndint_2d', lambda a, b: 100)

    def stun_duration(speed):
        fa, fb = duel()
        fa.speed_full = speed
        fa.cause_stun()
        return fa.status['stunned']

    assert stun_duration(8) < stun_duration(4)


def check_catch_breath_focus():
    assert ALL_MOVES_DICT['Catch Breath'].stam_cost == -20
    assert ALL_MOVES_DICT['Focus'].qi_cost == -20


def check_exp_strong():
    exponent = float(re.search(r'\*\* ([\d.]+)', inspect.getsource(BaseFight.give_exp))[1])
    assert exponent > 1


def check_exp_bonuses():
    fight = SimpleNamespace(timer=0)  # a 0-second win
    p = SimpleNamespace(name='A', took_damage=False, kos_this_fight=3, exp_bonuses=0,
                        show=lambda s: None, log=lambda s: None)
    assert BaseFight.handle_exp_bonuses(fight, p, 100) == pytest.approx(175)
    fight.timer = 2 * 11  # 11 seconds: too slow for 'Quick victory'
    assert BaseFight.handle_exp_bonuses(fight, p, 100) == pytest.approx(150)


def check_sparring():
    assert BaseSparring.handle_injuries is not BaseFight.handle_injuries
    assert BaseSparring.give_exp is BaseFight.give_exp


def check_injury():
    injured = []
    fighter = SimpleNamespace(is_player=True, hp=0, injure=lambda: injured.append(1))
    BaseFight.handle_injuries(SimpleNamespace(all_fighters=[fighter]))
    assert injured


CHECKS = {
    'block_from_health': check_block_from_health,
    'weapon_blocks': check_weapon_blocks,
    'repetition': check_repetition,
    'dodge_feeds_qi': check_dodge_feeds_qi,
    'complex_forms': check_complex_forms,
    'cost_on_miss': check_cost_on_miss,
    'momentum_knockback': check_momentum_knockback,
    'distance': check_distance,
    'antiground': check_antiground,
    'shock': check_shock,
    'nerve_slow': check_nerve_slow,
    'solar_breath': check_solar_breath,
    'debilitating': check_debilitating,
    'claws_bleed': check_claws_bleed,
    'statuses_speed': check_statuses_speed,
    'catch_breath_focus': check_catch_breath_focus,
    'exp_strong': check_exp_strong,
    'exp_bonuses': check_exp_bonuses,
    'sparring': check_sparring,
    'injury': check_injury,
}


def test_ids_are_unique_and_texts_present():
    assert len(BY_ID) == len(TEACHINGS)
    assert all(t.saying and t.fact for t in TEACHINGS)


def test_every_teaching_is_pinned_to_something():
    for t in TEACHINGS:
        assert t.ties or t.rule_tests or t.id in CHECKS, t.id
    assert set(CHECKS) <= set(BY_ID)


@pytest.mark.parametrize('t', TEACHINGS, ids=lambda t: t.id)
def test_doc_section_exists(t):
    fname, heading = t.doc.split(': ', 1)
    with open(os.path.join('docs', fname), encoding='utf-8') as f:
        headings = {line.lstrip('#').strip() for line in f if line.startswith('#')}
    assert heading in headings


@pytest.mark.parametrize('t', [t for t in TEACHINGS if t.ties], ids=lambda t: t.id)
def test_tied_values(t):
    f = lv1_fighter('A')
    for name, value in t.ties.items():
        assert getattr(f, name) == pytest.approx(value), f'{t.id}: {name}'


@pytest.mark.parametrize('t', [t for t in TEACHINGS if t.rule_tests], ids=lambda t: t.id)
def test_rule_tests_exist(t):
    for ref in t.rule_tests:
        path, cls_name, func_name = ref.split('::')
        with open(path, encoding='utf-8') as f:
            tree = ast.parse(f.read())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
        assert any(getattr(n, 'name', None) == func_name for n in cls.body), ref


@pytest.mark.parametrize('tid', sorted(CHECKS))
def test_behaviour(tid, monkeypatch):
    check = CHECKS[tid]
    if 'monkeypatch' in inspect.signature(check).parameters:
        check(monkeypatch)
    else:
        check()


def test_all_teachings_are_translated_to_russian():
    try:
        i18n.set_language('ru')
        ru = {t.id: t for t in get_teachings()}
    finally:
        i18n.set_language('en')
    for t in TEACHINGS:
        assert ru[t.id].saying != t.saying and ru[t.id].fact != t.fact, t.id


# --- the encounter ---

def make_student():
    random.seed(0)
    g = game.Game()
    g.new_game(num_players=1, coop=False, ai_only=True, auto_save_on=False,
               generated_styles=True, silent_ending=True, forced_aip_class=SmartAIP)
    p = g.players[0]
    assert not p.is_master
    return p


def test_teaching_is_kept_out_of_the_daily_encounter_pool():
    assert encounters.MasterTeaching not in encounters.all_random_encounter_classes
    assert encounters.MasterTeaching in encounters.PRACTICE_SCHOOL_ENCS


def test_master_shares_a_teaching_and_never_the_same_twice_in_a_row(monkeypatch):
    p = make_student()
    monkeypatch.setattr(school_mod, 'rnd', lambda: 0.0)
    shown = []
    for _ in range(30):
        n_log = len(p.plog)
        encounters.MasterTeaching(p)
        line = p.plog[n_log]
        shown.append(next(t.id for t in TEACHINGS if f'"{t.saying}" ({t.fact})' in line))
    assert all(a != b for a, b in zip(shown, shown[1:]))


def test_no_teaching_when_the_roll_fails(monkeypatch):
    p = make_student()
    monkeypatch.setattr(school_mod, 'rnd', lambda: 1.0)
    n_log = len(p.plog)
    encounters.MasterTeaching(p)
    assert len(p.plog) == n_log
