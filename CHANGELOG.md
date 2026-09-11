# Changelog

All notable changes to KFW are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); releases have codenames.

## [v0.7.2-beta "All Schools Under Heaven"] — 2026-09-11

### Added
- **New-game settings menu**: at the start of a new interactive game you can
  optionally customize the world (skippable — defaults apply, AI-only games
  never ask): level progression (sets the global exp base — The Long Road 15 /
  The Classic Path 20 / Crash Course 30; saved as `game.base_exp` and restored
  on load), crime (Peaceful Town / Rough Edges / Gang-Ridden), poverty
  (Prosperous / Getting By / Hard Times) and kung-fu enthusiasm (Kung-Fu
  Backwater / Martial Town / Kung-Fu Craze), each 0.05/0.125/0.2
- **Two school-management story lines** (gated on being a master with ≥ 2
  students):
  - `SchoolAttackStory` (lv 11–20): hired thugs attack the school at night;
    master and students defend it in a team fight — winning gives +8 rep and
    the 'School Defender' accomplishment, losing costs 100–300 c and 5 rep
  - `StudentRivalryStory` (lv 11–20): two students quarrel over who's the
    best; the master lets them duel (winner may level up), spars them both
    (±rep), or forbids it (25% they duel anyway)
- **Custom school techs at founding**: when a player founds a school, they
  choose up to 3 techniques (from the ones they know) their school will
  teach; students then have a 25% chance per lesson to learn a school tech
  they're missing. AI masters pick randomly
- **All-Schools Tournament**: a rare mega-event (2%/day) where every school
  fields its master and top 2 students in a group free-for-all between
  schools; the winning school's players get exp, reputation, a 200 c prize
  and the new 'All-Schools Champion' accomplishment
- **Teaching students actually teaches**: `teach_students` now gives every
  student a 20% chance to level up per lesson (up to the master's level − 2,
  above the old NPC-student cap of 8) and reports who improved, on top of the
  tuition income
- **`best_student` is now maintained** (strongest student by exp worth,
  refreshed on intake/teaching/monthly) — it was saved and read by the
  Foreigner story but never assigned, so that story branch finally works
- **Masters share their students' tournament glory**: a student's tournament
  appearance is logged; a student title earns the master +3 reputation and
  a `students_tourn_won` stat point, with the new 'Master of Champions'
  accomplishment at 3 student titles
- **New victory type — Uniter of Schools**: masters get a new day action,
  "Visit other masters" — convince every NPC school in town to join your
  kung-fu federation, either by beating the master in a spar or by persuading
  him (chance scales with reputation, capped at 75%). Each alliance gives +5
  rep; completing the federation awards the 'Founder of the Federation'
  accomplishment and wins the game. AI masters pursue the federation too
- **Tavern brawls**: the StreetBrawl encounter has a 50/50 flavor variant —
  stumbling into a tavern brawl between drunkards (same mechanics, Dirty
  Fighting style)
- **Group labels in group-FFA prefight screens**: each group is listed under
  a `--- Group N ---` separator with the human's group marked, so a 3v3 gang
  war no longer looks like "you vs 6 thugs"
- **FFA win-rate harness**: `dev_scripts/testing/run_test_ffa.py`
  (`Tester.test_ffa_win_rates`) measures plain-FFA / united-group / group-FFA
  win rates at equal levels; first report committed
  (`tests/ffa win rates lv=10 n=100.txt`)
- **State menu: Moves and Techniques screens** — moves/techs are no longer
  printed on the State menu's main screen; they get their own detailed screens
  (`m`, `t`), like Items and Accomplishments
- **State menu: Students screen** (`s`, masters only) — lists your school's
  students sorted by level, marking the best one
- **State menu: Finish Game** (`F`, only after winning and choosing to keep
  playing indefinitely) — reruns the victory routine (victory message, stats,
  bio, `game over.txt` save) and then quits
- **'Most feared move' and 'Max single blow' stats**: the feared move is the
  highest-tier attack move used (ties broken by usage), the max blow records
  the biggest single-strike damage and the move; both are shown in the full
  stats report, and the feared move appears in gossip and biographies
- **The school name becomes the style name**: when a player founds a school,
  the chosen name is now displayed as the master's (and their students')
  kung-fu style everywhere — pre-fight screens, stats, bios — with a warning
  at naming time (implemented as the display-only `custom_style_name`;
  restored from the saved school structure on load)

### Changed
- **Balance: global exp base lowered 25 → 20** (`BASE_FIGHT_EXP` in
  `kf_lib/constants/experience.py`): all exp sources scale ~20% down (fight
  wins, training, books, dreams, accomplishments); the level cost is unchanged
  (100 exp/level), so leveling is slower by default. Balance-affecting — a
  `dev_scripts/testing/run_test_fb.py` re-run is queued to refresh the
  fight-balance snapshot
- **Town stats are no longer randomized** at new-game start: `poverty`,
  `crime` and `kung_fu` all start fixed at 0.125 instead of a random draw from
  (0.05, 0.1, 0.15, 0.2); the new settings menu offers 0.05/0.125/0.2 per stat
- **State menu keys**: Save, Load, Quit, Save and Quit and Debug Menu moved
  to uppercase (`S`, `L`, `Q`, `X`, `D`) to free lowercase `s` for the new
  Students screen
- **Master's verbose info**: the meaningless "rank in school: n/a" line is no
  longer shown for masters; the students line (with best student) comes first,
  then friends/enemies
- **Overheard gossip condenses same-type opponents**: the OverhearConversation
  narration now says "beat 5 Thugs" instead of listing "Thug 1, ..., Thug 5,
  ..." (mixed groups are grouped too: "3 Thugs, Zhao Liao and 2 Robbers")
- **Reaching school rank 1 earns a reward**: the master's praise, +25 exp and
  +2 rep (replacing a fossil of the pre-v0.7.0 design, where rank 1 was meant
  to teach the secret technique — that has lived at lv 7 since)
- **Even unknown masters attract students**: the Students encounter now has a
  1% base chance (`BASE_STUDENT_CH`) before fame is added — a fresh master no
  longer needs fame to ever get applicants
- **Betting on tournaments costs reputation**: placing a bet applies −3 rep
  (the long-dormant `BET_REPUTATION_PENALTY`), win or lose — gambling is not
  honorable by wuxia morals
- **Free-for-all rebalancing**: FFA fights paid exp for the *sum* of all
  losers, so e.g. an 8-man Battle Royale win could grant 500+ exp and several
  levels at once. Now FFA exp (incl. group FFA) is per-capita — based on the
  *average* opponent's yield — since the losers were fighting each other too.
  Alongside: the pre-fight risk estimate for encounters known to be FFA up
  front (StreetBrawl, GangWar) compares against the average enemy instead of
  the pile (`get_rel_strength(..., mean=True)`), and the crowd accomplishments
  'Lone Warrior' / 'Against All Odds' are no longer awarded for FFA wins
  (astonishing-victory gossip uses the same per-capita ratio). The new
  `run_test_ffa.py` harness shows why: P(win FFA) ≈ 1/n while
  P(beat a united n−1) ≈ 0. Balance-affecting; `run_test_fb.py` re-run
  stays queued
- **FFA street encounters are ~2× rarer**: StreetBrawl 0.03 → 0.015,
  brawl-spreads-to-bystanders 0.25 → 0.125, GangWar crime/4 → crime/8
- **Learn-move menu shows the strike's distance change as `start->end`** (e.g.
  `1->2` for a retreating strike instead of `1(1)`)

### Fixed
- **All-Schools Tournament leaked secret style names**: the winner
  announcement used the school's true style name (the `game.schools` key);
  it now uses the displayed (public) name
- **End-of-FFA picture showed two lying fighters**: the final screen drew the
  viewer's *last target* (often another KO'd loser) while the win quote came
  from the actual winner; a losing viewer now faces `winners[0]` in the `Win`
  stance
- **AI attribute growth had no build logic**: the `random.randint(1, 2)` line
  in `set_att_weights` was commented out, so `rand_atts_mode` 1/2 set every
  weight to 1 and AI fighters grew attributes uniform-randomly. Restored —
  mode-1/2 fighters (AI heroes, some NPCs) now mildly specialize
  (balance-affecting; queue a `dev_scripts/testing/run_test_fb.py` re-run)
- **Exact-damage KOs kept qi points**: `change_hp` only zeroed qp when damage
  overshot the remaining hp; an exact-to-zero hit left qp intact
- **Pools stayed above shrunken maxes after item expiry**: e.g. cancelling an
  Elephant Herb left hp above the restored `hp_max`;
  `refresh_dependent_atts` now re-clamps hp/stamina/qp
- `FighterAPI`: `set_distances_before_fight` was missing `@abstractmethod`
  (a `Fighter` composed without `DistanceMethods` would instantiate and only
  crash later); fixed the invalid `weapon_bonus` type annotation
