# AI players (strategic AI)

How computer-controlled players play the game day to day, as implemented. Source
files: `kf_lib/actors/player/_ai_player.py` (AI classes), `_base_player.py`
(shared player logic), `_human_player.py` (menu-based counterparts, for
contrast), `kf_lib/game/_playing.py` (day loop), `kf_lib/game/_new_game.py`
(player creation), `kf_lib/actors/fighter/_exp_worth.py` (risk assessment),
`kf_lib/happenings/encounters/` (decision call sites). In-fight AI is a
separate system — see `docs/fight_mechanics.md` ("AI note"); despite the
package name, nothing in `kf_lib/ai/` makes day-level decisions.
Items marked ⚠️ look unintentional or surprising — verify before building on them.

## Overview

Class tree: `Fighter` → `BasePlayer` (`_base_player.py`) → `AIPlayer`
(`_ai_player.py`, `is_human = False`) → `VanillaAIP` (empty subclass),
`LazyAIP`, `SmartAIP`, `SmartAIPVisible`, `BaselineAIP`. `HumanPlayer` is a
sibling (`HumanControlledFighter, BasePlayer`) that implements the same
decision methods with menus — encounters call e.g. `p.fight_or_not(...)`
polymorphically and never check `is_human` for most decisions.

`AIPlayer` stubs out all UI: `cls`, `pak`, `refresh_screen`, `see_day_info`,
`end_turn` are no-ops, and `msg`/`write` funnel into `log()`, which appends to
`self.plog`. So every encounter "shows" text to AI players exactly as to
humans, and it all lands silently in the log.

## Instantiation

`NewGame._get_new_ai_player` (`game/_new_game.py`): random style from
`self.style_list`, class = `forced_aip_class` if given, else
`random.choice(ALL_AI_PLAYERS)` where
`ALL_AI_PLAYERS = (LazyAIP, SmartAIP, VanillaAIP, BaselineAIP)`
(`_ai_player.py`). `SmartAIPVisible` is deliberately not in the tuple — its
`log()`/`end_turn()` print and call the real `pak()`, so it would block a
headless game on keypresses; it exists for interactive games where the user
answers yes to "Do you want to see what AI players do?" (`kfw.py`).

All players (human and AI) go through `BasePlayer.__init__` with
`rand_atts_mode=2`, `occupation='hero'`, and `set_rand_traits()`: one random
negative trait, then one random positive trait, avoiding opposite pairs
(`actors/traits.py`). Traits matter for the AI: they shift
`feel_too_scared`/`feel_too_greedy`, `escape_bonus`, `wage_mult`,
`school_training_exp_mult`, `drink_with_drunkard`, `gamble_with_gambler`,
`gamble_continue`, and the `num_*_choose` sample sizes. Co-op mode in
`_init_players` only pre-populates `friends` between players.

Entry points (`kfw.py`): an interactive game forces all AI players to
`SmartAIP`/`SmartAIPVisible`; `--autoplay` sets `ai_only=True` with no forced
class, giving a random mix.

## The day loop and daily action choice

`Playing.game_loop` (`game/_playing.py`): for each player, show day info
(no-op for AI), handle inactivity, then `choice = p.choose_day_action()`;
`choice()` runs the action and a truthy return ends the turn (a falsy return —
e.g. `practice_school` without the tuition fee — re-enters the choice loop).
After a non-rest action, one random encounter is rolled (`enc.rand_enc()`);
`go_walk` rolls two extra. `check_inactive_player` decrements `inactive` and
offers medicine first: if injured and carrying Medicine, `use_med_or_not()`
decides (AI: `inactive >= min_days_use_med`, 2 days base, 3 for SmartAIP);
sick-from-drinking days are never medicated.

`AIPlayer.choose_day_action` is a fixed decision tree — no scoring, no memory:

- not a master: `money < min_non_master_money` (175) → `go_work`; else
  `non_master_practice_chance` (0.9) → `practice_school`, else `go_walk`.
- master: `money < min_master_money` (150) → `teach_students` if
  `students >= min_students_to_teach` (5) else `go_work`; else
  `master_practice_chance` (0.6) → `practice_master`, else `go_walk`.

So a standard AI player only ever works, practices, or walks. `buy_items`,
`fight_crime`, `help_poor`, `pick_fights`, `go_seedy` exist in
`get_day_actions()` (`_base_player.py`) but are only reachable by humans and by
`BaselineAIP`, whose `choose_day_action` is `random.choice` over that list.
Day actions themselves (`_base_player.py`, `_day_actions.py`): `go_work` pays
`WAGE * wage_mult` (a master working gets a shaming line but the same wage);
`practice_school` pays `TUITION_FEE`, grants exp ±20%, rolls school encounters
and a training injury; `practice_master` is the same exp mechanic free of
charge; `teach_students` earns `TUITION_FEE * students // 2`; the rest just
roll their encounter lists (`encounters/__init__.py`). Owning a Mannequin adds
free home-practice exp every day in `do_daily`.

