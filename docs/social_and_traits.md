# Social graph and traits

Friends, enemies, co-op bonds and personality traits, as implemented. Source
files: `kf_lib/actors/player/_base_player.py` (the lists, help channels, trait
(de)activation), `kf_lib/actors/traits.py` (trait definitions),
`kf_lib/game/_new_game.py` (co-op setup), `kf_lib/game/_save_game.py` /
`_load_game.py` (persistence), `kf_lib/happenings/encounters/` (`_challenger.py`,
`_ambush.py`, `_crime.py`, `_people.py`, `_gambling.py`, `_utils.py`). For the
encounter-level narrative see `docs/encounters.md`; for where the numbers sit in
the larger loop see `docs/gameplay.md`.
Items marked ⚠️ look unintentional or surprising — verify before building on them.

## The lists

`BasePlayer.__init__` (`_base_player.py`) creates `self.friends = []` and
`self.enemies = []`. Both hold fighter objects, not names.

- `add_friend(obj)`: appends only if `len(friends) < self.max_num_friends`
  (default 8, ±2 from the (un)friendly trait). Over-cap additions are **silently
  dropped** — callers print their "let's be friends" line first, so the message
  can announce a friendship that never happened ⚠️ (`_challenger.py:54-55`,
  `_school.py:57`, `_people.py:120`, `_beggar.py:44`).
- `add_enemy(enemy)`: appends and `game.register_fighter(enemy)` — enemies
  become persistent world fighters. No cap and no duplicate check.
- `remove_enemy(enemy)`: removes and unregisters (only used by the Ambush
  reform path). There is no `remove_friend` — friendship is permanent.

Persistence (`_save_game.py`, `_load_game.py`): both lists are stored as fighter
names and re-linked by name on load. `_refresh_roster` always includes enemies
in the saved roster, and appends any friend not otherwise present — needed
because the one-shot NPCs (`game.beggar`, `game.drunkard`) are set to `None`
right after being befriended, so the friend edge is the only thing keeping them
in the save.

Beyond the mechanics below, both lists appear on the stats screens
(`game_stats.py`, `get_p_info_verbose`) and nowhere else.

## Making friends

- **Co-op setup** — see Co-op section.
- **Challenger** (`encounters/_challenger.py`): after any accepted challenger
  fight — *win or lose*, the roll sits before the `if win:` branch —
  `rnd() <= CH_CHALLENGER_FRIEND * p.challenger_friend_mult` (0.1 base; the
  'friendly' trait doubles it, 'unfriendly' zeroes it), skipped if already a
  friend. Challengers are drawn from another school's roster
  (`get_random_other_school`), which includes other *players* in that school —
  a challenger-friend can be a co-op rival.
- **One-shot NPCs**: beating the persistent Beggar (spar) or the strong
  Drunkard befriends them (`_beggar.py`, `_people.py`).
- **MasterTrial** (`_school.py:57`): founding your own school befriends your
  old master.

## Making enemies

`try_enemy` (`encounters/_utils.py`): on a won crime fight, with the given
chance (0.1 in Extorters/Robbers/RobbingSomeone), the beaten thug renames
itself to a robber nickname and joins `p.enemies`. The Gambler's revenge fight
does the same on a win (`_gambling.py:129`), without the rename (the gambler
already has a proper name).

## What friends do: the help channels

Before group/street fights, `check_help(allies, master, impr_wp, school)`
(`_base_player.py`) rolls **exactly one** of the enabled channels, chosen
uniformly at random:

- `'a'` allies → `check_allies()`: for each friend, one roll —
  `coop_joins_fight` (0.5) for player friends (skipped while `inactive`),
  `friend_joins_fight` (0.3) for NPC friends. `max_num_allies` defaults to
  `max_num_friends`, so effectively uncapped here; `Criminal` caps it at 1 and
  only calls it when the convict outlevels the player (`_crime.py:66-67`).