- Debuffed attributes now display as `full(base)` instead of silently showing
  the base value (`get_att_str`)
- **Masters were helped by the wrong school in street fights**: `get_school()`
  returned the master's *old* style school, so help came from ex-schoolmates
  and the old master. Now the master's own students come to help (the master
  branch brings the strongest student); also fixed a crash when a school had
  fewer than 2 members available to help
- **Tournament crash paths**: nobody eligible showing up crashed with
  `IndexError` (the tournament is now canceled instead), and a drawn final
  raised `NotImplementedError` (now ends with no winner and all bets lost,
  like a battle-royale draw)
- **Missing keypress pauses**: the teach-students results and the human ally's
  criminal reward were shown without a `pak()`, scrolling by unread
- Removed unused tournament leftovers (`TOURN_PRIZE_MULT`,
  `DEFAULT_TOURN_FEE`)

## [v0.7.1-beta "Eight Tigers in One Cage"] — 2026-09-10

### Added
- **Ctrl+C exits the game at any keypress prompt**: the raw-mode keyboard layer
  translates the `'\x03'` byte into `KeyboardInterrupt`, caught gracefully in
  `kfw.py`
- **Group free-for-all fights**: `group_free_for_all()` /
  `BaseGroupFreeForAll` — several groups fight each other with no infighting
  within a group, last group standing wins
- **'Battle Royale Champion' accomplishment** for winning a battle-royale
  tournament
- **Five new story lines** built around the free-for-all mechanics:
  - `GrandMeleeStory` (lv 3–6): a shady promoter's prize melee, then an armed
    Night Melee for winners; rep penalties (fighting for money is against the
    wushu code), a comic reprimand from the hero's master, and a 20% chance of
    a school ban — while banned, school practice is a begging scene (no
    tuition, no exp, 25% forgiveness chance, 20% bullying chance per visit)
  - `SaintsDayRiotStory` (lv 5–9): a festival turns into a giant street riot
    FFA; the aftermath lets you take responsibility or pin the blame on a
    rival school (making its master your enemy)
  - `JadeTableStory` (lv 9–13): hired muscle at a crime-boss sit-down that
    explodes into a group free-for-all (hero vs each boss with bodyguards);
    winning decapitates the underworld, losing makes the boss a persistent
    enemy
  - `EightGatesStory` (lv 11–14): gated on the 'Battle Royale Champion'
    accomplishment; an 8-disciple FFA trial (no items/environment) with a
    secret-technique reward
  - `WrongPouchStory` (lv 4–8): a pickpocket who also robbed two gang fences;
    a comedic 6-way FFA over the loot pile, winning returns the stolen money
    plus a random item
- **Free-for-all fights**: new fight variant (`fighting/fight/_free_for_all.py`,
  `free_for_all()` helper) — 3+ fighters, no teams, every fighter targets
  everyone else, last man standing wins (draws possible on double KO / time
  limit). Exp, accomplishments (incl. 'Lone Warrior'), gossip and injuries work
  as in normal fights
- **Battle-royale tournaments**: 25% of tournaments are now 8-man free-for-all
  melees (`CH_TOURNAMENT_FFA`) instead of single elimination; a draw means no
  winner, no prize and all bets lost
- New encounters: `StreetBrawl` (jump into 3–5 brawlers already fighting each
  other) and `GangWar` (caught between two warring gangs, everyone fights
  everyone; boosted in `PICK_FIGHTS_ENCS` / `FIGHT_CRIME_ENCS`)
- Free-for-all branches in existing encounters: `Robbers` crowds may squabble
  over the loot (0.25), `HelpPolice` may draw a second gang into a three-way
  melee (0.25), `Brawler` fights may spread to bystanders (0.25)
- **'Accomplishments' option in the State menu** — lists all of the player's
  accomplishments with dates (the data was already stored, just never shown)
- **Biographies name the player's most feared move** — the strike with the
  highest times-used × power — when it differs from the signature move
- Trying to befriend someone over the friend cap now shows a note and logs
  "stays an acquaintance" instead of silently dropping the friendship

### Changed
- **`Fighter.level` is now a read-only property** — direct assignment
  (`f.level = n`) raises `AttributeError`, because it silently leaves
  attributes/techs/moves under-leveled; use `f.level_up(n)` everywhere
  (tests and dev scripts included)
- **Deterministic tech rolls**: `set_rand_techs` no longer picks from an
  unordered set of id-hashed tech objects (the choice depended on process
  allocation history, which made
  `test_set_rand_techs_upgrades_a_style_tech_at_lv_10_plus` flaky); style-tech
  upgrade and advanced-tech picks now sort candidates by name first
- Targeting/ally logic in the fight engine is now dispatched through
  `BaseFight.get_act_targets`/`get_act_allies` (used by `start_fight_turn` and
  `handle_items`), and the in-fight HP bar is built from `act_allies`/
  `act_targets` — two-sided behavior unchanged, free-for-all overrides the
  hooks

### Fixed
- **'Lightning-Fast Strikes' advanced tech was a no-op**: it reused the basic
  tech's `STRIKE_TIME_COST_MULT1` (−0.3) instead of `STRIKE_TIME_COST_MULT2`
  (−0.6), so upgrading 'Fast Strikes' changed nothing
- **`get_rand_moves` crashed on an empty move pool**: `random.choice(pool)` ran
  before the empty-pool check, raising `IndexError` instead of the documented
  fallback to the whole tier
- **`OverhearConversation` log lines were swapped** — the humiliating-defeat
  branch logged "astonishing victory" and vice versa
- **Lying fighters showed standing 'Hit Effect' art** on shock/stun/slow-down:
  the `'Lying '` prefix check used lowercase `startswith('lying')`, which never
  matched the stored `'Lying …'` names; the same typo in the KO path could show
  'Falling' art for an already-lying fighter
- **`repr()` of a player during `Fighter.__init__` crashed** with
  `AttributeError: ... no attribute 'traits'` on any warning path during
  construction (`BasePlayer` set `traits` only after `super().__init__()`);
  `traits` is now initialized before the super call
- **`EncControl.run_enc` dev hook raised `TypeError`**: it passed a nonexistent
  `test=` kwarg to encounters; it now maps `test` to `check_if_happens`
  (`test=True` forces the encounter, skipping the chance roll)

## [v0.7.0-beta "Secret Kung-Fu Manuscripts Don't Burn"] — 2026-09-07

First release after a four-year hiatus (since v0.6.9-beta, 2022-11-20): a
post-hiatus modernization cycle, and the first cycle developed with the aid
of coding agents (previous releases were written fully manually). Highlights:
JSON save format (with a legacy loader), secret style techniques with lv-10
upgrades, in-fight stats, a pytest suite, per-system docs, and a pile of
long-standing bug fixes (broken game loading, near-useless blocking, dead
SmartAIP knobs, the default-styles startup crash, broken handcrafted style
move strings).

### Added
- **Secret style techniques**: the lv-7 tech of every tech style is now secret —
  hidden from style descriptions (`???` placeholder) until learned. Generated
  styles also get a public name (`"{w2} {w3}"`, e.g. "Avalanche Leopard") shown
  everywhere, while the true three-word name (with the first adjective granting
  the secret tech) is revealed only to the style's disciples at lv 7 — for a
  human player, in a scene with the school master. Generated-style tech order
  changed accordingly: lv 3 second word, lv 5 noun, lv 7 first adjective
- **Style tech upgrades at lv 10**: one of the style's three techs (the secret
  one included) is upgraded to a doubled-effect `Advanced ...` version — the
  human player chooses, AI/NPCs upgrade randomly
- pytest suite in `test/` (230+ tests): seeded deterministic fights, style/move
  generation invariants, save/load roundtrips (both formats), leveling,
  economy, player AI, game mechanics, headless tournament, full-game
  integration tests
- `kfw.py`: single argparse-based entry point (`--autoplay`, `-n`,
  `--autosave`, `--silent-ending`, `--load`); the old `NG_*`/`load_*` root
  scripts were removed, and the profiler moved to `dev_scripts/profile_game.py`
- `AGENTS.md` (onboarding/pitfalls), `BACKLOG.md` (structured, replaces the
  old `docs/backlog.md` + `docs/todo.md` dumps), this changelog
- System docs in `docs/`, one per game system, mechanics-as-implemented with
  ⚠️ flags for suspicious behavior: `fight_mechanics.md`, `gameplay.md`,
  `encounters.md`, `ai_players.md`, `kung_fu.md`, `items.md`, `stats.md`,
  `social_and_traits.md`, `text_content.md`, `minigames.md`, `debug_menu.md`,
  `dev_scripts.md`