## Level-up choices

`Fighter.level_up` (`actors/fighter/__init__.py`) calls `upgrade_att`,
`resolve_techs_on_level_up`, `resolve_moves_on_level_up`; humans override each
with menus (`human_controlled_fighter.py`), AI players inherit the random
versions:

- Attributes: `upgrade_att` samples `num_atts_choose` (3) of the four stats and
  `choose_better_att` picks one from the highest-weighted group in
  `att_weights`. With `rand_atts_mode` 1 or 2 every weight is set to 1, so the
  choice is uniform random among the three. ⚠️ The mode-1/2 code sets
  `att_weights[att] = 1` unconditionally — the `random.randint(1, 2)` line that
  would differentiate modes is commented out (`_basic_attributes.py`), so
  `rand_atts_mode` 1 and 2 are identical and AI attribute growth has no
  build logic at all.
- Techs (`_techs.py`): style techs are automatic at their levels; at
  `ADVANCED_TECH_AT_LV` a random upgradable tech is upgraded
  (`choose_tech_to_upgrade`); at `LVS_GET_GENERAL_TECH` levels a random tech
  from a random sample of learnable ones is learned (`choose_new_tech`).
- Moves (`_moves.py`): style move strings resolve at their levels; at
  `LVS_GET_NEW_ADVANCED_MOVE` levels a tier-appropriate move is learned via
  `resolve_move_string` → `get_rand_moves` → `choose_new_move` =
  `random.choice(sample)`. The pool is biased by `fav_move_features` (see
  fight_mechanics.md), so strike-multiplier techs indirectly steer which moves
  the AI learns.

For AI players the `num_moves_choose`/`num_techs_choose` traits
(broad-minded/narrow-minded) only change the pre-filter sample size, not the
pick — the pick is flat random either way.

## Risk assessment and fight decisions

All "should I fight" hooks receive `opp_info = p.get_rel_strength(*opp, allies=...)`
(`_exp_worth.py`): `ratio = Σ opp exp_worth / (own + allies) exp_worth`
(exp worth = base-attributes product + 3 per tech, × weapon mult), plus
a legend from `RISK_DESCR_TABLE` ('no risk' … 'impossible'). AI decisions use
only the number:

- `fight_or_not`: `ratio <= acceptable_fight_threshold` (1.2; SmartAIP 1.1).
  Used for optional fights: crime-fighting encounters, challengers, school
  trials, master trial, prize-fighting stages after the first.
- `fight_or_run`: fight if `ratio <= threshold` **or** `esc_chance < 0.5`.
  ⚠️ The 0.5 is hardcoded and ignores `acceptable_escape_risk` (0.6; SmartAIP
  0.7), which is only consulted by `run_or_not` — so `fight_or_run` and
  `fight_run_or_pay` apply different escape standards.
- `fight_run_or_pay` (robbers): if the money can't be paid, reduce to
  fight-or-run; otherwise prefer fight, then run (`run_or_not`: `esc_chance >=
  acceptable_escape_risk`), then pay. Escape chances are
  `random.choice((0.3, …, 0.7)) + escape_bonus` (`encounters/_utils.py`).
- `brawl_or_not`: `brawl_chance` roll (0.25; SmartAIP 0 — never brawls) and
  the same threshold check.

