# KFW Backlog

Consolidated from the old `docs/todo.md` and `docs/backlog.md` idea dumps.
Sections are ordered roughly by priority within each category; individual items
are unordered unless marked.

## Engineering (tech debt) — do these first

1. ~~**Automated tests.**~~ ✅ Done (initial suite): `test/` has seeded
   deterministic `AutoFight` tests, generation invariants, and a full headless
   autoplay game. Next: broaden coverage (saves, encounters, stories).
2. **Replace exec-based saves with JSON.** `kf_lib/game/_load_game.py` exec()s
   save files line by line, which freezes class names, `Fighter.__init__`
   argument order, and `savable_atts` forever — and is a security smell.
   Provide a one-time loader shim for old saves. Do after tests exist.
3. **Hygiene:** add `tqdm`/`numpy` to `requirements_dev.txt`; add
   `pyproject.toml` with black config; deduplicate the near-identical root
   scripts into one entry point with flags.
4. **Structural refactors:** split `kf_lib/happenings/encounters/__init__.py`
   (1353 lines); tease apart the 17-mixin `Fighter`; the `# todo` markers
   (e.g. replace `Challenger`/`Master`/`Thug` subclasses with an occupation
   attribute, `fighter/__init__.py`).
5. Smaller code items from the old backlog:
   - subclass `Fight` more (spectator/no spectator; exp/no exp; stats/no stats)
   - `.__repr__`/`.__str__` in all classes instead of `get_init_string()`
   - generic Saver component saving relevant atts
   - stats class/component; Event class
   - rewrite the ugly `get_prefight_info` Fighter method
   - normalize values in uneven prob distributions
   - generate important fighters considering style emphases
   - `BasePlayer.get_name_as_master`; clear personal log method
   - collective_name attribute in fighters, filled in `fighter_factory.py`
   - `add_numbers` utility function; fight approximation formula
   - time AI play (when there are no human players); look for bottlenecks

## Bugs / known issues

