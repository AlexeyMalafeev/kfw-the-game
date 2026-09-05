# Fight mechanics

How a fight works, as implemented. Source files: `kf_lib/fighting/fight/` (fight
engine), `kf_lib/actors/fighter/` (`_fight_actions.py`, `_strike_mechanics.py`,
`_fight_attributes.py`, `_distances.py`), `kf_lib/fighting/distances.py`,
`kf_lib/kung_fu/` (moves, techniques, boosts), `kf_lib/ai/fight_ai.py`.
Items marked ⚠️ look unintentional or surprising — verify before building on them.

## Overview

A fight is an object (`BaseFight` subclass) that owns the event timeline. It is
*event-driven on a time axis*, not round-robin: fighters are scheduled in
`self.order` (dict `{time_unit: [fighters]}`) and the loop always advances
`self.timer` to the earliest scheduled time. 2 time units = 1 second
(`TIME_TO_SEC_DIVISOR` in `_base_fight.py`). (`TIME_UNIT_MULTIPLIER = 20` in
`_strike_mechanics.py` is defined but never used ⚠️.)

Each fighter acts alone on their turn: pick target, pick move, execute, pay its
costs, get re-queued `time_cost` units later. Attack moves resolve immediately
against the chosen target, including its defense and any preemptive/counter
strikes.

## Fight setup

`BaseFight.__init__` (`_base_fight.py`) stores `side_a`/`side_b`, derives
`all_fighters` and `active_*` copies, and rolls
`environment_bonus = environment_allowed * random.choice((1.2, 1.3, 1.5, 1.8, 2.0))`.
⚠️ When `environment_allowed` is `False` this is `0.0`, not `1.0`. Harmless today
only because `try_environment` independently checks `environment_allowed`; if
anything ever applies `environment_bonus` without that check, no-environment
fights would *zero out* combat numbers instead of leaving them unchanged.

`prepare_for_fight` (`_fight_actions.py`) resets per-fight state: `hp = hp_max`,
`stamina = stamina_max`, `qp = round(qp_max * qp_start)`, `bleeding = 0`,
`status = {}`, `momentum = 0`, `took_damage = False`, `kos_this_fight = 0`,
`exp_yield = get_exp_worth()`, `set_distances_before_fight()`.

Distances (`fighting/distances.py`, `fighter/_distances.py`): every pair of
fighters gets a random starting distance in 1–4, stored symmetrically in
`f.distances[other]`. Moves with `distance != 0` are only usable at exactly that
distance. Initial scheduling (`fight_loop`): each fighter is queued at
`max(speed_full) - speed_full`, so the fastest acts at time 0 and the rest are
offset by their speed deficit.

## Turn loop

`BaseFight.fight_loop`:

1. Jump `timer` to the earliest key in `order`; `elapsed` time passes.
2. `handle_status_times(elapsed)`: every status on every active fighter loses
   `elapsed` units; statuses at ≤ 0 are deleted.
3. Fighters scheduled at `timer` act in shuffled order. For each:
   - `apply_bleeding()` — lose `bleeding` HP (can KO: "passes out").
   - Skip if at `hp <= 0`; `check_fight_over()` runs after each KO.
   - If status `'skip'` is active: re-queue at `timer + status['skip']`, no
     action.
   - `start_fight_turn()`: refresh `act_targets` (opposing active side) /
     `act_allies`; reset `dfs_bonus = 1.0` and `dfs_penalty_mult = 1.0`; regen
     (`hp_gain`, `qp_gain`, `stamina_gain`); maybe grab an improvised weapon
     (`try_in_fight_impro_wp`); roll for fury (`try_fury`); recompute
     `stamina_factor`.
   - `choose_target()` (asks AI/human only when >1 target), `choose_move()`.
   - `time_cost = get_move_time_cost(action)`; `exec_move()`; re-queue at
     `timer + time_cost`.
4. `check_fight_over()` again; on end, winners get `'Win'` ascii, losers
   `'Lying'`.

