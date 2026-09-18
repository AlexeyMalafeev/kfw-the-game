# Debug menu and crash reports

The in-game debug/cheat menu and the crash-report hook, as implemented. Source
files: `kf_lib/game/debug_menu.py` (the menu itself), `kf_lib/game/_state_menu.py`
(entry point), `kf_lib/testing/debug_tools.py` (crash report), `kfw.py` (top-level
exception hook). Items marked ⚠️ look unintentional or surprising — verify before
building on them.

## Opening the menu

There is no config flag and no key-combination cheat: the debug menu is a regular
option of the status screen, available in every build.

- During a human player's turn, the day-action menu (`HumanPlayer.choose_day_action`,
  `kf_lib/actors/player/_human_player.py`) always ends with `Rest` (key `r`) and
  `State` (key `s`).
- `State` calls `Game.state_menu` (`kf_lib/game/_state_menu.py`), which prints the
  current player's full info and offers two rows of hotkeys:
  `i a m t [s] b` (`Items / Accomplishments / Moves / Techniques / [Students] /
  Back`) on the first line and `S L Q X D [F]` (`Save / Load / Quit / Save and
  Quit / Debug Menu / [Finish Game]`) on the second. Moves, techniques and
  accomplishments are listed enumerated (`1.`, `2.`, …). After viewing items,
  accomplishments, moves, techniques or students (and after saving or leaving
  the debug menu) the state menu is shown again; only `Back`, `Load`, `Quit`,
  `Save and Quit` and `Finish Game` exit it. Pressing `D` runs
  `self.debug_menu()`; `a` lists the player's accomplishments with dates
  (`get_accompl_info`).
- `Game.debug_menu` is a `DebugMenu(self)` instance created in
  `BaseGame.__init__` (`kf_lib/game/_base_game.py`); `DebugMenu.__call__` shows
  the menu and invokes the chosen bound method.

The menu operates on `game.current_player` — the player whose turn it is
(hot-seat: each human gets it on their own turn). AI-only autoplay games never
reach it, since `choose_day_action` is a `HumanPlayer` method.

`state_menu` returns `None`, so in the game loop (`Game.game_loop`,
`kf_lib/game/_playing.py`) the day action is *not* consumed: after any debug
option you land back at the day-action prompt with the day still unspent.

The debug menu ends with a **Back** option that returns to the state menu
without activating any debug tool.

## Menu options

Thirteen options, in menu order (`DebugMenu.__call__`). None of them sets any
"cheated" flag on the game or the save.

- **Get Money** — `get_int_from_user` for 1–10⁹, then `p.earn_money(amount)`
  (`_base_player.py`): adds to `p.money`, and — not silently — increments the
  `money_earned` stat and writes `Earns N c.` to the player log.
- **Get Item** — pick from all real item names (`sorted(items.all_items)`) plus
  `items.MOCK_ITEMS`, quantity 1–10⁹, then `p.obtain_item(name, qty)` (updates
  `inventory`, logs, bumps `items_obtained` stat). The three mock items
  (`constipation medicine` etc., `kf_lib/things/items.py`) cannot be used
  directly — they are not in `all_items`/`EFFECTS`, and fight-item selection
  filters `FIGHT_ITEMS` — but they are not useless: the `Weirdo` encounter
  (`kf_lib/happenings/encounters/_items.py`) asks for a random mock item and
  trades it for a Super Booster.
- **Level up** — 1–100 levels via `p.level_up(n)`. This is the real level-up
  path (`HumanPlayer.level_up` → `BasePlayer.level_up` → `Fighter.level_up`):
  per level it runs `upgrade_att` (interactive for humans),
  `resolve_techs_on_level_up` and `resolve_moves_on_level_up`, and recomputes
  `next_level`. Only exp is bypassed.
