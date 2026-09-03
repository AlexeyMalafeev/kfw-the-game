# Encounters, events, stories, tournaments

How the non-fight content of a game day works, as implemented. Source files:
`kf_lib/happenings/encounters/` (random street encounters, split into thematic
modules), `kf_lib/happenings/story/` (quest chains), `kf_lib/happenings/events.py`
(scheduled daily events, town stats), `kf_lib/happenings/tournament.py`,
`kf_lib/game/_playing.py` (day loop), `kf_lib/actors/player/` (`_base_player.py`,
`_day_actions.py`, `_human_player.py`, `_ai_player.py`). See
`docs/fight_mechanics.md` for the fights themselves.
Items marked ⚠️ look unintentional or surprising — verify before building on them.

## Encounter lifecycle

An encounter is a class, not an instance registry: `BaseEncounter`
(`encounters/_base_encounter.py`) is an ABC with two abstract methods,
`check_if_happens() -> bool` and `run()`. All the action happens in
`__init__(player, check_if_happens=True)`:

1. If `check_if_happens` is true, call `self.check_if_happens()`; a false result
   aborts silently (the instance is discarded).
2. On success the class name is counted in `game.enc_count_dict`,
   `p.refresh_screen()` runs, and `self.run()` executes the encounter body.

⚠️ The `__init__` parameter is named `check_if_happens`, shadowing the abstract
method it gates. It works (the parameter is local, `self.check_if_happens` still
resolves to the method) but is confusing, and the leftover `test=` kwarg in
`EncControl.run_enc` suggests it was renamed at some point.

`__init_subclass__` auto-registers every concrete subclass into
`all_random_encounter_classes` — unless the class has `guaranteed = True`, which
the `Guaranteed` mixin sets. Guaranteed subclasses (`class GChallenger(Guaranteed,
Challenger)`) also inherit `Guaranteed.check_if_happens`, a static method that
always returns `True` (it precedes the base class in the MRO), so they fire
whenever instantiated. Guaranteed variants exist for use in the day-action
category lists (below); they are never in the random pool.

