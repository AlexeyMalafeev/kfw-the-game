# Stats, accomplishments, gossip, biographies

How the game tracks a player's career, as implemented. Source files:
`kf_lib/game/game_stats.py`, `kf_lib/actors/player/_base_player.py`,
`kf_lib/actors/fighter/_stats.py`, `kf_lib/fighting/fight/_base_fight.py` and
`_auto_fight.py` / `_sparring.py`, `kf_lib/happenings/encounters/_people.py`
(gossip encounters), `kf_lib/game/biographies.py`, `kf_lib/game/_playing.py`
(victory + stats display), `kf_lib/game/_save_game.py` / `_load_game.py`.
Items marked ⚠️ look unintentional or surprising — verify before building on them.

## stats_dict: per-player statistics

Only players track stats. `BasePlayer.__init__` sets
`self.stats_dict = game_stats.get_blank_stats_dict()` — a dict built from
`DEFAULT_STATS` in `kf_lib/game/game_stats.py`. For NPC fighters,
`change_stat` is a no-op (`kf_lib/actors/fighter/_stats.py`), so fight code
never has to distinguish players from NPCs when bumping stats. ⚠️ Nothing in
fighter code actually calls `change_stat`, so the mixin exists purely as a
safety shim; only `BaseFight.handle_player_stats` bumps stats, and it already
filters by `is_player`.

Three accessors, all trivial (`_base_player.py`):

- `get_stat(name)` / `change_stat(name, value)` (adds) — the used pair.
- `set_stat(name, value)` and `write_stat(name, value)` are identical
  duplicates ⚠️; `set_stat` is used for `became_master*`, `write_stat` for the
  gossip records.

Tracked stats (defaults in `DEFAULT_STATS`, names self-explanatory): fight
counters (`num_fights`, `fights_won`, `num_kos`, `times_koed`,
`exp_bonuses` — a count of *bonuses earned*, not exp), life counters
(`days_inactive`, `got_drunk`, `became_master`, `became_master_at_lv`,
`num_stories`, `num_tourn`, `tourn_won`), money sums (`money_earned`,
`rew_money_earned`, `prize_money_earned`, `spent_on_training`, `donated`,
`gamb_won`, `gamb_lost`, `money_robbed`, `stolen_from`), item counters
(`items_bought`, `items_obtained`, `items_found`, `items_lost`,
`items_stolen_from`, `mock_items_bought`, `fight_items_used`, `healers_used`,
`super_herbs_obtained`), luck counters (`good_luck`, `bad_luck`), and the two
gossip records (`aston_victory`, `humil_defeat`, default `None`).

⚠️ Misleading names: `money_robbed` is money the *player* loses when paying
off robbers (`_crime.py`, `Robbers.pay`), not money robbed from others;
`stolen_from` is money taken by pickpockets (`steal_from`). The report labels
("Robbed,stolen") match this reading.

### Where stats update

- Fights: `BaseFight.handle_player_stats` (called from `give_exp`, i.e. at the
  end of every fight with a player) bumps `num_fights` for all players,
  `fights_won` for winners, `exp_bonuses` by the per-fight bonus count,
  `num_kos` by `kos_this_fight`, `times_koed` when the player ended at 0 hp.
  It also increments the game-global `g.fights_total` once per fight, which
  the stats report uses for the "Fights (total)" percentage. Sparring
  overrides `handle_player_stats` (and gossip/accomplishments) with no-ops —
  sparring stats are not tracked, though sparring still gives exp
  (`_sparring.py`).
- Money/items/training: inline in the corresponding `BasePlayer` methods
  (`earn_money`, `buy_item`, `obtain_item`, `donate`, `drink`, `use_med`,
  `use_item`, `enter_tourn`, `win_tourn`, `record_gamble_win/lost`,
  `steal_from`, `practice_school`).
- `days_inactive` ticks once per skipped day in
  `Playing.check_inactive_player` (`_playing.py`).
- `became_master` / `became_master_at_lv` are set in the school encounter
  that makes the player a master (`encounters/_school.py`).
- `num_stories` ticks when a story starts (`story/_base_story.py`).
- Various encounter/story files bump their own counters
  (`mock_items_bought`, `super_herbs_obtained`, `items_stolen_from`, ...).

