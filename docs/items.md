# Items

How items work, as implemented. Source files: `kf_lib/things/items.py` (item
definitions/effects), `kf_lib/things/weapons.py` (weapons),
`kf_lib/actors/player/_base_player.py` (inventory),
`kf_lib/actors/fighter/_weapons.py` (arming), `kf_lib/fighting/fight/`
(`_base_fight.py`, `_auto_fight.py`) for in-fight use, and the encounters under
`kf_lib/happenings/encounters/` (`_items.py`, `_craftsman.py`,
`_book_seller.py`, `_performer.py`, `_crime.py`). Items marked ⚠️ look
unintentional or surprising — verify before building on them.

## Overview

An "item" is just a *name string*; the player's inventory is a plain
`{name: count}` dict (`BasePlayer.inventory`, saved via `savable_atts`).
`Item` objects (`things/items.py:51`) exist *only for descriptions* — the
docstring says "Instantiated only for descriptions", and it is literal: nothing
in the game logic ever touches an `Item` instance except `get_item_descr()`.
Effects live separately in the `EFFECTS` dict keyed by item name. ⚠️ Because
the two are decoupled, `use_item`/`cancel_item` raise `KeyError` for any name
missing from `EFFECTS` (e.g. mock items handed out via the debug menu).

Three real item categories, all defined as name constants in
`things/items.py`:

- **Fight items** (`STD_FIGHT_ITEMS` + `SUPER_BOOSTER`): twelve herbs boosting
  one stat each (Tiger/Monkey/Fly/Dragon/Elephant/Ox Herb, regular and "Super"
  versions) plus the 'Super Mega Herb' boosting everything. Effects are additive
  increments to the fighter's `*_mult` attributes (`ef_boost` →
  `Fighter.boost`, values from `kung_fu/boosts.py`, e.g. `STRENGTH1 = 0.2`),
  the same mechanism techniques use.
- **Medicine** (`MEDICINE` = 'Ginseng Root'): `ef_recover` → `recover()`,
  clears injury/sickness. Not a fight item.
- **Mock items** (`MOCK_ITEMS`): 'constipation medicine', 'cough medicine',
  'culinary herb mix' — no effects at all (see Weirdo below).

The **wooden mannequin** (`MANNEQUIN`) is a special case: it is stored in the
inventory like an item but has no entry in `EFFECTS`; its effect is hard-wired
in the day loop (see below).

Books, wine and food are **not items**: no inventory entries exist for them.
The BookSeller's book and the Drunkard's wine are one-shot encounter effects;
the Wise Man's "lunch" is a flat 10-coin fee
(`encounters/_people.py`).

## Inventory and limits

`BasePlayer` (`actors/player/_base_player.py`):

- `obtain_item(name, quantity)` / `lose_item(name, quantity)` adjust counts and
  log; `check_item(name)` returns the count (0 if absent).
- There is **no capacity limit** and no weight; counts are unbounded.
- Keys are never deleted — a fully consumed item stays in the dict with count
  0; display and queries filter `v > 0`.
