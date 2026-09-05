# Kung fu: moves, styles, techniques, weapons

Content systems — how moves/styles/techs/weapons are *defined, generated and
learned*, not how they resolve in a fight (that's
`docs/fight_mechanics.md`, cross-referenced below as [fight]). Source files:
`kf_lib/kung_fu/` (`moves.py`, `styles.py`, `style_gen.py`, `techniques.py`,
`boosts.py`, `boost_combos.py`, `ascii_art.py`), `moves/` (move data),
`dev_scripts/move_gen.py`, `kf_lib/things/weapons.py`,
`kf_lib/actors/fighter/` (`_moves.py`, `_techs.py`, `_style.py`,
`_weapons.py`). Items marked ⚠️ look unintentional or surprising — verify
before building on them.

## Move data and loading

Moves are text data, not code. `moves/all_moves.txt` is the single loaded
file: pipe-separated columns (`name | distance | dist_change | power |
accuracy | complexity | stam_cost | time_cost | qi_cost | features |
functions | tier | freq`), every value `eval()`'d by
`read_moves` (`kung_fu/moves.py`). It is read **at import time**; each row
becomes a `Move` that self-registers in `ALL_MOVES_DICT` by name
(13,841 moves as of 2026-09).

`Move.__init__` additionally: adds a `distN` feature derived from `distance`
(`fighting/distances.py: DISTANCE_FEATURES`), computes `special_features =
features & {'drunken'}`, builds `descr`, and picks ASCII art via
`kung_fu/ascii_art.py` (`moves/ascii_mapping.txt` maps move names to art;
`get_ascii` falls back to "<prefix> <last word>" matches, then to the
`Stance` default — generated names need no mapping entry). ⚠️
`Move.descr_short` is initialized to `''` and never filled in — dead field.
Field semantics in a fight (power > 0 = strike, negative costs restore a
pool, etc.) are covered in [fight].

`BASIC_MOVES` (14 moves: Punch, Kick, maneuvers, Guard/Focus/Catch Breath,
finishers) are flagged `is_basic` and given to every fighter at creation
(`_moves.py: set_moves`).

## Procedural move generation

`all_moves.txt` is **generated** — never edit it directly
(`moves/_moves_readme.txt`). Sources:

- `moves/base_moves.txt` — 7 basic strikes (Claw, Elbow, Headbutt, Kick,
  Knee, Palm, Punch), all tier 0.
- `moves/extra_moves.txt` — 52 hand-written moves: maneuvers (Step Forward,
  Rush Forward, …), takedowns (Sweep/Throw/Trip), finishers, and all 35
  weapon moves (feature `'weapon'`, tier 0).
- `moves/style_moves.txt` — 6 signature moves referenced by style move
  strings (Backfist, Charging Step, Dragon Claw, Leopard Punch, Mantis
  Hook, No-Shadow_Kick), all tier 0, `freq 0`.

`dev_scripts/move_gen.py` (run from its own directory; it chdirs to repo
root) feeds **base moves + takedown moves only** into `gen_moves`. The
generator is a set of prefix *functions* (`light`, `heavy`, `long`,
`charging`, `flying`, `shocking`, `lethal`, …): each takes a move dict,
returns a modified copy (stat multipliers, added `functions`, new name
prefix) or `None` if the prefix is incompatible with the move (e.g.
`long` refuses distance-4 moves, most prefixes refuse `'takedown'` moves).
`prefix()` also adds the lowercased prefix to `features` — this is where
features like `'charging'`/`'flying'`/`'drunken'` come from.

Which prefixes may follow which is defined by
`moves/move_word_combinations.csv`: rows = first prefix, columns = second
prefix, `1` = allowed. ⚠️ The CSV tokens are resolved by name against
`move_gen.py` module globals (`module_vars[...]`), so a CSV typo is a
`KeyError`, and renaming a function silently breaks the matrix.

