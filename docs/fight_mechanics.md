# Fight mechanics

How a fight works, as implemented. Source files: `kf_lib/fighting/fight/` (fight
engine), `kf_lib/actors/fighter/` (`_fight_actions.py`, `_strike_mechanics.py`,
`_fight_attributes.py`, `_distances.py`), `kf_lib/fighting/distances.py`,
`kf_lib/kung_fu/` (moves, techniques, boosts), `kf_lib/ai/fight_ai.py`.
Items marked ⚠️ look unintentional or surprising — verify before building on them.
The master's teachings (`kf_lib/happenings/teachings.py`, see `encounters.md`)
paraphrase many rules below for players; `test/test_teachings.py` pins the
values they quote, so when a rule changes, reword the saying it flags (and its
Russian translation).

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
`all_fighters` and `active_*` copies, and rolls the fight's
`environment_bonus_mult` from `ENVIRONMENT_BONUSES` (1.2, 1.3, 1.5, 1.8, 2.0).
When `environment_allowed` is `False` (tournaments, the All-Schools
Tournament, the Foreigner / Renowned Master / Eight Gates boss fights) the
multiplier is a neutral `1.0`; the roll is still drawn so seeded runs don't
shift. `try_environment` checks `environment_allowed` first anyway, so
environment techs never trigger in those fights. (Until 2026-10 the attribute
was `environment_bonus` and was `0.0` when disallowed.)

`prepare_for_fight` (`_fight_actions.py`) resets per-fight state: `hp = hp_max`,
`stamina = stamina_max`, `qp = round(qp_max * qp_start)`, `bleeding = 0`,
`status = {}`, `momentum = 0`, `took_damage = False`, `kos_this_fight = 0`,
`exp_yield = get_exp_worth()`, `set_distances_before_fight()`.
`qp_start` is 0 unless a qi tech or qi herb raises it, so most fighters start
a fight with no qi. That head start is nearly all a qi tech is worth, and it
pays only at high levels, where moves cost up to 2.5 × level qi and fights
are short (at low levels moves cost almost no qi); the qi boosts give a
quarter bar (`QP_START1`) or half a bar (`QP_START2`) since 2026-10-24
(half / a full bar before).

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
`power > 0` = strike, else maneuver. A negative cost would *restore* a
pool; no move uses that since 2026-10-25, when Catch Breath and Focus moved to
move functions (see Maneuvers).

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

If `shocked`: `to_dodge = to_block = 0` (a stun only lowers them — see
below and Statuses). Otherwise:

```
x = dfs_penalty_mult * agility_full * 10
    * stamina_factor * rep_actions_factor * dfs_bonus * dfs_mult
if off-balance: x *= off_balance_dfs_mult   # 0.75
if lying:       x *= lying_dfs_mult         # 0.5
if stunned:     x *= STUN_DFS_MULT          # 0.8
to_dodge = x * dodge_mult / DODGE_DIVISOR   # /3
to_block = x / BLOCK_DIVISOR * wp_dfs_bonus * block_mult  # /2
dfs_pwr  = dfs_penalty_mult * BLOCK_DEFAULT_POWER * block_mult * BLOCK_POWER
           * health_full * stamina_factor * wp_dfs_bonus
if fury: dfs_pwr *= fury_to_all_mult
if stunned: dfs_pwr *= STUN_DFS_MULT          # 0.8
```

The three defensive buffs each do what their name says: `dodge_mult`
('dodge') raises dodge chance, `block_mult` ('blocks') raises block chance
*and* block power, `dfs_mult` ('defense') raises both chances. Until 2026-10
`dfs_mult` was set by its techs but read nowhere, `block_mult` raised only
block power, and `dodge_mult` sat in `x`, raising block chance too.

Block power comes from **health** since 2026-10 (strength before). A
blocked strike deals strike power minus block power, so with strength on
both sides one strength point raised the fighter's strikes *and* blocks,
and near the point where strikes and blocks are equal (low levels) it
turned many full blocks into damage: an extra strength point gave +45%
damage dealt at levels 1–7, an extra speed point +17%. Health's share of
toughness and stamina and the new tempo rule (below) came in the same
change; together they brought the four attributes within ±0.6 of neutral
in the fight-balance harness (strongest minus weakest: 4.0 → 0.9).

