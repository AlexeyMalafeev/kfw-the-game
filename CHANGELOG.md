# Changelog

All notable changes to KFW are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); releases have codenames
because kung-fu movies.

## [Unreleased]

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
- **New games always use randomly generated styles for now** (`kfw.py` forces
  `generated_styles=True`, interactive path included): 6 handcrafted style
  move strings are broken and silently degrade to random picks (Hung Ga lv8,
  Wing Chun lv2, White Crane lv6, Xing Yi lv2/4/8). ~~Revert once the strings
  are fixed~~ — fixed within the same release cycle (see Fixed); the startup
  "Randomly generated styles?" prompt is restored

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

## Historical releases (migrated from docs/version_history.md)

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

Reconstructed from the `! development.txt` changelog file in git history (the
old `docs/version_history.md` only went back to v0.6.1).

1. **feat: ability to observe what AI players do during their turns** (hence the codename)
2. **feat: machine learning-based prediction of fight outcomes, 90-91% accurate (LR, RF)**; the trained LR model's intercept and coefficients are usable without any heavy dependencies (`ml_fighter_pwr.py`)
3. feat: `utilities.multiply(numbers)`, `experience.extract_features(side_a, side_b)`
4. feat: style moves: Backfist (karate); default moves for some foreign styles
5. feat: generated throws (15789 -> 15803 moves)
6. feat: new style: Capoeira
7. feat: a handful of Thai and Brazilian names
8. feat: don't add random moves to choose from if there is at least one style string-based move -> more distinct styles
9. feat: always try to learn a move with a bonus
10. fix: evil crash in spectating fights
11. fix: style generation used the same subset of strings
12. fix: bug in learning new moves at level 10+
13. feat[dev]: `_run_test_lv_vs_crowd.py` shortcut, `tests` folder, improved `Tester.test_level_vs_crowds`

---

### v0.5.9 "Thousands of Styles" — 2020-05-11

The first version covered by the git repo (initial commit 2020-04-19 was an
upload of the project mid-cycle); reconstructed from `! development.txt`.

1. **feat: style generation**
2. feat: new fight AI `GeneticAIAggro`, good at both 1-on-1 and crowd-vs-crowd fights (internal rankings at the time: GeneticAIAggro 7629, GeneticAIExtraRules4 6870, GeneticAITrainedParams8 6795, WeightedActionsAI 6206, BaseAI 862)
3. feat: player confirms whether the randomly generated fighter is ok in RING
4. feat: successful blocks and dodges increase qp
5. feat: foreign styles have appropriate strikes and techs
6. balance: nerfed weapons; reduced exp multiplier for weapons
7. feat: moves: Charging and Onslaught elbow, claw and knee moves now possible (13803 -> 16125 moves)
8. feat: move generation constraints: 'surprise', 'shocking' and 'debilitating' don't overlap in one move (16125 -> 16041); x-based damage functions don't overlap (16041 -> 15789)
9. refactor: techniques.py, moves.py; removed `move_gen.modified_move` and `RING_debug.py`
10. feat: Unix support — the game is playable, although with small UI issues
11. fix: properly linked ASCII for weapon moves
12. fix: don't get the same move more than once when leveling up
13. fix: fight items are now canceled after exp earned is calculated
14. fix: exp bonuses are now properly recorded in statistics
15. feat: UI: move tier displayed in some situations; ASCII for all weapon moves; more ASCII art for old moves; more concise messages in fights
16. feat[dev]: reworked test level significance

---

### Pre-git era (2016–2020)

These releases predate the repository (the first git commit is 2020-04-19,
already mid-v0.5.9), so only versions, codenames and dates survive, from the
author's records. Note the codenames of v0.5.6/v0.5.7 — the v0.7.0 "comeback"
theme has a precedent:

- v0.5.0 "Another New System" — 2016-05-18
- v0.5.1 "Move with Style" — 2016-06-26
- v0.5.2 "Chatty" — 2016-07-22
- v0.5.3 "ASCII-fu" — 2016-08-11
- v0.5.4 "Epic Fights" — 2016-11-16 (re-released later with small changes)
- v0.5.5 "No-Shadow Kick" — 2017-05-09 (re-released later with small changes and bug fixes)
- v0.5.6 "2.5 Years Later" — 2020-01-07
- v0.5.7 "It's Alive" — 2020-01-10
- v0.5.8 "13.8K Moves and a Genetic Fight AI" — 2020-02-07