For each base move, `gen_moves` builds all allowed 1- and 2-prefix chains
(3-chains were considered and dropped), applies each chain right-to-left
(functions compose), and dedups by name. Every successfully generated move
also spawns up to 5 "quality" variants via `skillful`, `superior`,
`advanced`, `expert`, `ultimate` — each another tier up with ~5% better
power/accuracy/time for more stamina. ⚠️ On a name collision the chain
keeps composing from the *previous* stage's dict (`temp = new_move` sits
inside the not-already-seen branch) — surprising but apparently benign.
`pathetic`/`weak` prefixes exist but are commented out of the variant list.

Tier and qi scaling: `change_tier` adds the tier delta and, when raising,
`+5 qi_cost` per tier (`QI_COST_PER_TIER`) — this is why high-tier moves
cost qi even though no base move does. `freq` (random-selection weight)
drops for fancier prefixes (`mn=1` floor). Output: `all_moves.txt`
(alphabetical, column-formatted in batches of 25) and a pandas
`all_moves.csv` dump.

Tiers in the generated data run 0–14, but `TIER_MAX = 10` and
`get_move_tier_for_lv = ceil(level / 2)` caps at 10 for level-20 fighters.
⚠️ Tier 12–14 moves (291 of them, e.g. `Lethal …` chains with
`try_insta_ko`) are **unreachable through any normal channel**; tier 11 is
reachable only via a lucky book (see Learning). Per the author (2026-09) this
is deliberate for now — those tiers are reserved for future content (special
encounters, rare/extreme buffs). Tier 0 is never randomly
sampled either — it holds the basic/weapon/style moves that are only given
out by name.

## Random move selection and move strings

`get_rand_moves(f, n, tier, features)` (`kung_fu/moves.py`):

1. Resolve `tier`: `'auto'` = `ceil(f.level / 2)`; `'random'` = uniform
   1–10. `features='auto'` = `f.fav_move_features`.
2. Pool = moves of that tier, not already known, and not having a special
   (`drunken`) feature the fighter lacks — drunken moves are gated behind
   drunken techs/styles this way.
3. ⚠️ `random.choice(pool)` runs *before* the empty-pool check, so an
   empty pool raises `IndexError` instead of falling back to the whole tier
   (already flagged in [fight]). The fallback below it is unreachable.
4. Shuffle, stable-sort by overlap with `features` (descending), truncate
   to `n * 3`, then weight by `freq` (`weighted_pool.extend([move] *
   move.freq)`) and pick `n` distinct moves. When `n > 1`, one uniformly
   random move from the pre-sort pool is force-added "for variety".

`resolve_move_string(move_s, f)` is the mini-language behind style move
strings and level-ups:

- `'3'` (digit only) → choose 1 of `num_moves_choose` random tier-3 moves.
- `'Dragon Claw'` (exact name) → learn that move directly.
- `'2,kick'` or `'3,fast,kick'` → optional leading tier, then feature
  filters into `get_rand_moves`.
- anything else (blank, or an **unknown name**) → a fully random pick at
  the auto tier/features. ⚠️ Unknown literals don't raise — Hung Ga's
  level-8 `'No-Shadow Kick'` and Wing Chun's level-2 `'Short Fast Punch'`
  don't exist in `ALL_MOVES_DICT` (the former is `'No-Shadow_Kick'` with an
  underscore), so both styles silently get a random move instead of their
  signature move (verified against the data).
- ⚠️ Feature tokens are only meaningful if they exist in move data:
  White Crane (`'3,close-range'`) and Xing Yi (`'…,mid-range'`) use
  `close-range`/`mid-range`, which no move has (the real tokens are
  `dist1`–`dist4`); the filter silently does nothing.
- ⚠️ Tuples of names (Eagle Claw/Leopard/Monkey level 1) are handled by
  `set_rand_moves` but *not* by `resolve_move_string` — safe today only
  because all tuple entries sit at level 1, which `level_up` never passes
  through.

## Styles

`Style` (`kung_fu/styles.py`): name + `techs_dict {level: Tech}` +
`move_str_dict {level: move_string}`. A style with any techs is a
"tech style" (`is_tech_style`) — this flag gates *all* tech progression on
level-up, so the tech-less styles below get no techs at all. The style's
displayed "emphases" (`descr_short`, shown by
`get_style_string(show_emph=True)`) are just the deduped short descriptions
of its techs. Every `Style` self-registers in `all_styles` at import.