`rep_actions_factor` punishes repetitive attackers: `1 + 0.33 * n`, where `n` =
how many of the attacker's last 3 actions (`previous_actions`, a maxlen-3 deque)
are this move — up to ×1.99 to the *defender's* dodge/block.

`BLOCK_DEFAULT_POWER` (1.0, `_fight_actions.py`) is the per-fighter hook —
techniques can override it per fighter; `BLOCK_POWER` (12, `_strike_mechanics.py`)
is the global constant. It was 20 until 2026-10, when ~81% of blocks absorbed
the whole strike (attack power is `strength * power / 2`, so a Punch, power
26, did 13 per strength point vs 20 of block power); at 12 a little under
half do, and partial blocks are the commoner kind. They were once both named
`BLOCK_POWER` and `Fighter`'s MRO shadowed the global with 1.0, making blocks
absorb ~1/400 of the intended damage (fixed 2026-09; see CHANGELOG).

### `do_strike` order

1. `calc_atk(action)`
2. `try_environment('attack')`: if the fighter has `environment_chance`
   (tech-based), environment is allowed, and the roll succeeds — `atk_pwr` and
   `to_hit` × `environment_bonus_mult`.
3. `target.calc_dfs()`
4. `try_unblockable()`: `unblock_chance` roll → `target.to_block = 0`.
5. `target.try_environment('defense')`: `dfs_pwr`, `to_block`, `to_dodge` ×
   `environment_bonus_mult`.
6. `target.defend()`
7. `hit_or_miss()`
8. `target.apply_dfs_penalty()`: `dfs_penalty_mult -= dfs_penalty_step`
   (default 0.2, floored at 0). Since `start_fight_turn` resets it to 1.0, this
   is the anti-crowd mechanic: defense decays per strike taken *between your own
   turns*. The 'Behind You' tech line reduces the step.
9. If the move has `dist_change`, apply it; else `momentum = 0`.
10. Append the move to `previous_actions`.

### `defend` — dodge / block / hit

Two independent rolls — dodge first, then block if the dodge failed:

```
dodge_chance = to_dodge / attacker.to_hit
block_chance = to_block / attacker.to_hit
if rnd() <= dodge_chance: dodge — attacker.dam = 0, defender gains qp_gain
elif rnd() <= block_chance: block — dam = max(dam - round(dfs_pwr), 0),
    defender gains qp_gain // 2, try_block_disarm()
else: clean hit
if blocked and dam > 0: try_qi_shield()
```

**Qi shield** (`try_qi_shield`, since 2026-10-24): a fighter with qi training
— `qp_gain_mult` or `qp_max_mult` above 1.0, from a qi tech or a qi herb —
spends qi to absorb what got past its block, 1 QP per
`QI_SHIELD_HP_PER_QP` (2) HP, rounded up, as far as its qi lasts. If it
absorbs everything, the block counts as a full one (off-balance attacker,
counter chance, `full_blocks` stat). Dodges and clean hits aren't shielded.
It gives qi techs a use at every level: their extra qi did almost nothing,
since fighters rarely lack qi once a fight is under way (half a bar pays
for any move a fighter knows). In the harness it fires about 0.3 times per
fight for a qi-trained fighter and absorbs about 3% of its max HP.

So a strike is dodged with `dodge_chance`, blocked with
`(1 - dodge_chance) * block_chance`, and hits otherwise. A **full defense**
— a dodge, or a block that lets no damage through (`attacker.dam == 0` after
rounding) — leaves the attacker briefly off-balance
(`cause_off_balance(brief=True)`, 25–50 time units ÷ speed, about half a
turn; since 2026-10): it mostly weakens the attacker against the defender's
counter (`try_counter` runs right after) and quick follow-up, and rarely
outlasts the attacker's own next action. Chances above 1.0
mean guaranteed defense. (Until 2026-10 one shared roll was compared to both
chances, so the effective block chance was `block_chance - dodge_chance` and
a fighter whose dodge chance was at least their block chance never blocked;
over 300 sample auto-fights blocks rose from 9% to 19% of strikes, clean hits
fell from 72% to 62%.)

### `hit_or_miss` — only if `dam > 0`

