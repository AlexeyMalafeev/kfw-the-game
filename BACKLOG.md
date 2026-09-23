# KFW Backlog

Consolidated from the old `docs/todo.md` and `docs/backlog.md` idea dumps.
Items are ordered roughly by priority within each section (higher first).
Resolved entries were pruned 2026-09 — see `CHANGELOG.md` for what shipped.

## Engineering (tech debt)

1. **Broaden test coverage**: the initial suite (`test/`: seeded deterministic
   `AutoFight` tests, generation invariants, headless autoplay) is in place;
   next targets are saves, encounters, stories.
2. **Retire the legacy save loader** (`LoadGame._load_legacy`): while the
   exec()-based shim exists, class names, `Fighter.__init__` argument order,
   and `savable_atts` remain frozen. Drop it once old-save support is
   abandoned.
3. Smaller code items from the old backlog:
   - subclass `Fight` more (spectator/no spectator; exp/no exp; stats/no stats)
   - `.__repr__`/`.__str__` in all classes instead of `get_init_string()`
   - generic Saver component saving relevant atts
   - stats class/component; Event class
   - rewrite the ugly `get_prefight_info` (`fighting/fight/_helpers.py`)
   - normalize values in uneven prob distributions
   - generate important fighters considering style emphases
   - `BasePlayer.get_name_as_master`; clear personal log method
   - collective_name attribute in fighters, filled in `fighter_factory.py`
   - `add_numbers` utility function; fight approximation formula
   - time AI play (when there are no human players); look for bottlenecks
   - refactor accomplishments as dict {accomplishment: date} (inefficient now)

## Bugs / known issues

- **Explicitly address every remaining ⚠️ point across `docs/*.md`** (HIGH
  priority): the user confirmed only 2-3 of them are intended behavior, the
  rest are bugs. Go through them one by one, fix or document as intended.
  ~10 remain in `fight_mechanics.md` — environment_bonus = 0.0,
  dodge-checked-before-block, `do_mob_dam` naming, stun having no defense
  penalty, free counters, dead boosts/techs — plus ~50 more across
  encounters/gameplay/ai_players/items/kung_fu/minigames/stats/debug_menu/
  social_and_traits/text_content.
- weapon techs don't do anything — reintroduce them
- dead boosts: `GRAB_CH1/2`, `QI_WHEN_ATK`, `HP_MULT`, `epic_chance_mult`, all
  `WeaponTech`s; `TIME_UNIT_MULTIPLIER` unused
- trait selection iterates unsorted collections, so even with `random.seed()`
  the drawn traits vary with PYTHONHASHSEED across processes — a test-suite
  flakiness vector (bit us in `TestSmartAIPKnobs`; worked around with
  `traits_list=[]`). Consider sorting pools before sampling. Update
  2026-09-17: the analogous object-set sites in move/tech generation
  (`get_rand_moves`, `self.techs` iteration, tech selection pools) and the
  string-set tie-ordering in `compare_dicts` are fixed — the seeded
  fight-balance harness is now byte-reproducible across PYTHONHASHSEEDs;
  trait selection itself is still open.
- `TestJadeTableStory.test_completes_and_lose_branch_makes_enemy` is flaky
  across processes: with fixed `random.seed`s per run it still passes/fails
  depending on PYTHONHASHSEED (verified 2026-09-24: stable per hash seed,
  ~15–20% of seeds fail with `saw_win=False`). Some set-iteration site in
  game generation or the story/fight path is still hash-order dependent —
  same family as the trait-selection entry above.
- possible bug in exp progression in lazy/hardworking players
- y defense buff not working?
- bug in careless inactive time?
- fix style moves; "couldn't find any moves for move string 3,shocking;1,flying;2,flying"
- some upgradable techs shouldn't be upgradable
- double knockback! (note: v0.6.8 changelog claims "fix: double knockback (at
  last!)" — verify whether it regressed or the todo entry was stale)