- 24 handcrafted `default_styles` (Bagua Zhang … Xing Yi) — all are tech
  styles with techs at levels 3/5/7. 10 of them (Bagua Zhang, Choy Li Fut,
  Eagle Claw, Hung Ga, Leopard, Long Fist, Monkey, Poking Foot, Praying
  Mantis, Wing Chun) have custom named move strings at levels 1/2/4/6/8; the
  other 14 fall back to
  `DEFAULT_STYLE_MOVE_DICT = {2: '1', 4: '2', 6: '3', 8: '4', 10: '5'}`
  (a free choice from tiers 1–5). ⚠️ Six of the handcrafted move strings are
  broken (unknown names `'No-Shadow Kick'`/`'Short Fast Punch'`, unknown
  features `close-range`/`mid-range` — see above) and silently degrade to
  random picks, so `kfw.py` currently forces generated styles for new games.
- Special NPC styles: `BEGGAR_STYLE`, `THIEF_STYLE`, `DRUNKARD_STYLE`,
  `TURTLE_NUNJUTSU`.
- Tech-less placeholder styles with `{}` techs: Flower Kung-fu (the
  `set_style(None)` default), Dirty Fighting, Police Kung-fu, Monster
  Kung-fu, Savant, No Style.
- `FOREIGN_STYLES`: country → style (English Boxing, Wrestling, Karate,
  Taekwondo, Muai Thai, Capoeira) for foreigner NPCs.
- `get_style_obj(name)` lazily parses unregistered names as generated
  styles (`style_gen.get_style_from_str`) — this is how saved generated
  styles are reconstructed on load.

Game wiring (`game/_base_game.py`, `_new_game.py`): `BaseGame` defaults
`style_list = styles.default_styles`; the `generated_styles` option replaces
it with 10 generated ones (`NUM_STYLES`) — and also **mutates the module
global** `styles.default_styles` (marked with a todo). Since 2026-09 `kfw.py`
forces `generated_styles=True` for every new game (autoplay and interactive;
the `yn('Randomly generated styles?')` prompt in `new_game` is bypassed)
because of the broken handcrafted move strings above — revert that once the
strings are fixed.
Each style in `style_list` gets a school: one master + 6–8 students.
Players pick from `style_list`; most `fighter_factory` NPCs instead get a
fresh `style_gen.get_new_randomly_generated_style()` each, so the world's
styles far outnumber the schools'.

## Random style generation

`kung_fu/style_gen.py`: three word lists — `W1` (37 descriptive words:
Acrobatic…Vigorous), `W2` (33 elemental/atmospheric: Air…Wooden), `W3` (33
animals: Bear…Wolf) — each word mapped to one `Tech`. A generated style is
`"{w1} {w2} {w3}"` with techs `{3: W1[w1], 5: W2[w2], 7: W3[w3]}`;
`get_n_possible_styles()` = 40,293. `Tech` objects are shared between
styles (stateless param bags, applied additively — safe). Generated styles
have no move strings (a todo), so they use `DEFAULT_STYLE_MOVE_DICT`.

`generate_new_styles(n, overlap=False)` samples without replacement per
list (requires `n ≤ 33`); the `overlap=True` variant allows repeats and
dedups names afterwards, so it can return **fewer than n** styles — but no
caller uses it. `get_new_randomly_generated_style()` picks one word per
list independently, so two NPCs can share a style name (later registration
overwrites in `all_styles`, harmlessly).

## Techniques and boosts

`Tech` (`kung_fu/techniques.py`) = name + `params` dict of attribute deltas
+ flags (`is_upgradable`, `is_advanced`, `is_weapon_tech`) + `fav_moves`
(unused?). `Tech.apply(f)` *adds* each param to the fighter attribute and,
for `*_strike_mult` params, adds the corresponding feature to
`f.fav_move_features` (e.g. Iron Fist → `'punch'`) — this is the only way
`fav_move_features` grows, and it drives both random move selection and the
`*` hints in the human move menu (`get_move_stars`). `apply_tech` then
refreshes derived attributes. All multiplicative-sounding params are
additive increments to a 1.0 base — stacked techs add, never compound (see
[fight] for how the mults enter combat math).