- `'m'` master → `master_joins_fight` (0.5), your style's master joins.
- `'w'` improvised weapon → `grab_improvised_weapon` (0.5; +0.1 broad-minded).
  Distinct from the *in-fight* `in_fight_impro_wp_chance`, which is
  technique-based (see `docs/fight_mechanics.md`) — the similar names cover two
  different rolls.
- `'s'` schoolmates → `schoolmates_help` (0.5), 2–3 random non-player members
  of `get_school()`.

⚠️ The single-pick design means friends get rolled only when the `'a'` channel
is picked (1/4 with all channels on), and a failed roll on the chosen channel
produces no help at all — there is no fallback to the other channels.

⚠️ The `'a'` branch assigns `p.allies = p.check_allies()`, and `check_allies`
returns `None` (not `[]`) when the player has no friends — overwriting the
`p.allies = []` init. `fight()` tolerates `None`, but `Extorters` has to guard
explicitly (`p.allies if p.allies is not None else []`, `_crime.py:123`).

Call sites: `Ambush`, `Extorters`, `RobbingSomeone`, group/armed `Robbers`,
`Criminal` (direct `check_allies(1)`), plus weapon-only variants in
`HelpPolice` and `StolenTreasuresStory` (`allies=False, master=False,
school=False`). Allies join side_a of a real fight — exp, injuries and stats
apply to them as usual. In `Criminal`, a joined friend halves the reward (the
inconsistent rep/money split is flagged in `docs/encounters.md`).

`FriendMatch` (`_people.py`): pick-fights encounter with chance
`len(nonhuman friends) * 0.01` per sweep entry; a spar against a random friend.
`get_nonhuman_friends` filters `not f.is_human`, so AI *players* you are
friends with are eligible too (they are also reachable via `PlayerMatch`).

⚠️ `check_partners()` — friends joining *training*, with its own
`friend_joins_training` / `coop_joins_training` (0.25) attributes — is defined
in `_base_player.py` but **never called anywhere**. Friends give no training
bonus; the two attributes and the method are dead code.

## What friends do outside fights

Very little. `ForeignerStory.scene3` (`story/_foreigner.py:59`) picks a
non-player friend as the NPC the foreigner "beat" — flavor only; nothing
happens to the friend. Everything else is display. There is no romance system:
the Fat Girl encounter (`_people.py`) is a fight with a marriage *threat*, and
the wedding in `BanditFianceStory` is an NPC's.

## What enemies do

Exactly one thing: `Ambush` (`encounters/_ambush.py`), a global-sweep encounter
with chance `len(p.enemies) * 0.02` per roll — risk grows linearly with the
enemy list. A random enemy shows up with 2–4 weak thugs; `check_help()` runs
first; on a win, crime drops and with `CH_ENEMY_REPENTS` (0.5) the enemy is
removed (+10 rep, 'Enemy Reformed' accomplishment). Losing means the usual
injury. `Ambush` has no `is_master` gate, so masters keep getting ambushed
(and their `check_help` pulls allies from the school they left — see the ⚠️ in
`docs/gameplay.md`). Enemies have no other mechanical effect.

## Co-op setup

`NewGame._init_players` (`_new_game.py`): with >1 player a menu offers 'Full
co-op' (every pair of players friended), '2x2', '3x3' (two cliques, `add_friend`
within each half), or none. Friending players is what switches on the
`coop_joins_fight` (0.5) / `coop_joins_training` (dead, see above) rolls in
`check_allies`, vs 0.3 for NPC friends.

⚠️ '2x2' is applied only when there are exactly 4 players and '3x3' only with
exactly 6 (`elif coop_mode == '2x2' and n_players == 4 ...`). The menu offers
both options for any player count, so picking '3x3' in a 4-player game silently
creates no bonds at all.

## Traits: data model

`actors/traits.py`. Eight negative↔positive pairs (careless/careful,
greedy/generous, lazy/hardworking, cowardly/brave, narrow-minded/broad-minded,
unfriendly/friendly, undisciplined/disciplined, slow-witted/quick-witted), each
with one effect dict written for the **positive** trait as flat additive deltas
("if the lower an att the better, define the change as −x"). `TRAIT_EFFECTS` is
built by taking those dicts for the positive traits and auto-negating every
delta for the negative ones — there is no separate negative definition to drift
out of sync.

