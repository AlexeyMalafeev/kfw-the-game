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

Three lists: confirmed bugs (fix them), unverified reports (reproduce or rule
out first), and the index of ⚠️ points in `docs/*.md`. Fixed entries move to
`CHANGELOG.md` and are pruned from here.

### Confirmed bugs

- `minigames/Chocolate_mini_game.py` is broken — root-caused 2026-09
  (docs/minigames.md): stale import (`kf_lib.human_player` gone), scene
  tech/move names no longer in the data files, `learn_tech` now takes Tech
  objects. RING works (needs a TTY; run from `minigames/`).
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

### Unverified reports

Old notes nobody has reproduced recently — some may be stale. Check them
against the current code first, then fix, or delete the entry if it no
longer applies.

- possible bug in exp progression in lazy/hardworking players
- bug in careless inactive time?
- fix style moves; "couldn't find any moves for move string 3,shocking;1,flying;2,flying"
- some upgradable techs shouldn't be upgradable
- double knockback! (note: v0.6.8 changelog claims "fix: double knockback (at
  last!)" — verify whether it regressed or the todo entry was stale)
- from the old `docs/known bugs.txt` (migrated 2026-10-20; its notes that
  were already fixed or tracked elsewhere were dropped):
  - a tier-1 move offered at level 20
  - exp bonuses don't seem to work / don't register in the statistics
    (gossip)
  - shock and similar statuses: reschedule the fighter's turn immediately
  - exp miscalculated in fights with weapons
  - Bagua Zhang gets little exp from improvised weapons
  - Fat Girl encounter: no help from friends
  - six moves to choose from at level 10 — why?
  - multiple attempts for defeating beggars? (more a design question)

### Open balance / design questions

- weapons are OP? / remove weapon atk bonus
- flower kung-fu has only weak and pathetic moves (intended?)

### ⚠️ points in the docs

`docs/*.md` mark suspicious behavior with ⚠️. Every point was re-verified
against the code on 2026-10-19, and the actionable ones were resolved in
three batches, each item decided by the author: (a) player-visible bugs,
(a′) latent defects and (b) balance-affecting fight mechanics (2026-10-19/20;
fixes in `CHANGELOG.md`). Points confirmed as intended — e.g. negative money
as debt, WiseMan's unfiltered trait draw, Criminal's full rep — are now
documented as such; the unused boosts and weapon-tech placeholders became
the "Techs for the placeholder boosts" and "Weapon techs" items under Moves,
styles, techniques, weapons. The 52 that remain, by doc → pointer:

- **(c) Design questions — probably intended, per the author, 2026-10-19
  ("mostly they are features, not bugs"); to be revisited later.** Not bugs
  and not part of the fix batches. The ⚠️ markers stay, because no single
  point is confirmed intended yet:
  - `gameplay.md` + `encounters.md` Town stats — crime never rises
    (`CRIME_INCREASE_MONTHLY = 0.00`); `poverty`/`kung_fu` never change;
    `g.kung_fu` is read nowhere though the new-game menu asks for it
  - `gameplay.md` Reputation — doesn't feed student attraction (`get_fame`)
  - `gameplay.md` Progression — per-level cost is a flat 100 exp despite
    the `× level` formula
  - `gameplay.md` Economy — prize-fighting stage 1 pays 25 < 50 fee;
    gambling is a dominated option (EV 0, −rep, revenge risk)
  - `gameplay.md` Day actions — `WORK_ENCS` is empty; `fight_dummy` is
    commented out of the menu
  - `items.md` — merchant price ignores the item (basic vs Super herb); one
    Ginseng Root cures any injury length; mock items invisible to
    `get_items` (can't be stolen/lost)
  - `kung_fu.md` Weapons — no durability/breaking
  - `social_and_traits.md` — `check_help` picks one channel with no
    fallback; `check_partners` (friends joining training) never called
  - `stats.md` — no trait modifies the luck roll; the Gossip encounter
    shows the full stats table instead of rumors
  - `encounters.md` — `enc_count_dict` is write-only (show it or drop it)
  - `text_content.md` Quotes — the default `'fighter'` occupation has no
    quote pool (generic NPCs are silent)
  - `minigames.md` Chocolate — 4 stale-API points: revive or retire (see
    the Chocolate entry under Confirmed bugs)
- **(d) Informational / intended / harmless:**
  - `kung_fu.md` — tier 12–14 moves unreachable (author: reserved);
    `Move.descr_short` dead; move_gen CSV name lookup and collision-chain
    composition; unknown move-string literals degrade silently
    (test-guarded); tuple move strings work only at level 1
  - `ui.md` — ASCII art frames must stay uncolored
  - `dev_scripts.md` — chdir-before-body path gotcha (`ML_learn.py` still
    hit — see the dev scripts entry)
  - `fight_mechanics.md` — `TIME_UNIT_MULTIPLIER` unused;
    `DRAW_EXP_DIVISOR` duplicated, `LOSER_EXP_DIVISOR` unused; `do_mob_dam`
    only slows (name)
  - `encounters.md` — the `check_if_happens` parameter shadows the method;
    StreetPerformer's `p.disarm()` on decline is a harmless no-op (players
    are never armed outside fights). It's a leftover from 2020; keep it or
    remove it (author to decide)
  - `social_and_traits.md` — `'cowardly'` checked by name in
    `check_scary_fight`
  - `stats.md` — unused NPC `change_stat` shim; `set_stat`/`write_stat`
    duplicates; `money_robbed`/`stolen_from`, `exp_bonuses`,
    `handle_gossip` naming; parallel accomplishment lists (Engineering 3);
    bios ignore stats/accomplishments/gossip
  - `text_content.md` — `MISC` dead; only `Thug 1`/`Robber 1` get group
    names; unused name constants; terminal `'Flying'` art branch (3 moves
    on Stance); `concat` correct only at `BUFFER_WIDTH = 1`
  - `minigames.md` RING — `from_exp_worth` retry loop unbounded; `play`
    flag never cleared