- **Game loading is broken** (found 2026-09, pinned by `test/test_save_load.py`):
  `LoadGame.load_game` exec()s save lines in function scope, so names bound by one
  line (`fsd`) don't persist to the next; also some AI classes (e.g. `LazyAIP`)
  aren't in the exec namespace → `NameError` on load. Save side works. Fix via a
  shared exec namespace, or properly via the JSON save migration (Engineering #2).
- double knockback!
- y defense buff not working?
- bug in careless inactive time?
- weapon techs don't do anything — reintroduce them
- fix style moves; "couldn't find any moves for move string 3,shocking;1,flying;2,flying"
- organize move list, remove unused moves
- weapons are OP? / remove weapon atk bonus
- wtf is STAMINA_FACTOR_BIAS in fighter.py?
- some upgradable techs shouldn't be upgradable
- `minigames/Chocolate_mini_game.py` is broken (has a todo)

## Fight mechanics

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
- qi rethink: shouldn't increase by default (maybe decrease unless focused);
  increase on successful defense/attack; modify qi_when_atk; lose qi when defend?
- reflexes: compute to_block and to_dodge differently
- better defense move that requires qi
- moves like 'overdrives' that require lots of qp
- series of strikes as one move?
- turn numbers — another tactical dimension
- penalize repeated actions more, for more interesting fights
- knockback against a wall (connected with environment use?)
- nerve blocking
- multishadow kick (attack several enemies at once)
- catch breath & others restore stamina relatively?
- pain resistance technique: immune to shock/stun and debilitating strikes
- techniques triggered on dodge/block/hit/fall
- impro weapons: break chance on each hit (techs that reduce it), grab a
  weapon (Move), grab improvised weapons during fights (secret tech,
  automatic), interact with environment (esp. unblockables)
- free-for-all fights
- in-fight stats (strikes thrown/landed, accuracy, moves used, damage dealt)

## Moves, styles, techniques, weapons

- upgrade moves from pathetic to ultimate; complex moves as upgrades/modifications
- more moves (higher tiers, handle tiers)
- use `|` in style move strings (e.g. `short-range,punch|kick`)
- moves for generated styles: "ferocious", "acrobatic", etc.
- generate new maneuvers (fast charging step etc.); fixed chance of maneuvers
  when choosing new move
- style's secret technique, learned at lv 10, unknown in advance
  (e.g. snake fist: Weishen / false body); another advanced tech at lv 15?
- style with head strikes (bull?); style move ideas: Rakshasa Palm, Bite,
  no-shadow headbutt, flying forehead, Shadowless Hand, Putting On Her Makeup,
  Pretty Girl Looks In Her Glass
- named opponents: Iron Bullet, Bamboo King & other weapon masters, Thunderleg
- boosts: to dict and auto-adjust; boost reducing move complexity (Air style
  tech); boost reducing fall damage; add straight/circular/shocking/stam_dam/
  mob_dam to boosts and techniques
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

## AI

- style-specific AI retraining pipeline
- more complex genetic fight AI: thresholds (focus when qp < x), group
  advantage, stamina weight, consider enemy dfs/criticals
- compute distance change by efficiency of strikes, not sheer number
- different fight AI behaviors: aggressive, defensive, cautious, sneaky, erratic
- different AIs for common fighters vs masters/bosses; difficulty levels via AI choice
- online learning?
- AI players: choose techniques to match style; target enemies wisely; buy
  Magic Healers more; use fight items more (they buy but don't use)
- generic AI player decision function: money, rep, risk, exp (stakes dict),
  sum of feature-weight products
- intelligent but non-deterministic move/tech selection; att selection
  depending on style perks
- subclass Fighter for different enemies (Robber, Thug etc. — collective
  names, styles — instead of ugly style.name)
- new AI players; simulating AI (when choosing upgrades/techs)

## Balance & analysis

- evolutionary algorithm for balancing boosts
- exp: all levels are 100 exp; calc win exp relative to difficulty (+bonuses);
  exponential exp?; reduce/rewrite trait exp bonuses; test exp bonuses, reweigh
- which traits result in winning more often?; trait-related stats
- compare styles in 1on1 and 1 vs 3 fights
- new AI testing routine: one vs big crowd
- move filtering with pandas, save as csv, collect useful stats
- a simple utility to count total moves, styles, techs, etc.

## Game systems & gameplay

- **Late game / own school** (was top of todo.md):
  - choose actual style techs (from what you know as a master)
  - students participate in tournaments (collect stats + new accomplishments?)
  - mega-tournament where all schools fight (all fighters or top 3 + masters)
  - encounters/stories about running your school, gaining recognition
  - quest to unite all schools → new victory type (kung-fu federation /
    association); reputation could influence creating it
- exp/levels: all levels 100 exp (see Balance)
- config file (not to choose every time); new game settings in a text file
- save winner fighters at end of game; fight players from past games
  (legendary/story?)
- custom player creation option
- join a school early in the game? beg the master?
- on defeating your master: become head of your school instead of opening a
  new one?; master retires?; create a new style?
- school life: really teach students (fewer of them, simulate structure);
  best student you can train; arguments between students; masters have an
  argument (students fight); school challenges only when you go to school /
  sequential challenges; more interactive school training (disobey master,
  practice aspects, injury risk); fight master when disobeying
- more life sim: tavern day action (get quests?); persuade/talk checks
  (trait-dependent); depression (after important loss, or small chance);
  values/tenets; debt collectors; rich boy (monthly allowance) / prodigy
  (starting level); learn medicine, help the sick; work: promotion, run your
  business?; choice: extra money but get tired; work encounters
- days → weeks; work and training automatic? or choose focus (two actions/week)
- remove tedious routines — work/training as resources, not events
- money victory: become governor?
- luck: increase evasion and critical chances?
- coach mode
- (earn) nicknames; make it possible to change names
- clear town of crime; gangs (join one?)
- players learn moves used against them (special attribute/traits, small
  chance by default)
- accumulate wisdom instead of random chance for personality change
- item bundles; other interesting ways to lose items
- always get reward for helping people?
- if negative money, don't start some encounters
- get help: check impro weapon and walk-ins separately; always get help
  against crowds?
- ambush: never feel too scared? run away (some fights; secret tech?)
- enemy becomes friend (story?) — "changed my ways"; challengers become
  friends more often?; when a friend challenges you, he becomes stronger
- tournament improvements: store upcoming Tournament, start 3 days later;
  split prize on draw; winners become selected fighters (another way to
  generate strong fighters); large tournaments (128 participants);
  spectate tournaments; underground tournaments; advanced tournaments with
  super fighters; all appropriate-level fighters can take part (even enemies)
- collect stats: most damage in one blow, biggest gambling loss/win, most
  drinking player; summarize the player's career, highlight interesting things
- accompl: Crime Fighter; 3 exp bonuses at a time → accomplishment?
- display hp as percentage/string?

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
- events: kung-fu festival
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
- display all player fighter atts in state menu (suboption?)
- generate player description in text (style, strong points, everything)
- game beginning text
- show accomplishments in options (dates and types already stored)
- common log for all players; get verbose fighter info
- add timer to fight screens?