- `pyproject.toml` with black config; `numpy`/`tqdm` added to dev requirements
- **In-fight stats**: every fighter now accumulates per-fight stats (strikes
  thrown/landed, damage dealt, criticals/EPICs, per-move usage); the
  post-fight "Stats" menu option shows them (it previously printed an
  always-empty dict), players accumulate all-time `strikes_thrown/landed`,
  `dam_dealt`, `criticals`, `epics` and `move_usage` in saves, the full stats
  report shows them (new "Crits,EPICs" row), and biographies name the
  player's signature move (most-used strike)

### Changed
- **Save format is now JSON** (versioned schema); old exec-based saves still
  load via a legacy shim in `LoadGame._load_legacy`
- `encounters/__init__.py` (1353 lines) split into thematic modules
- `Challenger`/`Master`/`Thug` fighter subclasses replaced by a
  `Fighter.occupation` attribute; old saves keep loading via factory shims

### Fixed
- **"Fav. move" stats row counted defensive moves**: the full stats report
  showed e.g. Guard as the favorite move while the biography named a strike as
  the signature move; both now use `get_favorite_move(attack_only=True)`
- **Game loading was completely broken** (exec() namespace bug + missing AI
  classes in the loader namespace) — any save failed with `NameError`
- macOS/Linux support: `msvcrt`-only keyboard input now falls back to
  termios/tty; `cls` → `clear` on non-Windows
- **Blocking absorbed ~1/400 of intended damage**: the per-fighter hook and the
  global constant were both named `BLOCK_POWER`, and `Fighter`'s MRO shadowed
  the global (20) with the hook (1.0) — the "blocking hurts more than not
  blocking" bug. The hook is now `BLOCK_DEFAULT_POWER`
- **Draws crashed `give_exp`** with `ZeroDivisionError`; a draw now gives every
  player a flat `BASE_FIGHT_EXP / DRAW_EXP_DIVISOR` (12 exp)
- **`SmartAIP` set dead attribute names** (`drink_chance`,
  `continue_gambling_chance`, `buy_med_chance`) that nothing ever read, so the
  "smart" AI drank and chased gambling losses exactly like the base AI; it now
  overrides the real instance knobs (`drink_with_drunkard`, `gamble_continue`)
  post-init
- **Default-styles games crashed on startup**: 'Eagle Claw III' passed
  `critical_mult` instead of `critical_dam_mult`, so any Eagle Claw fighter
  reaching lv 7 (school masters are created at lv 11-14) crashed
  `_init_schools` — hidden since 2022 because tests/autoplay use generated
  styles
- **Hung Ga's lv-8 signature move was unreachable**: the style string said
  `'No-Shadow Kick'` but the move was spelled `'No-Shadow_Kick'` in the move
  data (a one-off underscore typo), so the level-up silently granted a random
  move. The move is renamed to the spaced spelling (which also matches its
  dedicated ASCII art, previously unreachable), and a `MOVE_ALIASES` shim in
  `get_move_obj` keeps old saves referencing the old spelling loadable
- **Remaining broken style move strings**: Wing Chun's lv-2 `'Short Fast
  Punch'` never existed in the data — added as a new tier-0 style move
  combining the perks of Short Punch and Fast Punch (distance 1, time cost
  40, stamina cost 20, `fast`+`punch`+`short` features). White Crane lv-6
  and Xing Yi lv-2/4/8 used invented feature tokens (`close-range`,
  `mid-range`) that silently did nothing; replaced with the real
  auto-derived distance features (`dist1`, `dist2`)

---

## Historical releases

v0.6.1–v0.6.9 were migrated from `docs/version_history.md`. Everything older
was reconstructed in September 2026 from the per-release `! development.txt` /
`changes.txt` files preserved in `old_versions/kfw/` (cross-checked against
git history for v0.5.9–v0.6.0). Wording is kept close to the original files,
including the move-count progressions; `!`-highlighted items in the sources
are bolded here. v0.1.x predates changelog-keeping entirely — those entries
are inferred from diffs between consecutive `to do.txt` files and marked as
such.

### v0.6.9-beta "Not Fail, But Experience" — 2022-11-20

1. **New experience system**:
   1. feat: change how exp is computed in fights
   2. feat: static accomplishment experience
   3. feat: modify exp per level (static) and school training exp
   4. feat: constants package, experience module inside it
   5. feat: misc exp-related tweaks for the new exp system
   6. feat: home training is only allowed when have a wooden mannequin
   7. feat: base and derived experience constants
   8. feat: losers get fixed amount of exp
   9. feat: add non-linearity to win exp
2. feat: biography generation for winning players
   1. feat: describe strengths
3. refactor:
   1. refactor: __init_subclass__ in base encounter for automatic class registration
   2. refactor: BaseEncounter is an ABC
   3. refactor: type annotations for BaseEncounter methods
   4. refactor: BookSeller to a separate module
4. feat: changes in encounters
   1. feat: change logic of learning moves from books
   2. feat: test encounters in debug menu
   3. feat: lucky and unlucky cases in book seller encounter
5. feat: moves
   1. feat: generate pathetic, weak, skillful, etc. variants for all moves (3768 -> 16844)
   2. feat: ultra short and ultra long strikes (with ASCII arts) (-> 18436)
   3. feat: remove weak and pathetic moves (-> 13844)
   4. feat: rebalance moves / tiers
   5. feat: improve random move selection logic (no duplicates, one random move for variety)
6. fix: in fighter_factory.py, first create fighters of level 1, then level them up for gradual move progression
7. feat: toughness - damage reduction that is level-dependent (for all fighters)
8. feat: Drunken has improved ground defense
9. fix: UI functions in stories
10. **refactor: FighterAPI (ABC for Fighter)**

---

### v0.6.8-beta "Drunken Boxing" — 2022-08-13

1. fixes: game loading, SpectateFight, qi-based damage, feel too scared
2. feat: add quotes from Dark
3. feat: add Weak and Pathetic moves
4. feat: ~8 more new quotes (various sources)
5. fix: bug in 'unlucky' craftsman encounter
6. **feat: Bandit Fiance story**
7. feat: test story in debug menu
8. refactor: ratio -> opp_to_self_pwr_ratio
9. feat: move fail chance multiplier and fall damage multiplier
10. feat: add descriptors for value validation
11. feat: exception handling when applying techs
12. refactor: major refactor of stories
13. feat: 3 new style words: Drunken, Acrobatic, Squirrel
14. feat: 2 new techs: Drunken Moves and Drunken Acrobat
15. feat: better move learning through debug menu
16. fix: double knockback (at last!)
17. fix: easy knockback when rushing forward
18. feat: improved handling of knockback
19. feat: new ASCII arts (drunken, acrobatic) (total 198 arts)
20. feat: redraw a few old ASCII arts
21. feat: detect duplicates in ASCII arts
22. feat: remove backflip strikes
23. **feat: combinations of move functions for generation are now described in a table ("move_word_combinations.csv"), not in the code**
24. feat: new "Drunken" moves, revamp move word combinations (generated 3095 -> 3768 moves)
25. refactor: strike multipliers
26. feat: common logger
27. refactor: Fighter.techs now consists of Tech objects, rather than strings
28. feat: acrobatic styles, techs and buffs
29. feat: reduce folk hero reputation
30. feat: boost_combos.py as SSOT for technique effects
31. feat: improve new move selection

---

### v0.6.7-beta "Blood Sport" — 2022-03-29

1. fix: nerf default block power, agility goes down in significance, balance improves
2. fix: remove depth-3 move generation for cleaner moves with shorter names (17699 -> 3095 moves)
3. fix: using @property, fix the upper bound of chance to resist KO to avoid endless / very long fights
4. fix: separate bonuses for Guard (as a move) and "guard while attacking"
5. fix: increase guard bonus for all
6. refactor: factor folder name constants and ensuring folders exist to a separate module
7. feat: also save moves as a Pandas DataFrame (for development purposes only)
8. refactor: separate fight into submodules
9. **feat: bleeding mechanic**
10. feat: techniques (and styles) related to bleeding
11. feat: "Slashing" moves (3095 -> 3313) and Claw is slashing by default
12. refactor: game.py is now a package
13. feat: school students are now levels 1-10, masters levels 11-14
14. fix: bug in saving game (duplicated players)
15. feat: change tournament levels: 1-3 "beginner", 4-6 "intermediate", 7-10 "advanced", 11-14 "master"
16. feat: hp gain is relative to max hp
17. feat: dam reduc is relative to damage
18. feat[dev]: basic move analysis (with pandas)
19. feat: overhaul move tiers

---

### v0.6.6-beta "Rebalance, Fixes and Fun" — 2022-02-24