## Fight mechanics

- **Coarse fight clock** (found 2026-10-23): `get_move_time_cost` rounds
  `time_cost / speed` to whole time units — 36–70 / speed 4–9 gives 4–18
  units, so rounding moves a single action's time by up to ±10% and some
  moves cost the same at speed 8 and 9. Unbiased on average (no balance
  effect measured), but any tempo rule that shortens actions further makes
  it worse; then consider finer units (×10 on move time costs, status
  durations and `TIME_TO_SEC_DIVISOR` together)
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
- stances/body parts?; run-up (status?) (a fumbled move and, since
  2026-10, a fully dodged/blocked strike already leave the attacker
  off-balance)
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
- make status attacks (stun, shock, …) level-dependent

## Moves, styles, techniques, weapons

- **Techs for the placeholder boosts** (HIGH priority, author 2026-10-20).
  These boost constants exist but no tech uses them, and two of them need a
  new combat mechanic before any tech can do something:
  - **Grab chance** (`GRAB_CH1` 0.2 / `GRAB_CH2` 0.4): fighters have no
    `grab_chance` attribute and combat has no grab action — grappling today
    is only a move feature ('grappling' moves, `grappling_strike_mult`).
    Design first: what a successful grab does (e.g. the target can't dodge
    the next strike, or it sets up a throw), when it's attempted (a chance on
    close-range strikes, or a move of its own), and how the target escapes
    (a strength/agility contest?). Then a regular/advanced tech pair raising
    `grab_chance`. Related: "grappling state" under Fight mechanics.
  - **Qi when attacking** (`QI_WHEN_ATK` 0.5): no `qi_when_atk` attribute and
    no rule yet. Design: how much qi an attack yields (a share of `qp_gain`?
    only on a hit, or on any attempt?). Decide together with "qi rethink"
    under Fight mechanics, since both change how qi flows in a fight.
  - **Epic chance** (`epic_chance_mult`, no boost constant yet): the hook
    already works in the epic-chance formula, so only the tech itself is
    missing (the code comment suggests a secret tech) — the quickest one.