In order (steps 1–2 only if the target didn't defend — see below):

1. `try_critical()`: `critical_chance` roll → `dam *= critical_dam_mult` (1.5).
   `critical_chance = (agility_full - 3) * 0.05 * critical_chance_mult`.
   Successful rolls increment `fight_stats['criticals']` (since 2026-09).
2. `try_epic()`: `epic_chance` roll → `dam *= epic_dam_mult` (2.0); successful
   rolls increment `fight_stats['epics']`.
   `epic_chance = 0.005 * level * epic_chance_mult` — every fighter has it
   (0.5% per level; 5% at lv 10, 10% at lv 20), no tech/move/style required.
   The crit and epic rolls are independent and both run on the same strike,
   so one hit can be critical *and* epic: `dam * 1.5 * 2.0 = ×3.0`.
   Criticals and epics need an **undefended** strike (`target.defended` is
   false): a block, even one that absorbs only part of the damage, denies
   both rolls, rewarding the defender (since 2026-10; before, they multiplied
   whatever got past the block). A dodge or a fully absorbed block never
   reaches `hit_or_miss` anyway. With `BLOCK_POWER` 12 (2026-10) partial
   blocks are ~11% of strikes in the fight-balance harness, so the rule
   bites more often than it did at 20 (~4%).
3. `dam = max(dam - toughness, 0)`; `toughness` from level and health, see
   "Pools and derived attributes".
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
    `hp = 1` and displays "<name> resists being knocked out!" (shown on screen
    in `NormalFight`, recorded in the fight `timeline` in all fight types);
    otherwise the attacker logs the KO (`kos_this_fight += 1`).

Steps 8–10 still run when the hit already reduced the target to 0 hp — a KO'd
fighter can be shown stunned/knocked back/falling before the KNOCK-OUT line;
`try_ko` comes last by design.

### Maneuvers

`maneuver()`: apply `dist_change` (clamped to 1–4 by `change_distance`), roll
`check_move_failed`, run `functions`. `Guard` (`functions=['guard']`) sets
`dfs_bonus *= guard_dfs_bonus * GUARD_POWER` (2.0; 1.5 until 2026-10-23),
lasting until the fighter's next turn. It restores stamina and qi only with
a Guard tech: `guard_restore` turns' worth of each (`stamina_gain` /
`qp_gain`, rounded) — 1 with Advanced Guard, 2 with Dragon Guards a Treasure
(`GUARD_RESTORE1/2`; the style techs that raise `guard_dfs_bonus` don't
restore). From 2026-10-23 to 2026-10-25 every Guard restored a flat 10
stamina and 10 qi. Catch Breath and Focus (functions `catch_breath` /
`focus`) restore `CATCH_BREATH_GAIN_MULT` / `FOCUS_GAIN_MULT` (2) turns'
worth of stamina / qi, so with the next turn's regeneration the fighter gets
3 turns' worth, and stamina/qi techs raise them through `stamina_gain_mult` /
`qp_gain_mult`; all three take 60 time units. Until 2026-10-25 Catch Breath
and Focus restored a flat 20 (the same at every level) and Catch Breath took
80. Meanwhile `guarding` is set, shown as a `[]`
status mark (see `ui.md`); `start_fight_turn` clears both. `dfs_bonus`
multiplies dodge and block chance, not block power: in staged exchanges
(`dev_scripts/testing/run_test_guard.py`) Guard saves 31% of the HP an
incoming strike would cost (18% at ×1.5), 49% with Advanced Guard, 64% with
Dragon Guards a Treasure. The default fight AI guards mostly when it can't
afford an attack, so whole-fight harness runs can't price Guard.
`guard_while_attacking` (tech) instead multiplies `dfs_bonus` by
`1 + guard_while_attacking` inside `attack()`, and sets `guarding` too, so
such a fighter is marked `[]` after attacking (until 2026-10 also by the
Guard move's 1.5, so the +50% tech gave a free ×2.25 on every attack — more
than an untrained Guard move costing a whole turn). Any move without
`dist_change` resets `momentum` to 0.

