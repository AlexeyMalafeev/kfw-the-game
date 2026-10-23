# Dev scripts

Developer utilities in `dev_scripts/`: move generation, profiling, balance
harnesses, fight-AI training/evaluation, the ML experiment runners, and the
localization catalog tooling.
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
- ⚠️ The chdir happens *before* the script body, so any relative path in a
  script resolves against the repo root, not the script's directory —
  `'../../...'` literals in the script body therefore point *outside* the
  repo. Most instances found in 2026-09 were fixed; `ml/ML_learn.py` still
  has one (see its verdict below). Keep the gotcha in mind when adding paths
  to these scripts.
- Most scripts end with `input('Press Enter to exit')` — harmless with piped
  stdin if you send one newline (`echo | ...`), an EOFError otherwise.
- Interactive prompts (`ui.menu`/`ui.yn`) go through termios
  (`kf_lib/ui/_keyboard.py`) and need a real TTY, same TTY pitfall as the
  minigames.
- The output dirs `tests/genetic/` and `tests/AI actions/` are gitignored and
  not created by `kf_lib/utils/_folders.py` (which mkdirs only `moves/` and
  `tests/`), so the two scripts that need them
  (`ai/run_fight_ai_gen.py`, `ai/run_fight_ai_test.py`) mkdir them themselves
  before running.

## count_lines.py

Counts non-empty lines in every `.py` file under the repo and prints the
totals. Run: `cd dev_scripts && ../.venv/bin/python count_lines.py`.

Works: verified — walks the repo with `os.walk`, skipping `.venv/`, `.git/`,
`__pycache__` and other hidden dirs, and tolerates non-UTF-8 files
(`errors='ignore'`). (Before the 2026-09 fix it walked *every* directory,
including `.venv/`, and died with `UnicodeDecodeError` on the first
non-UTF-8 file.)

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
- Output is byte-deterministic: `save_moves` and the CSV dump repr feature
  sets in sorted order (`repr_deterministic`), so a no-change regeneration
  produces identical files regardless of `PYTHONHASHSEED` (verified 2026-09
  with two runs at different hash seeds). Don't commit a regeneration unless
  the content actually changed.
- Works: ran to completion, exit 0 (`generated 13845 moves`). Note the
  footer count (13,845 rows) vs `ALL_MOVES_DICT` (13,842 entries) — three
  generated names (`Sweep`, `Throw`, `Trip`) collide with the takedown moves
  from `extra_moves.txt` and overwrite on registration.

## profile_game.py

cProfile wrapper around a headless autoplay game. Shows a two-option menu
("Sorting?": `cumulative` / `calls`), then shells out
`{sys.executable} -m cProfile -s <sorting> kfw.py --autoplay --silent-ending`
and saves to `tests/profile_<sorting>.txt`.

- Run: `cd dev_scripts && ../.venv/bin/python profile_game.py`. The menu
  needs a real TTY (termios). From the repo root it dies with
  `ModuleNotFoundError: kf_lib` (the `Path('..')` hack lands outside the
  repo) — the module docstring says so; run it from its own directory.
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
leftover of an abandoned rich experiment whose only other trace is a
commented-out `from rich import print` in
`kf_lib/actors/human_controlled_fighter.py`. (The engine that eventually
shipped in v0.7.4 lives in `kf_lib/ui/_rich_format.py` — a hand-rolled,
dependency-free module that borrows rich's tag syntax but does not use the
package; see `docs/ui.md`.)

## i18n — localization catalog tooling

Tooling for the Russian localization (system described in `docs/i18n.md`);
all four use the top-level `Path('..')` chdir hack — run from `dev_scripts/`.
They operate on `locale/<lang>/LC_MESSAGES/{kfw,kfw_names}.po`, with the
compiled `.mo` files committed next to the sources.

### i18n_common.py

Shared library, not run directly: minimal .po parse/write helpers and a
pure-Python .po→.mo compiler, so catalog maintenance needs no gettext
binaries. Gotcha baked into it: the header `msgstr` must contain real
newlines — writing a literal `\n` sequence produces a catalog gettext
cannot parse (`UnicodeDecodeError` on the charset line).

### i18n_extract.py

`cd dev_scripts && ../.venv/bin/python i18n_extract.py` — AST-scans
`kf_lib/` and `kfw.py` for bare-name `_()` / `ngettext()` calls (prose
domain `kfw`) and harvests names for the `kfw_names` domain from the content
modules (moves, techs, styles, style_gen word lists, items, traits, weapons,
GROUP_NAMES, ROBBER_NICKNAMES, EXTRA_NAMES, plus `Advanced `-prefixed
style-tech twins). Attribute calls like `p.add_accompl('...')` are matched
too, but prose wrapped as `i18n._(...)` is **not** seen — always use the
bare-name import. Merges into the .po files, never deleting existing
translations.

