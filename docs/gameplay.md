# Gameplay: day loop, economy, victory

The day-to-day game loop, money, reputation, progression, and win conditions, as
implemented. Source files: `kf_lib/game/` (`_playing.py` day loop & victory,
`_base_game.py` world state, `_new_game.py` setup), `kf_lib/actors/player/`
(`_base_player.py` day actions & player state, `_human_player.py`,
`_ai_player.py`), `kf_lib/happenings/` (`encounters/`, `events.py`,
`tournament.py`, `story/`), `kf_lib/things/items.py`,
`kf_lib/constants/experience.py`. For combat numbers see `docs/fight_mechanics.md`.
Items marked ⚠️ look unintentional or surprising — verify before building on them.

## Overview

`Game` is a god-class composed of LoadGame + NewGame + Playing + SaveGame +
StateMenu (`kf_lib/game/_game.py`). `Playing.game_loop` (`_playing.py`) is the
heart: an endless loop over days; each day every player takes one turn (one "day
action"), then end-of-day processing runs. There is no time limit and no loss
condition — the game ends only when some player meets a victory condition or
everyone quits.

World state held by the game: `day/month/year` (30-day months, 12-month years),
town stats `poverty`, `crime`, `kung_fu` (each starts at 0.05–0.2), `schools`
(dict style name → list of fighters), `masters` (style name → NPC master), a
`criminals` list (5 wanted convicts + 1 new per month), and four one-shot
special NPCs (`beggar`, `drunkard`, `thief`, `fat_girl`) that are consumed
(`= None`) for everyone once their unique fight is won — in multiplayer, the
first player to beat the Beggar/Tough Thief/strong Drunkard/Fat Girl takes
that accomplishment off the table.

## A game day

`game_loop` per player, in order:

1. `p.see_day_info()` (date + level/exp/money; no-op for AI).
2. Inactivity check (`check_inactive_player`): if `p.inactive > 0`, the player
   is injured/sick. If injured *and* carrying Ginseng Root, they're offered to
   use it and act normally; otherwise the day is skipped (`inactive -= 1`,
   `days_inactive` stat +1) and no encounters roll.
3. `choice = p.choose_day_action()`; `brk = choice()`. An action returning
   `True` ends the turn; returning `None`/falsy (e.g. cancelled practice when
   broke, or the State menu) re-prompts. Load/quit requests break the loop via
   `chosen_load`/`chosen_quit`.
4. If the action was not `rest`, `self.enc.rand_enc()` runs one full sweep of
   the global encounter table; `go_walk` gets two extra sweeps
   (`WALK_EXTRA_ENC = 2`). Rest is the only action with zero encounter exposure.
5. `p.end_turn()`, `p.ended_turn = True`.

After all players: `check_victory()`, then `next_day()`: date advance,
`do_daily()` (mannequin home-training for non-inactive owners, see Items),
monthly `do_monthly()` on day 31 (crime up — see ⚠️ below, add a new escaped
convict, 10% chance for each NPC school student below lv 8 to level up,
`rerank_schools()`), `events.randevent(self)`, autosave if enabled.

### Day actions

`BasePlayer.get_day_actions()` (`_base_player.py`). The menu differs for
masters (own school):

- **Practice at school** (non-master): costs 20 c tuition; if broke, the turn
  is *not* consumed. Grants `SCHOOL_TRAINING_EXP` (10) ×
  `school_training_exp_mult` × rnd 0.8–1.2, silently. Then a school encounter
  sweep (`MasterTrial`×3, `SchoolChallenge`×3, `SchoolBullying`) and a 5%
  training injury roll (`training_injury`; 1 inactive day).
- **Practice** (master): same exp formula (`MASTER_TRAINING_EXP`, also 10) but
  no tuition, no encounters, no injury roll. Strictly better than school
  practice.
- **Go to work**: earn `WAGE` (50) × `wage_mult`. No targeted encounters
  (`WORK_ENCS` is an empty list ⚠️, and `go_work` never calls
  `random_encounters` anyway — only the global sweep applies).
- **Buy items**: sweep of Craftsman/BookSeller/Merchant/StreetPerformer
  (weighted list with `Guaranteed` merchant entries, so merchants always show).
- **Fight crime**: sweep of Criminal/Extorters/HelpPolice/RobbingSomeone.
- **Help the poor**: sweep of Beggar/WiseMan.
- **Pick fights** (non-master): sweep of Brawler/Challenger/FriendMatch/
  PlayerMatch.
- **Teach students** (master): earn `TUITION_FEE * students // 2` = 10 c per
  student per day. Does nothing if you have no students (turn not consumed).
- **Go to seedy places**: sweep of Gambler/Drunkard/OverhearConversation/
  PrizeFighting.
- **Go for a walk**: one walk sweep (ContinueStory/OverhearConversation/
  StreetPerformer/Merchant/Gossip/Weirdo) plus the normal global sweep plus
  **two extra global sweeps** — walking is the "roll for content" action,
  roughly tripling generic encounter exposure (including thieves and ambushes).
- **Rest** / **State** (human menu only): rest ends the turn safely; State is
  the info/save/load/quit/debug screen (`_state_menu.py`) and doesn't consume
  the turn.

`fight_dummy` (spar vs a lv-1 punching bag) exists in `_base_player.py` but is
commented out of the menu ⚠️ — dead code, and would be a zero-risk exp trickle.

### Encounters

Pipeline (`encounters/_base_encounter.py`, `__init__.py`): every encounter
class has `check_if_happens()` (a probability roll, often gated on town stats,
player level, `is_master`, etc.) and `run()`. `random_encounters(p, encs)`
shuffles the given list and instantiates *every* class in it — so day-action
lists with repeated classes (`[Merchant] * 3`) mean multiple independent rolls,
not weights. After the action's own sweep, `EncControl.rand_enc()` sweeps the
full global table (`all_random_encounter_classes`). Any sweep stops early if
the player became inactive mid-sweep.

Common machinery (`encounters/_utils.py`):

- Fight decisions show the player a risk estimate from
  `get_rel_strength()` (`fighter/_exp_worth.py`): ratio of opponents' exp worth
  to yours, mapped to "no risk … impossible".
- Even after agreeing to fight, `check_scary_fight` can cancel it:
  `feel_too_scared` (0.3) × opp-ratio chance. Skipped when clearly stronger,
  unless the player is 'cowardly' — then the fear roll happens even against
  weaker opponents. Similarly `check_feeling_greedy` (`feel_too_greedy` 0.3)
  can cancel purchases/donations. These are forced "personality" dice, not
  choices.
- Escapes: `get_escape_chance` = random 0.3–0.7 + `escape_bonus`; a failed
  escape is a beating → `injure()` (1–7 inactive days), no fight.
- Before group/street fights, `check_help` picks one of four help sources:
  friends (`friend_joins_fight` 30% each, `coop_joins_fight` 50% for players),
  your master (50%), an improvised weapon (50%), or 2–3 schoolmates (50%).
  ⚠️ For masters the schoolmate branch still pulls from their *old* school
  (`get_school()` returns `schools[self.style.name]`, which the master was
  removed from when founding their own).

## Victory

`Playing.check_victory_conditions` (`_playing.py`), checked once per day after
all players have acted. Four types, all independent and combinable:

- **Grandmaster**: `level >= 20` (`GRANDMASTER_LV`).
- **Folk Hero**: `reputation >= 100` (`FOLK_HERO_REP`).
- **Kung-fu Legend**: `len(accompl) >= 8` unique accomplishments
  (`KFLEGEND_ACCOMPL`). 21 labels exist: 6 story rewards, 8 encounter ones
  (Beggar's Friend, Drunkard's Friend, Fat Girl Defeated, Gambler Beaten, Beat
  Tough Thief, Enemy Reformed, Weird Item, Personality Change), 4 fight ones
  (see fight doc), Tournament Champion (3 wins), Lucky/Unlucky Devil (10
  extreme luck rolls of the same kind, 5% each per `check_luck`).
- **Greatest Fighter**: `fights_won >= 75` **and** `num_kos >= 100`
  (`GT_FIGHTER_FIGHTS`). Sparring doesn't count (`BaseSparring.handle_player_stats`
  is a no-op); crowd fights do — KOs, not fights, are the binding constraint.