- **Weapon techs** (feature): the 7 `WeaponTech` placeholders (Strange But
  Deadly, Weapons Competence, Butterfly Swords, Sky Saber, Lightning Spear,
  Thunder Staff, Star Sword) carry no bonus and no fighter ever gets one.
  Needs: what each gives (an atk/dfs bonus for a weapon type — `wp_type` /
  `wp_bonus` are already there), who learns them (weapon-style masters?
  stories? a weapon-practice action?), and combat actually reading
  `weapon_bonus` (nothing does today).
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
- more strike types — new move-name words for `dev_scripts/move_gen.py`
  (ideas from the old `docs/strike notes.txt`; the words already in use
  live in `move_gen.py`):
  - effect ideas: Bull (the more HP, the more damage — or a tech?); Rage
    (the less HP, the more damage — or a tech?); Sacrifice (spend own HP);
    Reckless (lower own defense? lower accuracy? dist_change −2?); Precise
    strikes with an increased critical chance; Overhand (unblockable?);
    unbalancing; All-Rounder (strength + speed + agility based damage);
    drain or damage the enemy's qi; weaken the enemy (vital points, pressure
    points, nerve-blocking); Tackle as a special move with derivatives
    (Takedown, Throw, Trip and Sweep moves already exist); grab, lock and
    hold wrestling moves (wrestling = strength & agility; see also the
    grab-chance item above); more moves with level-based damage
    (`do_level_based_dam`, used by 1 move so far)
  - unused name words: Aggressive, Astral, Brutal, Crashing, Crushing,
    Crazy, Insane, Crappy, Weak (etc.), Deceptive, Diamond, Dirty, Divine,
    Explosive, Extravagant, Fierce, Gold, Hard, Heavenly, Platinum, Shadow,
    Silver, Sudden, Uncanny, Weird
- when choosing new moves, always offer at least some that the fighter's
  techs give a bonus to (the `*` moves)
- organize the move list, remove unused moves

## AI

- **Retrain the genetic fight AI's weights** (`kf_lib/ai/fight_ai_gen.py`;
  author 2026-10-22, action item once the 2026-10 balance pass is polished):
  `prob_atk` / `prob_guard` / `prob_focus` … were tuned for the old rules, and
  the AI now spends ~25% of its turns on Guard. Retrain after the defense
  rework, the Guard/counter/qi/health follow-ups and the final
  `run_test_fb.py` re-run, then re-run the harness once more
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
- fight AI: step forward when ahead, or at distance 4 when the opponent has
  a range-4 attack; step forward more when its group outnumbers the enemy

## Balance & analysis