`time_limit = 500000` is a runaway guard: on exceed,
`handle_time_limit_exceeded` prints debug info and sets every active fighter's
`hp = -10`, forcing a draw.

## Action selection

`get_av_moves` (`_fight_actions.py`) filters `self.moves` + `weapon.moves`:
enough `stamina`/`qp` for the costs; `distance` moves must match the current
distance to the target; `'antiground only'` / `'also antiground'` moves require
a lying target, all other distance moves require a standing one. Moves with
`distance == 0` (maneuvers, Guard, Focus, …) are always available.

`Move` fields (`kung_fu/moves.py`, data in `moves/all_moves.txt`): `distance`,
`dist_change`, `power`, `accuracy`, `complexity`, `stam_cost`, `time_cost`,
`qi_cost`, `features` (a `distN` feature is auto-added from `distance`),
`functions` (names of `Fighter` methods run on hit/execution), `tier`, `freq`.
`power > 0` = strike, else maneuver. Negative costs *restore* a pool
(`Catch Breath` has `stam_cost = -20`, `Focus` has `qi_cost = -20`).

Humans (`human_controlled_fighter.py`) pick from a menu when `is_auto_fighting`
is `False` (set by `NormalFight`); otherwise `fight_ai` chooses (see AI note).

## Strike resolution pipeline

`exec_move`: `action.power` → `attack()`, else `maneuver()`; then
`apply_move_cost()` — stamina/qi are paid even if the strike whiffed or was
preempted. `attack()` → `try_strike()` → `check_move_failed()` → `do_strike()`;
afterwards the target may `try_counter()`. If the target rolls a preemptive
(`preemptive_chance`, tech-based), `do_preemptive()` fires *instead of* the
incoming attack: the defender strikes the attacker with a random available
attack move (paying its cost) and the original attack never happens.

### Move failure

`get_move_fail_chance = (complexity * move_complexity_mult)^2 / agility_full^2`.
On failure: a strike is silently skipped (plus `cause_off_balance()` on the
attacker if `complexity >= 1`); a maneuver prints `'Fail!'` and causes
`cause_fall()` if `complexity >= 3`, else `cause_off_balance()`.

### Attack numbers — `calc_atk`

```
atk_bonus = atk_mult * Π(feature_strike_mult for action.features)   # each defaults to 1.0
if off-balance: atk_bonus *= off_balance_atk_mult                    # 0.75
atk_pwr = strength_full * power * atk_bonus * stamina_factor / DAM_DIVISOR   # /2
to_hit  = agility_full * accuracy * atk_bonus * stamina_factor
both *= (1 + 0.1 * momentum)                # MOMENTUM_EFFECT_SIZE
if fury: both *= fury_to_all_mult           # 1.6
```

`stamina_factor = stamina / stamina_max / 2 + 0.5` ∈ [0.5, 1.0], computed at the
start of the fighter's own turn.

### Defense numbers — `calc_dfs` (on the defender)

If `shocked`: `to_dodge = to_block = 0` (stunned alone does **not** zero
defense — see Statuses). Otherwise:

```
x = dfs_penalty_mult * agility_full * dodge_mult * 10
    * stamina_factor * rep_actions_factor * dfs_bonus
if off-balance: x *= off_balance_dfs_mult   # 0.75
if lying:       x *= lying_dfs_mult         # 0.5
to_dodge = x / DODGE_DIVISOR                # /3
to_block = x / BLOCK_DIVISOR * wp_dfs_bonus # /2
dfs_pwr  = dfs_penalty_mult * BLOCK_DEFAULT_POWER * block_mult * BLOCK_POWER
           * strength_full * stamina_factor * wp_dfs_bonus
if fury: dfs_pwr *= fury_to_all_mult
```

`rep_actions_factor` punishes repetitive attackers: `1 + 0.33 * n`, where `n` =
how many of the attacker's last 3 actions (`previous_actions`, a maxlen-3 deque)
are this move — up to ×1.99 to the *defender's* dodge/block.