Any player meeting any condition ends the game for everyone (hot-seat race).
On victory: the day count is recorded (`n_days_to_win`), stats and a generated
biography (`biographies.py`) are shown and dumped into the save folder along
with a `game over.txt` save, and the player is asked "Keep playing
indefinitely?" — which sets `play_indefinitely` so `check_victory` never fires
again. ⚠️ `Playing.play()` then re-invokes itself recursively, growing the
stack by one frame per victory-and-continue.

## Defeat

There is none. Players never die and there is no game-over on any failure
path. The punishments for losing are:

- **Injuries**: a player at `hp == 0` after a real fight gets
  `injure(rndint(1, max_days_to_recover=7))` inactive days (`handle_injuries`;
  sparring excepted). Failed escapes and training accidents also injure.
  Inactive days are pure time loss — no decay otherwise.
- **Money losses**: robbery payoffs (40–180 c), thief steals (25–200 c or an
  item, `thief_steals` 30% per Thief encounter), gambling losses, tournament
  fees.
- **Enemies**: losing/attacking some NPCs (`try_enemy` 10%) registers a named
  enemy who later ambushes you with 2–4 thugs (2% per enemy per global sweep);
  winning the ambush has a 50% chance to reform them (+10 rep, accomplishment).

The only true "endings" are the four victories and quitting.

