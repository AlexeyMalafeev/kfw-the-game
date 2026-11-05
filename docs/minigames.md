# Minigames

Three mini-games, Chocolate, RING and the Punching Bag, launched from the
main entry point with `python kfw.py --minigame {chocolate,ring,bag}` (plus
the usual `--lang` and `--no-color`), or on Android from the title screen's
**Mini-games** button. Sources: `kf_lib/minigames/` (`_chocolate.py`,
`_ring.py`, `_punching_bag.py`, `_records.py`; `MINIGAMES` in `__init__.py`
maps the flag value to a `play_*()` function; `kfw.py` repeats the keys in
its `--minigame` choices because it can't import `kf_lib` that early),
`kf_lib/actors/fighter_factory.py`, `android/python/kfw_android.py`. Tests:
`test/test_minigames.py`, `test/test_android_runtime.py`.
Items marked ⚠️ look unintentional or surprising — verify before building on
them.

## Shared conventions

- They reuse the main game's machinery: `HumanControlledFighter` (the
  human-driven fighter without a `Game` attached; its level-up banner and
  sound are the ones `HumanPlayer` uses, `announce_level_up()`),
  `Fighter.fight()` with its prefight screen, "Auto fight?" prompt and
  post-fight menu, the color markup (`ui.rprint`; no bare `print()`, so every
  line gets the automatic colors) and the i18n catalogs. They create no
  `Game`, so nothing is saved and no exp, stats or accomplishments are
  recorded (those hooks in `BaseFight` act on players only).
- Records (`_records.py`): RING and the Punching Bag keep their best results
  in `save/minigame_records.json` (`{"ring": {difficulty: record}, "bag":
  {"best": record}}`). A missing or damaged file counts as no records, a
  damaged field as a score of 0, and a file that can't be written just loses
  the new record (written via a `.tmp` file and a rename). On Android the
  file sits in the app's save folder; the load and export lists skip it
  because they list valid saves only. Tests point `_records.SAVE_FOLDER` at
  a temporary folder.
- `kfw.py` sets the language and colors first, then dispatches to the
  mini-game; Ctrl+C ends it with the usual farewell. Crashes print a plain
  traceback (no `crash_report`, which needs a `Game`).
- Interactive: like the main game they need a real TTY, or the Android app.
- Music (heard on Android only, see `docs/audio.md`): fights pick their own
  tunes as in the main game, and the end-of-fight jingle stops the music, so
  the screens between fights are quiet until a mini-game starts a tune again.

## On Android

The title screen's **Mini-games** button opens a picker (Chocolate, RING,
Punching Bag; `MINIGAMES` in `MainActivity.java` lists their keys in that
order). `MainActivity` starts the session with
`kfw_android.run(mode="minigame", minigame=<MINIGAMES key>)`, which calls the
`play_*()` function inside the usual Android runtime: native menu buttons,
the keyboard for names and RING's level, colors kept. When the mini-game
returns, the app goes back to the title. Leaving early with ‹ or Back asks
for confirmation with a mini-game message (the game itself isn't saved;
records are kept as they are set), and a crash dialog mentions only
`errors.txt` (there is no `Game` for an emergency save). The instrumentation
self-test plays all three mini-games on the device; `android/scripts/
ui_smoke.py` plays a whole RING run and a Punching Bag round from the title
screen, and leaves Chocolate early.

## Chocolate — `kf_lib/minigames/_chocolate.py`

A scripted campaign, a homage to the Thai film *Chocolate* (2008). No real
people are named anywhere in the game.

- The hero, `Zen` (a `HumanControlledFighter` subclass), is fixed: lv.12,
  style 'Savant' (`styles.ZENS_STYLE`, no techs or moves of its own),
  attributes 5/10/7/5, female. Her `set_rand_moves`/`set_rand_techs` are
  no-ops, so she starts with only the basic moves and no techniques. She
  never gains exp or levels up.