**Pending final `run_test_fb.py` re-run** — the defense rework of
2026-10-20 (the 'defense' buff works, block techs raise block chance,
guard-while-attacking nerfed, a full defense leaves the attacker briefly
off-balance, block power 20 → 12; values set by A/B modeling against the
median general tech) is balance-affecting. An interim 100k run against
`tests/test f.b. rand.act.=False n=100000.txt` (the same code before the
rework, first report of the 100k harness): defense −12.7 → −1.3, guard
while atk +15.5 → −1.2, blocks −12.0 → −4.1, full blocks 81% → 43% of
blocks, fights 59.7 → 57.1 s; guard (−12), counters (−12) and qi (−7.5)
still lose. Re-run and refresh the snapshot once the author's follow-ups
below are decided:
- **Defense rework follow-ups** (author 2026-10-20/22). Done 2026-10-22:
  the 'dodge' buff raises dodge chance only (`EVADE1/2` 0.4/0.8 → 0.7/1.4,
  modeled); qi regeneration 20% → 10% of max per turn (qi buff −7.5 → −3.6,
  Lotus Stance A/B +6.9 → +10.4). Done 2026-10-23: health and speed —
  setup D + linear tempo adopted (see the Health and Speed items and
  CHANGELOG). **Guard, counters, qi: tested 2026-10-22 as rule variants,
  author to decide** (`dev_scripts/testing/rule_variants.py`, full tables in
  `tests/balance experiments 2026-10-22.txt`; baseline fights 62.7 s, +27%
  vs 49.5 s before the ⚠️ batches). Then implement the chosen ones in the
  engine (docs, tests, i18n), drop them from `rule_variants.py`, and run the
  final re-run:
  - **Guard**: the AI guards only when it can't attack, and 92% of Guard
    turns receive no strike, so a stronger Guard (×2.0) or Guard doubling
    counter chance changes nothing. Guard also recovering 10 stamina + 10
    qi (× guard bonus) makes fights 62.7 → 53.9 s and Guard turns 29% → 21%,
    but guard techs stay dead; a stored guard (the bonus waits for the next
    incoming strike) lifts the guard buff −11.8 → −8.2. Untested: stored
    guard + ×2.0; guarding chosen by the AI with guard techs in mind
  - **Counters**: best-move counters, partial-block counters for counter
    techs, free counters — no effect; free counters + counter techs ×3:
    counters buff −12.5 → −8.5. The limit is frequency (~0.3 counters per
    fighter per fight). Untested: counter techs ×5–10 with free or
    half-price counters
  - **Qi** (qi techs only): qi shield (a partial block spends qi to absorb
    the rest) −3.6 → −1.1; qi-charged strikes at +10% → +3.0, with the
    shield +7.2 (at +30%: +16.9, too strong)
  - **Health — adopted 2026-10-23** (setup D: 40 HP per health point, 20%
    of toughness and 30% of stamina from health, block power from health;
    with the Speed item's linear tempo the four attributes end within ±0.6,
    gap 4.0 → 0.9). Left over: health is a bit strong at levels 1–7 (+1.3)
    and weak at 15–20 (−1.3); HP gain techs +12.2 → ~+5 and fury +8.0 → ~+5
    after the HP cut. History of the tests: block power from (strength + health) / 2: −2.0 → −1.7
    (negligible); 25% of toughness and stamina from health: health → +0.2
    (neutral), fights +2 s, but the 'health' techs +3.4 → +11.8 and speed
    −1.9 → −2.7; 100% from health: +5.8 (too strong). Speed is the next
    weakest attribute. Also tested: 20 HP per health point instead of 50.
    Alone it leaves health at −1.8 (HP stays proportional to health, so
    the HP ratio of two fighters is the same) but fights get 3× shorter
    (62.7 → 20–22 s, 3–4 strikes, a stun every ~2.5 strikes), HP gain,
    fury and stamina techs fall to dead-slot level, and every Diff% shrinks
    (a useless slot ≈ −7 instead of −12). With 50% of toughness and
    stamina from health: the most even attributes so far (strength −0.1,
    agility +0.7, speed −1.2, health +0.5); with 100%: health +3.1 leads.
    2026-10-23: 10% of toughness + 25% of stamina from health (50 HP):
    health −0.7, speed −2.3, fights unchanged; 40 HP + 50%: fights 51.4 s
    (near the pre-batch 49.5), but health +1.8 overshoots and speed −2.9.
    At 50 or 40 HP speed is the weakest attribute in every setup — raising
    health only pushes speed further down, so speed needs its own fix.
    Setup C (40 HP, 20% of toughness + 30% of stamina from health): health
    −0.1, strength +1.3, agility +1.1, speed −2.2 — the smallest gap at
    40–50 HP; fights 49.4 s (the pre-batch length); 'health' techs +10.8
    (on par with strength/agility techs), HP gain +12.2 → +4.2, fury
    +8.0 → +4.2
  - **Speed — adopted 2026-10-23** (tempo `1.5 * (speed - 2)` instead of
    `speed`). Left over: speed is a bit weak at levels 1–7 (−1.6) and a bit
    strong at 15–20 (+1.0); techs that boost speed score ~+5 vs ~+12…+15
    for the other attributes' techs — re-price their boost values with
    `run_test_tech_ab.py`. History: speed only sets how often a fighter acts;
    strength sets damage *and* block power. An attribute point is worth
    +15.9 for speed vs +26.6…+36.2 for the others at levels 1–7 (about even
    at 15–20; toughness is not the cause): extra turns partly go to Guard /
    Catch Breath, and extra strikes meet the same blocks, while a strength
    point turns many full blocks into damage. Fixes tested: dodge from
    (agility + speed) / 2 (speed −1.9 → −1.2); strike power from 20% speed
    + 80% strength (speed +0.1, strength 0.0); action time ∝ 1/speed^1.5
    (speed −0.2, health −2.6). On top of setup C the last two give the most
    even attributes yet (gap 1.8 / 1.7; all four within ±1.1). Per level
    band both lift a speed point at levels 1–7 from +15.9 to +20–21.5, but
    the others stay at +26…+36 there; mid levels even out, and at 15–20
    speed becomes slightly the best point. Round 2 (harness now reports
    attributes per level tier; "gap" = strongest minus weakest attribute):
    the author's speed-in-defense rule (dodge and block from speed instead
    of agility) overshoots — agility falls to −2.2 (gap 3.5); default
    preemptives for the faster defender add ~+1.5 to speed (gap 1.6 alone,
    5.1 with speed-in-defense); block power from health ("D") evens strength
    and health. Best: D + linear tempo from speed above 2 (`Sa2`) — gap
    0.9 overall, 2.9 / 1.1 / 2.2 per tier; low levels still favor health
    over speed (+1.3 vs −1.6). Tempo normalization by level doesn't matter
    for balance (only the clock)