- **Learn Move** — free-form string fed to `resolve_move_string(move_s, p)`
  (`kf_lib/kung_fu/moves.py`): a digit means "random pool of that tier", an
  exact move name learns it directly, a comma list means `[tier,] features…`
  (tier defaults to the player's current tier), a blank string means a random
  pool of the player's tier. Pool cases go through the normal
  `choose_new_move` selection menu; `IndexError` (e.g. empty pool) is caught
  and only logged to `kfw.log` — from the user's seat the option silently does
  nothing. Input that is neither blank, a tier digit, a comma-separated
  feature list nor an exact move name (i.e. a typo) is rejected up front with
  `No such move: ...` instead of silently falling into the "random pool"
  branch (`MoveNotFoundError` itself is raised only by `get_move_obj`, which
  `resolve_move_string` does not use).
- **Learn Tech** — pick from `techniques.get_all_techs_dict()` (all techs in
  the game, alphabetically), then `p.learn_tech(tech)` (`fighter/_techs.py`):
  applies the tech's attribute deltas immediately; already-known techs are
  skipped. Level/style prerequisites are not checked.
- **Fight Thug(s)** — 1–20 thugs from `fighter_factory.new_thug(n=n)` (random
  level in `THUG_LV`, Dirty Fighting style). One thug: `p.fight(thug)`;
  several: `p.fight(thugs[0], en_allies=thugs[1:])`. This is a real
  `NormalFight` via the `fight()` helper — full exp, injuries and stats apply;
  losing genuinely injures the player. Not a sandbox.
- **Tournament** — prompts for participants (2–20), fee (0–10000) and level
  range, then constructs `tournament.Tournament(...)`, which runs the entire
  tournament inside `__init__` (`self.run()`): all active players are asked to
  join and pay the fee, brackets are fought, bets placed and resolved.
  If nobody joins (the level range matches no one and the players decline),
  `run()` prints `...but nobody shows up, so the tournament is canceled.` and
  aborts cleanly.
- **Encounter** — pick any class from `all_random_encounter_classes`, run as
  `enc_class(p, check_if_happens=False)`: `BaseEncounter.__init__` skips the
  trigger conditions and runs the encounter immediately, also incrementing
  `game.enc_count_dict` (a saved attribute, so debug encounters pollute the
  encounter statistics in saves).
- **Story** — pick from `get_all_stories()`, then run the *registered*
  instance from `game.stories` (created by `_init_stories`):
  `start(current_player)` + `advance()` in a loop until `state == -1` (i.e.
  until some scene calls `story.end()`). A story that has already started is
  refused. The level gate (`story.test()`) is intentionally not checked —
  testing stories off-level is the point of the debug option. If the story
  crashes mid-run, the player is detached (`p.current_story = None`), the
  boss is deleted and the story state is reset to `None` before the exception
  propagates, so the save's story links stay consistent and the story can
  trigger normally later.
- **Inspect Player** — type an attribute name to `pprint` its value and type,
  or `all` to dump `vars(p)`. Read-only; unknown names just print
  `No such attribute!`.
- **Set Attribute** — type an attribute name; if `hasattr(p, att)` passes and
  the attribute is not callable (methods are refused), the value is read with
  `input()`, parsed with `ast.literal_eval` (literals only, so no arbitrary
  code execution; unparseable input is rejected with a message) and stored
  with `setattr`. A wrong-typed literal (e.g. a string into `money`, an int
  into `moves`) still corrupts state silently and typically crashes later or
  poisons the save — it is a debug tool, not a validator.
- **Spar** — pick any other player (human or AI), then `p.spar(opp)`. This is
  *sparring* (`fighting/fight/_sparring.py`), not a real fight — injuries,
  gossip, stats and accomplishments are disabled, but exp is still awarded
  (sparring gives exp by design).
- **Back** — returns to the state menu without doing anything.

## Crash reports

`kfw.py` wraps everything after `Game()` construction in a bare
`except Exception:` that calls `crash_report(g)`
(`kf_lib/testing/debug_tools.py`; added in v0.6.1 per CHANGELOG). On any
uncaught exception it:

1. Prints the traceback to the console and appends it to `errors.txt`
   (cwd-relative → repo root in normal use), preceded by a timestamp — crash
   history is kept across runs instead of keeping only the latest crash. All
   files are written inside `with` blocks.
2. Writes `debug.txt` the same way: timestamp plus `pprint(vars(game_inst))` —
   a full dump of the `Game` god-object, relying on everything in it being
   printable.
3. Attempts `game_inst.save_game('emergency_save.txt')` (into the `save/`
   folder). A failure is swallowed by a bare `except` that only shows
   `-FAILED TO SAVE GAME-`. Since the save runs *after* the crash, whatever
   corruption caused the crash may be baked into the emergency save — a
   possibly-tainted save is still considered better than no save.
4. Waits for Enter, then returns — the exception is never re-raised, so the
   process exits with status 0 after a crash (deliberate: a crashed game
   session should still feel like a graceful exit to the player).
   `KeyboardInterrupt` (Ctrl-C) is not an `Exception`, so it bypasses the
   crash report entirely.

## Related: get_key debug mode

`kf_lib/ui/_keyboard.py` has a commented-out `# DEBUG MODE` line in `get_key()`
that replaces raw `getch()` with `input('key:')` (v0.6.3 changelog: "debug mode
in user input"). It is a source-edit toggle for piping/scripting input, not a
runtime feature, and is unrelated to the debug menu above.