`handle_exp_bonuses` (quick victory ≤ 10 s, "Not a scratch", multi-KO ≥ 3)
also increments the transient per-fight `p.exp_bonuses`, which
`prepare_for_fight` resets to 0 and `handle_player_stats` folds into the stat
— two same-named attributes with different lifetimes ⚠️ (the stat and the
per-fight counter are both `exp_bonuses`; the stat counts bonuses, the attr
counts bonuses in the current fight).

## Accomplishments

`BasePlayer.add_accompl(label)`: appends the label to `self.accompl` (a list)
and the current date to the parallel `self.accompl_dates` list, shows
"Accomplishment: ...", awards `ACCOMPL_EXP` (62), and pauses. Both lists are
in `savable_atts`. ⚠️ Parallel lists with a `label not in self.accompl`
membership scan — the `todo` comment says to refactor to
`{accomplishment: date}`; same item in BACKLOG.md ("inefficient now").

Accomplishments come from three sources:

- Fight end, `BaseFight.handle_accompl` — single winner only, only if a
  player won: 'Lone Warrior' (≥ 5 losers), 'Narrow Victory' (winner hp ≤ 5%
  of max), 'Against All Odds' (losers' exp yield ≥ 1.5× winner's),
  'Split-Second Victory' (fight ≤ 1 s). Disabled in sparring.
- Stat thresholds inside player methods: 'Lucky Devil' / 'Unlucky Devil'
  (10 good/bad luck rolls), 'Tournament Champion' (3 tournament wins).
- Encounter/story scripts: 'Beggar's Friend', 'Drunkard's Friend',
  'Fat Girl Defeated', 'Personality Change' (Wise Man changes a trait),
  'Gambler Beaten', 'Weird Item', 'Beat Tough Thief', 'Enemy Reformed', plus
  one per completed story ('Beat Self', 'National Treasures', 'TMNT',
  'Renowned Master', 'Beat Bandit Fiance', 'Foreign Challenger').

