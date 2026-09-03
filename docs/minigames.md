# Minigames

Standalone prototypes in `minigames/` plus any minigame wiring in the game itself.
Sources: `minigames/RING_mini_game.py`, `minigames/Chocolate_mini_game.py`,
`kf_lib/actors/fighter_factory.py`, `kf_lib/ui/` (`_menu.py`, `_interactive.py`,
`_keyboard.py`). Items marked ⚠️ look unintentional or surprising — verify before
building on them.

## Overview

There are exactly two minigames, both in `minigames/`, both vintage 2020–2022
prototypes (per git history). Neither is wired into the main game: a
case-insensitive search for `mini_game` / `minigame` / `Chocolate` / `RING`
across `kf_lib/` and `kfw.py` finds no references, and `kfw.py` has no minigame
entry point. AGENTS.md's "standalone prototypes, not wired into the game" is
accurate.

## Shared conventions

- Both scripts start with the same `Path('..')` chdir/sys.path hack as
  `dev_scripts/`: they resolve the parent of the cwd and chdir into it. **They
  must be run from the `minigames/` directory** (e.g.
  `cd minigames && ../.venv/bin/python RING_mini_game.py`). Run from the repo
  root they chdir one level too far up and die with
  `ModuleNotFoundError: No module named 'kf_lib'` (verified).
- Both call `main()` at import time (no `__main__` guard) inside a
  try/except that prints the traceback and then waits on
  `input('Press Enter to exit')`.
- Both are interactive and need a real TTY: input goes through
  `kf_lib/ui/_keyboard.py` (termios), so piped stdin crashes at the first
  `pak()` with `termios.error` (verified). Both run fine through a pty.

## RING — `minigames/RING_mini_game.py`

An endless arena ladder around the normal fight engine:

1. Difficulty menu (`ui.menu`): easy 0.9 / normal 1.0 / hard 1.1 / extreme 1.2
   — a multiplier on opponent strength.
2. `fighter_factory.new_custom_hcf()` builds the player's
   `HumanControlledFighter`: `input('Name: ')`, a style menu over
   `styles.default_styles`, a level prompt (1–20) applied via `level_up()`.
3. Each round, opponents come from `fighter_factory.from_exp_worth(
   p.get_exp_worth() * difficulty)`: a retry loop that rolls a random group
   (`new_fighter`, level 1–20, up to 5 members, 35% weapon chance for a lone
   opponent) until the group's total `get_exp_worth()` lands in
   `[x, x + x / 10)`.
4. `p.fight(opp[0], en_allies=opp[1:], hide_stats=difficulty >= 1.0)` — the
   standard fight pipeline, including the "Auto fight?" prompt. Win →
   `p.level_up()` (full interactive level-up: attribute pick, move/tech
   choices). Loss → one of 3 attempts is spent. Game over at 0 attempts;
   prints the reached level.

Works. Verified 2026-09 by driving it through a pty (feeding keys to the
menus): complete session — banner, difficulty/style/level prompts, several
full fights via "Auto fight?", level-ups to lv.13 — with no exceptions. With
piped stdin it fails at the first `pak()` exactly as the TTY pitfall in
AGENTS.md predicts.

- ⚠️ `from_exp_worth` carries a `# todo reimplement` in `fighter_factory.py`:
  the retry loop has no termination guarantee beyond eventually rolling a
  matching group.
- ⚠️ `play = True` is never set to `False`; the loop only exits via the
  `attempts == 0` break. Harmless but dead.
- Not wired into the game. BACKLOG ("Minigames & far-future mods") has related
  ideas — RING score for exp bonuses, kumite mini-game, tournament betting —
  none implemented.

## Chocolate — `minigames/Chocolate_mini_game.py`

A scripted story-campaign prototype: a fixed hero `Zen` (a `HumanPlayer`
subclass with exp gain and all level-up choices no-op'd; level 12,
`styles.ZENS_STYLE` 'Savant', atts (5, 10, 7, 5)) fights through scenes. Each
scene grants fixed techs and moves (`p.learn_tech(...)`, `p.learn_move(...)`),
prints hero vs opponents exp worth, then repeats
`p.fight(scene_boss, en_allies=rest, hide_stats=False)` until won — losing
costs nothing. Comments sketch 7 movie-inspired scenes; 5 are implemented.
A `game.Game()` is created and assigned to `p.game` but never otherwise used;
a difficulty menu is commented out.

**Broken, and known to be**: the file carries
`# todo fix Chocolate mini-game, it's not working now` and BACKLOG repeats it.
It does not even reach its own banner — line 16 `from kf_lib import
human_player` raises `ImportError`, because the module no longer exists
(player classes moved to `kf_lib/actors/player/`). Verified 2026-09: run from
`minigames/` with the venv python, exits 1 on that import.

The rot goes deeper than the import. Shimming `kf_lib.human_player` in-memory
(alias to `kf_lib.actors.player.HumanPlayer`, no repo files touched) and
running under a pty, the next crash is in the constructor:

- ⚠️ `Zen.set_rand_moves` learns all `moves.BASIC_MOVES`, but
  `Fighter.set_moves` (`_moves.py`) already learns all basic moves *before*
  calling `set_rand_moves()`. Every learn attempt hits the "already known"
  warning, which interpolates `repr(self)` — and repr-ing a player inside
  `Fighter.__init__` crashes with `AttributeError: 'Zen' object has no
  attribute 'traits'`, because `BasePlayer.__init__` sets `traits` (and the
  other player attributes) only *after* `super().__init__()` returns. This is
  a latent kf_lib bug, not just a Chocolate one: any `repr()` of a player
  during `Fighter.__init__` raises.

Further staleness, established by reading the current APIs (the script can't
be run far enough to hit these without fixing the two bugs above):

- ⚠️ `p.learn_tech(*s_techs)` passes tech *names*, but `learn_tech`
  (`fighter/_techs.py`) now expects `Tech` objects — a string reaches
  `Tech.apply` via `add_tech` and would raise `AttributeError`. Two of the
  scene techs (`'Mighty Elbows'`, `'Mighty Knees'`, scene 5) no longer exist
  in `kung_fu/techniques.py` at all; the other eight do.
- ⚠️ Eight of the nine scene move names are gone from `moves/all_moves.txt`
  ('Jumping Kick', 'Roundhouse Kick', 'Spin Kick', 'Dragon Block',
  'Dragon Evasion', 'Dragon Elbow', 'Jumping Knee', 'Volcano Knee') —
  `learn_move` would raise `MoveNotFoundError`. Only 'Energy Kick' (scene 4)
  still exists.
- ⚠️ Zen's no-op overrides are stale: `can_learn_new_tech` no longer exists
  anywhere in `kf_lib`, and `choose_new_move(self)` no longer matches the
  current signature `choose_new_move(self, sample)`
  (`fighter/_moves.py`, `human_controlled_fighter.py`).

Not wired into the game; nothing in `kf_lib/` references it.

## Wiring summary

| Minigame | Runs today | Referenced by the game |
|---|---|---|
| `RING_mini_game.py` | Yes — from `minigames/`, needs a TTY (verified via pty run) | No |
| `Chocolate_mini_game.py` | No — `ImportError` at line 16, plus deeper rot (verified) | No |