- some dev scripts remain broken (details + per-script verdicts in
  `docs/dev_scripts.md`; the output-path, missing-dir, determinism and
  `count_lines.py` defects were fixed 2026-09):
  `try_rich.py` (`rich` not installed; abandoned experiment),
  `compare_AIPs.py` (stale import — `game.BaselineAIP` doesn't exist, the
  AIP classes live in `kf_lib/actors/player`),
  `collect_AIP_data.py` (per-game styles prompt — `new_game` called without
  `generated_styles=` → 100 interactive prompts; also persists nothing
  despite the name),
  `ML_learn.py` (input path `'../../ml/...'` resolves outside the repo)
- `minigames/Chocolate_mini_game.py` is broken — root-caused 2026-09
  (docs/minigames.md): stale import (`kf_lib.human_player` gone), scene
  tech/move names no longer in the data files, `learn_tech` now takes Tech
  objects. RING works (needs a TTY; run from `minigames/`).
- weapons are OP? / remove weapon atk bonus
- flower kung-fu has only weak and pathetic moves (intended?)
- organize move list, remove unused moves
- wtf is STAMINA_FACTOR_BIAS in fighter.py?

## Fight mechanics

- qi rethink: shouldn't increase by default (maybe decrease unless focused);
  increase on successful defense/attack; modify qi_when_atk; lose qi when defend?
- penalize repeated actions more, for more interesting fights
- rage: fixed chance (higher for thugs), taunts increase it; keep only
  step/rush forward and strikes. Some opponents enter fury spontaneously.
- fury: when hp low, increase atk_pwr & to_hit
- berserk-like state (gradually decrease HP, get attack bonus) — different
  from rage and fury
- drunken: actually get drunk and suffer penalties (complexity, fall damage);
  drunken boxers can buy wine; drink wine during fight?
- grappling state: grabs work like preemptive but different; depends on
  relative strength/agility; handle grappling differently from strikes
- stances: change tactics, always a trade-off except hidden ones (speed vs
  stamina, speed vs dfs, dfs vs atk, dfs vs mobility, preemptive vs dfs)
- stances/body parts?; off-balance when dodge; a miss → off-balance status;
  run-up (status?)
- counters; a special enemy (story?) that can only be defeated with counters
- more throws (close range), defensive throws; more trips/sweeps that knock
  the enemy down ("ездящая подсечка")
- more defense: grabs, counters, side-steps?, acrobatics?
- disarm opponent as a Move; disarm-and-snatch-weapon tech; grab enemy's
  weapon; supreme control — against disarming
- reflexes: compute to_block and to_dodge differently
- better defense move that requires qi
- moves like 'overdrives' that require lots of qp
- series of strikes as one move?
- turn numbers — another tactical dimension
- knockback against a wall (connected with environment use?)
- pain resistance technique: immune to shock/stun and debilitating strikes
- techniques triggered on dodge/block/hit/fall
- impro weapons: break chance on each hit (techs that reduce it), grab a
  weapon (Move), grab improvised weapons during fights (secret tech,
  automatic), interact with environment (esp. unblockables)
- nerve blocking
- multishadow kick (attack several enemies at once)
- catch breath & others restore stamina relatively?
- yell (as a move function?)
- tests of strength/speed/health/agility in encounters and stories — new
  mechanics beyond fighting

## Moves, styles, techniques, weapons

- more moves (higher tiers, handle tiers); upgrade moves from pathetic to
  ultimate; complex moves as upgrades/modifications
- boosts: to dict and auto-adjust; boost reducing move complexity (Air style
  tech); boost reducing fall damage; add straight/circular/shocking/stam_dam/
  mob_dam to boosts and techniques
- use `|` in style move strings (e.g. `short-range,punch|kick`)
- moves for generated styles: "ferocious", "acrobatic", etc.
- generate new maneuvers (fast charging step etc.); fixed chance of maneuvers
  when choosing new move
- another advanced tech at lv 15? (secret tech at lv 7 and one style-tech
  upgrade at lv 10 shipped 2026-09)
- style with head strikes (bull?); style move ideas: Rakshasa Palm, Bite,
  no-shadow headbutt, flying forehead, Shadowless Hand, Putting On Her Makeup,
  Pretty Girl Looks In Her Glass