**Snapshot 2026-10** (`tests/test f.b. rand.act.=False n=10000.txt`, seed 42,
re-run 2026-10-20 after the ⚠️ batches; Diff% = winner-vs-loser
correlation). The pre-batch code (4f157e9) reproduces the 2026-09 report
byte-for-byte, so every shift comes from the batch fixes. **One 10k report is
noisy** — a row's 95% noise margin is about ±196/√Sum Diff% points (style
buffs ±4, techs 1 ±9, techs 2 ±25) — so the comparison below pools 5 seeds ×
10,000 fights per code version (old → new):
- **Fights ~20% grindier**: mean length 49.5 → 59.9 s (median 33 → 37,
  slowest 10% from 108 → 136 s), strikes/fight 9.2 → 11.3, same total damage.
  Strike outcomes: dodged 19 → 21%, fully blocked 7 → 16%, partly blocked
  1.5 → 4%, clean hits 72 → 59%. (Counted by a hook script, not the harness.)
- **Compounding defense rewards whatever scales both chances**: unblock.
  −5.9 → +2.1 (removing the block roll now costs the defender ~half its
  defense, not a third); guard while atk +12.1 → +17.6 (tech Guard While
  Striking +5.7 → +15.4 — now the strongest buff); agility pulled further
  ahead (+1.1 → +2.0; health −1.3 → −1.8).
- **Defense-labelled buffs still lose**: blocks −10.2 → −10.7 (`block_mult`
  is block *power* only, and 82% of blocks already absorb the whole strike),
  guard −10.5 → −12.6 (the Guard move costs a turn), defense −12.4 → −13.5
  (dead — see "Bugs"). Only 'dodge' is mildly positive (+1.8 → +4.2).
  A dead tech slot costs about −9 to −13 here, the yardstick for "useless".
