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
  current player's full info and offers
  `Items / Back / Save / Load / Quit / Save and Quit / Debug Menu`
  with keys `ibslqxd`. Pressing `d` runs `self.debug_menu()`.
- `Game.debug_menu` is a `DebugMenu(self)` instance created in
  `BaseGame.__init__` (`kf_lib/game/_base_game.py`); `DebugMenu.__call__` shows
  the 12-option menu and invokes the chosen bound method.

The menu operates on `game.current_player` — the player whose turn it is
(hot-seat: each human gets it on their own turn). AI-only autoplay games never
reach it, since `choose_day_action` is a `HumanPlayer` method.

`state_menu` returns `None`, so in the game loop (`Game.game_loop`,
`kf_lib/game/_playing.py`) the day action is *not* consumed: after any debug
option you land back at the day-action prompt with the day still unspent.

⚠️ The debug menu itself has no Back/cancel: `menu()` is called with the default
`weak=False`, so an unrecognized key just re-prompts. Once opened, the only way
out is to pick one of the 12 options (or kill the process).

## Menu options

All twelve options, in menu order (`DebugMenu.__call__`). None of them sets any
"cheated" flag on the game or the save.

- **Get Money** — `get_int_from_user` for 1–10⁹, then `p.earn_money(amount)`
  (`_base_player.py`): adds to `p.money`, and — not silently — increments the
  `money_earned` stat and writes `Earns N c.` to the player log.
- **Get Item** — pick from all real item names (`sorted(items.all_items)`) plus
  `items.MOCK_ITEMS`, quantity 1–10⁹, then `p.obtain_item(name, qty)` (updates
  `inventory`, logs, bumps `items_obtained` stat). ⚠️ The three mock items
  (`constipation medicine` etc., `kf_lib/things/items.py`) are plain flavor
  strings: they are not in `all_items`/`EFFECTS`, so they can never be used
  (fight-item selection filters `FIGHT_ITEMS`) — they sit in the inventory
  forever. Harmless: `get_inventory_info` only prints name and count.
- **Level up** — 1–100 levels via `p.level_up(n)`. This is the real level-up
  path (`HumanPlayer.level_up` → `BasePlayer.level_up` → `Fighter.level_up`):
  per level it runs `upgrade_att` (interactive for humans),
  `resolve_techs_on_level_up` and `resolve_moves_on_level_up`, and recomputes
  `next_level`. Only exp is bypassed.
- **Learn Move** — free-form string fed to `resolve_move_string(move_s, p)`
  (`kf_lib/kung_fu/moves.py`): a digit means "random pool of that tier", an
  exact move name learns it directly, a comma list means `[tier,] features…`
  (tier defaults to the player's current tier), anything else/blank means a
  random pool of the player's tier. Pool cases go through the normal
  `choose_new_move` selection menu; `IndexError` (e.g. empty pool) is caught
  and only logged to `kfw.log` — from the user's seat the option silently does
  nothing. ⚠️ No validation feedback on typos: a misspelled move name falls
  into the "random pool" branch instead of raising `MoveNotFoundError` (that
  exception is raised only by `get_move_obj`, which `resolve_move_string`
  does not use).
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
  ⚠️ If nobody joins (level range matches no one and the players decline),
  `run()` does `self.spectator = self.participants[0]` on an empty list —
  `IndexError`, straight to the crash hook.
- **Encounter** — pick any class from `all_random_encounter_classes`, run as
  `enc_class(p, check_if_happens=False)`: `BaseEncounter.__init__` skips the
  trigger conditions and runs the encounter immediately, also incrementing
  `game.enc_count_dict` (a saved attribute, so debug encounters pollute the
  encounter statistics in saves).
- **Story** — pick from `get_all_stories()`, then
  `story_class(self.g)` + `start(current_player)` + `advance()` in a loop until
  `state == -1` (i.e. until some scene calls `story.end()`). ⚠️ The story is a
  *new, detached instance* — it is not the registered instance in
  `game.stories` (created by `_init_stories`), and the level gate
  (`story.test()`) is never checked. If the story crashes mid-run,
  `p.current_story` still points at the detached instance: the save then
  records `current_story: <name>` while `stories` lacks that entry's state,
  and the loader's `self.stories[pdata['current_story']]` re-links to the
  *pristine* registered instance (state `None`) — the player is attached to a
  story that never started, with the boss gone.
- **Inspect Player** — type an attribute name to `pprint` its value and type,
  or `all` to dump `vars(p)`. Read-only; unknown names just print
  `No such attribute!`.
- **Set Attribute** — type an attribute name; if `hasattr(p, att)` passes, the
  value is read with `input()` and stored as `setattr(p, att, eval(val))`.
  ⚠️ Raw `eval()` on user input — arbitrary code execution by design, and any
  existing attribute (including methods) can be overwritten with anything.
  A wrong-typed value (e.g. a string into `money`, an int into `moves`)
  corrupts state silently and typically crashes later or poisons the save.
- **PvP** — pick any other player (human or AI), then `p.spar(opp)`.
  ⚠️ Misleadingly named: this is *sparring* (`fighting/fight/_sparring.py`),
  not a real fight — injuries, gossip, stats and accomplishments are disabled,
  but exp is still awarded (sparring gives exp by design).

## Crash reports

`kfw.py` wraps everything after `Game()` construction in a bare
`except Exception:` that calls `crash_report(g)`
(`kf_lib/testing/debug_tools.py`; added in v0.6.1 per CHANGELOG). On any
uncaught exception it:

1. Truncates `errors.txt` (cwd-relative → repo root in normal use) to the
   current timestamp, prints the traceback to the console, then appends the
   traceback to `errors.txt`. ⚠️ The truncate-then-append means only the
   *latest* crash is kept, and the file objects are never closed (CPython GC
   closes them; contents can be lost if the process is killed first).
2. Writes `debug.txt` the same way: timestamp plus `pprint(vars(game_inst))` —
   a full dump of the `Game` god-object, relying on everything in it being
   printable.
3. Attempts `game_inst.save_game('emergency_save.txt')` (into the `save/`
   folder). A failure is swallowed by a bare `except` that only shows
   `-FAILED TO SAVE GAME-`. ⚠️ Since the save runs *after* the crash, whatever
   corruption caused the crash is baked into the emergency save.
4. Waits for Enter, then returns — the exception is never re-raised, so the
   process exits with status 0 after a crash. ⚠️ Scripts/CI checking the exit
   code cannot tell a crash from a clean exit. `KeyboardInterrupt` (Ctrl-C) is
   not an `Exception`, so it bypasses the crash report entirely.

## Related: get_key debug mode

`kf_lib/ui/_keyboard.py` has a commented-out `# DEBUG MODE` line in `get_key()`
that replaces raw `getch()` with `input('key:')` (v0.6.3 changelog: "debug mode
in user input"). It is a source-edit toggle for piping/scripting input, not a
runtime feature, and is unrelated to the debug menu above.