- Seven scenes (`get_scenes()`). Each scene first teaches its techniques and
  moves (`learn_tech` / `learn_move`, shown on screen), then runs its fights
  in order. A fight is a factory that builds a fresh gang (first member is
  the leader) plus an optional weapon for Zen. A lost fight is replayed
  against a newly built gang, so weapons knocked away last time are back.
  Losses cost nothing but are counted and reported at the end.
- Scene 6 is the only two-fight scene: a duel against a lv.18 Drunken Dragon
  fighter, then Zen picks up a sword against a sword-armed boss and three
  swordsmen.
- Scene 5 teaches two mini-game-only techs, `Mighty Elbows` and `Mighty
  Knees` (the advanced elbow/knee strike bonus, `boosts.STRIKE_MULT2`). They
  are plain `Tech`s (not upgradable or advanced), so they never enter the
  main game's level-up pools; like every `Tech`, they register in
  `get_tech_obj`'s lookup table when the module is imported.
- Difficulty, measured 2026-10 with the default fight AI auto-fighting for
  Zen (30–40 runs per fight, noisy): scenes 1–3 ≈ 100% wins, scene 4 ≈ 90%,
  scene 5 ≈ 50%, scene 6 ≈ 65% then ≈ 40%, scene 7 ≈ 30–45%. A human
  choosing moves may do better or worse.
- Russian: scene titles and messages go through `_()`; the hero, gang names
  and the two techs are in the names catalog (`EXTRA_NAMES` in
  `dev_scripts/i18n_extract.py`, translations in `dev_scripts/_names_ru.py`).
- Music: Strange Dreams (the main game's story tune) on the welcome screen
  and every scene card; A Legend Is Born on "The End".

History: a 2020–2022 prototype in `minigames/Chocolate_mini_game.py`, broken
for years by stale imports and renamed moves/techs; revived 2026-10. Moves
gone from the data were replaced by their nearest current names (Jumping
Kick → Flying Kick, Roundhouse/Spin Kick → Acrobatic/Onslaught Kick,
Dragon Elbow/Jumping Knee/Volcano Knee → Energy Elbow/Flying Knee/Shocking
Knee); the old defensive moves Dragon Block/Dragon Evasion were dropped
because blocking and evading are passive now. Scenes 6 and 7 existed only
as comments and were written in the revival.

## RING — `kf_lib/minigames/_ring.py`

An endless arena ladder around the normal fight engine:

1. The welcome screen lists the records (below), then the difficulty menu:
   easy 0.9 / normal 1.0 / hard 1.1 / extreme 1.2, a multiplier on opponent
   strength (`DIFFICULTIES`).
2. `fighter_factory.new_custom_hcf()` builds the player's fighter: a name
   prompt (`get_str_from_user`; an empty or blank name is asked again), a
   style menu, and a level prompt (1–20) applied via `level_up()` — the
   level-up banner once, then the usual attribute and move choices for every
   level gained. The style menu (`choose_generated_style`) offers ten freshly
   generated styles (`style_gen.generate_new_styles`, as many as a new game's
   `NUM_STYLES`) and a last option, "(other styles)", that clears the screen
   and rolls a new ten — the counterpart of the main game's "Are these
   styles ok?". Styles are listed the way the main game's style menu lists
   them: `display_public_name` (translated) and `public_descr_short`, so the
   secret technique shows as `???` until the fighter learns it. Until 2026-11
   the menu listed the hand-made `styles.default_styles`.
3. Each round, opponents come from `fighter_factory.from_exp_worth(
   p.get_exp_worth() * difficulty, max_lv=p.level + OPP_LV_MARGIN)` (margin
   5): it rolls random groups (`new_fighter`, 1 to 5 members of one level
   from 1 to `max_lv`, 35% weapon chance for a lone opponent) until the
   group's total `get_exp_worth()` lands in `[x, x + x / 10]`, and after 300
   rolls settles for the closest group rolled. Measured 2026-11 (player
   levels 1–80, easy and extreme, 8 searches each): a median search took
   0.03–0.6 s, the slowest 1.6 s, and the fallback was needed once, for a
   lv.1 player on extreme (only three exp values fit the band there). Until
   2026-11 the cap was a fixed level 20 with no roll limit: five lv.20
   fighters are worth about 850, a lv.40 player about 900, so from about
   level 40 (35 on extreme) the loop never ended.
4. `p.fight(opp[0], en_allies=opp[1:], hide_stats=strength >= 1.0)`, where
   `strength` is the difficulty's multiplier. Win → `p.level_up()` (full
   interactive level-up, bold green banner). Loss → one of 3 attempts is
   spent; the remaining count shows in yellow, red at 0. At 0 attempts it
   prints the reached level (cyan), the fights won, the record line and a
   bold "Game over".