There is no per-encounter state, outcome object, or cleanup — outcomes are applied
imperatively inside `run()` by calling methods on the player (`p.fight(...)`,
`p.pay(...)`, `p.gain_rep(...)`, `p.add_friend(...)`, ...). Choices are delegated
to the player object via `*_or_not` methods (`fight_or_not`, `fight_or_run`,
`fight_run_or_pay`, `buy_item_or_not`, `gamble_or_not`, ...), so the same
encounter code serves humans (menus with risk legends, `HumanPlayer` in
`_human_player.py`) and AI players (threshold/chance rolls, `AIPlayer` in
`_ai_player.py`). Risk display comes from `p.get_rel_strength(*opp)`
(`fighter/_exp_worth.py`): the ratio of summed enemy `exp_yield` to own (plus
allies'), mapped through `RISK_DESCR_TABLE` to a legend like 'very risky'.

Shared helpers live in `encounters/_utils.py`: escape rolls
(`get_escape_chance` = a random base from 0.3–0.7 plus the trait-driven
`p.escape_bonus`; failed escape = `beating()` → `p.injure()`), greed/fear
personality checks (`check_feeling_greedy`, `check_scary_fight`, gated on
`feel_too_greedy` / `feel_too_scared` and the 'cowardly' trait), weapon-duel
setup, and `try_enemy` (a beaten thug renames itself to a robber nickname and
joins `p.enemies` with a given chance).

## How encounters are selected

There are no cooldowns or per-encounter repeat limits — selection is purely
probabilistic, re-rolled every time, with conditions in `check_if_happens` doing
the gating (player level, `is_master`, school rank, having enemies/friends/items,
town stats, a special NPC still being around).

Trigger points (`game/_playing.py:126` `game_loop`):

- After any day action that ends the turn (the action returns truthy) — except
  `rest` — `self.enc.rand_enc()` runs `random_encounters(p)`
  (`encounters/__init__.py`): shuffle **all** registered random encounter classes
  and instantiate each one, giving every encounter exactly one
  `check_if_happens` roll per call.
- 'Go for a walk' gets `WALK_EXTRA_ENC` (2) additional `rand_enc()` calls.
- Most day actions first run their own thematic list:
  `practice_school` → `PRACTICE_SCHOOL_ENCS`, `buy_items` → `BUY_ITEMS_ENCS`,
  `fight_crime` → `FIGHT_CRIME_ENCS`, `help_poor` → `HELP_POOR_ENCS`,
  `pick_fights` → `PICK_FIGHTS_ENCS`, `go_seedy` → `SEEDY_PLACES_ENCS`,
  `go_walk` → `WALK_ENCS` (`_day_actions.py` / `_base_player.py`). These lists
  express weights by **duplicating class objects** (e.g. `[Beggar] * 10`), and
  `random_encounters` instantiates every entry, so each duplicate is an
  independent extra roll. `WORK_ENCS` is an empty leftover; `go_work` rolls no
  encounters.
- If `p.inactive` becomes true mid-cascade (e.g. an injury from a lost fight),
  `random_encounters` aborts the remaining classes.

⚠️ The duplication-as-weights scheme misfires for *guaranteed* classes: each
duplicate fires unconditionally, so `BUY_ITEMS_ENCS` (`[GMerchant] * 5`) forces
five merchant offers in a single 'Buy items' action, and `HELP_POOR_ENCS`
(`[GBeggar] * 3`) three beggars per 'Help the poor'. The `# todo reimplement enc
extra chances with random.choices` comment suggests lists were meant as weights
for a single pick, not independent rolls.

`enc_count_dict` counts every encounter that fired (`BaseGame.__init__` seeds it
with all random classes) and is persisted in saves. ⚠️ It is never read or
displayed anywhere — write-only statistics.

`EncControl.run_enc(name, test)` (`encounters/__init__.py:75`) is a dev hook that
`exec()`s `"{name}(p, test={test})"`. ⚠️ Broken: no encounter `__init__` accepts
a `test` kwarg (the second parameter is `check_if_happens`), so calling it — e.g.
from `kf_lib/testing/testing_tools.py:50` — raises `TypeError`. Passing the flag
positionally, as `testing_tools.test_enemy` does with `Ambush(p, False)`, works.

## Encounter categories

Grouped by module; examples are representative, not exhaustive. Chance constants
(`ENC_CH_*`) live at the top of each module.

### Crime (`_crime.py`) — chances scale with the `game.crime` town stat

- `Robbers` (chance = crime/2): 1, 2–4 or 5–8 robbers demand money;
  `fight_run_or_pay`. Winning vs a group lowers `game.crime`, grants rep per
  robber, and may create an enemy; paying records the `money_robbed` stat.
- `Thief` (crime/3): pickpocketing vs `p.thief_steals`; steals a random item or
  cash. A caught thief fights back; 10% of the time (at the player's levels) it
  is the persistent named `game.thief`, whose defeat yields the 'Beat Tough
  Thief' accomplishment and removes him from the game.
- `Extorters` / `RobbingSomeone` / `HelpPolice` (crime/4 each): intervene in
  street crime alongside friends/schoolmates or the police; winning lowers
  crime. Extorters can end with a grateful shop owner's item gift or a bill for
  breakages (refusing to pay costs rep).
- `Criminal` (flat 0.03, needs `game.criminals`): fight a wanted convict; the
  reward is `criminal.level * random multiplier`, split with one helping ally.
  ⚠️ In `Criminal.reward` the ally gets the halved `rep_gain`, but the player
  still gets full `c.level` rep while the *money* is halved — the split is
  applied inconsistently.

### Street people (`_people.py`)

- `Brawler`: provoked in the street; brawling costs rep, apologizing gains a
  little — but the brawler may attack anyway (0.2).
- `Drunkard`: drink (rep penalty, a sick day) or refuse and risk a fight. The
  persistent legendary `game.drunkard` (lv 8–12) can befriend the player and
  teach a move, then leaves the game.
- `WiseMan`: pay 10 c. for a conversation; 0.15 chance to gain a positive trait
  (or lose its opposite) — the only encounter that changes traits.
- `Gossip` (pay to see game stats), `OverhearConversation` (relays recorded
  `aston_victory` / `humil_defeat` facts about players). ⚠️
  `OverhearConversation.run` swaps the log lines: the humiliating-defeat branch
  logs "astonishing victory" and vice versa (`_people.py:269,276`).
- `FriendMatch` / `PlayerMatch`: friendly spars with friends or other AI
  players, chance scaling with friend count.

### Gambling and seedy places (`_gambling.py`)

- `Gambler`: rock-paper-scissors for escalating bets; the gambler's throws are
  secretly weighted half the time. Winning ≥ 100 can trigger a revenge fight;
  losing that fight hands the winnings back. Gambling costs rep.
- `PrizeFighting`: pay a 50 c. fee for a 5-stage underground ladder
  (`LV_PRIZE_FIGHTERS = (2, 4, 7, 10, 15)`); each stage may be declined, a loss
  forfeits everything, prizes grow per stage. Rep penalty for entering.

### Items and merchants (`_items.py`, `_book_seller.py`, `_craftsman.py`, `_performer.py`)

- `Merchant` (medicine or a fight item at a random price), `FindItem` /
  `LoseItem` (chances from the `item_is_found` / `item_is_lost` attributes),
  `Weirdo` (trade any mock item for the `SUPER_BOOSTER`).
- `BookSeller`: 100 c. for a book that is rubbish (bad luck), exp, or a move a
  tier above/below the player's level band depending on `check_luck`.
- `Craftsman`: sells the training `MANNEQUIN` (500 c.); good luck means a free
  mannequin after a spar, bad luck means it breaks immediately. Never occurs
  once the player owns one.
- `StreetPerformer`: randomly a challenge for double-or-nothing, a shady
  'elixir' sale (50% mock item), or thugs to fight off for a reward. ⚠️
  Declining the challenge runs `p.disarm()` — the player loses their equipped
  weapon for saying no (`_performer.py:86-89`, comment "disarm player!!!").

### School and mastership (`_school.py`)

- `SchoolChallenge` / `SchoolBullying`: rank up (or be ambushed) within your
  school; chances scale with school size.
- `MasterTrial`: at rank 1 and `MASTER_LV` (11+), beat your master in a spar,
  pay 1000 c., and found a school — flips `is_master`, which changes the day
  action list and excludes the player from many encounters.
- `Students` (masters only): applicants arrive at rate `min(fame, 0.07)`;
  groups must be beaten first. AI masters auto-accept single applicants.

### Story hook (`_story.py`)

- `ContinueStory`: if `p.current_story` exists, 0.07 chance to advance it one
  scene (weighted ×3 in `WALK_ENCS`). See Stories below.

### Enemies (`_ambush.py`)

- `Ambush`: chance = `len(p.enemies) * 0.02` — odds grow with your enemy list
  (cf. `FriendMatch`, which scales with your friend count). A named enemy plus 2–4 weak thugs;
  winning lowers crime and gives a 0.5 chance the enemy repents (removed from
  enemies, +10 rep, 'Enemy Reformed' accomplishment).

## Stories

`BaseStory` (`story/_base_story.py`): a story is a per-game singleton object
created at `NewGame._init_stories` for every class in `get_all_stories()`
(another `__init_subclass__` registry, populated by the imports in
`story/__init__.py`). Class attributes `min_level` / `max_level` define the
eligibility window; `state` is `None` (not started), `0..n` (current scene), or
`-1` (ended).

- **Starting**: `events.new_story` (daily roll, chance 0.1, see Events) picks a
  random not-yet-started story, then a random player with no `current_story`
  whose level passes `story.test()`. `start(player)` sets `p.current_story`,
  bumps the `num_stories` stat, sets `state = 0`, and runs `intro()`. If the
  chosen story has no eligible player, nothing happens that day; a story that
  the player outlevels before it starts never starts.
- **Advancing**: the `ContinueStory` encounter calls `advance()`, which
  increments `state` and runs the scene via
  `exec(f'self.scene{self.state}()')`. ⚠️ Dynamic dispatch by string `exec` —
  a `state` with no matching `sceneN` method crashes with `AttributeError`
  instead of ending cleanly; scenes must call `self.end()` themselves.
- **Ending**: `end()` sets `state = -1`, unregisters the `boss` fighter (if
  any), and clears `p.current_story`. Ended stories never restart
  (`state == -1` fails `check_hasnt_started`), so each story happens at most
  once per game, for one player.
- **Persistence**: `SaveGame._story_to_data` stores `state` plus player/boss by
  name; `LoadGame` re-links them to the loaded fighters (`_load_game.py:101`).
  Bosses are real registered fighters (`ForeignerStory.intro` creates one via
  `fighter_factory.new_foreigner()`), so mid-story saves work. The
  `get_init_string` / `__repr__` machinery is the legacy exec-based save path.

Six stories exist: `StrangeDreamsStory` (lv 6–8; dream spars incl. a copy of
yourself, exp rewards), `BanditFianceStory` (6–9; two scenes, boss fight, +25
rep), `StolenTreasuresStory` (8–10; four scenes, bribe-or-infiltrate choice,
+30 rep), `ForeignerStory` (9–12; watch the foreign boss fight for exp, then
challenge him, +30 rep), `NinjaTurtlesStory` (12–15; one fight, reward is the
full Turtle Nunjutsu tech line), `RenownedMasterStory` (14–16; defend your
school's honor against a challenger master). Rewards are rep, exp,
accomplishments, moves and techs.

## Scheduled events and town stats

`events.randevent(g)` runs once per day from `Playing.next_day`
(`_playing.py:192`), after all players have acted. It shuffles three
independent rolls: new story (0.1), school-vs-school brawl (0.04), new
tournament (0.15) — so zero to three events per day.

`school_vs_school(g)` picks two random non-empty schools, drops inactive
players from the rosters, and runs one NPC fight (`fight.fight(...)`) between
them with school names displayed; participants just log the event.

Town stats (`game.crime`, `game.poverty`, `game.kung_fu`) are rolled once at
`BaseGame.__init__` from `(0.05, 0.1, 0.15, 0.2)`. `crime` is read by the crime
encounters and lowered by `crime_down` (called after crime-fight wins); it is
also 'raised' monthly by `do_monthly` → `events.crime_up`. ⚠️
`CRIME_INCREASE_MONTHLY = 0.00`, so the monthly raise is a no-op — crime only
ever decays to `MIN_CRIME` over a long game. ⚠️ `kungfu_up/down` and
`poverty_up/down` are defined but never called (their `randevent` integration
is a todo); `poverty` is at least read (by `Beggar`), but `g.kung_fu` is never
read anywhere despite the stale "used only for tournaments" comment — both
stats are effectively static flavor.

Also monthly (`Playing.do_monthly`, `_playing.py:107`): a new escaped convict
joins `game.criminals` (feeding the `Criminal` encounter), and NPC school
students level up with chance 0.1 up to lv 8, then schools are re-ranked.

## Tournaments

`Tournament` (`happenings/tournament.py`) runs entirely inside `__init__` →
`run()`: announce → gather → show → bets → rounds → prize → resolve bets.

- **Creation**: daily via `events.new_tournament` — a random level bracket from
  `TOURNAMENTS` (beginner 1–3 … master 11–14), participant count drawn by
  `random.choices` (heavily favors 8 or 16), fee from `TOURN_FEES` (50–150).
- **Gathering** (`_gather_participants`): active players in the level range are
  asked (`tourn_or_not`; AI always accepts) and pay the fee via `enter_tourn`.
  ⚠️ No money check — a broke player (human or AI) pays anyway and can go
  negative. Remaining slots are sampled from masters and school students in
  range. ⚠️ `self.spectator = self.participants[0]` (used for round
  announcements) raises `IndexError` if the bracket ends up empty — latent
  crash for level ranges with no eligible fighters.
- **Rounds** (`_do_rounds`): single elimination. Each round shuffles the
  remaining list and pairs fighters off; an odd one out gets a bye. Every match
  is a real `fight.fight(...)` (no environment, no items) — players' fights are
  interactive as usual, so tournament losses injure and wins grant exp exactly
  like street fights. A final with both fighters KO'd raises
  `NotImplementedError` (draws can't produce a winner).
- **Prize** (`_calc_prize`): `fee * num_participants / 2`, rounded to tens —
  i.e. the organizer pockets half the fees. Only a *player* winner is paid
  (`win_tourn`: prize money, `tourn_won` stat, 'Tournament Champion'
  accomplishment at 3 wins); an NPC winner gets nothing. ⚠️ `TOURN_PRIZE_MULT`
  and `DEFAULT_TOURN_FEE` in `events.py` are unused leftovers.
- **Betting**: after the participant list is shown, every active player may
  bet (`bet_on_tourn_or_not`, AI: `gamble_chance` roll; AI picks a random
  highest-level participant). The stake (10/25/50/100) is paid up front in
  `place_bet_on_tourn`. In `_resolve_bets` a winning bet pays
  `stake * max(current_round, 1.5)` (the 1.5 floor covers one-round
  tournaments) and is recorded as gambling income; losers have already lost
  their stake. ⚠️ `BET_REPUTATION_PENALTY = -3` is defined but never applied —
  betting is reputation-free.

## How outcomes feed back into the sim

Encounters don't return results; they mutate the sim directly. The feedback
channels:

- **Exp/levels**: fights and spars award exp per `give_exp` (see
  `docs/fight_mechanics.md`; note sparring *does* award exp). Books, dreams and
  spectating grant exp directly via `p.gain_exp`, which can cascade
  `level_up()`.
- **Money**: `pay` / `earn_money` / `earn_prize` / `earn_reward` / `donate` /
  `steal_from`, each logging to its own `stats_dict` counter.
- **Reputation**: `gain_rep` — positive for heroics (crimefighting, reforming
  enemies, story rewards), negative for gambling, brawling, drinking and prize
  fighting. Rep feeds the 'Folk Hero' victory condition.
- **Friends/enemies**: `add_friend` (beggar, drunkard, challengers, masters)
  grows the ally pool used by `check_help` / `check_allies`; `add_enemy` feeds
  `Ambush`. Friends/enemies are saved by fighter name.
- **Items and money sinks**: merchants, gifts, theft, mock items; the
  `MANNEQUIN` grants free home practice every day (`Playing.do_daily`).
- **Traits**: only `WiseMan` (plus starting traits) modifies them; traits in
  turn modulate encounter behavior (`feel_too_greedy`, `feel_too_scared`,
  `escape_bonus`, `thief_steals`, ... via `actors/traits.py`).
- **Accomplishments**: `add_accompl` labels from encounters/stories/tournaments
  count toward the 'Kung-fu Legend' victory condition
  (`Playing.check_victory_conditions`).
- **Injuries**: `p.injure()` sets `inactive` days; injured players skip turns
  (`check_inactive_player`) and can only use medicine or rest.
- **Town state**: winning crime fights lowers `game.crime`, directly reducing
  future crime-encounter frequency.
- **Mastership**: `MasterTrial` flips `is_master`, swapping day actions
  (teach students for income) and gating master-only encounters (`Students`)
  and the master tournament bracket.