`get_move_time_cost = time_cost / (tempo * (0.7 if slowed down))`, with
`tempo = 1.5 * max(speed_full - 2, 1)` (`TEMPO_PER_SPEED`, `TEMPO_SPEED_BASE`):
speed counts from a base of 2, like agility's `(agility_full - 3)` in
counter chance, so each point is a bigger step at low speed (4 → 5 acts 50%
more often, 8 → 9 about 17%); the 1.5 keeps a speed-6 fighter's action times
unchanged. Until 2026-10 tempo was plain `speed_full`, and a speed point was
worth half an average other attribute point at levels 1–7. Then ×
`strike_time_cost_mult` (if `power`) or × `maneuver_time_cost_mult` (elif
`dist_change`); Guard/Focus-type moves get neither multiplier. The result is
rounded to whole time units (4–18 for most moves, so one action's time can
be off by up to ~10%; unbiased on average — see BACKLOG "Coarse fight clock").

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
- `stunned` (50–150): `skip` + dodge/block chances and block power (`dfs_pwr`)
  × `STUN_DFS_MULT` (0.8, since 2026-10). A minor shock by design: the target
  loses the initiative but keeps most of their reflexes. `calc_dfs` applies
  the penalty on every strike while the status lasts, so nothing needs
  restoring when it wears off.