`BLOCK_DEFAULT_POWER` (1.0, `_fight_actions.py`) is the per-fighter hook —
techniques can override it per fighter; `BLOCK_POWER` (20, `_strike_mechanics.py`,
comment: "Punch power = 26") is the global constant. They were once both named
`BLOCK_POWER` and `Fighter`'s MRO shadowed the global with 1.0, making blocks
absorb ~1/400 of the intended damage (fixed 2026-09; see CHANGELOG).

### `do_strike` order

1. `calc_atk(action)`
2. `try_environment('attack')`: if the fighter has `environment_chance`
   (tech-based), environment is allowed, and the roll succeeds — `atk_pwr` and
   `to_hit` × `environment_bonus`.
3. `target.calc_dfs()`
4. `try_unblockable()`: `unblock_chance` roll → `target.to_block = 0`.
5. `target.try_environment('defense')`: `dfs_pwr`, `to_block`, `to_dodge` ×
   `environment_bonus`.
6. `target.defend()`
7. `hit_or_miss()`
8. `target.apply_dfs_penalty()`: `dfs_penalty_mult -= dfs_penalty_step`
   (default 0.2, floored at 0). Since `start_fight_turn` resets it to 1.0, this
   is the anti-crowd mechanic: defense decays per strike taken *between your own
   turns*. The 'Behind You' tech line reduces the step.
9. If the move has `dist_change`, apply it; else `momentum = 0`.
10. Append the move to `previous_actions`.

### `defend` — dodge / block / hit

One roll against both chances:

```
dodge_chance = to_dodge / attacker.to_hit
block_chance = to_block / attacker.to_hit
if roll <= dodge_chance: dodge — attacker.dam = 0, defender gains qp_gain
elif roll <= block_chance: block — dam = max(dam - round(dfs_pwr), 0),
    defender gains qp_gain // 2, try_block_disarm()
else: clean hit
```

⚠️ Because a single roll is compared to dodge first, the *effective* block
probability is `block_chance - dodge_chance`; if `to_dodge >= to_block`,
blocking can never trigger. Chances above 1.0 mean guaranteed defense.

### `hit_or_miss` — only if `dam > 0`

In order:

1. `try_critical()`: `critical_chance` roll → `dam *= critical_dam_mult` (1.5).
   `critical_chance = (agility_full - 3) * 0.05 * critical_chance_mult`.
   Successful rolls increment `fight_stats['criticals']` (since 2026-09).
2. `try_epic()`: `epic_chance` roll → `dam *= epic_dam_mult` (2.0); successful
   rolls increment `fight_stats['epics']`.
   ⚠️ Both multipliers apply to *post-block* damage, since `defend()` already
   ran (hence the "Critical, then evade" oddity in `known bugs.txt`: the
   CRITICAL! line prints after the block/dodge line).
3. `dam = max(dam - toughness, 0)`; `toughness = (level - 1) * 3`.
4. `dam_reduc` (tech): `dam *= 1 - dam_reduc`.
5. `target.take_damage(dam)` → `change_hp(-dam)`, sets `took_damage`.
6. `try_cause_bleeding()`: `chance_cause_bleeding` roll → target's `bleeding`
   pool grows by `max(1, round(dam * 0.15))`; the pool is subtracted from hp at
   the start of each of the *target's own* turns.
7. `try_hit_disarm()`; then the move's `functions` run (`do_move_functions`):
   extra damage (`do_strength_based_dam` & co. = `rndint_2d(1, stat * 5)`;
   qi-based = `rndint_2d(qp, qp * 2)`; level-based = `rndint_2d(1, level * 10)`),
   forced knockback (`do_knockback`: 1–3 steps), shocks, stamina damage
   (`do_stam_dam`: 20% of target `stamina_max`). ⚠️ `do_mob_dam` is
   misleadingly named — it only causes `slowed down`, no damage.