1. feat: start using rich module for colorful text
2. refactor: significant overhaul of utils, ui and testing tools
3. refactor: remove unnecessary tech classes, reimplement their functionality as attributes
4. feat: preemptive strikes are tech-only
5. feat: fury is tech-only
6. feat: new flexible profiling script
7. **feat: new fight AI that is more fun (rushes in from distance 4 when hp and stamina are full)**
8. fix: ASCII art errors in weapon strikes
9. fix: old bug with umbrella turning into a pole
10. fix: old bug with standard moves
11. feat: confirm randomly generated styles with the player, regenerate if not ok
12. fix: guard and guard while attacking now work properly
13. fix: qi gain techs now work properly
14. fix: stamina and qp are now properly spent when missing
15. fix: counters and preemptives can now miss, too
16. fix: criticals are now working properly
17. fix: blocks are now working properly
18. fix: counter techniques
19. **feat: complete rebalance of techniques, boosts and strikes**
20. fix: moves with distance bonus are now properly suggested on level up

---

### v0.6.5-beta "Fist of Fury" — 2022-02-12

1. feat: luck (extremely good/bad, corresponding stats and accomplishments)
2. feat: learn other fighters' moves
3. refactor: encounters.py
4. feat: lucky and unlucky scenarios in Challenger encounter
5. feat: counters, preemptive strikes and criticals are now agility-based
6. fix: test fight balance
7. feat: improved fight balance (agility is no longer weak)
8. feat: quotes from Chinese classic "The Outlaws of the Marsh"
9. feat: lucky and unlucky scenarios in Craftsman encounter
10. feat: use completely new randomly generated styles in many encounters
11. refactor: use type hints in Fighter, accept both strings and objects as style
12. feat: reimplement takedown generation, hence more moves: 15805 -> 17699
13. fix: bug in prefight quotes not being said by second participant
14. feat: fury, another (hopefully) fun game mechanic
15. feat: fury-related techniques and styles
16. feat: new fight AI that rushes when fights against 4-distance moves or when has a bigger crowd
17. feat: improved testing of fight balance and AI
18. feat: lucky and unlucky scenarios in strong Beggar encounter
19. refactor: genetic algorithm for fight AI training
20. feat: remove help in Fat Girl encounter
21. feat: in genetic algo, mutation only applies to children
22. refactor: player as a package
23. feat: train a new powerful genetic fight AI (pop=32 fights=160 n_gen=128 gen=84)

---

### v0.6.4-beta "Flashy Fights" — 2021-12-25

1. docs: add a (more or less) proper README
2. feat: PvP in debug menu
3. fix: turn off items in ninja turtles fight
4. feat: momentum!
5. feat: ability to learn any existing tech via the debug menu
6. feat: ability to inspect current player's attributes in the debug menu
7. feat: ability to set any player attribute in the debug menu
8. feat: faster strike / maneuver mechanics (28594 possible unique styles)
9. feat: utility for counting the number of possible generated styles
10. feat: new styles for generation (including preemptive strikes)
11. feat: preemptive strikes!
12. feat: ASCII additions and improvements
13. fix: bug in debug menu (current player was assigned only once)
14. feat: new formula for knockback caused by damage
15. feat: visualize knockback
16. feat: criticals are level-dependent
17. feat: "~*~*~EPIC!!!~*~*~"
18. refactor: basic and fight attributes
19. feat: a few new hero quotes
20. feat: 3x3 co-op mode

---

### v0.6.3-beta "Bet on Tournaments" — 2021-10-31

1. feat: ability to bet on tournament outcome
2. feat: ability to start a tournament via the debug menu
3. feat: knockdown and off-balance are relative to current hp, not max hp (knockback and stun remain relative to max hp)
4. feat: probability of feeling too scared to fight is now proportional to risk
5. feat: debug mode in user input (get_key)
6. feat: a few new quotes, inspired by Lady Bloodfight
7. feat: one of the rewards for protecting street performer from thugs is new move
8. feat: new "Super" fight items
9. refactor: Tournament
10. refactor: major refactor of Fighter (split into submodules) as well as some other modules
11. refactor: put docs to separate folder, add some todos
12. fix: bug in tournaments with odd numbers of fighters
13. fix: small import bug in encounters
14. fix: bug when fights didn't happen because fighters started with 0 hp
15. fix: import bug in turtles reward
16. fix: fight items have relative effect
17. fix: qp-related custom styles
18. fix: qi cost rebalance

---

### v0.6.2 "Debug Menu" — 2021-06-17

1. feat: add debug menu to status screen
2. fix: proper input validation in get_int_from_user
3. feat: ability to get money via debug menu
4. feat: ability to get items via debug menu
5. feat: ability to level up via debug menu
6. feat: first custom exception - MoveNotFoundError
7. feat: randomly choosing weapons in school challenges
8. feat: ability to learn moves (by name or tier) via debug menu
9. feat: ability to fight thugs via debug menu

---

### v0.6.1 "Fist of Vengeance" — 2021-06-16

1. feat: if lose to strong Beggar/Drunkard/Performer, learn a move
2. feat: books sometimes give moves
3. feat: more flexible tournaments (variable number of participants)
4. feat: new default move: Weak Short Punch
5. refactor: flynt (convert to f-strings)
6. feat: max stamina is relative to level and stamina gain is relative to max stamina
7. feat: stamina boosts in techs are relative (and a bit nerfed?)
8. feat: stamina damage is relative
9. balance: Guard doesn't gain additional stamina, but also doesn't reduce qi
10. feat: add Do Nothing move
11. feat: qp max / gain increases with level
12. balance: leaps, sweeps and other basic moves don't expend qp
13. balance: reduce qi cost for moves
14. feat: qi-related boosts are multipliers, like with stamina
15. feat: COUNTERS!
16. feat: crash report generation
17. feat: counter chance increases with level
18. feat: boosts / techniques / styles related to counters
19. fix: adjust qi-based damage
20. fix: 20 options on screen by default
21. fix: counter chance increases by 0.02, not by 2
22. fix: game loading didn't work after refactoring
23. fix: "Ox Herb" and "Dragon Herb" now work properly
24. feat: add version history

---

### v0.6.0 "I'll Be Watching You" — 2020-10-31

Reconstructed from the release snapshot's `! development.txt`
(`old_versions/kfw/`, cross-checked against git history).

1. **feat: ability to observe what AI players do during their turns** (hence the codename)
2. **feat: machine learning-based prediction of fight outcomes, 90-91% accurate (LR, RF)**; the trained LR model's intercept and coefficients are usable without any heavy dependencies (`ml_fighter_pwr.py`)
3. feat[dev]: `utilities.multiply(numbers)`, `experience.extract_features(side_a, side_b)`
4. feat: style moves: Backfist (karate); default moves for some foreign styles
5. feat: generated throws (15789 -> 15803 moves)
6. feat: new style: Capoeira
7. feat: a handful of Thai and Brazilian names
8. feat: don't add random moves to choose from if there is at least one style string-based move -> more distinct styles
9. feat: always try to learn a move with a bonus
10. fix: evil crash in spectating fights
11. fix: style generation used the same subset of strings
12. fix: bug in learning new moves at level 10+
13. fix: fight items are now canceled after exp earned is calculated
14. fix: exp bonuses are now properly recorded in statistics
15. feat[dev]: `_run_test_lv_vs_crowd.py` shortcut, `tests` folder, improved `Tester.test_level_vs_crowds`

---

### v0.5.9 "Thousands of Styles" — 2020-05-11

Reconstructed from the release snapshot's `! development.txt`
(`old_versions/kfw/`, cross-checked against git history; this is the first
version covered by the repo at all — the initial commit of 2020-04-19 was an
upload of the project mid-cycle).

1. **feat: style generation**
2. **feat: Unix support — the game is playable, although with small UI issues**
3. feat: new fight AI `GeneticAIAggro`, good at both 1-on-1 and crowd-vs-crowd fights (internal rankings at the time: GeneticAIAggro 7629, GeneticAIExtraRules4 6870, GeneticAIExtraRules7 6852, GeneticAITrainedParams8 6795, GeneticAIExtraRules9 6786, WeightedActionsAI 6206, BaseAI 862)
4. feat: player confirms whether the randomly generated fighter is ok in RING
5. feat: successful blocks and dodges increase qp
6. feat: foreign styles have appropriate strikes and techs
7. balance: nerfed weapons; reduced exp multiplier for weapons
8. feat: moves: Charging and Onslaught elbow, claw and knee moves now possible (13803 -> 16125 moves)
9. feat: move generation constraints: 'surprise', 'shocking' and 'debilitating' don't overlap in one move (16125 -> 16041); x-based damage functions don't overlap (16041 -> 15789)
10. refactor: techniques.py, moves.py; removed `move_gen.modified_move` and `RING_debug.py`
11. fix: properly linked ASCII for weapon moves
12. fix: don't get the same move more than once when leveling up
13. feat: UI: move tier displayed in some situations; ASCII for all weapon moves; more ASCII art for old moves; more concise fight messages
14. feat[dev]: reworked test level significance

---

### v0.5.8 "13.8K Moves and a Genetic Fight AI" — 2020-02-07