Boost values are named constants in `kung_fu/boosts.py`; themed bundles
(QI1/2, STAMINA1/2, CRITICAL1/2, DRUNKEN1/2, …) live in
`kung_fu/boost_combos.py`. `boosts.PMAP` maps param names to short/long
descriptions; `set_descr` renders `Tech.descr`/`descr_short` from it.
⚠️ PMAP lacks `head_strike_mult` and `claw_strike_mult`, so techs granting
them (Exotic Boxing, Hardened Palms, style words like 'Exotic' /
'Open-Handed') display **incomplete descriptions** — the bonus and the
fav-feature still apply.

Upgrading: `LINKED_TECHS` pairs 30 regular techs (`is_upgradable=True`)
with their advanced versions (`is_advanced=True`); `UPG_MAP_REG_ADV` maps
between them. `upgrade_tech` = unlearn (subtract deltas) + learn the
advanced twin. `get_learnable_techs(f)` = all upgradable techs minus what
`f` has, including the regular twin of any advanced tech `f` holds.
⚠️ `Lightning-Fast Strikes` (advanced) uses the same −0.3 as basic
`Fast Strikes` instead of −0.6 — upgrading is a no-op (also flagged in
[fight]).

Weapon techs: `WeaponTech` adds a `(atk, dfs)` pair into
`f.weapon_bonus[wp_type]`, but all 7 declared `WeaponTech`s leave
`wp_type=''` and `wp_bonus=(0,0)` — nothing configures them, and the code
carries the todo "weapon techniques do nothing; implement" (flagged in
[fight]). ⚠️ Additionally each `WeaponTech` is appended to
`_weapon_techs` **twice** (both `Tech.__init__` and `WeaponTech.__init__`
append), and `WeaponTech.set_descr` is dead code — `Tech.__init__` calls
the module-level `boosts.set_descr` instead.

⚠️ `_style_techs` is declared but never appended to anywhere, so
`get_style_techs()` always returns `[]` (only `testing/tech_test.py` calls
it).

## Weapons

`kf_lib/things/weapons.py`: a `Weapon` is a name, a `dfs_bonus` (stored as
`1.0 + bonus`), and 1–2 moves resolved by name from `ALL_MOVES_DICT` — all
weapon moves are tier-0 `'weapon'`-feature moves from `extra_moves.txt`
(never randomly learnable; they enter a fight only via `weapon.moves`, see
[fight]). Four subclasses define the types: `NormalWeapon` (5: swords,
saber, spear, staff, sword), `ImprovisedWeapon` (14: fan, bench, guqin,
chain, …), `RobberWeapon` (3: axe, bludgeon, knife), `PoliceWeapon` (1:
baton). `WEAPON_TYPES` groups them by `wp_type`. `get_exp_mult()` =
`1 + mean(dfs_bonus, atk_mean)` feeds the weapon exp multiplier in
[fight].

Arming (`fighter/_weapons.py`): `arm(weapon)` accepts `None` (fully random
weapon), a type string (`'improvised'` etc.), a `Weapon` instance, or a
weapon name; it calls `disarm()` first to avoid stacking bonuses, then sets
`self.weapon` and `wp_dfs_bonus` (block-only, see [fight]). Convenience
wrappers `arm_improv/arm_normal/arm_police/arm_robber` are used by
encounters (robbers, police, gamblers, school sparring) and
`fighter_factory.from_exp_worth` (35% weapon chance).