- named opponents: Iron Bullet, Bamboo King & other weapon masters, Thunderleg
- tech ideas: Light Body (cheaper jumps, less fall damage); knockback/stun/
  shock resistance; powerful attack when hp < 10%; stronger attacks when low
  on hp (Sekibayashi Jun); analyze (atk/dfs vs same opponent improve);
  predict opponent's actions; coordinated attacks (bonus with allies);
  Deep Focus; damage opponent's qi; breathe: health↔qi conversion; weapon
  techs (sacrifice dfs for atk, all-weapons attack/defense); Invisible Armor
  (dam reduc); special techs not normally available (hp recovery, qi fountain)
- technique names: Eight Methods, Eight Trigrams Palm, Ultimate Supreme Fist,
  five fists of sth, eight drunken fairies, Five Explosive Fists
- unique techs named after the player; fav_strikes in techs
- weapons: chain hammer, Iron Gauntlet/Fist, Iron Claws, meat weapon, hidden
  weapon 'flying guillotine', evil weapons, more impro weapons
- styles: add Hapkido, Jeet Kune Do; style moves for non-playable styles
  (Muay Thai etc.) + emphases; learn several styles and switch before/in
  fights?; create new style with extra bonus at lv 20 (or 15)
- butt strike, hip strike — handle specially
- learn weak/pathetic moves from books?; improve a move with books
- in-fight nunchaku tech (like impro weapons)
- momentum style/techs — use own and opponent's momentum, like Judo
- strong-against-stronger / strong-against-weaker techs (intimidating,
  fearless, Giant Killer)
- more strike types (see `docs/strike notes.txt`)

## AI

- different fight AI behaviors: aggressive, defensive, cautious, sneaky, erratic
- different AIs for common fighters vs masters/bosses; difficulty levels via AI choice
- style-specific AI retraining pipeline
- more complex genetic fight AI: thresholds (focus when qp < x), group
  advantage, stamina weight, consider enemy dfs/criticals
- fight AI rule: hurry and finish off knocked-down opponents
- compute distance change by efficiency of strikes, not sheer number
- AI players: choose techniques to match style; target enemies wisely; buy
  Magic Healers more
- generic AI player decision function: money, rep, risk, exp (stakes dict),
  sum of feature-weight products
- intelligent but non-deterministic move/tech selection; att selection
  depending on style perks
- subclass Fighter for different enemies (Robber, Thug etc. — collective
  names, styles — instead of ugly style.name)
- new AI players; simulating AI (when choosing upgrades/techs)
- online learning?

## Balance & analysis

**Snapshot 2026-09** (`tests/test f.b. rand.act.=False n=10000.txt`; refreshed
2026-09-17 with the now-**seeded** harness, `seed=42` — the report is
byte-reproducible, so future diffs against this file reflect real balance
changes, not run noise; Diff% = winner-vs-loser correlation):
- **Offense wins mirror matches; all defense-oriented buffs correlate with
  losing**: agility +16.8, strength +12.4, guard-while-atk +9.0, attack +8.8,
  punches +8.6 win; close-range −14.0, defense −13.3, counters −11.2,
  unblock. −7.4 (n ≈ 1400), guard −7.3, blocks −6.1 lose. Blocking well
  doesn't deal damage.
- **'Lightning-Fast Strikes' after its no-op fix: +29.8** — top of techs 2,
  directionally consistent with the tech now actually working, but n = 57,
  so within noise; keep watching. (Unseeded runs had it anywhere from
  −13.5 to +2.6.)
- **The AI attribute-growth fix is NOT exercised by this harness**:
  `test_fight_balance` uses `new_fighter()` = `rand_atts_mode=0`, so the
  restored mode-1/2 specialization has no effect here. Its balance impact is
  unmeasured — needs a dedicated test (e.g. mode-1/2 mirror matches).
- Range/mobility hierarchy holds: flying +8.8, dist4 +6.3 win; vanishing
  −6.0, ultra short −3.1 lose; lethal −1.4 (n ≈ 1600) and power −1.3 sit at
  neutral — earlier swings (lethal +3.5→−4.8) were unseeded-harness noise.