1. **feat: a brand new fight AI, GeneticAI, optimized with a genetic algorithm**
2. **feat: moves explosion: 1237 -> 1527 -> 1673 -> 2009 -> 2031 -> 10892 -> 11397 -> 13803 moves**
3. feat: moves: level-based damage for some moves; special style moves (Dragon Claw, No-Shadow Kick, Charging Step, Leopard Punch, Mantis Hook); Acrobatic moves (agility-/strength-based damage at the cost of increased complexity); Pushing moves (knockback); Solar moves (damage stamina); Nerve moves (mobility damage); Ferocious, Piercing, Onslaught, Vanishing, Backflip, Debilitating strikes
4. feat: lv-1 style moves; move frequency is taken into account; guard-while-attacking mechanics (and corresponding techs); moves have up to 3 prefixes
5. refactor: improved move generation; distances module
6. feat[dev]: fight_ai_gen, _run_fight_ai_gen modules
7. fix: learning specific style moves didn't work properly; learning style moves at lv 1; defense didn't work at the beginning of a fight

---

### v0.5.7 "It's Alive" — 2020-01-10

1. **feat: IT'S ALIVE! — AI players manage to reach the end of the game** (hence the codename)
2. feat: new sophisticated fight AI (which unfortunately loses to older AIs)
3. feat: special technique: chance to resist KO; on success, the fighter is left with 1 HP
4. feat: `rndint_2d` function simulating double dice rolls
5. feat: moves: Leap Forward and Leap Back
6. balance: worked on game balance
7. refactor: reviewed the fight module and boosts (small fixes); major fight_ai clean-up; optimized the fight loop
8. fix: pak() in RING; fall damage properly scaled; move-while-attacking works properly; fighters created at higher levels learn higher-tier moves (not tier 1); additional damage; time issues; defense didn't work properly
9. feat: UI: better menu for choosing a new move to learn

---

### v0.5.6 "2.5 Years Later" — 2020-01-07

1. **feat: new move system**
2. feat: tournaments happen more often
3. feat: UI: menu with pages; "boring" slideshow

---

### v0.5.5 "No-Shadow Kick" — 2017-05-09

1. **feat: cool new moves: Energy Palm, Spin Kick To Body, Flying Spin Kick, No-Shadow Kick (!), Shove, Power Punch, Flying Punch, Power Palm, Fast Kick**
2. feat: new move effects: additional qi-based damage; instant KO chance
3. feat: rebalance and reorganize moves
4. feat: dummy fighting
5. feat: new encounters: FatGirl, LoseItem, FindItem
6. feat: 60+ Bruce Lee quotes
7. fix: BookSeller encounter wasn't properly introduced in the game
8. feat: UI: number of steps knocked back is shown; save slideshow option; ASCII art for weapon strikes

A "with small changes and bug fixes" re-release followed (same changelog file,
same date): tournament chance 0.1 -> 0.15, boring-fight labeling
(`check_epic` returns `' (epic!)'` / `' (boring...)'` instead of a bool), and
the fight-end message (win quote + "The fight lasted ...") refactored into a
`show_message()` method.

---

### v0.5.4 "Epic Fights" — 2016-11-16

1. **feat: "epic fights" as determined by the percentage of unique ASCII "pictures"** (hence the codename)
2. feat: new encounters: PrizeFighting, School Bullying, Book Seller
3. feat: 'play indefinitely' option after winning
4. feat: off-balance status when missing/failing a maneuver or taking damage
5. feat: mobility damage caused by some moves ('slowed-down' status); all tier-2+ moves cost small amounts of qi; new techs improving Guard
6. balance: more frequent tournaments; decreased exp if armed; Guard gives a 50% defense bonus (not 25%); tournament fee can be paid 'on credit'
7. fix: KO stats were changed in sparrings
8. feat: UI: stun/shock ASCII; lots of new or improved ASCII; post-fight slideshows; 'full contact' ASCII art concatenation

The later "v0.5.4 release" folder is a code-identical redistribution with the
dev/test harness stripped (no changelog of its own).

---

### v0.5.3 "ASCII-fu" — 2016-08-11

1. **feat: ASCII art for fights (tens of items)** (hence the codename)
2. feat: falling down is finally implemented, including fall damage; strong strikes result in falling; defense penalty while lying on the ground
3. feat: new takedown moves: Throw, Trip; new moves: Body Palm, Kick to Knee, Jump Back, Rush Forward
4. feat: dirty moves; anti-ground moves ("let's be realistic")
5. feat: added Chinese wisdom (Confucius etc.) — not used in-game yet
6. refactor: moved quotes to separate text files in a separate folder
7. feat: UI: annotate move effects with '!', shock with '(!!)', stun with '(!)'

---

### v0.5.2 "Chatty" — 2016-07-22

1. **feat: lots of quotes from kung-fu movies** (hence the codename)
2. feat: teenage mutant ninja turtles mini-story for late game
3. feat: implemented shocking moves
4. feat: retreat move (backward handspring)
5. feat: school and master challenges are now sparrings
6. feat: renamed Magic Healer to Ginseng Root
7. balance: no new tech at lv 9; slightly improved (~4%) fight AI (no longer steps back or catches breath at distance 4 with max stamina)
8. feat: UI: display moves in the game status menu; visualize distance; stamina annotations for moves; visualize fight state (`1 /////////////\\\\\\\ 2`)

---

### v0.5.1 "Move with Style" — 2016-06-26

1. **feat: style moves — at last — including 26 new moves** (hence the codename)
2. feat: fight AI OptiWeightAI (square weights for the n best options); the CarefulManeuvers series — about 5% stronger
3. feat: Guard move: restores less stamina than Catch Breath, but boosts defense
4. feat: knockback distance depends on damage; some strikes damage the opponent's stamina
5. feat: no learning new techs before mastering your style
6. feat: a new formula for calculating exp
7. fix: correctly implemented stamina change on maneuvers
8. refactor: major overhaul of fight.py and fighter.py (most methods moved from the Fight classes to Fighter); overhaul of moves.py and techniques.py
9. feat: UI: pretty tables when choosing the target and a new move to learn

---

### v0.5.0 "Another New System" — 2016-05-18

1. **feat: new fighting system (yet another one!): automatic defense; new move system; distance to enemy; speed of attacks; stun handled automatically (dam >= hp_max/3); knockback; fight timer ('The fight lasted XX sec.'); move complexity and fight time limit (not fully implemented yet)**
2. feat: 4 new styles: Centipede, Gecko, Scorpion, Toad
3. feat: new exp bonus and accomplishment: "Quick Victory" / 'Split-Second Victory'
4. feat: tournaments support any number of participants
5. balance: minor tech rebalance
6. refactor: HumanControlledFighter; HumanPlayer moved to player.py; `Fighter.current_fight`; `new_dummy_fighter`; `menu_weak`; utilities: ranked, median, summary, get_time, pretty_table, add_to_dict, dict_diff, dict_comp
7. feat[dev]: new test_fight_balance; tools for analyzing attribute significance for winning; style, tech and move efficiency comparison
8. feat: UI: post-fight menu with stats/timeline (not fully implemented yet); move tips when choosing a move
9. feat: RING: choose start level

---

### v0.4.9 "New System" — 2015-10-04

1. **feat: absolutely new fighting system: stamina factored in; repeated-attacks penalty; 6 basic + 47 advanced moves; defense moves; new moves every other level starting from lv 4; 14 -> 20 styles; new items; grab an improvised weapon in fight; 56 techniques total (42 standard, 14 weapon); stun; new weapon handling (weapon replaces LP/HP/block, each weapon attack has a range); style techs at different levels; bonus moves marked with asterisks when choosing**
2. feat: Muay Thai style for certain NPCs
3. feat: new fight AI WeightedAtkDfsAI that can choose defense moves intelligently (more or less)
4. **feat: better estimates of fighters' strength**
5. feat: guaranteed encounters when choosing certain day actions; fixed number of rounds with the gambler; school ranks go backwards (from last to first); monthly school reranking now affects players; grateful shop owners give rewards to all participating players; can refuse school challenges; can't feel too scared of robbers; tech: start fight with half/full qp
6. balance: yet another tech rebalance; numbers of atts/techs/moves to choose from changed; increased story chance
7. refactor: removed SimFight / .sim_fight (used to create confusion)
8. fix: well-hidden school ranking bug (in crowd games, some AIPlayers fought themselves)
9. feat: UI: short move descriptions (`3, 3, -2, (-3)`); short style descriptions; HP/SP/QP bars + numbers; cls on each attack; prompt which moves the player has bonuses for; school names shown in school-vs-school fights; more concise in-fight text; item effect descriptions

---

### v0.4.8 "Things To Do In Foshan" — 2015-06-15