Weapons are **per-fight equipment**: `AutoFight`/`SpectateFight` call
`disarm_all()` at the end ("to avoid having people running around with
weapons"), and mid-fight the only losses are `try_block_disarm` /
`try_hit_disarm` (tech-gated, see [fight]). Tech-gated fighters can grab an
improvised weapon mid-fight (`try_in_fight_impro_wp`, requires
`environment_allowed`). ⚠️ There is **no durability or weapon-breaking
mechanic** anywhere — weapons never wear out; they only appear and
disappear per fight.

## Learning moves and techniques

Level-up pipeline (`fighter/__init__.py: level_up` →
`_moves.resolve_moves_on_level_up`, `_techs.resolve_techs_on_level_up`):

- Moves: if the level is a key in `style.move_strings`, resolve that move
  string; **elif** the level is in `LVS_GET_NEW_ADVANCED_MOVE = {12, 14,
  16, 18, 20}`, offer a choice at tier `ceil(level/2)` (6–10). (Misleading
  name: these "advanced moves" are unrelated to `Advanced`-prefixed moves
  or advanced techs.) Other levels grant no move.
- Techs (tech styles only): style tech at the style's keyed levels (3/5/7);
  one tech upgrade at `ADVANCED_TECH_AT_LV = 19`; a new general tech at
  `LVS_GET_GENERAL_TECH = {13, 15, 17}`.
- Choice sizes: `num_moves_choose = 3`, `num_techs_choose = 3`,
  `num_techs_choose_upgrade = 3` (`_fight_attributes.py`, `_abc.py`),
  modifiable by traits (`actors/traits.py`: broad-minded/narrow-minded ±1).
  `HumanControlledFighter` shows menus with full stat columns; the base
  (AI/NPC) implementations just `random.choice` from the same sample.

Level-by-level view (default styles; generated styles use the default move
dict at 2/4/6/8/10 and techs at 3/5/7 — `style_gen.py:187`):

| Level | Move | Tech (tech styles only) |
|-------|------|-------------------------|
| 1 | named style move (10 custom styles only) | — |
| 2 | style move (tier 1 for default-dict styles) | — |
| 3 | — | style tech I |
| 4 | style move (tier 2) | — |
| 5 | — | style tech II |
| 6 | style move (tier 3) | — |
| 7 | — | style tech III |
| 8 | style move (tier 4) | — |
| 9 | — | — |
| 10 | style move, tier 5 (default-dict styles only) | — |
| 11 | — | — |
| 12 | "advanced" move choice, tier 6 | — |
| 13 | — | new general tech, choice of 3 |
| 14 | "advanced" move choice, tier 7 | — |
| 15 | — | new general tech, choice of 3 |
| 16 | "advanced" move choice, tier 8 | — |
| 17 | — | new general tech, choice of 3 |
| 18 | "advanced" move choice, tier 9 | — |
| 19 | — | upgrade one tech to its advanced twin, choice of 3 |
| 20 | "advanced" move choice, tier 10 | — |

Levels 9 and 11 grant nothing. Non-tech styles (Police Kung-fu, Flower
Kung-fu, etc.) skip the whole tech column — `resolve_techs_on_level_up`
returns early for them.

NPC creation takes the same content through constructors:
`Fighter(..., level=N)` samples moves/techs for the level outright
(`set_rand_moves` walks style strings and advanced-move levels;
`set_rand_techs` samples general techs — only if the style is a tech
style); a few factory functions instead create at level 1 and call
`level_up(lv - 1)` ("to gradually learn techs and moves").

Other learning channels:

- **Books** (`encounters/_book_seller.py`): buy for 100 coins; bad luck →
  rubbish; else 50% a random move at `get_move_tier_for_lv() − 1` (lucky:
  **+1** — the only source of tier-11 moves), otherwise flat exp.
- **Learning from NPCs** (`_moves.learn_move_from`): beggar, drunkard,
  street performer and challenger encounters copy a uniform-random unknown
  move from the NPC's list. This bypasses tier and `fav_move_features`
  gating entirely — it can hand out tier-0 style moves or drunken moves the
  fighter isn't "allowed" to roll.
- **Techs from events**: the beggar encounter (good luck) teaches a random
  new tech; the ninja-turtles story grants all three Turtle Ninjutsu techs
  directly.
- `fav_move_features` (`fighter/__init__.py`, grown only by
  `Tech.apply`): biases `get_rand_moves` sorting and gates the `drunken`
  special feature — so learning e.g. a Drunken Moves tech both strengthens
  drunken strikes and unlocks drunken moves in future random picks.
