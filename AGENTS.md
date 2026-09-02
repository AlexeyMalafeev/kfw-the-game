# KFW (Kung-Fu World)

Turn-based hot-seat text RPG set in a fantasy kung-fu world. Pure Python, no runtime
dependencies for playing (pandas/numpy/scikit-learn only for the optional ML tooling).
In development on and off since 2013; the code carries significant tech debt — change
things incrementally and verify by playing, not by test suite (there is none).

Minimum Python: 3.8. Dev venv: `.venv` (see `requirements_dev.txt`).

## Running the game

All scripts **must be run from the repo root** — moves, quotes and saves use
cwd-relative paths.

- `python NG_default.py` — normal interactive game
- `python load_game.py` — load `save/save.txt` (also `load_auto_save.py`, `load em save.py`)
- `python NG_autoplay.py` — headless AI-only game; the de-facto smoke test
- `python NG_autoplay_crowd.py` — 100-player stress test
- `python NG_autoplay_silent_ending.py` — fast quiet autoplay (used for profiling)

There is a small pytest suite in `test/` (run `.venv/bin/python -m pytest` from the
repo root): seeded deterministic fights, generation invariants, and a full headless
autoplay game as an integration test. After any change, run it — and for riskier
changes also `NG_autoplay_silent_ending.py`. `kf_lib/ai/fight_ai_test.py` and
`kf_lib/testing/` provide manual balance/benchmark harnesses (their output goes to
`tests/`, which holds committed logs, not test code).

## Layout

- `kf_lib/actors/fighter/` — `Fighter` composed from ~17 private mixin modules
  (`_fight_actions.py`, `_strike_mechanics.py`, `_techs.py`, ...); API contract in `_abc.py`
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
- `docs/` — `version_history.md` (changelog conventions), `known bugs.txt`,
  combat/content design notes; the structured backlog lives at repo root
  (`BACKLOG.md`)

## Conventions

- Formatting: black-ish at 88 cols, but not enforced and no config; match surrounding style
- Private modules use a leading underscore; public API is re-exported through `__init__.py`
- Absolute imports across packages (`from kf_lib.actors import fighter_factory`),
  relative within a package (`from ._base_game import BaseGame`)
- Leaf packages (`utils`, `ui`, `constants`) must not import upward — layering is by
  convention, there are no cycle guards
- Commit messages: conventional commits (`fix:`, `docs:`, `refactor:`, `chore:`, `RELEASE:`)

## Pitfalls — read before editing

- **Save files are executable Python**, `exec()`ed line by line on load
  (`kf_lib/game/_load_game.py`). Saves serialize via constructor-call strings.
  Consequences:
  - Never reorder `Fighter.__init__` arguments (explicit warning at
    `kf_lib/actors/fighter/__init__.py`) — old saves break
  - Renaming classes or changing `savable_atts` / `get_init_string()` breaks old saves
- **Import-time side effects**: `kung_fu/moves.py` reads `moves/all_moves.txt`,
  `actors/quotes.py` reads `quotes/*.txt`, `utils/_folders.py` mkdirs folders, and
  `utils/__init__.py` configures a root logger writing `kfw.log`. Importing `kf_lib`
  from the wrong cwd fails or litters files.
- Runtime artifacts at repo root (`debug.txt`, `errors.txt`, `kfw.log`) are generated
  on crashes/runs; don't commit them.
- Terminal input goes through `kf_lib/ui/_keyboard.py` (msvcrt on Windows, termios
  elsewhere) — game scripts need a real TTY; piped stdin raises EOFError at prompts.