### translate_names.py

`cd dev_scripts && ../.venv/bin/python translate_names.py` — machine-fills
empty `msgstr`s in `kfw_names.po` from the compositional dictionary in
`_names_ru.py` (adjective gender triples + head nouns + possessive genitives
+ hand-written overrides; `'Advanced X'` → `'<X> (продвинутый)'`
recursively). Deterministic; never overwrites an existing translation —
hand-edited entries are safe. Output is a **draft for human review**.

### fill_prose_ru.py

One-shot script that machine-filled the milestone-1 prose catalog
(`kfw.po`) from the hand-written mapping in `_prose_ru.py` (264/264
matched). Kept for reference; new prose strings are translated by editing
the .po directly.

### compile_locale.py

`cd dev_scripts && ../.venv/bin/python compile_locale.py` — compiles all
`.po` under `locale/` to `.mo` (via `i18n_common`). Run after any catalog
edit; commit the `.mo` together with the `.po`.

### i18n_coverage.py

`cd dev_scripts && ../.venv/bin/python i18n_coverage.py` — reports extracted
msgids vs translated msgstrs per domain (should read 100% before a commit
that adds `_()` strings).

## ai/ — fight-AI and AI-player runners

Thin wrappers over `kf_lib/ai/` and `kf_lib/game`; all use the
`Path('..', '..')` version of the chdir hack. On crash,
`collect_AIP_data.py` and `compare_AIPs.py` write the traceback to
`errors.txt` (repo root, post-chdir) and also try
`g.save_game('emergency_save.txt')`.

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

### compare_AIPs.py

Would play 100 AI-only games for each of `BaselineAIP`, `SmartAIP`,
`LazyAIP`, `VanillaAIP` and write average `n_days_to_win` per class to
`'AI players comparison.txt'`.

**Broken at line 14** (verified by running): `game.BaselineAIP` doesn't
exist — `kf_lib/game/__init__.py` re-exports only `Game`; the AIP classes
live in `kf_lib/actors/player`. The `AttributeError` fires inside the `try`,
so the handler runs and writes its traceback to `errors.txt`.

- With the import fixed, the output would land in
  `tests/AI players comparison.txt` (post-chdir-relative path fixed
  2026-09), where the committed sample lives.
- Also inherits the per-game styles prompt problem of
  `collect_AIP_data.py`.

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
The dir is gitignored, so the script creates it (`mkdir`) before the runs;
`output()` also tolerates an all-zero generation 0 (no record set yet —
`record_generation` stays `None` and the generation suffix is omitted).

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

It runs with `write_log=True`, and `BaseAI.__init__` then opens
`tests/AI actions/<AIClass>.txt` for append — the dir is gitignored, so the
script creates it (`mkdir`) before the runs.

- The final comparison write goes to `tests/fight AI comparison.txt`
  (post-chdir-relative path fixed 2026-09), overwriting the tracked sample
  as intended.

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
Runs are reproducible: `ml_fighter_pwr` seeds both `numpy`
(`np.random.seed(0)`) and the fight RNG (`random.seed(0)` —
`kf_lib/utils/_random.py` wraps the `random` module), so repeated runs
produce byte-identical datasets (verified with two 50-example runs).

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

`test_fight_balance(rand_actions=False, n=100_000, seed=42)`: 100,000 mirror
matches — two fresh random fighters at the *same* random level (1–20), both
driven by the default fight AI (`rand_actions=False`; `True` would use
uniform-random `BaseAI`). Fighters come from `new_fighter()`, i.e. randomly
*generated* styles only — the classic hard-coded styles (Dragon, Snake, …)
never appear, which is fine: they're legacy.

The fights are split into seeded chunks of `chunk_size=2000` (chunk *i* uses
`seed + i`) played in parallel worker processes (`workers=None` = one per
CPU; ~1.5 min for 100k on 10 cores). The report depends only on `n`, `seed`
and `chunk_size` — not on the worker count or the platform (workers are
always spawned fresh) — so repeated runs are byte-identical modulo the
timestamp line. With one chunk (`n=10000, chunk_size=10000`) it reproduces
the old single-process harness exactly. The script needs its
`if __name__ == '__main__'` guard (workers re-import it) and anchors its
chdir on `__file__`, so unlike the other dev scripts it runs from any cwd.