1. **feat: 5 new day actions that increase the probability of certain encounters: Buy items, Fight crime, Help the poor, Pick fights, Go to seedy places**
2. feat: players actually open new schools, which become part of standard gameplay (challenges, school-vs-school fights); limited the number of students in the player's school
3. feat: Thief can steal items, not only money; skewed Gambler (biased towards some options almost half of the time)
4. feat: No-Shadow Kick: unblockable + critical
5. feat: Super Herb and trait-change accomplishments ('Weird Item' and 'Personality Change'); 7 new item-related player stats
6. feat: BaselineAIP class (random day actions); tests show SmartAIP is indeed the strongest AI player (average days to win)
7. balance: redo criticals and evasion (independent of the atk/dfs stat); Gambler encounter chance 2% -> 5%; up to 7 days to recover by default; 'feel too scared' works only at low risk and higher; upper bound for NPC student level-ups; attacking a focusing fighter removes part of his focus; defend spends stamina when countered or damaged
8. fix: could get two opposite traits at the beginning of the game; beggar friends were lost when saving; horrible well-hidden bug: Magic Healer usable in fights (list was referenced, not copied)
9. refactor: player.py clean-up
10. feat[dev]: 'silent' play mode and win-statistics collection; `_collect_AIP_data.py` and `_compare_AIPs.py` (AI player comparison by average days to win); 'testing' folder

---

### v0.4.7 "Nasty Bugs and Small Fixes" — 2015-05-17

