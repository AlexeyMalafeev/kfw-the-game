# Dev scripts

Developer utilities in `dev_scripts/`: move generation, profiling, balance
harnesses, fight-AI training/evaluation, and the ML experiment runners.
Sources: `dev_scripts/` itself plus the modules the scripts drive —
`kf_lib/testing/testing_tools.py`, `kf_lib/ai/fight_ai_gen.py`,
`kf_lib/ai/fight_ai_test.py`, `ml/ml_fighter_pwr.py`. Items marked ⚠️ look
unintentional or surprising — verify before building on them.

All verdicts below were verified 2026-09 by actually running each script with
`.venv/bin/python` (details per script). Tracked report files overwritten
during verification were restored with `git checkout`; no run artifacts were
left behind (`git status` clean).

## Shared conventions

- Every script except `try_rich.py` starts with the same hack as the
  minigames (see `docs/minigames.md`): it resolves `Path('..')` (top-level
  scripts) or `Path('..', '..')` (`ai/`, `ml/`, `testing/`) from the cwd,
  chdirs there and appends it to `sys.path`. **Run each script from its own
  directory**, e.g.:

  ```
  cd dev_scripts         && ../.venv/bin/python move_gen.py
  cd dev_scripts/ai      && ../../.venv/bin/python run_fight_ai_test.py
  cd dev_scripts/ml      && ../../.venv/bin/python ML_gen_data.py
  cd dev_scripts/testing && ../../.venv/bin/python run_test_fb.py
  ```

  Run from the repo root they chdir one level too far up and die with
  `ModuleNotFoundError: No module named 'kf_lib'` (verified for
  `profile_game.py`).
- ⚠️ The chdir happens *before* the script body, so any `'../../...'` path
  written later resolves against the repo root, not the script's directory —
  several scripts therefore aim their outputs *outside* the repo (details per
  script).
- Most scripts end with `input('Press Enter to exit')` — harmless with piped
  stdin if you send one newline (`echo | ...`), an EOFError otherwise.
- Interactive prompts (`ui.menu`/`ui.yn`) go through termios
  (`kf_lib/ui/_keyboard.py`) and need a real TTY, same TTY pitfall as the
  minigames.
- ⚠️ The output dirs `tests/genetic/` and `tests/AI actions/` are gitignored
  and never created by any code (`kf_lib/utils/_folders.py` mkdirs only
  `moves/` and `tests/`) — two scripts below crash on exactly this.

## count_lines.py

Counts non-empty lines in every `.py` file under the repo and prints the
totals. Run: `cd dev_scripts && ../.venv/bin/python count_lines.py`.

**Broken.** It walks *every* directory at the repo root with no filtering —
including `.venv/` — and dies with `UnicodeDecodeError` on the first
non-UTF-8 file (verified: exits 1 at line 20 on
`.venv/.../joblib/test/test_func_inspect_special_encoding.py` and friends).
⚠️ Even with the encoding fixed, the count would include `.venv/`, `.git/`
and any other stray directory, so the number was never meaningful since the
venv moved inside the repo. The leading `print(os.getcwd())` is a debug
leftover.

## move_gen.py

Regenerates `moves/all_moves.txt` (and `all_moves.csv`) from the hand-edited
sources. The generation pipeline itself — prefix functions, the combination
matrix, tier/qi scaling, quality variants — is documented in
`docs/kung_fu.md` ("Procedural move generation"); this section is only about
running it.

- Run: `cd dev_scripts && ../.venv/bin/python move_gen.py`. Needs pandas
  (dev venv). Takes seconds; prints `generated N moves` and waits on
  `input()`.
- Reads `moves/base_moves.txt`, `extra_moves.txt`, `style_moves.txt`,
  `move_word_combinations.csv`. Writes `moves/all_moves.txt`,
  `moves/all_moves.csv` — and also **rewrites the three source files in
  place** (reformatting them through `save_moves`).
- ⚠️ Output is not byte-deterministic: feature sets are `repr()`'d in hash
  order, so a no-change regeneration rewrites all four tracked files with
  pure set-ordering churn (`{'charging', 'acrobatic'}` →
  `{'acrobatic', 'charging'}`, ~25k diff lines, varies with
  `PYTHONHASHSEED`). Verified 2026-09; the files were restored with
  `git checkout`. Don't commit a regeneration unless the content actually
  changed.
- Works: ran to completion, exit 0 (`generated 13844 moves`). Note the
  footer count (13,844 rows) vs `ALL_MOVES_DICT` (13,841 entries) — three
  generated names collide and overwrite on registration.