What they give: flat exp on earning; `len(p.accompl)` feeds the 'Kung-fu
Legend' victory condition (≥ 8, `Playing.check_victory_conditions`) and
`get_fame()` (`(tourn_won + len(accompl) + fights_won // 10) * 0.01`, the
chance a new student joins the player's school in `encounters/_school.py`).
⚠️ Accomplishments are otherwise invisible — the stats report shows only the
count, and nothing displays the label+date pairs in-game (BACKLOG: "show
accomplishments in options (dates and types already stored)").

## Luck

`BasePlayer.check_luck()` rolls `randint(1, 20)`: 1 = bad luck (returns −1),
20 = good luck (returns +1), else 0. Called at fixed points in a handful of
encounters — Beggar's lesson, Craftsman sale, Book Seller, Challenger
aftermath — where +1/−1 pick the extra-good/extra-bad outcome branch (e.g.
free tech vs. injury; rubbish book vs. bonus-tier move). Each extreme bumps
`bad_luck`/`good_luck`; at 10 of one kind the matching Devil accomplishment
fires. No trait or attribute modifies the roll ⚠️ — the "Lucky Devil" is
purely a 1/20 counter, and `silent=True` (suppress the LUCKY!/BAD LUCK! flash)
has no callers.

## Gossip and personal records

Two systems share the theme and are easily confused:

- `BaseFight.handle_gossip` ⚠️ misleadingly named — it gossips with no one;
  it records the player's personal best/worst fight into stats. After a
  non-draw fight: a *lone* player winner whose opponents' exp yield /
  own yield ≥ `ASTON_VICTORY_MIN_RATIO` (1.2) writes `aston_victory` =
  `(date, level, [loser info strings], ratio)` if it beats the previous
  record's ratio; a *lone* player loser with the winners' ratio ≤
  `HUMIL_DEFEAT_MIN_RATIO` (0.8) similarly writes `humil_defeat`, keeping the
  smallest ratio. Only solo fights qualify, and each stat only ever moves
  toward more extreme.
- Encounters in `happenings/encounters/_people.py`:
  - `Gossip` ⚠️ — paying the gossipmonger shows... the players' full stats
    table (`game.show_stats()`), not rumors. It is the only in-game way to see
    the full report before the ending.
  - `OverhearConversation` — collects every player's non-`None`
    `aston_victory`/`humil_defeat` records and narrates one at random
    ("Haven't you heard? X at lv.N beat Y..."). ⚠️ The log lines are swapped:
    the `humil_defeat` branch logs "astonishing victory" and vice versa
    (`_people.py:269,276`). The shown text is correct; only `p.log` is wrong.
    The records are otherwise never shown to the owning player — the stats
    report doesn't include them.

Player logs: every stat-affecting event also writes to `p.plog` (via `log()`),
dumped to `save/<name>'s log.txt` on each save (`SaveGame._dump_player_logs`)
— the de facto narrative record the gossip records duplicate.

## Display and saving

- Full report: `game_stats.get_full_report_string(game)` builds a fixed-label
  multi-column table (one column per player) mixing stats with live
  attributes (level, atts, friends/enemies/students counts, money,
  reputation). `Playing.show_stats` prints it and writes it to
  `save/stats.txt`. Called from the Gossip encounter and at victory
  (`check_victory`); with `--silent-ending` the ending never shows it.
- The per-day header shows a short Fights/Wins/KOs line
  (`get_fight_statistics`, in `get_p_info_verbose`).
- The post-fight menu option "Stats" (`BaseFight.post_fight_menu`) prints
  per-fighter in-fight stats collected during the fight (since 2026-09):
  each fighter's `fight_stats` (`strikes thrown/landed`, `dam_dealt`,
  `criticals`, `epics`, per-move `moves_used` counts, reset in
  `prepare_for_fight`) is rendered as one line — accuracy, damage,
  criticals/epics, top-3 moves. Before that it printed `self.stats`, a dict
  initialized to `{}` and never written.
- Saving: `stats_dict`, `accompl`, `accompl_dates`, `move_usage` are in
  `BasePlayer.savable_atts`, serialized under `players[].atts` in the JSON
  save (`_save_game.py`). On load (`_load_game.py`), any stat missing from
  the save is back-filled from `DEFAULT_STATS` (so new stats are
  save-compatible), and the two gossip records are converted from JSON lists
  back to tuples (`TUPLE_STATS`).

## In-fight stats and move usage

Added 2026-09. During a fight every fighter accumulates `fight_stats`
(`{'thrown', 'landed', 'dam_dealt', 'criticals', 'epics', 'moves_used'}`),
hooked in `do_strike` (thrown/landed/damage, including counters and
preemptives), `try_critical`/`try_epic` (critical/EPIC counts) and `maneuver`
(per-move usage). "Landed" = the defender neither dodged nor blocked and the
strike dealt damage; fumbled moves (`check_move_failed`) never reach
`do_strike` and don't count as thrown. Damage includes bonus function damage
and fall damage caused by the strike (measured as the target's hp delta).
At fight end, `handle_player_stats` adds the numbers into the player's
`stats_dict` (`strikes_thrown`/`strikes_landed`/`dam_dealt`/`criticals`/
`epics`) and merges `moves_used` into the persistent `p.move_usage` dict
(move name → count). `get_favorite_move(attack_only=...)` reads the all-time
leader; the full report shows strikes landed, damage dealt, crits/EPICs and
favorite move, and biographies use the favorite *strike* ("His signature
move was the …").

## Biographies

`biographies.generate_bio(player)` runs at game end: `check_victory`
(`_playing.py`) collects players who met a victory condition and calls
`show_bio(winners)`, which prints the bios and writes `save/bio.txt`. The
generated text covers: the victory title(s), the style name, the signature
move (most-used strike, from `move_usage`, since 2026-09), and a
3-sentence attribute-spread blurb derived from the gap between the player's
best and worst full attribute (≤ 2 "rather versatile", ≤ 5 "outstanding", else
"almost inhuman ... at the cost of ..."). Other stats, accomplishments, traits
and the gossip records are **not** used ⚠️ — the module docstring-comment lists
planned content (undefeated record, money habits, notable
fights, "unwrap accomplishments into short stories") that was never
implemented; BACKLOG has matching items. With `--silent-ending`, `show_bio`
never runs and no `bio.txt` is written.

## Traits and stats

Traits (`actors/traits.py`) don't interact with stats directly — no stat
counts trait events (BACKLOG: "trait-related stats"). The only touchpoints:
trait effects modify the probability attributes behind stat-feeding events
(e.g. `item_is_lost`, `thief_steals`, `drink_with_drunkard` → `items_lost`,
`stolen_from`, `got_drunk`), and the Wise Man encounter's trait change grants
the 'Personality Change' accomplishment.