- Bottom techs: 18 Defense Forms −12.8 (techs 1, n = 546), Retaliative Blows
  −12.6; grappling buff −12.2 (n = 376) persists in the seeded run, so it's
  probably real, not noise. Techs 2 have n ≈ 50–85 each, so even seeded
  their ±20–30 spreads (Advanced Blood Strikes −22.6, Hero's Resilience
  −25.6) are largely small-sample noise.
- **Resolved — the harness is seeded and deterministic**: earlier run-to-run
  drift of ±5–8 Diff% points came from unseeded style generation plus
  PYTHONHASHSEED-dependent iteration of id-hashed object sets in fighter
  generation (`get_rand_moves`' move pool, `self.techs`) and of the string
  set in `compare_dicts` (tie ordering); fixed 2026-09-17, same `seed=42`
  now gives byte-identical reports across processes.

- exp: all levels are 100 exp; calc win exp relative to difficulty (+bonuses);
  exponential exp?; reduce/rewrite trait exp bonuses; test exp bonuses, reweigh
- speed up early progress / slow down late progress (progressive exp step)
- evolutionary algorithm for balancing boosts
- which traits result in winning more often?; trait-related stats
- compare styles in 1on1 and 1 vs 3 fights
- new AI testing routine: one vs big crowd
- compute crowd exp worth differently? — group-FFA exp/risk addressed in
  v0.7.3 (RMS of per-group sums, `BaseGroupFreeForAll.aggregate_exp_yield`);
  plain FFA deliberately keeps the per-capita average
- further reduce dist3/dist2 bonuses?
- nerf guard while attacking
- buff attribute-based damage for strikes
- come back to experiments with level significance
- move filtering with pandas, save as csv, collect useful stats
- a simple utility to count total moves, styles, techs, etc.

## Game systems & gameplay

- **Refine game victory balance**: review the victory conditions (incl. the
  new 'Uniter of Schools') for relative difficulty, pacing and how long a
  typical winning run takes
- config file (not to choose every time); new game settings in a text file —
  partially addressed 2026-09 by the new-game settings menu (level
  progression, crime, poverty, kung-fu enthusiasm), but there is still no
  persistent config file
- **mod support**: world parameters (crime rate, kung-fu prevalence, etc.)
  fixed at their current defaults, but overridable by mods the player picks
  at the start of a new game via a new "advanced settings" menu (builds on
  the config-file idea above and the v0.7.2 settings menu; defines a mod =
  named bundle of stat/constant overrides)
- custom player creation option
- **Romance system** (added 2026-09): shipped 2026-09 in two batches — meeting
  a gendered love-interest NPC (NewRomance encounter), courtship via dates and
  the Visit-sweetheart day action, marriage (spouse as fight ally via a
  check_help channel, small daily household income); jealous-rival duels
  (defeated rivals can become persistent enemies, losing can end the
  courtship), the KidnappedSweetheartStory quest line, and family/children
  (births, small expenses, kung-fu practice with a grown child, family
  mentioned in the ending biography). Remaining ideas: deeper legacy content
  (children as full fighters / school students, playing as the heir).
- remove tedious routines — work/training as resources, not events
- days → weeks; work and training automatic? or choose focus (two actions/week)
- school life: really teach students (fewer of them, simulate structure);
  best student you can train; arguments between students; masters have an
  argument (students fight); school challenges only when you go to school /
  sequential challenges; more interactive school training (disobey master,
  practice aspects, injury risk); fight master when disobeying
- on defeating your master: become head of your school instead of opening a
  new one?; master retires?; create a new style?
- join a school early in the game? beg the master?
- more life sim: tavern day action (get quests?); persuade/talk checks
  (trait-dependent); depression (after important loss, or small chance);
  values/tenets; debt collectors; rich boy (monthly allowance) / prodigy
  (starting level); learn medicine, help the sick; work: promotion, run your
  business?; choice: extra money but get tired; work encounters
- save winner fighters at end of game; fight players from past games
  (legendary/story?)
- money victory: become governor?
- clear town of crime; gangs (join one?)
- players learn moves used against them (special attribute/traits, small
  chance by default)
- accumulate wisdom instead of random chance for personality change
- enemy becomes friend (story?) — "changed my ways"; challengers become
  friends more often?; when a friend challenges you, he becomes stronger
- tournament improvements: store upcoming Tournament, start 3 days later;
  split prize on draw; winners become selected fighters (another way to
  generate strong fighters); large tournaments (128 participants);
  spectate tournaments; underground tournaments; advanced tournaments with
  super fighters; all appropriate-level fighters can take part (even enemies)
- exp/levels: all levels 100 exp (see Balance)
- coach mode
- luck: increase evasion and critical chances?
- (earn) nicknames; make it possible to change names
- collect stats: biggest gambling loss/win, most drinking player; summarize
  the player's career, highlight interesting things ('Max single blow' and
  'Most feared move' shipped in v0.7.2)