## profile_game.py

cProfile wrapper around a headless autoplay game. Shows a two-option menu
("Sorting?": `cumulative` / `calls`), then shells out
`{sys.executable} -m cProfile -s <sorting> kfw.py --autoplay --silent-ending`
and saves to `tests/profile_<sorting>.txt`.

- Run: `cd dev_scripts && ../.venv/bin/python profile_game.py`. The menu
  needs a real TTY (termios).
- ⚠️ The module docstring says "Run from anywhere: `python
  dev_scripts/profile_game.py`" — false: it has the same `Path('..')` hack
  as the rest, and from the repo root it dies with `ModuleNotFoundError:
  kf_lib` (verified).
- `tests/profile_calls.txt` is a committed sample; `profile_cumulative.txt`
  is untracked — don't commit either blindly.
- Works: verified via a pty-driven run (answered the menu, full profile
  completed: ~6.5M function calls, ~1.7 s of game time). The output file
  created during verification was deleted.

## try_rich.py

Three-line smoke test for the `rich` package (prints a colored "Hello
world", waits on `input()`). The only script without the chdir hack — it
imports nothing from `kf_lib`.

**Broken**: `rich` is not installed in the dev venv and is absent from
`requirements_dev.txt` → `ModuleNotFoundError` at line 1 (verified). It's a
leftover of an abandoned rich experiment: `kf_lib/ui/_rich_format.py` is an
empty file star-imported by `ui/__init__.py`, and the only other trace is a
commented-out `from rich import print` in
`kf_lib/actors/human_controlled_fighter.py`.

## ai/ — fight-AI and AI-player runners

Thin wrappers over `kf_lib/ai/` and `kf_lib/game`; all use the
`Path('..', '..')` version of the chdir hack.

⚠️ Shared defect: the `except` handlers in `collect_AIP_data.py` and
`compare_AIPs.py` write `'../../errors.txt'` — post-chdir that is the repo's
*grandparent* directory, i.e. outside the repo (verified: running
`collect_AIP_data.py` created `~/errors.txt`; removed). On crash they also
try `g.save_game('emergency_save.txt')`.

### collect_AIP_data.py

Plays 100 AI-only games (`game.Game().new_game(ai_only=True, ...)`) with a
random AI-player class. Despite the name it **persists nothing** on success —
no stats file, no aggregation; it's a soak/crash-hunting runner whose only
output is `i / 100` progress lines.

**Effectively broken**:

- Headless it dies immediately: `new_game` is called without
  `generated_styles=`, so every one of the 100 games asks "Randomly
  generated styles?" through the termios menu → `termios.error` at the first
  prompt with piped stdin (verified).
- Under a TTY it *runs*, but you must answer the styles prompt 100 times
  (verified via pty: answering "yes" lets games complete, one prompt per
  game).
- ⚠️ Answering "no" (the 20 default styles) crashes game 1 during worldgen:
  `AttributeError: 'Fighter' object has no attribute 'critical_mult'`. Root
  cause is a latent kf_lib content bug, not the script: the 'Eagle Claw III'
  tech (`kf_lib/kung_fu/styles.py:114`) passes `critical_mult=b.CRIT_M1`,
  but the Fighter attribute is named `critical_dam_mult`
  (`fighter/_abc.py`); stale since commit `78cf89a` (2022-02). Because
  school masters are level 11–14 and learn style techs at creation
  (`fighter_factory.new_master`), **any new game with default styles crashes
  in `_init_schools`** (verified: `new_game(generated_styles=False)` and
  `new_master(..., 'Eagle Claw')` both raise). Autoplay and the pytest suite
  never see it because `kfw.py --autoplay` passes `generated_styles=True`.

### compare_AIPs.py

Would play 100 AI-only games for each of `BaselineAIP`, `SmartAIP`,
`LazyAIP`, `VanillaAIP` and write average `n_days_to_win` per class to
`'AI players comparison.txt'`.

**Broken at line 14** (verified by running): `game.BaselineAIP` doesn't
exist — `kf_lib/game/__init__.py` re-exports only `Game`; the AIP classes
live in `kf_lib/actors/player`. The `AttributeError` fires inside the `try`,
so the handler runs and writes its traceback outside the repo (see above;
cleaned up after verification).

- ⚠️ Even with the import fixed, the output would land in the repo root
  (post-chdir cwd), not in `tests/` where the committed sample
  `tests/AI players comparison.txt` lives.
- Also inherits both problems of `collect_AIP_data.py` (per-game styles
  prompt; Eagle Claw crash on default styles).

### run_fight_ai_gen.py

Trains fight-AI weights with the hand-rolled genetic algorithm
(`kf_lib/ai/fight_ai_gen.py`). Two runs back to back, 128 generations each:

1. `pop_size=16, n_fights_1on1=8, n_fights_crowd=2, infighting=True` —
   every individual fights every other (4,800 fights per generation, ~615k
   total);
2. `pop_size=32, n_fights_1on1=64, n_fights_crowd=16, infighting=False` —
   against the current `DefaultFightAI` (~1.3M fights total).

`output()` dumps the top half of each generation (fit values, gene vectors,
all-time record) to `tests/genetic/pop=... fights=... n_gen=... gen=N.txt`.

**Broken at the end of generation 1** (verified end-to-end: generation 1
completed within a 280 s timeout, then crashed): `tests/genetic/` is
gitignored and never created, so `output()` raises `FileNotFoundError`.
`mkdir tests/genetic` would unblock it (not done — no code changes).

- ⚠️ `output()` also assumes a record was set in generation 0: if every
  fitness score is 0, `record_generation` stays `None` and `output()` raises
  `TypeError: ... NoneType + int` before even reaching the file write (found
  with a synthetic 2-individual run).
- The committed `tests/fight_ai_gen output*.txt` logs predate the current
  per-generation file naming.
- Budget note: nothing here is interrupt-safe — a crash loses all
  generations since the last `output()` (which, today, means everything).

### run_fight_ai_test.py

Round-robin evaluation of 9 fight-AI classes (`BaseAI`, `GeneticAIAggro`,
`GeneticAIMoreAggro`, and six `GeneticAIMoreAggroTrained*` variants — all
still present in `kf_lib/ai/fight_ai.py`) over two harnesses from
`kf_lib/ai/fight_ai_test.py`: `CrowdVsCrowdFair` (4–9 equal allies per side)
and `FightAITest` (1v1), `rep=1000` per pairing, each rep effectively
doubled by swapping which fighter uses which AI (~144k fights in total).
Per-pair results are appended to `tests/fight ai test.txt` (tracked); the
final sorted tables are meant to overwrite `tests/fight AI comparison.txt`.

**Broken on the first fight** (verified): it runs with `write_log=True`, and
`BaseAI.__init__` then opens `tests/AI actions/<AIClass>.txt` for append —
`tests/AI actions/` is gitignored and never created → `FileNotFoundError`.
Setting `write_log = False` (line 17) would presumably unblock the run (not
verified end-to-end; not changed).

- ⚠️ The final comparison write uses `Path('../../tests', 'fight AI
  comparison.txt')`, which post-chdir resolves *outside* the repo — the
  tracked `tests/fight AI comparison.txt` would not be updated even if the
  run completed.
- Verification run appended 3 header lines to the tracked
  `tests/fight ai test.txt`; restored with `git checkout`.

## ml/ — ML fight-outcome prediction runners

`dev_scripts/ml/` holds only thin runners; the implementation is the
top-level `ml/` package (`ml/ml_fighter_pwr.py`, empty `__init__.py`):
feature extraction (15 features — per-side level/atts/techs/crowd/weapon
absolutes plus ratios, label = side_a wins), data generation, and sklearn
learners. The committed datasets and reports live in `ml/` (see AGENTS.md:
"ML fight-outcome prediction experiment; not needed to play").

### ML_gen_data.py

`cd dev_scripts/ml && ../../.venv/bin/python ML_gen_data.py` — runs
`ml_fighter_pwr.generate_data(examples=10000)`: 10,000 random `AutoFight`s
(levels 1–20, crowd sizes up to 8, 50% group fights, 10% weapon chance,
75% tech-style fighters), one CSV row per fight, written to
`ml/ML_fight_data m=10000, lv=1-20, max_crowd=8.csv` — a **tracked file the
script truncates on startup**.

Works: verified — ran to completion in under two minutes ("Successfully
generated 10000 examples"), then the CSV was restored with `git checkout`.
⚠️ Runs are not reproducible: `ml_fighter_pwr` sets `np.random.seed(0)`, but
the fight RNG is the `random` module (`kf_lib/utils/_random.py`), so each
run produces a different dataset.

### ML_learn.py

`cd dev_scripts/ml && ../../.venv/bin/python ML_learn.py` — would train a
RandomForest and a LogisticRegression on the m=10000 dataset with three
feature subsets (all / 5 ratios / 10 absolutes) and write
`ml/ML report {RFC,LR} m=10000 n={5,10,15}.txt` plus LR coefficient files —
overwriting six committed sample reports.

**Broken** (verified): the input path is hardcoded as
`'../../ml/ML_fight_data m=10000, ...csv'`, which post-chdir resolves
outside the repo → `FileNotFoundError` at the first `pd.read_csv`. The
script exits through its `except` + `input()` handler.

## testing/ — balance harnesses

Thin wrappers around `Tester` (`kf_lib/testing/testing_tools.py`); all write
tracked reports into `tests/` (which AGENTS.md correctly describes as
committed logs, not test code). Run from `dev_scripts/testing/`.

### run_test_fb.py — fight balance

`test_fight_balance(rand_actions=False, n=10000)`: 10,000 mirror matches —
two fresh random fighters at the *same* random level (1–20), both driven by
the default fight AI (`rand_actions=False`; `True` would use uniform-random
`BaseAI`). For winners vs losers separately it tallies: sums of the four
base atts and full atts, a histogram of att spread (max − min), tech
description features ("style buffs"), upgradable techs, advanced techs, and
move features. Each category is emitted as a `compare_dicts` table —
`D1` = winner count, `D2` = loser count, `Diff%`, `Sum` — printed to stdout
and appended to `tests/test f.b. rand.act.=False n=10000.txt` (tracked).

How to read: in a balanced game every `Diff%` hovers near 0; a persistent
bias marks things that win or lose fights (the verified run:
`'ultra short'` moves at −13.5%, `'takedown'` at −5.6%, i.e. losers had them
more often). Committed samples exist for n = 50…50000.

Works: verified — ran to completion within a 280 s timeout; the
overwritten tracked report was restored.

### run_test_lv_vs_crowds.py

`test_level_vs_crowds(n_fights=100)`: how one fighter levels 1–20 fares
against crowds of 2–5 opponents, for each crowd-member level 1–5 — 100
fights per cell, 40,000 fights total. Fights are NPC-vs-NPC, so they resolve
headless as `AutoFight`s. One file per crowd level:
`tests/lv_vs_crowd {1..5} 100.txt` (tracked); rows = lone-fighter level,
columns = crowd size, cells = win percentage.

Works: verified — all five tables completed within a 280 s timeout (the
committed samples match this shape); all five overwritten reports were
restored.

### run_test_level_sign.py

`test_level_significance(rep=100)`: the full 20×20 level-vs-level 1v1
matrix, 100 fights per cell (40,000 fights), followed by a second table with
+1 smoothing (`(wins+1)/(rep+1)`) to soften the 0%/100% cells. Output:
`tests/test level significance rep=100.txt` (tracked). Read row `lv1`,
column `lv2` as "lv1 beats lv2 in x% of fights" — the gradient shows how
much a level gap is worth (verified run: level 20 beats everything up to
~level 14 at 100%).

Works: verified — ran to completion within a 280 s timeout; the overwritten
tracked report was restored.

## Summary

| Script | Runs today | Verified by |
|---|---|---|
| `count_lines.py` | No — `UnicodeDecodeError` walking `.venv/` | ran, crashed at line 20 |
| `move_gen.py` | Yes — but nondeterministic churn in 4 tracked files | ran to completion, exit 0; restored |
| `profile_game.py` | Yes — from `dev_scripts/`, needs a TTY | pty-driven run to completion; also verified it fails from repo root despite its docstring |
| `try_rich.py` | No — `rich` not installed | ran, `ModuleNotFoundError` |
| `ai/collect_AIP_data.py` | Only interactively ("yes" × 100); persists nothing; default styles crash | headless `termios.error`; pty runs both ways (game completes / `critical_mult` crash) |
| `ai/compare_AIPs.py` | No — `game.BaselineAIP` doesn't exist | ran, `AttributeError` at line 14 |
| `ai/run_fight_ai_gen.py` | No — crashes after generation 1 (`tests/genetic/` missing) | full generation 1, then `FileNotFoundError` |
| `ai/run_fight_ai_test.py` | No — crashes on first fight (`tests/AI actions/` missing) | `FileNotFoundError` on startup; `tests/fight ai test.txt` append restored |
| `ml/ML_gen_data.py` | Yes | ran to completion (10,000 rows, < 2 min); CSV restored |
| `ml/ML_learn.py` | No — `'../../ml/...'` resolves outside the repo | ran, `FileNotFoundError` |
| `testing/run_test_fb.py` | Yes | n=10000 ran to completion; report restored |
| `testing/run_test_lv_vs_crowds.py` | Yes | all 5 tables ran to completion; reports restored |
| `testing/run_test_level_sign.py` | Yes | full 20×20 matrix ran to completion; report restored |