1. feat: new fight ability: total concentration (techs 'Six Harmonies' and 'Twelve Harmonies'); new fight ability: supreme defense ('Wall-like Protection' and 'Emperor's Fortress')
2. feat: three tiers of tournaments; tournament chance tied to the town's kung-fu value
3. feat: pay 1000 coins (debt allowed) to open your school
4. feat: see opponents' stats when undergoing school trials
5. feat: fight_ai: CoordinatingAI, CoordinatingAI2, CoordinatingAI3 (intelligent target selection — ganging up on the same target is, of course, effective)
6. balance: payment to robbers no longer depends on their number; 'feel too scared' is now a fixed probability independent of the number of enemies
7. feat: five robber lines; the PC may feel too greedy in more encounters (Craftsman, Merchant, StreetPerformer, WiseMan, even Extorters)
8. fix: spectate fight bug (win_messages); fighters_list wasn't filled after loading a game; Super Herb obtainable like simple items; school reranking bug (top rank without the special tech); wrong school in the school-fight win message; strange dream turning into gossip; a NASTY well-hidden bug with master name clashes (same master for multiple schools)
9. feat[dev]: fight_ai_test.CrowdVsCrowdFair; more convenient tech testing; tech testing with different fighters of the same level
10. refactor: cleaned up fighter registering

---

### v0.4.6 "Four Encounters" — 2015-04-24

1. feat: finished the Street Performer encounter at last (rewards: a basic weapon technique or exp; sells Gold Magnificent Elixir — can be a good item or a constipation medicine)
2. feat: new Craftsman encounter: buy a wooden mannequin (on credit) to improve home training
3. feat: new Weirdo encounter: trade a mock item for a Super Herb; Super Herb item (+3 to all, +2 stamina)
4. feat: new WiseMan encounter: change your character
5. feat: unique special NPCs for each game (beggar, drunkard, tough thief, criminals) — can be encountered multiple times, but defeated only once
6. feat: new escaped convict every month; schoolmates can help the player in tough fights; school-vs-school fights and stories slightly more often; NPC school students have a 10% monthly level-up chance; poverty/crime/kung-fu values change at each game
7. feat: fight AI uses fight items only when the opponents seem stronger
8. fix: a funny bug where a weak drunkard could become the player's friend
9. feat[dev]: NG autoplay single mode for testing
10. feat: UI: challenger encounter shows the challenger's rank in school

---

### v0.4.5 "Best in Foshan!!!" — 2015-03-27

1. **feat: persistent students in all schools; challengers are now students of other schools (persistent); school challenges advance school ranks; fights between schools!**
2. **feat: new fight AIs: ExponentialCCDSAI (stronger than CrowdConsciousDSAI3 in 1x1), FocusAgainstDefenseAI (really tough in 1x1), FocusAgainstDefenseAI2; CalculatingAI wins group fights but loses miserably in 1x1**
3. balance: Narrow Victory -> 5% hp instead of exactly 1 hp; defense doesn't use stamina unless countering; gain qi only when qi_full > damage taken; only known fighters (from schools) participate in tournaments
4. fix: loading a game with saved traits; a well-hidden bug where known fighters changed their names after becoming friends
5. refactor: keep only 3 AIPlayer varieties (LazyAIP, SmartAIP, VanillaAIP); win_messages argument for fights; weighted_rand_choice integer forcing
6. feat: UI: swap sides when the player is in side_b with no players in side_a
7. feat: RING: difficulty levels (affect enemy generation); display the level reached when losing

---

### v0.4.4 "Traits (At Last)" — 2015-03-04

1. **feat: traits (x16)** (hence the codename)
2. feat: gambling and drinking are no longer completely optional — they depend on the character's discipline; fear checks before dangerous fights; greediness checks
3. balance: interest in kung-fu and poverty no longer change randomly; Challenger/Student encounter chances no longer depend on kung-fu interest; another tech rebalance
4. fix: Fighter.choose_better_att depended on alphabet ordering; nasty well-hidden bugs in countering and display (dfs_when_fcs didn't work; silent multiple counterattacks were possible; .cdam miscounted in turn-line visualization); debugged tech_test.TechTester
5. feat[dev]: more flexible tech_test.TechTester; 100-AIPlayer test game (~39 seconds; name generation could freeze the game — not enough Drunkard names)

---

### v0.4.3 "Major Gameplay Changes After a 6-Month Hiatus" — 2015-02-13

1. **chore: started using Git**
2. **balance: less steep exp curve; rebalanced encounters (crime-based ones happen less often); crime does not increase (for now)**
3. **feat: better, more intelligent random attribute generation for fighters (style emphases taken into account); AI players use the best attribute-upgrade strategy (as tested: ~500 vs ~180, ~2.5 times better)**
4. feat: new statistics: became_master_at_lv, friends, enemies, students
5. feat: new encounter with stories about players (humiliating defeats and astonishing victories)
6. **feat: UI: visualize turns**
7. feat: UI: 'Save and Quit' option in the game menu; improved statistics output (blocks, names and styles inside columns)
8. refactor: new convenient BaseStyle methods
9. feat[dev]: count how many encounters of each type happen throughout the game; test_rand_att_schemes

---

### v0.4.2 "Balanced Techs and Mini-Game" — 2014-07-15

1. **feat: mini-game: RING**
2. **feat: dramatically rebalanced techniques**; stamina techs also increase the stamina restored with focus
3. feat: new branching encounter: street performer
4. **feat[dev]: new module tech_test for comparing technique efficiency (single/multiple opponents, armed fights)**; `_test_techs.py` shortcut; Tester.test_disarm()
5. refactor: chances converted to floats (50 -> 0.5) throughout the code; utilities.rnd()/rndint() reworked; utilities.mean()/.percentage(); techniques.get_style_techs(); encounters.set_up_weapon_fight(); fighter_factory.from_exp_worth; fight.py spectate function

---

### v0.4.1 "Crowd AI and Crime" — 2014-06-29

1. **feat: better vs-crowd fight AI (CrowdConsciousDSAI, 2, 3)**
2. feat: crime rate grows steadily every month; players can decrease the crime rate
3. feat: ForeignerStory: watch the foreigner fight
4. balance: less exp for a defeated fighter's techs; increased 'qi when attacking' multiplier in the corresponding tech; tournaments organized more often; varying tournament participation fee
5. fix: qi when attacking didn't work
6. refactor: Tournament class (tournaments are independent events); Game.do_daily()/do_monthly(); Player.spectate(); fighter factory functions can return single or multiple fighters
7. feat[dev]: improved fight_ai_test.FightAITest; introduced FightAITestCrowds

---

### v0.4.0 "Items and Gameplay" — 2014-06-25

1. **feat: items usable in fights** (items module)
2. **feat: automatic practice at home; exp gained depends on level, number of friends and multiplier**
3. **feat: estimate fight outcomes (no SimFight)**
4. **feat: maximum number of attackers (4 by default), other attacks fail; 2 new techniques decreasing it; bigger crowds of enemies**
5. feat: 2 vs 2 coop game mode
6. feat: weak drunkard fight in the Drunkard encounter; new encounters: match with a friend, robbery (help another person)
7. feat: new stats: most humiliating defeat and most astonishing victory
8. refactor: DataMiningFight class; SpectateFight; fight.py gather_fight_data; Fighter.get_features (for machine learning) and friends; fighter_factory.new_fighter; EncControl.runenc; try_enemy; level_up(times)

---

### v0.3.9 "Misc Tweaks" — 2014-05-10

1. **feat: subclassed AIPlayer for various behaviors (cautious, reckless, gambler, etc.) via adjustable class parameters**
2. **feat: new accomplishments: Lone Warrior (win alone against 5+ enemies), Narrow Victory (win with 1 hp), Against All Odds (win against very strong opponents); exp for each accomplishment**
3. **balance: different level-up exp curve (steeper, 50x^2); only one counterattack allowed when defending; tech tweaks (counter +, critical chance +)**
4. **feat: can have multiple meds**; randomized values: convict reward, gossip cost, med cost, robber money, breakages cost
5. feat: record dates of accomplishments; 'Tournament Champion' now requires 3 tournaments (was 5)
6. balance: changed Dragon and Xing Yi style techs; max 5 enemies in Ambush (was 6)
7. refactor: Polish-notation renaming of the numerous encounters.py constants; Player inventory; get_p_info_verbose; fight.py optimization
8. feat: UI: got rid of show/write with delay; cleaner counter display; more info in the status menu (friends, enemies); simple inventory screen

---

### v0.3.8 "Exp and Stories" — 2014-03-26

1. **feat: exp bonuses: not a scratch, multi-knockout, strong enemy; exp bonuses stat; exp precalculated before a fight**
2. **feat: each story now focuses on just one player**; maximum level for stories; stories start more often
3. feat: monster in the dream story; Monster Kung-fu style; 'participated in stories' stat
4. feat: removed the 'master challenge' encounter, added the RenownedMaster story
5. feat: medicine as a reward from the shop owner (or pay for breakages); variable gambling bets; sparring now works only with computer players; master's various reactions to failures; new accomplishments (beggar/drunkard friend, beat thief, beat gambler, enemy repents)
6. **refactor: fight, sim_fight and spar are Fighter methods now, called throughout the code**; story saving/mechanics rework; register/unregister_fighter Game methods; text alignment function; autoplay launcher for testing; g.show/g.pak/g.msg redirect to Player methods; safer loading (missing stats filled with defaults)
7. feat: UI: rewrote story text (you -> name); aligned narrative text in encounters and stories; more compact statistics; some messages displayed with a small delay; no 'Round 1' display when human players don't participate

---

### v0.3.7 "Names and Styles" — 2014-03-21

1. **feat: names module; new styles module; styles are now classes** (hence the codename)
2. **feat: predefined styles to choose from at the beginning; standard styles have 3 emphases; style techniques (learned after passing all school challenges; some fighters have style techs, all masters do)**
3. feat: defense bonus possible when attacking or focusing; qi bonus possible when attacking; unblockable attacks
4. balance: Dirty Fighting and Police Kung-fu have only 1 bonus each; exp calculation takes the number of techs into account; evade tied to defense, critical chance to attack; lower exp for training
5. fix: advanced techs were not applied properly when upgrading; fighters' random techs did not apply! (found by chance)
6. refactor: removed the constants module; game roster (fighters_dict & fighters_list); optimized name collection; error reports have date and time; fight attributes and style bonuses no longer calculated every time
7. feat: UI: improved critical attack display; removed skip_next_pak; "Thugs/Robbers win"; style info and date in the stat report

---

### v0.3.6 "Tougher Opponents" — 2014-01-15

1. feat: new fight AIs: DeadlySimplisticFightAI 1-4 (checking for finishing blows, not defending when the enemy can't attack, not focusing with max qp); default AI = DeadlySimplisticAI2 (hence the codename)
2. fix: fight AI didn't really consider the opponent's available fight action — it used the previous turn's info
3. refactor: get_style_name Fighter method
4. feat[dev]: new optimized FightAITest class

---

### v0.3.5 "16 Techniques" — 2014-01-06

1. **feat: 16 new techniques: 18/36 Attack Forms, 18/36 Defense Forms, Lotus/Golden Lotus Stance, Horse-like Stamina/Strong as an Ox, Stinging Bee/Fist of Vengeance, Iron Fist/Cannon Fist, Iron Vest/Superior Iron Vest, Shadow Slips Away/Shadow of a Shadow** (hence the codename)
2. feat: critical attacks; evade attacks
3. feat: choose between 3 techniques (was 2); cooler names for some old techs
4. balance: fewer robbers in groups and crowds; max level for tournaments; defense doesn't cost qp when not attacked
5. refactor: fully rewrote the techniques module (much more general Tech class; techs stored with fighters as strings); Player.can_pay -> check_money; Fighter.check_lv; tech-related Fighter parameters
6. feat: UI: display enemies' weapons and stamina in group fights; changed counterattack display; skip next pak() on level up

---

### v0.3.4 "Balanced Fighting" — 2014-01-02

1. **feat: new fighting system with much better balance: counterattacks; defend costs stamina; focus restores stamina; qi not always lost when hit; no 'health' style emphasis; max qi is x2, not x3** (hence the codename)
2. feat: new fight AIs: BaseAI, SimpleAI, RockPaperScissorsAI, AdvRockPaperScissorsAI, SimplisticAI
3. feat: player is asked whether to use medicine; min player level for Beggar and Drunkard fights
4. fix: horrible bug in fight_ai_test (reverse mode didn't work); test_fight_balance bug (wrote 'focus' instead of 'qi')
5. refactor: Fighter.change_stamina; adjustable fighter parameters (atk_mult, dfs_mult, fcs_mult, ...) — item truncated in the source
6. feat[dev]: test_fight_balance (very useful)
7. feat: UI: slightly revamped fight UI

---

### v0.3.3 "Upgrade Your Kung-fu" — 2013-12-30

1. **feat: 'upgrade' a technique at level 10; new advanced techniques (upgraded versions of regular ones)** (hence the codename)
2. feat: new encounters: Brawler, PlayerMatch, MasterChallenge
3. feat: new stats: money gave to robbers, days inactive, times KOed, when became master
4. feat: AIPlayer is more efficient and can use the master's day actions
5. refactor: set_stat/check_help Player methods; tourn_or_not/brawl_or_not/p_match_or_not/accept_master_chall_or_not; get_act_players/get_random_style/get_new_style Game methods; optimized techniques module; fighter.techs is a set; got rid of almost all constants in the constants module

---

### v0.3.2 "Den'gi" — 2013-12-07

1. feat: gossipmonger encounter; medicine seller encounter (hence the codename — "money")
2. feat: choose a weapon when fighting armed challengers; new weapon: piece of cloth
3. feat: master gets 1/2 of the tuition fee for each student; new statistics: spent_on_training, fights_total
4. balance: drunkards and beggars encountered more rarely
5. fix: challenger fights without a weapon (pick_normal_weapon bug); Master Xue got reduplicated in a tournament (friend of two players)
6. refactor: new Player methods; new handling of player statistics; more efficient Fight.give_exp; clearer saving code and save files; better testing facilities (incl. emergency save); better stats report generation

---

### v0.3.1 "Strange Dreams" — 2013-11-30

1. **feat: Strange Dreams story** (hence the codename)
2. feat: sparrings are possible (no injuries)
3. feat: thief's success depends on the player's level
4. feat: experimental fight AI — initially logged as a failure, but that turned out to be a horrible bug in fight_ai_test; Experimental is actually slightly stronger than Default
5. fix: loading a game while playing no longer crashes the game
6. refactor: Fighter arming methods (arm_improv, arm_police, arm_robber); weapons module get_rnd_*_wp functions; DefaultFightAI class (fight AI is no longer a function); Fighter.is_armed/get_init_atts/pick_normal_weapon; copy_fighter; class-based fight_ai_test; player logs cleared on save/load; coop/ai_only/auto_save_on configuration options; is_weapon_tech; WeaponTech.if_applies_to_weapon

---

### v0.3.0 "Superbug, Victory, Stats" — 2013-11-10

1. **feat: 4 individual victory conditions — it is now actually possible to beat the game** ("Victory")
2. **fix: the horrible (nastiest ever?) bug with occasional infinite loops in sim fights, caused by incorrect binding of Player and fight AI** ("Superbug")
3. feat: the game can be played with AI players only (silently)
4. feat: thief/convict encounter chance depends on the town crime level; lower Extorters and HelpPolice chance
5. feat: accomplishments are more meaningful; 'win 5 tournaments' accomplishment; all players' statistics in one report ("Stats")
6. feat: AI chooses the lower of two attributes at level-up (more balanced builds)
7. refactor: statistics module; once again reorganized the fight/player/ai_player/human_player/fighter code; .show accepts multiple arguments; got rid of the get_full_pwr method (sometimes worked incorrectly)
8. feat: UI: much more informative logs

---

### v0.2.9 "Others" — 2013-11-05

1. **feat: AI players**
2. feat: fight-or-run choice when an enemy attacks; the player can get help when fighting extorters
3. balance: reputation gain from donations is relative to the donation size
4. refactor: HumanPlayer and AIPlayer classes (with composites) in their own modules; players' logs saved to separate files in the new save folder and loaded with the game; RealFight and SimFight subclasses of a new BaseFight class; fighter factory functions moved to a separate module; f.is_human -> f.is_player; constants moved out of constants.py
5. fix: Player methods were called instead of HumanPlayer methods (inheritance order issue); unexpected exp gains (turned out to be home training); partner didn't get half of the convict reward
6. feat: new Player methods (e.g. donate)
7. feat: UI: '<name> wins!' fight outcome; player logs; player first in the action display

---

### v0.2.8 "Classy Encounters" — 2013-09-21

1. **refactor: encounters are now classes (subclasses of the generic Enc class) with factory functions: Ambush, Beggar, Challenger, ContinueStory, Convict, Drunkard, Extorters, Gambler, MasterTrial, HelpPolice, Robbers, SchoolChallenge, Students, Thief** (hence the codename)
2. feat: gambler fights; new student challenges; ambush escape; see win chance for ambushes, helping police and extorters
3. balance: triple encounter chance when going for a walk; defense penalty when fighting several opponents
4. feat: slightly better anti-crowd AI; a bunch of new AI tests
5. fix: ai_test conflict with the fight's simulation mode; horrible ai_test bug (all allies in group fights got the default AI)
6. refactor: player.game hook; EncControl class; add_enemy/get_master Player methods; test_enemy Tester method
7. feat: UI: player character's name instead of 'you'

---

### v0.2.7 "Kung-Fu Classes" — 2013-09-15

1. **refactor: weapons are now Weapon class instances (new weapons module); techniques module with a Tech class and subclasses; game moved to a separate module; testing_tools module with a Tester class** (hence the codename)
2. feat: earn_reward method (and a new stat for total rewards earned)
3. feat: Thief encounter
4. feat: auto save
5. balance: convict reward multiplier decreased to 25; convict reward split with an ally; convict can be armed
6. feat: show the approximate win chance when encountering extorters
7. feat: UI: reordered practice/teach-students options; tournament winner announcement shows name, level and style ("Unknown (lv.10 Flying Elephant) wins the tournament"); gambler win message tweak

---

### v0.2.6 "Bug, Fun, Treasures" — 2013

1. **feat: National Treasures story** ("Treasures")
2. feat: the 'deadly' Flower Kung-fu style
3. feat: new encounters: police fighting thugs, racketeers ("Fun")
4. feat: accomplishments (like defeating the foreigner boss); randomized attack order (with ordered display); auto fight option in school challenges
5. balance: fairer exp distribution in group fights; style bonus limited to max 50% per emphasis (reached at level 10); stories develop more slowly; rarer convict, beggar and drunkard encounters and school challenges; decreased tournament prize; more noticeable changes in crime, poverty and interest in kung-fu
6. fix: state display raised an error when the player had no techniques; a fighter could get disarmed in simulation (fixed with fighter copies); challenger disarm bug at the beginning of a fight ("Bug")
7. refactor: delete the foreigner boss after the story; Player.get_fame(); story module functions to classes; more readable save files; attack/defend/focus are Fighter methods now; test_story/quick_exp/quick_money testing functions
8. feat: UI: more informative fight messages; enemy levels displayed when choosing a target in group fights

---

### v0.2.5 "Technical IOSMW" — 2013

("Technical In Oh So Many Ways", per the source file's first line)

1. **feat: weapon techniques (x7); learn a new technique every 3 levels (choose one of two, descriptions shown); Qi, Dragon and Warrior Breathing; Attack and Disarm / Defend and Disarm — actually work!**
2. feat: NPCs get random techs (persistent — saved properly); challengers have fixed levels and can be armed; chance to grab an improvised weapon when attacked by an armed robber; tournament skipped if no players participate
3. feat: new improvised weapon: hammer
4. balance: gamblers encountered less frequently; similar style emphasis pairs (qi+health vs health+qi) are avoided
5. fix: multiple weapon bonuses could apply; fighters weren't disarmed after fights; encounters on the day before full recovery; shifted fight UI lines
6. refactor: all modules except kung_fu moved into a subfolder; error messages redirected to errors.txt; game_loop split into state_menu/show_turn_info/inact_check; new Fighter methods (breathe, gain_hp, gain_qp); improved Fighter/Player inheritance
7. feat: UI: techniques shown in state; improved state display

---

### v0.2.4 "Sugar" — 2013

1. feat: UI: save/load/quit and player info in the 'State' submenu; detailed player info available in-game; style emphases displayed pre-fight (and at level-up only when needed); better fighters' info before tournaments; better fight messages
2. feat: to become a master, the player must complete a minimum of school challenges; no school challenges after 3; no tournaments if players aren't experienced enough; players' friends sometimes participate in tournaments; stories can't start until a player reaches TOURNAMENT_LV[0]
3. fix: injured players can no longer participate in tournaments
4. refactor: used names derived rather than saved; disarm moved into level_up; clearer fight code; calc_st_bonus/get_att_string/get_full_pwr are Fighter methods; get_fighters_info is a Player method

---

### v0.2.3 "First Story" — 2013

1. **feat: the first story — the foreigner; 4 foreign countries and styles, a few names** (hence the codename)
2. feat: no identical emphases when generating styles; escaped convicts are anonymous; new weapon: piece of rope
3. feat: UI: fight messages display HP after all attacks; the game pauses when you can't pay for something; pak() is 'silent' by default
4. fix: players are no longer occasionally greeted as masters during walks
5. feat[dev]: post_mortem debugging function
6. refactor: story module; __str__ for fighters/players (great for save_game); g.bosses dictionary

---

### v0.2.2 "Qi Machine" — 2013

1. refactor: chi -> qi, cp -> qp throughout (hence the codename)
2. feat: fight AI: attack an exhausted enemy only if some damage can be dealt; new AIs (ai_new2c/2d/2e/3a — 2d strongest but predictable and boring); DEFAULT_AI = ai_new2e
3. feat: possible injuries during training
4. balance: poverty-based encounters limited to 1 at a time
5. feat: UI: marker for maxed-out qi points; improved school-practice output; fighters' stats properly hidden before fights
6. fix: nasty bug in run_test3 (it was always ai_new3 vs ai_old!)
7. feat[dev]: run_test4 (500,000 fights); some new name parts

---

### v0.2.1 "Wuxia" — June 2013

1. **feat: weapons! Traditional (staff, sword etc.), improvised (broom, umbrella, chopsticks etc.), robber weapons and armed robbers; more exp for defeating armed fighters**
2. feat: improved fight mechanics: limit qi; select target; better display; enemy stats hidden before fights
3. feat: master joins some fights; school challenges; gambling reduces reputation; more realistic Chinese names
4. feat: better AI (ai_new2b); gang leader instead of robber 1; anonymous tournament participants (Participant A, B etc.); y/n menu changed to 1/2
5. refactor: reorganized fight and constants modules; improved robbers function; AI tests in a separate module

---

### v0.2.0 — 2013

1. feat: improved display of fighters' info
2. feat[dev]: fight AI test suite
3. feat: improved fight AI

---

### v0.1.x (2013) — the pre-changelog era

No changelogs were kept yet: v0.1.0 is a single-file-game snapshot with no
notes at all, and v0.1.1–v0.1.9 contain only `to do.txt` files — flat todo
lists with no done-marking. The entries below are **inferred** from items
disappearing between consecutive versions' todo lists (and from new files
appearing in the snapshots), so treat them as approximate.

### v0.1.9 — 2013

- (inferred) challenger friendship chance based on level and victory; thugs and robber groups nerfed to level 1; new-student encounter; gambler; conditional encounters

### v0.1.8 — 2013

- (inferred) money_earned statistic; tournaments; students

### v0.1.7 — 2013

- (inferred) friends join home training; town name; random events (`events.py` appears in this snapshot)

### v0.1.6 — 2013

- (inferred) full character info option (statistics, friends, enemies); character features (friendly/greedy, fast learner/hard worker); background features (rich/poor parents); events (crime/poverty/kung-fu rises and falls; enemies/friends grow stronger/weaker)

### v0.1.5 — 2013

- (inferred) style emphases factored in; can't join fights if injured; draws; statistics; exhaustion (to nerf attack)

### v0.1.4 — 2013

- (inferred) challenger looks tough or weak; fight() moved to the Fighter class (Player overloads it); load-game error fixed; beggar money tiers; auto-battle; beggar fights; drunkard; challenger; friends join fights
- (inferred) refactor: code split into modules (constants, encounters, fight, fighter, player, utilities)

### v0.1.3 — 2013

- (no completions detectable — this version's todo list is a strict superset of v0.1.2's)

### v0.1.2 — 2013

- (inferred) defense chi bonus limited and no longer increasing until the next turn; better fight AI; auto-battle reviewed; friends

### v0.1.1 — 2013

- (no change info — the first `to do.txt` appears here)

### v0.1.0 — 2013

- The earliest snapshot: a single-file game (`kung_fu.py` + `interface.py`), no notes kept