8. `try_stun()`: stun if `dam >= target.hp_max / 2.8` or `stun_chance` roll.
9. `try_knockback()`: skipped if the move has its own `do_knockback`. If the
   target isn't lying: `kb = int(dam / target.hp_max * 5) - target.momentum`;
   `kb > 0` knocks the target back `kb` steps, `kb < 0` *reduces* the target's
   momentum (a rushing target absorbs knockback).
10. `try_knockdown()`: `dam >= 50%` of pre-hit hp → `cause_fall()`;
    `>= 25%` → `cause_off_balance()`. `cause_fall` also deals fall damage
    (`rndint(25, 50) * fall_damage_mult`) and zeroes momentum.
11. `try_ko()`: if target's `hp == 0`, a `resist_ko` roll (tech, max 0.5) sets
    `hp = 1`; otherwise the attacker logs the KO (`kos_this_fight += 1`).

Steps 8–10 still run when the hit already reduced the target to 0 hp — a KO'd
fighter can be shown stunned/knocked back/falling before the KNOCK-OUT line;
`try_ko` comes last by design.

### Maneuvers

`maneuver()`: apply `dist_change` (clamped to 1–4 by `change_distance`), roll
`check_move_failed`, run `functions`. `Guard` (`functions=['guard']`) sets
`dfs_bonus *= guard_dfs_bonus * 1.5`, lasting until the fighter's next turn.
`guard_while_attacking` (tech) instead multiplies `dfs_bonus` by
`1.5 * (1 + guard_while_attacking)` inside `attack()`. Any move without
`dist_change` resets `momentum` to 0.

`get_move_time_cost = time_cost / (speed_full * (0.7 if slowed down))`, then ×
`strike_time_cost_mult` (if `power`) or × `maneuver_time_cost_mult` (elif
`dist_change`); Guard/Focus-type moves get neither multiplier.

Momentum: `change_distance(d, targ)` sets `self.momentum = -d` — closing in
(negative `dist_change`) builds positive momentum (≤ +2 via `Rush Forward`),
retreat/knockback builds negative (down to −3). It scales `atk_pwr`/`to_hit` by
±10% per point and feeds into knockback resistance.

## Statuses and durations

`status` is a dict `{name: remaining_time_units}`; `add_status` *adds* to an
existing duration. All combat status durations are
`rndint_2d(MIN, MAX) // speed_full` — a bell-ish 2d roll divided by speed, so
faster fighters shed statuses in fewer time units. Durations tick down by
`elapsed` every loop iteration.

- `skip`: turn skipped; re-queued after the remaining duration. Always paired
  with `lying` / `stunned` / `shocked`.
- `lying` (100–200): `lying_dfs_mult` (0.5) to dodge/block; immune to further
  knockback/knockdown; enables attackers' antiground moves.
- `stunned` (50–150): only `skip`, no defense penalty. ⚠️ Only `shocked` zeroes
  `to_dodge`/`to_block`; mechanically stun is *nothing but* lost turns.
- `shocked` (50–100): `skip` + zero dodge/block.
- `off-balance` (50–100): atk and dfs × 0.75.
- `slowed down` (300–600): time costs × 1/0.7.
- `fury` (500–1000): `atk_pwr`, `to_hit`, `dfs_pwr` × 1.6. Rolled each own turn
  with chance `(1 - hp/hp_max) * fury_chance` (tech-gated).

## Pools and derived attributes

`_fight_attributes.py`:

- `hp_max = health_full * 50`; `change_hp` clamps to `[0, hp_max]` and zeroes
  `qp` when `hp` hits 0. `hp` never goes negative, so all `hp <= 0` checks are
  effectively `hp == 0`.
- `stamina_max = (50 + 10 * level) * stamina_max_mult`; `stamina_gain` = 10% of
  max per own turn. `qp_max = 5 * level * qp_max_mult`; `qp_gain` = 20% of max
  per own turn (plus full/half `qp_gain` on successful dodge/block). Both clamp.