The report (`tests/test f.b. rand.act.=False n=100000.txt`, tracked) opens
with **fight stats** over all fights: length in seconds (mean, median,
slowest 10%), strikes / counters / preemptives / criticals / epics / stuns
per fight, strike outcomes (dodged, fully blocked, partly blocked, clean
hits — from the defender-side counters in `fight_stats`, see
`docs/stats.md`), the action mix (strikes, Guard, Focus, Catch Breath,
other maneuvers — from `fight_stats['moves_used']`), and what's left at the end (winner's HP, both fighters'
stamina and QP). Then, for winners vs losers: sums of the four base atts
(overall, then per level tier — `atts lv 1-7`, `lv 8-14`, `lv 15-20`, since
2026-10-23: averaging over all levels hid that speed is weak early and
strong late; each tier has a third of the fights, so its margins are ~1.7×
wider) and full atts, a histogram of att spread (max − min), tech description
features ("style buffs"), upgradable techs, advanced techs, and move
features — each a `compare_dicts` table, `D1` = winner count, `D2` = loser
count, `Diff%` = (D1 − D2) / Sum, `Sum`, plus **`+-95%`**: the noise margin
of that Diff%, estimated from the chunk-to-chunk spread (cluster variance of
the ratio, so it is honest for correlated rows too — a fighter has many
moves); `*` marks rows whose |Diff%| exceeds it. With ~150 rows a few `*`
are expected by chance.

How to read: in a balanced game every `Diff%` hovers near 0; a persistent
bias marks things that win or lose fights (the 100k snapshot of 2026-10:
`'close-range'` buffs at −14.6 ± 1.5, `'defense'` at −12.7 ± 1.6 — and
'defense' did nothing at all then, so about −9 to −13 is what a dead tech
slot scores). A single 10k run is too noisy for techs (margins ±9 for
techs 1, ±25 for techs 2); committed samples of the old single-process
harness exist for n = 50…50000.

Options (2026-10-22): `-n`, `--seed`, `--out PATH` (default: the tracked
report in `tests/`), and `--variants FILE:NAMES`, which runs FILE's
`apply(NAMES)` in every worker before its fights — rule experiments as
runtime monkeypatches, e.g. `--variants rule_variants.py:Gc+Hb25`. Relative
paths resolve against the folder you run from. Give variant runs an `--out`,
so they don't overwrite the tracked report.

The variants are applied once in the main process before any worker starts,
so a misspelled name, a missing file or a patch that crashes stops the run
at once with a traceback and a non-zero exit code. (Until 2026-10-22 they
were applied only in the workers: a typo like `Hb2` crashed every worker on
startup, the pool respawned them forever, and the run hung without a
report.)

**Batches of variant runs.** Run them one after another, not side by side:
one 100k run already keeps 10 cores 87% busy (measured 2026-10-22: 898 s of
CPU in 104 s), so parallel runs only split the cores and could at best
recover the idle 13% at the end of each run, when fewer chunks than cores
remain. Two silent failures to guard against:

- zsh, the macOS default shell, does not split an unquoted variable into
  words: `arg="--variants rule_variants.py:Hb25"; run_test_fb.py $arg`
  hands the script one argument, argparse rejects it, and the run exits in
  under a second. Write the flag literally, with its value quoted.
- A loop that doesn't check exit codes reports a batch of failed runs as
  done. Stop at the first failure, and give the script `< /dev/null`: on an
  error it waits on `input()`, which would block a background job.

```zsh
cd dev_scripts/testing
for v in Hb25 Hp20 Hp20+Hb; do
  ../../.venv/bin/python run_test_fb.py --variants "rule_variants.py:$v" \
    --out "$OUT/$v.txt" < /dev/null > "$OUT/$v.log" 2>&1 || { echo "FAILED: $v"; break; }
done
```

The baseline is a run without `--variants`. Before comparing, check that
every report exists and that its header's `variants=` line names what you
meant; a 100k run takes 1.5 min on 10 cores, so one that ends in seconds
failed.

Works: verified 2026-10-20 — 100k in 93 s on 10 cores; worker count 1 vs 2
gives byte-identical reports; 2026-10-22 — a `--variants` run matches the
scratch driver it replaced fight for fight; a misspelled variant now fails
in 1 s with exit code 1 (it used to hang), and a valid run's report stayed
byte-identical after that change.

### run_test_tech_ab.py — what is a technique worth