- `shocked` (50–100): `skip` + zero dodge/block.
- `off-balance` (50–100; 25–50 after the opponent's full defense): atk and
  dfs × 0.75 (`off_balance_atk_mult` / `off_balance_dfs_mult`, which the
  drunken techs raise).
- `slowed down` (300–600): time costs × 1/0.7.
- `fury` (500–1000): `atk_pwr`, `to_hit`, `dfs_pwr` × 1.6. Rolled each own turn
  with chance `(1 - hp/hp_max) * fury_chance` (tech-gated).

## Pools and derived attributes

`_fight_attributes.py`:

- `hp_max = health_full * 40` (50 until 2026-10); `change_hp` clamps to `[0, hp_max]` and zeroes
  `qp` when `hp` hits 0. `hp` never goes negative, so all `hp <= 0` checks are
  effectively `hp == 0`.
- **Health level**: `health_lv = (health_full - 3.449) / 0.267`, the level
  whose typical generated fighter has this much health. Since 2026-10
  toughness and max stamina come partly from it (level only before), so
  health buys more than HP.
- `stamina_max = 0.7 * (50 + 10 * level) * stamina_max_mult
  + 0.3 * max(30, (50 + 10 * health_lv) * stamina_max_mult)` (the level part
  rounded first); `stamina_gain` = 10% of
  max per own turn. `qp_max = 5 * level * qp_max_mult`; `qp_gain` = 10% of max
  per own turn, rounded up (plus full/half `qp_gain` on successful dodge/block,
  the half rounded down). Both clamp. Until 2026-10-27 `qp_gain` was rounded
  to nearest, so a level-1 fighter (`qp_max` 5) regenerated no qi at all and
  Focus restored nothing — yet the fight AI still chose it; now it is 1.
  Qi regeneration was 20% until 2026-10, when fighters ended fights with ~37%
  of their qi unspent, so the qi buffs barely mattered.
- `toughness = 0.8 * (level - 1) * 3 + 0.2 * max(0, (health_lv - 1) * 3)`,
  rounded — flat subtraction from every hit.
- `*_full = round(base * *_mult)` for the four base atts
  (`_basic_attributes.py`).
- `counter_chance = (agility_full - 3) * 0.05 * counter_chance_mult`
  (`counter_chance_mult` is a hook: no tech sets it since 2026-10-23);
  `epic_chance = 0.005 * level * epic_chance_mult`.

Counter-attacks (`try_counter`) answer a strike that missed
(`check_move_failed` zeroes the attacker's `to_hit` and, since 2026-10-23,
its `dam`, which until then kept the previous strike's value) or was fully
dodged/blocked (`defended` and `attacker.dam == 0`), if the defender is
alive. Until
2026-10-23 any strike with `dam == 0` qualified, including an undefended hit
that toughness fully absorbed. A fighter without counter techs then rolls
`counter_chance`; one with counter techs counters for sure,
`guaranteed_counters` times in a row (1 per counter tech, 2 for Double Revenge
or an upgraded style counter tech), stopping early if either fighter is down
or it can't afford an attack move at that distance; it never rolls. Each
counter (`do_counter`) runs the full strike pipeline back at the attacker
with a random available attack move, and pays that move's stamina/qi cost
(`apply_move_cost`) exactly like `do_preemptive` (counters were free until
2026-10), but no time. A counter-tech counter has `to_hit ×
COUNTER_TECH_HIT_MULT` (2.0; `do_counter` sets `is_countering` for
`calc_atk`), i.e. half the attacker's usual dodge and block chance. The
attacker is off-balance at that moment (see `defend`), so every counter
meets ×0.75 defense on top. Until 2026-10-23 counter techs raised
`counter_chance_mult` by +50% / +100%; that left them at a quarter of an
average tech (A/B tool), and guaranteed counters plus the hit bonus bring
them to about average (tables in `tests/balance experiments 2026-10-22.txt`).

## Techs, moves, boosts

`kung_fu/techniques.py`: a `Tech` is a name + flat dict of attribute deltas,
applied by *addition* (`Tech.apply`: `setattr(f, p, getattr(f, p) + delta)`),
then `refresh_full_atts`/`refresh_dependent_atts`. Multiplicative-sounding
params are additive increments to a `1.0` base (e.g. `atk_mult +0.1`), so
stacked techs add rather than compound. Strike-multiplier techs
(`punch_strike_mult` etc.) multiply into `atk_bonus` per matching move feature
in `calc_atk`, and add the feature to `fav_move_features` (biases random move
learning). Values live in `kung_fu/boosts.py` / `boost_combos.py`.
A distance buff (`dist1/2/3_strike_mult`) is worth roughly its value times
the share of strikes thrown at that distance, and fighters throw only ~14%
of their strikes at close range (it is hard to reach and hold: the opponent
strikes or pushes you away on the way in) against ~42% mid and ~43% long
range. So since 2026-10-28 close range keeps the biggest distance buff
(+40%) while mid range drops to +20% (was +25%), alongside the general cuts
to attack (+10%, was +15%) and punches (+20%, was +25%); grappling, close
range too, went up to +40% (was +25%). Close-range and
grappling techs also carry `guard_while_advancing` (a flag): every maneuver
that closes the distance (`dist_change < 0`: Step Forward, Rush Forward,
Charging Step, Leap Forward) also acts as Guard — `dfs_bonus *=
guard_dfs_bonus * GUARD_POWER` and `guarding` set until the fighter's next
turn, without the Guard techs' restore. Charging strikes don't count: they
are attacks, not maneuvers. In A/B tests (`run_test_tech_ab.py`, levels
1-20) the flag alone is worth about +7 Diff%, nearly as much as the
close-range buff itself; it doesn't make fighters strike at close range more often
(~11% of strikes either way), it makes approaching cheaper.

Unfinished features, not bugs (placeholders kept on purpose; the techs that
would use them are queued in `BACKLOG.md`): the boost constants `GRAB_CH1/2`
(fighters have no `grab_chance` attribute yet) and `QI_WHEN_ATK` (no
`qi_when_atk` attribute yet) are used by no tech (`HP_MULT` was removed in
2026-10 as redundant with the `health_mult` techs);
`epic_chance_mult` is a working hook in the epic-chance formula that no tech
raises yet; and the 7 `WeaponTech`s carry no bonus ("weapon techniques do
nothing; implement"). The advanced 'Lightning-Fast Strikes' tech doubles the
basic 'Fast Strikes' effect (`STRIKE_TIME_COST_MULT2` = −0.6 vs −0.3).

`kung_fu/moves.py` loads `moves/all_moves.txt` at import (each line `eval()`d
into a `Move`). `get_rand_moves` filters by tier and `fav_move_features`, sorts
by feature overlap, weights by `freq`. An empty pool falls back to the whole
tier (with a warning in `kfw.log`).

## End of fight

`check_fight_over` (`_base_fight.py`): fighters at `hp == 0` drop out of
`active_*`. One side empty → the other side wins (`win = True` iff side_a wins).
Everyone down → draw: `winners = []`, `losers = all`, `win = False`.

`give_exp` (only players get exp):

- `winners_diff = (Σ losers' exp_yield / Σ winners' exp_yield) ** 1.5`;
  `winners_gain = winners_diff * BASE_FIGHT_EXP` (20). Beating stronger
  opposition scales exp superlinearly; beating weaker gives little. In
  free-for-all fights both sums are replaced by per-capita
  averages (`aggregate_exp_yield`, overridden in `BaseFreeForAll`) — the
  losers were fighting each other too, so the difficulty anchor is the
  average opponent, not the whole pile. In a *group* FFA
  (`BaseGroupFreeForAll`) the anchor is instead the **RMS of per-group
  sums**: win-rate simulations (`dev_scripts/testing/sim_group_ffa.py`)
  show the effective opposition is dominated by the strongest groups,
  since they tend to survive to the endgame.
- Losers get a flat `LOSER_EXP` (2 = 10% of base) regardless of difficulty.
- `handle_exp_bonuses`: +25% per bonus — quick victory (≤ 10 s), "Not a
  scratch" (`not took_damage`), multi-knockout (`kos_this_fight >= 3`).
- `exp_yield = 10 + str*agi*spd*hlt*0.03 + 3 per tech`, × weapon exp mult
  (`_exp_worth.py`).

On a draw there are no winners, so the ratio formula above doesn't apply:
every player gets a flat `BASE_FIGHT_EXP / DRAW_EXP_DIVISOR` (20 / 2 = 10)
instead. (Before 2026-09 this path raised `ZeroDivisionError`; draws are nearly
unreachable in normal play — mutual KO or the 500000-unit time limit — which is
why the crash survived.) `DRAW_EXP_DIVISOR` is still duplicated in
`constants/experience.py` ⚠️, and `LOSER_EXP_DIVISOR` is an unused leftover.

`handle_accompl` (single winner only): 'Lone Warrior' (≥ 5 losers), 'Narrow
Victory' (winner hp ≤ 5% of max), 'Against All Odds' (losers' yield ≥ 1.5×
winner's), 'Split-Second Victory' (≤ 1 s). 'Lone Warrior' and 'Against All
Odds' are not awarded in free-for-all fights — winning a melee is not
comparable to beating a united group. `handle_gossip` records personal-best
`aston_victory` (lone win vs yield ratio ≥ 1.2) / `humil_defeat` (lone loss
vs ratio ≤ 0.8), using the same `aggregate_exp_yield` as `give_exp` (FFA
ratios are per-capita too). `handle_injuries`: players at `hp == 0` → `injure()` → inactive
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
- Free-for-all (`_free_for_all.py`): `free_for_all(fighters, ...)` builds
  `AutoFreeForAll`/`NormalFreeForAll` — `BaseFreeForAll(BaseFight)` with every
  fighter as their own side (all fighters passed as side_a, side_b empty;
  `win` reports whether `fighters[0]` won). `get_act_targets` returns every
  other active fighter, `get_act_allies` just the fighter themselves; the
  fight ends when at most one fighter is standing (`winners` is that one
  fighter or empty on a draw, e.g. double KO / time limit). Exp uses
  per-capita yields (see `give_exp` above), the crowd accomplishments
  ('Lone Warrior', 'Against All Odds') are skipped, and injuries work
  unchanged. The targeting/allies logic lives in
  `BaseFight.get_act_targets`/`get_act_allies` (used by `start_fight_turn`
  and `handle_items`), which `BaseFreeForAll` overrides; the HP bar
  (`visualize_fight_state`) is built from `act_allies`/`act_targets`, so it
  shows "me vs the rest" in a melee. The prefight screen is titled
  `Free for all!` to distinguish it from a regular fight against an allied
  group (which shows `-vs-` between the sides instead).
- Group free-for-all (`group_free_for_all(groups, ...)`,
  `BaseGroupFreeForAll`): like FFA but participants fight in groups — no
  infighting within a group, targets are all active fighters outside one's
  group; the fight ends when a single group has anyone standing (`winners` is
  that whole group, incl. downed members, matching two-sided side semantics;
  `win` reports whether `groups[0]` won). The prefight screen is titled
  `Group free for all!` and labels each group (`--- Group N ---`, marking
  the human's), and exp uses the RMS of
  per-group yields (see `give_exp` above). Used by `JadeTableStory` and the
  GangWar encounter.

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