- `toughness = (level - 1) * 3` — flat subtraction from every hit.
- `*_full = round(base * *_mult)` for the four base atts
  (`_basic_attributes.py`).
- `counter_chance = (agility_full - 3) * 0.05 * counter_chance_mult`;
  `epic_chance = 0.005 * level * epic_chance_mult`.

Counter-attacks (`try_counter`): after the defender fully negated a strike
(`attacker.dam == 0`) and is alive, roll `counter_chance` → `do_counter()` runs
the full strike pipeline back at the attacker with a random available attack
move. ⚠️ Asymmetry: `do_preemptive` pays the move's stamina/qi cost,
`do_counter` does not — counters are free.

## Techs, moves, boosts

`kung_fu/techniques.py`: a `Tech` is a name + flat dict of attribute deltas,
applied by *addition* (`Tech.apply`: `setattr(f, p, getattr(f, p) + delta)`),
then `refresh_full_atts`/`refresh_dependent_atts`. Multiplicative-sounding
params are additive increments to a `1.0` base (e.g. `atk_mult +0.15`), so
stacked techs add rather than compound. Strike-multiplier techs
(`punch_strike_mult` etc.) multiply into `atk_bonus` per matching move feature
in `calc_atk`, and add the feature to `fav_move_features` (biases random move
learning). Values live in `kung_fu/boosts.py` / `boost_combos.py`.

⚠️ Dead/unused boosts: `GRAB_CH1/2` (`grab_chance` unused), `QI_WHEN_ATK`,
`HP_MULT`, `epic_chance_mult`, all `WeaponTech`s ("weapon techniques do
nothing; implement"). ⚠️ The advanced 'Lightning-Fast Strikes' tech uses
`STRIKE_TIME_COST_MULT1` (−0.3) — the same value as basic 'Fast Strikes' —
instead of `STRIKE_TIME_COST_MULT2` (−0.6); upgrading changes nothing.

`kung_fu/moves.py` loads `moves/all_moves.txt` at import (each line `eval()`d
into a `Move`). `get_rand_moves` filters by tier and `fav_move_features`, sorts
by feature overlap, weights by `freq`. ⚠️ `random.choice(pool)` runs *before*
the empty-pool check, so an empty pool raises `IndexError` instead of falling
back to the whole tier.

## End of fight

`check_fight_over` (`_base_fight.py`): fighters at `hp == 0` drop out of
`active_*`. One side empty → the other side wins (`win = True` iff side_a wins).
Everyone down → draw: `winners = []`, `losers = all`, `win = False`.

`give_exp` (only players get exp):

- `winners_diff = (Σ losers' exp_yield / Σ winners' exp_yield) ** 1.5`;
  `winners_gain = winners_diff * BASE_FIGHT_EXP` (25). Beating stronger
  opposition scales exp superlinearly; beating weaker gives little.
- Losers get a flat `LOSER_EXP` (2 = 10% of base) regardless of difficulty.
- `handle_exp_bonuses`: +25% per bonus — quick victory (≤ 10 s), "Not a
  scratch" (`not took_damage`), multi-knockout (`kos_this_fight >= 3`).
- `exp_yield = 10 + str*agi*spd*hlt*0.03 + 3 per tech`, × weapon exp mult
  (`_exp_worth.py`).

On a draw there are no winners, so the ratio formula above doesn't apply:
every player gets a flat `BASE_FIGHT_EXP / DRAW_EXP_DIVISOR` (25 / 2 = 12)
instead. (Before 2026-09 this path raised `ZeroDivisionError`; draws are nearly
unreachable in normal play — mutual KO or the 500000-unit time limit — which is
why the crash survived.) `DRAW_EXP_DIVISOR` is still duplicated in
`constants/experience.py` ⚠️, and `LOSER_EXP_DIVISOR` is an unused leftover.

`handle_accompl` (single winner only): 'Lone Warrior' (≥ 5 losers), 'Narrow
Victory' (winner hp ≤ 5% of max), 'Against All Odds' (losers' yield ≥ 1.5×
winner's), 'Split-Second Victory' (≤ 1 s). `handle_gossip` records personal-best
`aston_victory` (lone win vs yield ratio ≥ 1.2) / `humil_defeat` (lone loss vs
ratio ≤ 0.8). `handle_injuries`: players at `hp == 0` → `injure()` → inactive
days. `handle_player_stats`: fights, wins, KOs, times KO'd, exp bonuses — plus
the in-fight stats: each fighter's `fight_stats` (strikes thrown/landed,
damage dealt, criticals/EPICs, per-move usage — collected in
`do_strike`/`try_critical`/`try_epic`/`maneuver`) is folded into the players'
all-time `stats_dict` and `move_usage`, and shown per fighter by the
post-fight "Stats" menu option (see `docs/stats.md`).