A/B test, the tool behind every boost value set in the 2026-10 balance pass:
for each named tech, `-n` (default 16,000) mirror matches between two fresh
random fighters at the same level (`--levels`, default 13–20, where general
techs are learned); one side, picked at random, is given the tech (pairs
where it already had it are skipped). It prints Diff% = 2 × win rate − 1
(the harness's units) with a ±95% margin. Every tech plays the same seeded
fighter pairs, with the same side treated, so techs compare against each
other with less noise: each fight is seeded from `--seed` and its index.
Until 2026-10-23 the run was seeded once, and since each tech's fights use
up a different amount of the random stream, the pairs drifted apart after
the first fight (2 of 30 pairs matched between two techs; now all do).
Names of the generated styles' techs ("Emphasis on Speed", "Strength
Training", ...) were rejected as unknown until the same day, because the
names were checked before `style_gen` built those techs.
`--all-general` adds every general tech and prints their median — the
yardstick: a tech scoring near the median is "an average technique".
Overrides for "what if" runs, applied in every worker: `--set CONST=VALUE`
(a `Fighter` class constant, e.g. `GUARD_POWER=2.5`), `--scale PARAM=FACTOR`
(multiplies that param in every Tech, i.e. tries another boost value), and
`--variants FILE:NAMES`, which calls `FILE`'s `apply(NAMES)` — a module of
monkeypatched rule experiments (e.g. a `def Ga(): ...` that patches
`Fighter.try_counter`, and `apply` calling the named ones), for trying a
rule before writing it into the engine. The overrides are applied once in
the main process before the workers start, so a misspelled `--set`
constant, a `--scale` param that no technique has (which would silently
measure nothing) or a bad variant name stops the run at once with exit
code 1 instead of hanging (verified 2026-10-22). Parallel like the harness
(spawned workers, `__main__` guard, runs from any cwd); prints only, no
report file.

A name `+ATT` (`+strength`, `+agility`, `+speed`, `+health`) gives the
treated side one extra point of that attribute instead of a tech — what an
attribute point is worth, e.g. per level band with `--levels 1-7`.

It runs one worker per name, so with fewer names than cores, several
invocations side by side do use the spare cores (unlike the harness). Start
them with `&`, collect each `$!`, and `wait` on each PID. Don't loop over
`$(jobs -p)`: in zsh the `$(...)` runs in a subshell with no jobs (bash
special-cases it), so `for j in $(jobs -p); do wait $j; done` returns at
once while the runs go on unwatched.

Works: verified 2026-10-22 — a 300-fight run matches a single-process
reference run fight for fight, with and without `--scale`. (`--scale` must
run after `style_gen` is imported, which builds the generated styles' techs;
the script imports everything first.)

### run_test_guard.py — what Guard does, without the fight AI

Controlled exchanges (2026-10-23): the harness and the A/B tool can't price
Guard, because the default fight AI guards only when it can't attack and
92% of its Guard turns then receive no strike. Here, for each of `-n`
samples (default 100,000), two fresh random fighters at the same random
level (`--levels`, default 1–20) get a random mid-fight stamina and qi
(25–100% of max, full HP); B picks a random attack move it can afford
against a standing target, at that move's distance. A then takes one turn
under each condition — `nothing` (defense as is), `Guard` (with A's own
guard techs), `G+AG` / `G+DG` (A's guard bonus as given by Advanced Guard /
Dragon Guards a Treasure alone) — and B strikes once. Every condition
replays the same pair, states and random rolls (seeded per sample), so the
columns differ by the condition alone; B's damage value starts at 0, as a
fresh fighter's. It prints, per condition: how B's strike ended (preempted,
missed, dodged, fully/partly blocked, hit), HP lost by A (also paired
against `nothing`), A's counters and the HP they cost B, the net HP swing,
what A's turn recovered, and HP lost per level tier as % of `nothing` in
that tier. Each `--variants FILE:NAMES` (repeatable) adds a column set,
run in its own worker pool (the new Guard was measured this way as
`rule_variants.py:Gb+Grec` at commit ae74b9f, before it was adopted).
Parallel like the harness (chunks of 2,000 samples, spawned workers, runs
from any cwd); prints only. Works: verified 2026-10-23 — the engine's
`G+DG` column (guard ×1.5 × bonus 2.0) equals `Gb+Grec`'s `G+AG` (×2.0 ×
1.5) to the last digit, as it must.

### compare_fb_reports.py — reports side by side

`python compare_fb_reports.py OLD.txt NEW.txt [MORE.txt ...]` prints each
report's fight-stats lines, then every table row's Diff% in each report,
sorted by the last one; a `*` marks a change from the first report beyond
the two reports' combined noise margin (√(m1² + m2²), from the `+-95%`
column — old single-process reports have no margins, so no `*`).
`--section "techs 1"` and `--key guard` narrow the output. Works:
verified 2026-10-22 on the tracked 10k and 100k reports.