- `get_items(incl_healer=False, incl_mock=False)` returns owned items as a
  list (one entry per unit) or dict. Defaults exclude medicine and mock items.
  ⚠️ `incl_mock=True` has no callers — mock items are invisible to every
  item-consuming system (can't be lost, stolen or used through these paths).
- `check_fight_items()` scans for any `FIGHT_ITEMS` entry with count > 0.
  ⚠️ Returns `None` (not `False`) when nothing is found.

## Acquisition

There is no shop UI. Buying is encounter-driven: the "Buy items" day action
(`buy_items` → `_day_actions.buy_items`) rolls `BUY_ITEMS_ENCS`
(`encounters/__init__.py`): Craftsman ×2, BookSeller ×2, **GMerchant ×5**
(guaranteed — `Guaranteed.check_if_happens` returns `True`, so the day action
always offers at least one merchant), Merchant ×3, StreetPerformer ×2. Merchants
also appear on walks (`WALK_ENCS`).

- **Merchant / GMerchant** (`encounters/_items.py:48`): offers 'Ginseng Root'
  or one random `STD_FIGHT_ITEMS` herb (coin flip) at a random price from
  `PRICES = (70, 80, 100, 120, 150)`. Refuses if the player can't pay; a
  `check_feeling_greedy` roll (`feel_too_greedy`) can make the player decline
  involuntarily. ⚠️ Price is item-independent — a basic herb and its "Super"
  version draw from the same price range.
- **Street Performer** (`encounters/_performer.py:110`): sells the "Golden
  Magnificent Elixir" for 40–60; 50% it is a real random standard item, 50% a
  mock item (stat `mock_items_bought`). This is the *only* source of mock
  items.
- **Craftsman** (`encounters/_craftsman.py`): sells the wooden mannequin for
  `MONEY_MANNEQUIN = 500`, once — `check_if_happens` excludes players who
  already own one. Luck roll: good luck → free after a sparring match; bad
  luck → the mannequin breaks immediately and is lost. ⚠️ There is **no
  `check_money` call** before charging: `buy_item(item, 500)` runs regardless,
  so money silently goes negative. The sales pitch ("you can pay the rest
  later") describes a debt mechanic that doesn't exist.
- **BookSeller** (`encounters/_book_seller.py`): sells a kung-fu book for
  `MONEY_BOOK = 100`. Not an inventory item: bad luck → "complete rubbish"
  (money gone); otherwise 50% a random move of the player's tier (−1 tier,
  +1 on good luck) or a flat exp gain (×3 on good luck). ⚠️ Asks "Buy it?"
  *before* checking money (Merchant checks money first), so a broke player is
  asked and then refused.
- **FindItem** (`encounters/_items.py:15`): `item_is_found` (0.01) roll after
  any non-rest day action (`rand_enc` in `game/_playing.py:160`) → a random
  standard item. The Lucky trait pair shifts `item_is_found`/`item_is_lost`
  (`actors/traits.py:26`).
- **Rewards**: beating Extorters gives a random standard item from the grateful
  shop owner (2/3 chance, `encounters/_crime.py:120`); helping the Street
  Performer can give one too.
- **Weirdo** (`encounters/_items.py:75`): asks for a random mock item; if the
  player has one, trades it for the 'Super Mega Herb' + 'Weird Item'
  accomplishment. The only source of `SUPER_BOOSTER` — merchants and
  `get_random_item()` (`ALL_STD_ITEMS`) never yield it.
- **Debug menu** (`game/debug_menu.py:53`): grants any item, any quantity.

## Usage effects

### Fight items — pre-fight pipeline

Items are used *before* a fight, not during one. `AutoFight.__init__` order:
`handle_items()` → `prepare_fighters()` → fight loop → `disarm_all()` →
`cancel_items_for_all()`. `handle_items` (`fight/_base_fight.py:278`) runs only
when `items_allowed` and the player owns fight items: the chosen item is
consumed (`use_item` → `lose_item` + `items.use_item` → `boost()`), then
`prepare_for_fight` recomputes pools off the boosted mults, so e.g. a health
herb raises `hp_max` *before* `hp = hp_max`. After the fight
`cancel_items_for_all` calls `unboost()` (negated boost) on whatever
`p.used_item` records. The item is permanently spent for a one-fight buff.
Only players use items; NPCs never do.

Humans pick from a menu (`_human_player.py:128`); `AIPlayer` uses a random
owned herb whenever the opposing side's total power exceeds its own
(`_ai_player.py:134`) — no matter how hopeless the fight, so AIs burn herbs on
lost causes.

`items_allowed` defaults to `True` in `AutoFight`/`fight()` but is `False` in
`BaseFight`, and most scripted fights opt out: tournaments, story bosses
(`story/_foreigner.py`, `_renowned_master.py`, `_ninja_turtles.py`),
challengers, school rank tests, the Performer/Drunkard/Gambler fights, and all
sparring. In practice herbs apply mostly to random crime/street fights.

### Medicine

Usable only outside fights, only when injured: at the start of an inactive day
(`game/_playing.py:37`) the player may `use_med_or_not()` → `use_med()`, which
clears `inactive`/`inact_status` entirely (stat `healers_used`). ⚠️ One root
cures a 1-day sprain and a 7-day injury identically, and `use_med` decrements
the inventory directly instead of via `lose_item` (no item log line).

### Mannequin

Passive, permanent: `Playing.do_daily` (`game/_playing.py:104`) grants
`HOME_TRAINING_EXP` (4 exp) every non-inactive day if the player owns one.
Cannot be lost or stolen — `get_items()` never includes it, so `LoseItem` and
the thief can't take it; the only way to lose it is the bad-luck breakage at
purchase.

## Weapons vs items vs improvised weapons

Weapons are a separate system (`things/weapons.py`), *not* inventory items:
nobody owns one. A `Weapon` is a name, a `dfs_bonus` (stored as `1.0 + bonus`,
fed into block/dodge via `wp_dfs_bonus`), and 1–2 exclusive moves. Types:
`normal` (swords, saber, spear, staff), `improvised` (fan, bench, guqin, …),
`robber` (axe, bludgeon, knife), `police` (baton) — types exist so encounter
code can arm the right NPCs (`arm_robber()`, `arm_police()`, … in
`actors/fighter/_weapons.py`).

Arming is always temporary and scene-driven:

- Encounter code arms NPCs (robbers/extorters/police, gamblers, challengers).
  ⚠️ `set_up_weapon_fight` (`encounters/_utils.py:48`) announces "Let's duel
  with blades" but arms only the NPC — the player fights barehanded. The
  school challenge (`_school.py:126`) is the one place the player gets a
  normal weapon too.
- `check_help` may arm the player with a random improvised weapon before a
  street fight (`grab_improvised_weapon` = 0.5).
- In-fight: `try_in_fight_impro_wp` (`_fight_actions.py:296`) rolls
  `in_fight_impro_wp_chance` each own turn (unarmed, environment allowed) —
  tech-gated ('Unlikely Weapons' 0.25 / 'Anything Is a Weapon' 0.5, Bagua
  Zhang III).
- `disarm_all()` at the end of every fight removes all weapons "to avoid
  having people running around with weapons".

Weapon moves merge into the move pool while armed (`get_av_moves`), and the
weapon's `get_exp_mult()` scales an armed fighter's `exp_yield` (snapshotted
in `prepare_for_fight`, before `disarm_all`). ⚠️ `get_exp_mult` computes
`1.0 + mean((self.dfs_bonus, self.atk_mean))`, but `dfs_bonus` already
includes the 1.0 base — so every normal weapon inflates exp worth to ~1.8–2.0×
(verified: sword 1.92, pair of swords 1.97), likely double-counting the base.

Weapons can be knocked away mid-fight: `try_hit_disarm` / `try_block_disarm`
roll the attacker's/blocker's `hit_disarm`/`block_disarm` (from the 'Monkey
and Fox' tech line, `kung_fu/techniques.py:124`). Weapon breakage and weapon
shopping do not exist; `WeaponTech`s are dead code (see
`docs/fight_mechanics.md`).

## Loss and theft

- **LoseItem** (`encounters/_items.py:31`): `item_is_lost` (0.01) roll after
  day actions → loses one random owned standard/medicine item.
- **Thief** (`encounters/_crime.py:289`): `thief_steals` (0.3) roll → coin
  flip between stealing one random item (from the same `get_items` pool) or
  25–200 coins (all of it, if poorer).
- **Breakage**: only the mannequin, and only at purchase (bad luck).

## Economy role

Items are one of the few money sinks besides tuition (`TUITION_FEE = 20`),
books (100) and the mannequin (500). Reference points: wage is 50/day,
starting money is 10. Herb prices (70–150) sit at 1.5–3 days' wages; the
mannequin at 10. Stats tracked: `items_bought`, `items_obtained`,
`items_found`, `items_lost`, `items_stolen_from`, `fight_items_used`,
`healers_used`, `mock_items_bought`, `super_herbs_obtained`
(`game/game_stats.py`).