- **Counters**: 0.42 → 0.61 per fight, ~26 stamina (16% of max) + ~6 QP
  each, damage per counter 51 → 42 (corrected: the first hook script missed
  counters that reused the fighter's last move); the counters buff is
  unchanged (−10.6 → −9.8) — the cost doesn't bite because fighters end
  fights with ~61% stamina and ~37% QP. A +50% counter tech adds ~6 HP of
  damage per ~410 HP fight.
- **Criticals / stun: no measurable shift** (criticals +0.3 → −1.5, stun
  −1.5 → −0.5). Crits per strike 11.9 → 10.0% (fewer clean hits), per fight
  unchanged. Only 2.6% of strikes hit a stunned fighter, already 87% clean
  hits before (skipping turns never resets the per-strike defense decay).
- **Dragon III / Snake III: not visible to this harness** (`new_fighter()`
  only makes generated styles; the author keeps it that way — classic
  styles are legacy). A/B over 40,000 same-style lv 7–20 fights: the +10%
  max QP side won 50.2% (Diff% +0.5 ± 1.0) — correct fix, no balance effect,
  since qi isn't scarce (qi buffs −7.9).
- Borderline (|z| 2.5–3.5 among ~150 comparisons): preemptive +3.9 → +0.1,
  dam.reduc. +3.6 → −0.1, drunken moves −4.2 → −6.5, ultra short −3.1 →
  −8.6. Single-run swings in techs 2 are noise: Sky Dragon +4 → +49 and
  Emperor's Fortress +1 → −43 in the seed-42 report, but +12 → +20 and
  −5 → −17 pooled.
- Still true from 2026-09: the AI attribute-growth fix isn't exercised
  (`new_fighter()` = `rand_atts_mode=0`); the harness is byte-reproducible
  per seed across processes (fixed 2026-09-17).

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
- **buff counters** (author 2026-10-20): counters now pay their move's cost;
  the 2026-10 re-run shows the counters buff unchanged at ≈ −10 (dead-slot
  territory) — the problem is size, not cost (~6 HP per fight from a +50%
  counter tech). Done 2026-10-20: a fully dodged/blocked strike leaves the
  attacker briefly off-balance, so the counter meets ×0.75 defense — the
  counters buff stayed at −11.7 in the interim 100k run, so it isn't enough
  on its own. Still open:
  - raise the counter techs' chance/efficiency
  - discount counters (e.g. half the move's stamina/qi cost) — a middle
    ground between free and full price ("using the attacker's momentum");
    weak lever while stamina/qi aren't scarce
  - a higher stun chance for counters — go gently: a stun now also lowers
    defense, so counter-stun chains could snowball
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
- **Master's teachings during "Practice at school"** (author 2026-10-23):
  now and then the master shares a random *true* fact about the fight
  mechanics, phrased as kung-fu wisdom rather than a rule ("Improving your
  strength makes your block harder" → something like "A strong arm turns
  the blow; a weak one only meets it"). Keep the facts true as mechanics
  change: tie each to the `docs/` paragraph it paraphrases (or to the
  constant it depends on) so a rule change flags the saying; new strings
  go through i18n
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
- story outlines (from the old `docs/story notes.txt`; steps → rewards):
  - **King of Robbers:** news about the gang, crime goes up → raid(s) → a
    big crowd of robbers, fought with allies → final showdown (kidnapping?).
    Rewards: money, rep
  - **Chief of Police:** rumors about corrupt police officers → witness
    extortion, fight the police, the chief appears → police letting
    criminals go → a set-up, possible arrest of the hero? → a meeting where
    he acts friendly and offers a large bribe. Rewards: rep
  - **Out-of-towners:** a new hostile school → it challenges the other
    schools (open-ended?) → resorts to criminal methods, intimidates
    students → the hero's students fight the out-of-towners → masters'
    showdown. Rewards: rep, tech
  - **Evil sect:** a new sect appears, aims unknown → attacks → the leader
    is mad (large damage reduction). Rewards: rep, tech
  - **Spirit of Wushu:** train alone → fight the spirit (a few times?).
    Rewards: techs, moves, advanced tech
  - **Daughter of the Tavern Owner:** meet at the tavern, spend money → the
    girl vs thugs, help out → a friendly match with the girl → thugs kidnap
    her father; help, get married. Rewards: money, exp (the romance system
    shipped since — this could become a romance storyline)
  - titles only: Wandering Master, Shaolin, Secret Scroll, Honest Cop (the
    first three overlap the one-liners above: wandering master, Shaolin
    wooden fighters, lost manuscript)
- when NPC schools fight each other, show which school won
- inspiration for characters and stories: the major characters of *Outlaws
  of the Marsh* — http://www.outlawsofthemarsh.com/major-characters/
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

- **Natural physique** (author 2026-10-23): drawn at random at game start, a
  permanent ±25% to one of the four basic attributes that nothing can
  change ("naturally healthy" / "frail", "dexterous" / "clumsy", "strong" /
  "weak", "quick" / "sluggish"). Notes: 25% is about one attribute point at
  levels 1–7 and two at level 20, and one point at levels 1–7 is worth
  +16…+36 Diff% (58–68% win rate in mirror matches, 2026-10-23 A/B), so a
  penalty draw makes the early game noticeably harder — consider pairing
  each bonus with a smaller penalty elsewhere, or showing it at creation
  with a reroll. Implement as its own multiplier next to the `*_mult` ones
  (techs change those); it must be saved (`savable_atts` /
  `get_init_atts`, see the save-format pitfalls in AGENTS.md)
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
- hide Step Forward / Step Back in the fight menu when the distance makes
  them pointless

## Localization (see `docs/i18n.md`)

Milestones 1+2 shipped 2026-09-28: menus, meta UI, fight text, quotes,
encounter/story/event/tournament prose, player-life messages, stats report,
debug menu, biographies (gender-aware), all name catalogs — 954 prose +
14,483 name entries, 100% machine-translated. What remains:

- **Human review pass** over the machine-drafted `kfw.po` and
  `kfw_names.po` (+ `dev_scripts/_names_ru.py` dictionary) — draft quality
  by design; this is the main open item
- **Russian fighter-name generation** — proper names stay Chinese-ish
  syllables transliterated as-is; a Russian flavor would need a new
  name-pool pipeline
- **Menu key mnemonics** — menu option keys are derived from English
  letters; under ru the auto-keys follow the translated labels, which may
  collide or be awkward; consider explicit keys
- **Move `descr` stat blocks** ('Dist:2 Pwr:5' etc.) — kept English on
  purpose; translate if a compact Russian notation is wanted
- **Full declension machinery** — currently avoided via case-neutral
  phrasing; a few interpolated fighter names still sit in oblique-case
  positions (acceptable with undeclined Chinese names, but noticeable)
- **Mid-process `set_language()`** does not regenerate import-time PMAP
  descriptions or already-built `Tech.descr` strings (harmless in the real
  game; only matters for tests/dev scripts)
- **'Weird' prefix in `_strange_dreams.py`** is glued to an enemy's name in
  code (`en.name = 'Weird ' + en.name`), so it stays English — a display-layer
  prefix mechanism would be needed
- **Two-count sentences** ("{n} police officers fighting {m} thugs") can't
  inflect both counts via one `ngettext`; current phrasing parenthesizes the
  numbers