## Fight variants

- `AutoFight` (`_auto_fight.py`): the whole fight runs inside `__init__` —
  items → prepare → prefight quotes → `fight_loop()` → disarm/cancel items →
  win message & post-fight menu (human main player only) → injuries, gossip,
  exp, accomplishments (player involved only). Headless: all UI methods are
  no-ops. Used by tests and NPC-vs-NPC fights.
- `NormalFight` (`_normal_fight.py`): `AutoFight` + real output through
  `main_player`; humans get `is_auto_fighting = False` (interactive menus).
- Sparring (`_sparring.py`): `spar()` builds `AutoSparring`/`NormalSparring`;
  `BaseSparring` disables items, accomplishments, injuries, player stats,
  quotes and gossip — but **not** `give_exp`, so sparring still awards exp.
- `SpectateFight` (`_spectating.py`): display-only `NormalFight` with
  `players = []`, so no exp/injuries/stats; prints via plain `print`.
- `fight()` helper (`_helpers.py`): builds sides, swaps them so a human is on
  side_a, optionally prompts "Auto fight?", picks Auto/Normal.

## AI note

`ai/fight_ai.py`. `BaseAI` = uniform random move/target. The default is
`DefaultFightAI = GeneticAIAttackWhenReady` — a `GeneticAI` subclass with
genetic-algorithm-tuned weights (`prob_atk`, `prob_move`, `prob_focus`,
`prob_guard`, `prob_catch`) doing a `random.choices` over: best attack move, a
maneuver, Focus, Guard, Catch Breath (the last three gated on low qp/stamina
or, in aggro variants, only when no attack is available). Attack moves are
weighted by `calc_atk(m)` → `atk_pwr * to_hit` (note: this mutates the fighter's
`atk_pwr`/`to_hit` as a side effect). `get_a_maneuver` scores each reachable
distance by the total `atk_pwr * to_hit` of the fighter's moves usable there and
returns `None` when already at the best distance. `GeneticAIAttackWhenReady`
also forces a closing maneuver at distance 4 when the opponent has dist-4 moves
and the fighter doesn't, when outnumbering, or when fully rested. Target choice
stays uniform random.

## Key invariants

- `0 <= hp <= hp_max`; hitting 0 zeroes `qp` and (barring `resist_ko`) ends the
  fighter's fight. `0 <= stamina <= stamina_max`; `0 <= qp <= qp_max`. All
  clamped in `change_*`, never negative.
- Distance between any two fighters stays in [1, 4] (`change_distance` clamps)
  and is stored symmetrically (`a.distances[b] == b.distances[a]`).
- `dfs_penalty_mult` ∈ [0, 1], reset to 1.0 at the start of the fighter's own
  turn; `dfs_bonus` likewise.
- Status durations only decrease (by elapsed time) and are removed at ≤ 0;
  `'skip'` guarantees a skipped turn is re-queued, not lost.
- `win is True` ⟺ side_a won; `win is False` covers both side_b winning and a
  draw — callers of `fight()`/`spar()` cannot distinguish the two.
- A fighter is re-queued exactly once per completed action at
  `timer + time_cost`; the loop terminates only via `check_fight_over` or the
  time limit.