On top of the AI decision, encounters apply a trait-driven "feelings" layer
(`encounters/_utils.py`), identical for humans and AI: `check_scary_fight`
rolls `feel_too_scared * ratio` (skipped when `ratio < 1.0` and the player
isn't cowardly) and vetoes the fight; `check_feeling_greedy` rolls
`feel_too_greedy` and vetoes paying/buying/donating. An AI class cannot turn
these off — a cowardly SmartAIP still chickens out.

## Items and medicine

AI players acquire items only through encounters (Merchant/Craftsman/
BookSeller sell, `buy_item_or_not` = flat `buy_item_chance` 0.5 roll for every
AI class) plus the random find/lose rolls and fight loot; only `BaselineAIP`
can take the "Buy items" day action, which just re-rolls those encounters.
Pre-fight, `BaseFight.handle_items` offers each player a fight item:
`use_fight_item_or_not` compares `get_opponents_power()` vs
`get_allies_power()` (sums of exp worth over `act_targets`/`act_allies`, set to
the fight's sides) and returns a uniform-random item from the inventory only
when outpowered; otherwise nothing. Medicine is used via `use_med_or_not` as
described above.

## Money, gambling and social choices

- Donations (Beggar): `donate_or_not` returns the full amount on a
  `donate_chance` 0.5 roll, else 0. ⚠️ It never checks `check_money` (the
  human version only offers what the player has), so a broke AI player donates
  into negative money.
- Gambling (Gambler encounter): `gamble_or_not` = `gamble_chance` roll (0.5;
  LazyAIP 0.7, SmartAIP 0.2), but the encounter also rolls
  `gamble_with_gambler` (0.3) as an independent temptation. Rock-paper-scissors
  picks are uniform random; after 5 rounds the continue/stop decision is
  `rnd() < gamble_continue` (0.4, trait-modified). ⚠️ `SmartAIP` defines
  `continue_gambling_chance = 0` and `drink_chance = 0` (and
  `buy_med_chance = 100`) — none of these attributes is read anywhere; the real
  knobs are `gamble_continue`, `drink_with_drunkard` and `buy_item_chance`, so
  SmartAIP is exactly as drunkard-prone and gambling-sticky as VanillaAIP.
- Fixed answers: `hear_rumors_or_not` → False (AI never buys gossip),
  `talk_wise_or_not` → True, `p_match_or_not` → True (all friendly
  friend/player spars accepted), `tourn_or_not` → True (every tournament and
  prize-fighting entry).
- Tournaments (`happenings/tournament.py`): `bet_on_tourn_or_not` reuses
  `gamble_chance`; `place_bet_on_tourn` picks a random participant among those
  at the max level and a random bet from `possible_tournament_bets`. ⚠️ The bet
  is paid with no `check_money` — another negative-money path (the human menu
  version doesn't check either).

## School and mastery

A player becomes a master only via the MasterTrial encounter
(`encounters/_school.py`): school rank 1, level requirement met, then a 0.05
roll per encounter check (it sits in `PRACTICE_SCHOOL_ENCS` and the generic
random-encounter pool). The AI's only say is `fight_or_not` against its master; winning
the spar founds a school named `'{name}'s school'` (`choose_school_name` — no
collision check, unlike the human prompt) and pays `MONEY_OPEN_SCHOOL`.
⚠️ That payment has no `check_money` — the AI never saves up for it and can go
deeply negative the day it wins the trial.

As a master: the Students encounter (`get_fame()`-gated) asks a human whether
to accept a single applicant but hardcodes `choice = True` for AI, and the
2–5-man "show us your skill" group challenge is an unconditional fight with no
`fight_or_not` at all — the master AI can't decline either. `teach_students`
and the master's day-action branch are covered above; students level up
monthly on their own (`do_monthly`).

## The AI classes

- `VanillaAIP`: the defaults, listed at the top of `AIPlayer` — threshold 1.2,
  escape risk 0.6, brawl 0.25, buy 0.5, donate 0.5, gamble 0.5, practice
  0.9/0.6, money floors 175/150, 5 students to teach, medicine at 2 days.
- `LazyAIP`: practices less (0.3/0.2), gambles more (0.7).
- `SmartAIP`: tighter threshold 1.1, higher escape standard 0.7, never brawls,
  gambles less (0.2), practices 0.8/0.5, waits 3 days before medicine. It also
  redeclares `min_non_master_money`, `min_master_money` and
  `min_students_to_teach` with values identical to the base — reads like
  tuning, changes nothing ⚠️ — plus the three dead attributes flagged above.
- `BaselineAIP`: same decision hooks as `AIPlayer`, but `choose_day_action` is
  a uniform random pick over `get_day_actions()` — the "monkey" baseline. It
  can pick `practice_school` without the fee; the action returns falsy and the
  day loop simply re-rolls.
- `SmartAIPVisible`: SmartAIP with real output (prints every log line and waits
  on `pak()`), for watching one AI's decisions in an interactive game.

Pinned by `test/test_player_ai.py` (seeded characterization tests of the
day-action tree, fight thresholds and the fight/run/pay matrix).

## Autoplay and self-play harnesses

- `python kfw.py --autoplay [-n N] [--autosave] [--silent-ending]` (`kfw.py`):
  all-AI game, random mix of `ALL_AI_PLAYERS`, generated styles. Victory ends
  the game (`Playing.check_victory`, four conditions in `_playing.py`);
  `n_days_to_win` records how long it took.
- `test/test_game_integration.py`, `test/test_autoplay_variants.py`: headless
  full-game runs (4 and 6 players, and a forced-`BaselineAIP` game) as
  integration tests.
- `dev_scripts/ai/compare_AIPs.py`: 100 single-player games per class with
  `forced_aip_class`, averaging `n_days_to_win` into `AI players
  comparison.txt` — the way AI "personalities" are benchmarked.
  `dev_scripts/ai/collect_AIP_data.py` is the same loop with random classes.