### rule_variants.py — rule experiments of the 2026-10 balance pass

Not a script: a module of functions that monkeypatch `Fighter` to try a rule
change without editing the engine (Guard recovering stamina/qi, stored
guard, cheaper counters, qi shield, qi-charged strikes, health-based
toughness/stamina, …), with `apply('A+B')` to combine them. Feed it to
`run_test_fb.py --variants` or `run_test_tech_ab.py --variants`. Its header
lists every variant with its measured effect; the full tables are in
`tests/balance experiments 2026-10-22.txt`. When a variant is adopted, it
becomes engine code and should be removed from this file; the rest stay as
a record of what was tried.

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

### run_test_ffa.py

`test_ffa_win_rates(n_fights=100)`: win rates in free-for-all formats at
equal levels (lv 10), 100 fights per cell. Table 1: plain FFA of n = 2–8
fighters — fighter 1's win rate next to the expected 1/n and next to the
same fighter facing a *united* group of n−1 (win rate ≪ 1/n, 0% already at
n ≥ 4). This is the evidence that FFA wins are far easier than crowd wins
and why FFA exp is awarded per-capita. Table 2: group FFA of 2–4 groups of
2–3 — group 1's win rate vs the expected 1/g. Output:
`tests/ffa win rates lv=10 n=100.txt` (tracked).

Works: verified — both tables ran to completion; sample report committed.

### sim_group_ffa.py — group FFA effective opposition

Standalone experiment (not a `Tester` wrapper; prints to stdout, no report
file). Measures how hard a group free-for-all actually is for the protagonist
group: win rate of group 1 over 300 runs per config, mapped onto an
equivalent *united* enemy group size k via a calibration curve (my group vs
k united enemies). Runs three tiers — equal levels (lv 10) and the player
side at +3/+4 levels — since equal-level big configs saturate at 0% win.
This is the evidence behind the group-FFA exp/risk formula (RMS of per-group
sums, `BaseGroupFreeForAll.aggregate_exp_yield` and
`get_rel_strength(groups=...)`): RMS tracks the measured effective opposition
across configs, while the old per-capita average badly underestimates it.

Works: verified — full three-tier run completed (~27 min).

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
| `count_lines.py` | Yes | ran to completion (19,123 lines in 165 files) |
| `move_gen.py` | Yes — byte-deterministic across `PYTHONHASHSEED`s | ran to completion, exit 0; two runs at different hash seeds byte-identical; restored |
| `profile_game.py` | Yes — from `dev_scripts/`, needs a TTY | pty-driven run to completion; verified it fails from repo root (docstring now says so) |
| `try_rich.py` | No — `rich` not installed | ran, `ModuleNotFoundError` |
| `ai/collect_AIP_data.py` | Only interactively ("yes" × 100); persists nothing | headless `termios.error`; pty run (game completes) |
| `ai/compare_AIPs.py` | No — `game.BaselineAIP` doesn't exist | ran, `AttributeError` at line 14 |
| `ai/run_fight_ai_gen.py` | Should run — creates `tests/genetic/` itself; not re-run end-to-end (hours-scale) | `output()` verified on a synthetic all-zero generation (no `TypeError`) |
| `ai/run_fight_ai_test.py` | Should run — creates `tests/AI actions/` itself; not re-run end-to-end (hours-scale) | short `FightAITest` with `write_log=True` completed after the mkdir |
| `ml/ML_gen_data.py` | Yes — reproducible (`random` seeded) | two 50-example runs byte-identical; full 10,000-row run earlier restored |
| `ml/ML_learn.py` | No — `'../../ml/...'` resolves outside the repo | ran, `FileNotFoundError` |
| `testing/run_test_fb.py` | Yes | n=10000 ran to completion; report restored |
| `testing/run_test_guard.py` | Yes | 100k-pair run with `--variants rule_variants.py:Gb+Grec` to completion (2026-10-23); shared columns match to the digit |
| `testing/run_test_lv_vs_crowds.py` | Yes | all 5 tables ran to completion; reports restored |
| `testing/run_test_ffa.py` | Yes | both tables ran to completion; report committed |
| `testing/sim_group_ffa.py` | Yes | full three-tier run to completion (~27 min); stdout only, no report file |
| `testing/run_test_level_sign.py` | Yes | full 20×20 matrix ran to completion; report restored |
| `i18n_extract.py` / `compile_locale.py` / `i18n_coverage.py` / `translate_names.py` | Yes | catalogs regenerated, machine-filled, compiled and verified at 100% coverage (2026-09) |