- Records: one per difficulty, the run with the most fights won (not the
  level reached: the starting level is the player's own choice), stored with
  the name, the style's public name, the starting and the final level. A run
  that beats it (with at least one win) replaces it and gets a bold green
  "New record for {difficulty}!"; otherwise the current record is shown.
  Ties keep the older record.
- Music: Choosing a Style (the main game's setup tune) from the welcome
  screen through character creation, until the first fight.
- BACKLOG ("Minigames & far-future mods") has related ideas — turning RING
  scores into exp bonuses in the main game, a kumite mini-game, tournament
  betting with non-kung-fu styles — none implemented.

## Punching Bag — `kf_lib/minigames/_punching_bag.py`

One minute of fight time to deal as much damage as possible to a bag that
never fights back:

1. The welcome screen states the rules and the record. `new_custom_hcf(
   level=FIGHTER_LEVEL)` builds the fighter: a name, a generated style (the
   same menu as RING's) and a fixed level 10, reached through the usual
   interactive level-ups. The level is fixed so records compare like with
   like.
2. Each round is a `BagRound`, a `NormalFight` subclass: `TIME_LIMIT = 120`
   time units (60 s at `TIME_TO_SEC_DIVISOR` 2), no environment, no items,
   no prefight quotes, the Bamboo Courtyard tune (`fight_music`). The move
   menu's title shows the clock ("time left: 0:42", via `get_turn_note`).
   The engine checks the limit before anyone's next move starts, so no move
   begins after the bell. A gong (`gong_clash`) ends the round instead of
   the victory jingle, and a score screen replaces the win message: damage
   (the HP the bag lost), strikes landed, the hardest blow and its move,
   criticals and epics. The usual post-fight menu (stats, timeline,
   slideshow) follows.
3. "Another round?" repeats the round with the same fighter (HP, stamina
   and qi are reset by the fight, as always), so the level-ups happen once.

- The bag (`PunchingBag`, a `Fighter` on 'No Style') has 9999 HP, no
  toughness or damage reduction, and zero dodge and block chances, so every
  strike that doesn't fail lands in full. The round never queues it, so it
  never takes a turn (no "Punching Bag: Do Nothing" screens). It can't fall,
  lose balance, be stunned, shocked or slowed (those `cause_*` methods are
  no-ops) and never counters or speaks. `is_living = False` makes the
  engine skip bleeding and stamina damage ("gasps for breath!") on it. Heavy
  pushes and knockback moves still swing it away, so footwork matters. A
  single blow can't take its last HP, which only an instant knock-out could
  (lethal moves are far above level 10).
- What decides the score: affordable high-power moves, keeping stamina and
  qi up (Catch Breath and Focus cost time too), closing the distance after
  knockbacks, and luck with criticals and epics. Measured 2026-11 with the
  first menu option everywhere (8 fighters × 5 rounds): about 1,100 damage
  on average; one fighter's rounds ranged 489–1,403, and the build
  mattered (one fighter averaged about 1,900, another about 600).
- Records: the best damage, with the name and the style's public name; a
  better round gets a bold green "New record!".
- Music: Bamboo Courtyard (the main game's practice tune) from the welcome
  screen on; the round's end stops it with the gong, and it comes back for
  "Another round?".