Effects apply by addition to player policy attributes
(`BasePlayer.activate_trait` / `deactivate_trait`: `setattr(self, att, val ±
change)`). The defaults live in `BasePlayer.__init__` (e.g. `feel_too_scared =
0.3`, `wage_mult = 1.0`); the `num_*_choose` targets are `Fighter`-level
defaults of 3 that traits shift to 2 or 4. Additive means: 'brave' sets
`feel_too_scared` to exactly 0.0 (fear rolls still happen vs stronger opponents
but always fail), 'unfriendly' zeroes challenger befriending.

## Trait assignment and changes

- **Creation**: `set_rand_traits()` picks one negative, then one positive,
  via `get_rand_traits(1, player=self, ...)` which excludes already-owned
  traits *and their opposites* — so a new player always has exactly one trait
  from each side, from two different pairs.
- **In-game**: the WiseMan encounter (`_people.py:314`) is the **only** trait
  changer. Paying for the talk rolls a random positive trait; with
  `CH_CHANGE_TRAIT` (0.15), and only if that trait isn't already owned, it
  either removes its opposite from you (`remove_trait`, which subtracts the
  negated deltas via `deactivate_trait`) or adds it (`add_trait`), plus the
  'Personality Change' accomplishment. `add_trait` itself raises if the trait
  or its opposite is already present — the WiseMan flow is the only caller and
  guards both cases.
  ⚠️ The talked-about trait is drawn with `get_rand_traits(negative=False)`
  *without* the `player` filter, so it can name a trait you already have — the
  `trait not in p.traits` gate then quietly wastes the 0.15 change roll.
- **Persistence**: `get_init_atts()` includes `self.traits` as a constructor
  arg; on load `__init__` re-runs `activate_trait` for each, so mid-game trait
  changes survive save/load (covered by `test/test_save_load.py`).

⚠️ `'cowardly'` is additionally checked **by name** in `check_scary_fight`
(`encounters/_utils.py:28`): the fear roll normally requires a stronger
opponent, but cowardly players roll it against anyone. This is the one place a
trait has an effect beyond its `TRAIT_EFFECTS` deltas.

## Where each trait-affected attribute is consumed

- `escape_bonus` → `get_escape_chance` (`_utils.py`), added to a random 0.3–0.7
  base.
- `training_injury` → `check_training_injury`, rolled after school practice
  only.
- `thief_steals` → the Thief encounter's steal roll.
- `item_is_lost` / `item_is_found` → the LoseItem / FindItem encounter chances.
- `feel_too_greedy` → `check_feeling_greedy` (cancels purchases/donations).
- `feel_too_scared` → `check_scary_fight` (cancels agreed fights), × opponent
  ratio; see the 'cowardly' name check above.
- `wage_mult` → `go_work`; `school_training_exp_mult` → `practice_school` and
  `practice_master`.
- `num_techs_choose` / `num_techs_choose_upgrade` → tech pick pool sizes
  (`fighter/_techs.py`); `num_moves_choose` → move learning pool
  (`fighter/_moves.py`, `kung_fu/moves.py`); `num_atts_choose` → attributes
  offered per level-up (`fighter/_basic_attributes.py`).
- `grab_improvised_weapon` → the `'w'` channel of `check_help` (only).
- `max_num_friends` → `add_friend` cap; `challenger_friend_mult` → Challenger
  befriending roll.
- `drink_with_drunkard` → Drunkard temptation; `gamble_with_gambler` → forced
  gamble entry; `gamble_continue` → gambling streak continuation
  (`_gambling.py`).
- `next_lv_exp_mult` → `get_next_lv_exp` (level cost; 'quick-witted' −0.1).

All of these are forced dice or economy numbers — traits never change combat
attributes directly.