- item bundles; other interesting ways to lose items
- always get reward for helping people?
- if negative money, don't start some encounters
- get help: check impro weapon and walk-ins separately; always get help
  against crowds?
- ambush: never feel too scared? run away (some fights; secret tech?)
- accompl: Crime Fighter; 3 exp bonuses at a time → accomplishment?
- display hp as percentage/string?
- donate to friends / to charity

## Content: encounters, events, stories

- encounters: sect members (attack or ignore; sects fighting each other);
  market troublemakers (items as reward); help people more / protect
  townspeople; tavern owner's daughter; troublemaker (flower kung-fu but can
  be strong); wandering master, sometimes a fraud (pay → exp or tech);
  old man?; school rivals attack you; tavern trouble (losers pay for
  breakages); foreign devils (moral standards); out-of-towners; a large gang
  of robbers attacks Foshan; strong robber + accomplishment; criminal
  protected by thugs; more rare things (suddenly a very strong robber);
  unique encounters per location (school, walk, etc.)
- stories: righteous sect vs evil sect, triads; thugs burn down school;
  arrest gang leader to prove innocence; school attacked; 10 masters from the
  North; powerful item; style stories (drunken, Wong Fei-Hung master of fan);
  school bullying; do master a favour; lose fight on purpose; begging master
  to teach you; strong old man protects you from robbers; challenge a REALLY
  strong opponent who later teaches you; wins out of three matches; dirty
  money; showdown: all masters and players vs huge crowd (epic fight);
  Master Disappears; ginseng; major international tournament; girl kidnapped
  by bandits (bring money to the fish market); criminal syndicate; lost
  manuscript; rival schools; family trouble; master turns evil; betrayal;
  archenemy; Shaolin wooden fighters; Shaolin gets destroyed?; stolen
  mannequin?; seven Japanese masters; martial arts spirit/world
- better story rewards: lots of rep/exp/money, special techs/items, remove
  character flaw, special friend, move, 100 magic healers
- societies: bandits, sects (Righteous, White Lotus)
- events: kung-fu festival
- school practice encounter: improve a move
- mind training — fight enemies in your mind; time travel item; secrets of
  kung-fu book
- mine more quotes; use phrases from unused files (friends, never repay);
  trait-based quotes?; style lines spoken when attacking
- more ASCII art + better name↔art matching; stance ASCII per style (helps
  the punching bag idea); waves (ASCII); align ASCII in the middle
- add Thai names
- increase Wiseman trait chance; temp traits after talking to wise man?

## Traits

- observant: see fighters' atk/dfs/fcs; observe opponent selectively, with ??
- gullible (easy to fool; plot twists, lured into traps) — vs careless?
- honest / unscrupulous; prone to depression?
- knowledge of medicine: recovery time -1 day (min 1); fast/slow recovery
- analysis skill

## Minigames & far-future mods

- punching bag: max damage in limited time; other fight minigames
  (evade/block as many attacks as possible)
- RING: score (for exp bonuses); kumite mini-game; tournament betting with
  non-kung-fu styles
- Location class (street, mall, home…) affecting impro weapons; rain → slip
- PyGame?; fighting game mod; fighting game generator (make roster);
  SSS / Tekken / Streets of Rage mods; Jackie Chan mod
- merge with School World! (fight classmates, relationships)

## UI / UX

- use a custom console (colors at least); revisit the abandoned rich stub
- game beginning text
- generate player description in text (style, strong points, everything)
- display all player fighter atts in state menu (suboption?)
- common log for all players; get verbose fighter info
- add timer to fight screens?
