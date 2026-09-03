# KFW (Kung-Fu World)

Turn-based hot-seat text RPG set in a fantasy kung-fu world. Pure Python, no runtime
dependencies for playing (pandas/numpy/scikit-learn only for the optional ML tooling).
In development on and off since 2013; the code carries significant tech debt — change
things incrementally and verify with the pytest suite in `test/` plus autoplay runs.

Minimum Python: 3.8. Dev venv: `.venv` (see `requirements_dev.txt`).

## Running the game

All scripts **must be run from the repo root** — moves, quotes and saves use
cwd-relative paths.

- `python kfw.py` — single entry point (argparse: `--autoplay`, `-n N`,
  `--autosave`, `--silent-ending`, `--load FILE`); the only script at repo root

There is a small pytest suite in `test/` (run `.venv/bin/python -m pytest` from the
repo root): seeded deterministic fights, generation invariants, and a full headless
autoplay game as an integration test. After any change, run it — and for riskier
changes also `python kfw.py --autoplay --silent-ending`. `kf_lib/ai/fight_ai_test.py` and
`kf_lib/testing/` provide manual balance/benchmark harnesses (their output goes to
`tests/`, which holds committed logs, not test code).

## Layout

- `kf_lib/actors/fighter/` — `Fighter` composed from ~17 small private mixin modules
  (`_fight_actions.py`, `_strike_mechanics.py`, `_techs.py`, ...). `_abc.py` defines
  `FighterAPI`, an ABC every mixin inherits: it declares the full attribute/method
  surface with types. Audited 2026-09: all 153 abstract methods implemented, no
  attribute drift — keep new attributes/methods declared there when adding them.
  Fighters have an `occupation` attr ('fighter'/'thug'/'master'/'challenger'/'hero')
  that drives quote selection.
- `kf_lib/actors/player/` — `HumanPlayer` and AI player variants (`SmartAIP` etc.)
- `kf_lib/actors/fighter_factory.py` — NPC constructors (`new_opponent`, `new_thief`, ...)
- `kf_lib/ai/` — fight AI heuristics + hand-rolled genetic algorithm (`fight_ai_gen.py`)
- `kf_lib/fighting/fight/` — fight engine: `BaseFight`, `AutoFight` (headless), `NormalFight`
- `kf_lib/game/` — `Game` god-class (`_game.py`) = LoadGame + NewGame + Playing + SaveGame + StateMenu
- `kf_lib/happenings/` — content: `encounters/` (random street encounters), `story/`
  (quest lines), `events.py`, `tournament.py`
- `kf_lib/kung_fu/` — moves, styles, techniques, boosts; loads `moves/all_moves.txt` at import
- `kf_lib/ui/` — terminal UI; `kf_lib/utils/` — helpers; both star-export via `__init__.py`
- `moves/` — move source data. Edit the `*_moves.txt` files, regenerate with
  `dev_scripts/move_gen.py` (see `moves/_moves_readme.txt`); `all_moves.txt` is generated
- `quotes/` — dialogue text files loaded at import
- `dev_scripts/` — dev utilities (each starts with a `Path('..')` chdir/sys.path hack)
- `ml/` — ML fight-outcome prediction experiment; needs the dev venv, not needed to play
- `minigames/` — standalone prototypes, not wired into the game
- `docs/` — `known bugs.txt`, combat/content design notes; changelog lives at
  repo root (`CHANGELOG.md`, Keep-a-Changelog-ish with release codenames),
  the structured backlog in `BACKLOG.md`

## Conventions

- Formatting: black-ish at 88 cols (`pyproject.toml` has the black config; the old
  code is only approximately formatted — match surrounding style, don't mass-reformat)
- Private modules use a leading underscore; public API is re-exported through `__init__.py`
- Absolute imports across packages (`from kf_lib.actors import fighter_factory`),
  relative within a package (`from ._base_game import BaseGame`)
- Leaf packages (`utils`, `ui`, `constants`) must not import upward — layering is by
  convention, there are no cycle guards
- Commit messages: conventional commits (`fix:`, `docs:`, `refactor:`, `chore:`, `RELEASE:`)

## Pitfalls — read before editing

- **Save files are JSON**, written by `kf_lib/game/_save_game.py` (fighters via
  class name + `get_init_atts()` constructor args, cross-references by fighter
  name; a fighter's `occupation` is stored as a separate optional key so the
  constructor args keep their legacy shape). `load_game()` auto-detects the
  format: old saves are executable Python and are loaded by a legacy shim that
  `exec()`s them line by line (`LoadGame._load_legacy`). Consequences while the
  shim exists:
  - Never reorder `Fighter.__init__` arguments (explicit warning at
    `kf_lib/actors/fighter/__init__.py`) — old saves break
  - Renaming classes or changing `savable_atts` / `get_init_atts()` breaks saves;
    removed fighter classes (Challenger/Master/Thug) stay mapped to factory
    shims in `LoadGame.FIGHTER_CLASSES`
- **Import-time side effects**: `kung_fu/moves.py` reads `moves/all_moves.txt`,
  `actors/quotes.py` reads `quotes/*.txt`, `utils/_folders.py` mkdirs folders, and
  `utils/__init__.py` configures a root logger writing `kfw.log`. Importing `kf_lib`
  from the wrong cwd fails or litters files.
- Runtime artifacts at repo root (`debug.txt`, `errors.txt`, `kfw.log`) are generated
  on crashes/runs; don't commit them.
- Terminal input goes through `kf_lib/ui/_keyboard.py` (msvcrt on Windows, termios
  elsewhere) — game scripts need a real TTY; piped stdin raises EOFError at prompts.