## Economy

Money is a gate, not an upkeep system — nothing charges you per day.

Income:
- Work: 50 c/day (60 with the 'hardworking' trait's +0.2 `wage_mult`).
- Teaching: 10 c/student/day, up to 8 students → 80 c/day; beats work at ≥ 5
  students.
- Wanted criminals: `level × rnd(10..40)` reward (halved if a friend joined).
- Tournaments: fee 50–150, prize = `fee × n_participants / 2` rounded to tens
  (400 c for the default 8-man, 100-fee bracket). Spectators can bet 10–100 c;
  a correct bet pays `bet × num_rounds` (min ×1.5).
- Prize fighting (seedy places): 50 c fee, 5 stages vs lv 2/4/7/10/15; the
  prize is only the *last* stage won (25/50/100/150/250). ⚠️ Stage 1 pays 25 —
  less than the fee; profit starts at stage 3. −5 rep on entry.
- Street performer challenge: pay 40–60, win double back.
- Gambling: rock-paper-scissors, bets 20–50, up to 5 rounds per "streak";
  the gambler plays a skewed distribution half the time, but both AI players
  and an uninformed human pick uniformly, so EV ≈ 0. −3 rep per session, and
  winning ≥ 100 c can trigger a revenge fight that takes it all back on loss.
  ⚠️ Dominated option: zero EV, negative rep, fight risk.

Expenses: tuition 20/day, merchant items 70–150 (`items.PRICES`), kung-fu book
100, wooden mannequin 500, tournament fees, gossip 15–35, wise man 10, beggar
donation 10, opening your school 1000.

⚠️ `pay()` never clamps and the MasterTrial path pays the 1000 c school outlay
**unconditionally** — money can go negative. Most purchases gate on
`check_money`, but the school founding and the gambler's revenge clawback
(`p.money -= self.won`) don't.

⚠️ Dead constants: `TOURN_PRIZE_MULT` and `DEFAULT_TOURN_FEE` (`events.py`),
`BET_REPUTATION_PENALTY` (`tournament.py`) are defined but never used — betting
carries no rep cost.

### Town stats

`crime` gates all crime-encounter chances (`crime/4`, `crime/2`, `crime/3` per
sweep) and drops by 0.002 per crime-fight win (`crime_down`). ⚠️
`CRIME_INCREASE_MONTHLY = 0.00`, so `do_monthly`'s `crime_up` is a no-op —
crime is monotonically non-increasing and the world gets permanently safer as
players fight crime. `poverty` only gates the Beggar chance (`poverty/2`) and
never changes: `poverty_up/down` and `kungfu_up/down` exist but are never
called (todo in `randevent`). ⚠️ `g.kung_fu` is read nowhere at all (the
`_base_game.py` todo claims tournaments use it; they don't).

## Reputation and fame

Reputation is a single integer on the player (`gain_rep`). Sources: defeating
criminals (their level), crime fights (+2/enemy), robber groups (+1/robber, win
only), donations (0.2/coin), reforming an enemy (+10), stories (+25/30),
protecting the performer (+n−1). Penalties: gambling/drinking/brawling −3,
prize fighting −5, refusing to pay shop breakages −1.

⚠️ Extorters, HelpPolice, RobbingSomeone and the performer's thugs call
`gain_rep` *before* the fight — the rep is kept even if you lose. Reputation
can thus be farmed by repeatedly starting (and losing) crime fights, at the
cost of injuries.

⚠️ Reputation's **only** mechanical effect is the Folk Hero victory check (and
a line on the stats screen). Nothing else reads `p.reputation`. In particular,
student attraction uses `get_fame()` — `(tourn_won + len(accompl) +
fights_won // 10) × 0.01` — which ignores reputation entirely, so a
rep-grinding Folk Hero gets no help founding a school, and a hated champion
attracts students just fine.

## Progression levers

**Exp and levels.** Exp sources: fights (winner `25 × (losers' yield / winners'
yield)^1.5`, loser flat 2, sparring included — see fight doc), school/master
practice ≈ 10/day, mannequin 4/day, books 6–25 (×3 on lucky), story dreams
12/25/38, spectating the foreigner 6–19, accomplishments +62 each
(`ACCOMPL_EXP`). Level thresholds are `EXP_PER_LEVEL × next_lv_exp_mult × level`
(100 × level by default), but exp is **cumulative** and never reset on level-up,
so each level-up effectively costs a flat 100 exp (90 for 'quick-witted');
reaching lv 20 needs 1900 total. ⚠️ The `× level` in the formula looks like an
escalating cost but isn't — the per-level cost is constant. Verified by
script: thresholds 100, 200, …, 1900, deltas all 100.

Per level-up (`Fighter.level_up`): +1 to a chosen attribute (humans pick from
3 randomly offered atts; AI uniform-random — all `att_weights` end up equal),
plus style moves/techs at scripted levels, advanced-move choices at
lv 12/14/16/18/20, general techs at 13/15/17, a tech upgrade at 19.

**Moves/techs outside level-ups:** `learn_move_from` after beating/befriending
the beggar, drunkard, performer, or a lucky challenger win; books (50% move,
tier ±1 by luck); master trial and story rewards for techs.

**Traits** (`actors/traits.py`): one negative + one positive at creation,
adjusted via WiseMan (15% per talk) and 'Personality Change'. Effects are flat
adds to player policy numbers (wages, training exp, greed/fear dice, escape
bonus, `next_lv_exp_mult`, etc.).

**Items** (`things/items.py`): herbs are one-fight consumables — applied
pre-fight (`handle_items`, at most one per fight via `use_fight_item_or_not`)
and canceled after. Ginseng Root cancels injury. Mock items (bought from shady
performers 50% of the time) do nothing except feed the Weirdo, who trades one
for a Super Mega Herb (all tier-2 boosts at once). The wooden mannequin (500 c,
Craftsman) makes `do_daily` call `practice_home` for a silent +4 exp every day,
forever — worth ~8 c/day at the school rate (10 exp per 20 c), so it pays for
itself in about two months of training and stacks with everything. ⚠️ Its description says "allows home training", but there is
no home-training day action; it's a passive trickle, which the text doesn't
convey.

**Luck**: `check_luck` is a d20 rolled in several encounter resolutions; 1 =
bad, 20 = good (5% each), flipping outcomes (free mannequin vs shoddy one,
extra tech from the beggar vs injury, challenger's master shows up, ...).

## Friends, enemies, school rank

Friends (max 8, +2 for 'friendly') join fights/training with per-friend dice
and enable FriendMatch spars; co-op players are pre-friended at game start
(`_new_game.py`). Enemies trigger ambushes (above). School rank is the position
in `schools[style]` sorted monthly by `get_exp_worth()`; winning a
SchoolChallenge spar swaps you up one rank. Rank 1 is required for the master
trial. ⚠️ The commented-out code in `_school.py` shows reaching rank 1 was
meant to teach the school's secret technique; it currently grants nothing but
a compliment.

## The own-school loop

Implemented via the MasterTrial encounter (`encounters/_school.py`): requires
`not is_master`, school rank 1, and `level >= 11` (`fighter_factory.MASTER_LV[0]`),
then 5% per `MasterTrial` entry per school-practice sweep (3 entries → ~14%/day).
Beat your master in a spar, pay 1000 c (unconditionally — see ⚠️ above), pick a
school name: you're removed from the old school, become `masters[your_school]`,
and `is_master = True` permanently changes your action list (practice is free,
pick-fights becomes teach-students) and locks you out of student-only
encounters (Brawler, Challenger, SchoolChallenge/Bullying, Fat Girl).

Students arrive through the `Students` encounter (any non-rest day action):
chance `min(get_fame(), 0.07)` per global sweep — so a fresh master with no
accomplishments, tournament wins or 10+ wins has fame 0 and **never** gets
students until they build fame. Intake is either one student (AI always
accepts) or a group of 2–5 that must be beaten in an items-off fight. Cap 8
(`MAX_NUM_STUDENTS`); new students are random lv 1–10 and get +10%/month level
ups below lv 8. Teaching yields 10 c/student/day. Your school joins the
`schools` dict, so it takes part in monthly re-ranking and the 4%/day
school-vs-school brawl event.

⚠️ `best_student` is saved/loaded and read by ForeignerStory but **never
assigned** anywhere in gameplay — that story branch is dead code.

## Random events

`events.randevent` runs once per day (`next_day`), independent rolls:
10% a new story begins (a random unstarted story picks a random eligible
player in its level window; a started story then advances via the
ContinueStory encounter, 7% per encounter sweep), 4% school-vs-school brawl
(the top fighter of each of two random schools, rest as allies — a real fight,
so players involved get exp, stats and can be injured; nothing else about the
schools changes), 15% a tournament starts.

Tournaments (`happenings/tournament.py`): random level band (1–3/4–6/7–10/
11–14), 8 participants usually, single elimination with byes on odd counts,
fights are items-off/no-environment but otherwise real (injuries, stats,
accomplishments, exp all apply). Entry fee paid up front; winner takes the
prize (see Economy). 3 wins → 'Tournament Champion' accomplishment. ⚠️ The
no-winner case (mutual KO in the final) raises `NotImplementedError` — nearly
unreachable, but a real crash path.

## Strategic trade-offs the numbers imply

- **Time is the only real currency.** Everything is exp/day, money/day or
  rep/day, and nothing punishes slowness except rival players racing to a
  victory. Rest/walk/actions differ mainly in encounter exposure.
- **Work ↔ practice:** one work day (50 c) funds 2.5 school days (20 c each,
  ~10 exp). Sustainable pure training ≈ 7 exp/day average, so lv 20 by
  training alone takes ~270 days; mixing in winnable fights (25+ exp each, no
  fee, but injury risk and robbery exposure) roughly halves that. The
  mannequin is the best early purchase.
- **Victory paths overlap deliberately:** fight exp feeds Grandmaster and
  Greatest Fighter; crime fights feed Folk Hero and Greatest Fighter
  simultaneously; stories/tournaments feed Kung-fu Legend and fame. Folk Hero
  via pure donations is ~500 c of beggar money gated behind `poverty/2`
  encounter rolls — slow but safe.
- **AI policies** (`_ai_player.py`): base AI works until 175 c, then practices
  90% of days; masters teach when broke with ≥ 5 students. ⚠️ `SmartAIP` sets
  `drink_chance`, `continue_gambling_chance` and `buy_med_chance` — none of
  these names exist; the real attrs are `drink_with_drunkard` (0.25),
  `gamble_continue` (0.4) and `min_days_use_med`. So the "smart" AI drinks and
  chases gambling streaks exactly as much as the base AI.
