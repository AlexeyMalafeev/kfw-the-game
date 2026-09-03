# Text content: quotes, names, ASCII art

How the game's written/drawn content is stored, selected and shown, as
implemented. Source files: `kf_lib/actors/quotes.py`,
`kf_lib/actors/fighter/_quotes.py`, `kf_lib/actors/names.py`,
`kf_lib/game/_base_game.py` (`get_new_name`), `kf_lib/kung_fu/ascii_art.py`,
`kf_lib/actors/fighter/_ascii.py`, data in `quotes/` and
`moves/ascii_mapping.txt`. Biographies are a separate text pipeline — see
`docs/stats.md`.
Items marked ⚠️ look unintentional or surprising — verify before building on them.

## Quotes

### Loading

`actors/quotes.py` reads `quotes/*.txt` at import with cwd-relative paths
(`open(os.path.join('quotes', file_name))`), one quote per line via
`f.read().split('\n')` — importing from the wrong cwd raises `FileNotFoundError`.
Nine files are loaded; `quotes/_unused.txt` exists in the folder but is never
read, and `MISC = ''` is a dead leftover ⚠️.

Pool sizes (lines per file): hero prefight 211 / hero win 130, thug prefight
126 / thug win 48, challenger prefight 53 / challenger win 40, wisdom 133,
master criticism 23, training injury 21. No blank lines, so pool size == line
count.

### Occupation → pool mapping

Two dicts at the bottom of `quotes.py` map occupation strings to pools:

- `PREFIGHT_QUOTES` / `WIN_QUOTES`: `challenger` / `hero` / `thug` get their
  own prefight and win files; `master` maps to `WISDOM` for **both** (masters
  recite proverbs before and after the fight).
- The default occupation `'fighter'` (set in `Fighter.__init__`,
  `actors/fighter/__init__.py`) is in neither dict ⚠️ — generic NPCs are
  silent. Players are `'hero'` (`actors/player/_base_player.py`).

On the fighter side (`fighter/_quotes.py`): the property `quotes` just returns
`self.occupation` (a confusing name — it shadows the imported `quotes` module
inside the class). `say_prefight_quote` / `say_win_quote` do
`pool = PREFIGHT_QUOTES.get(self.quotes)` → `random.choice(pool)` →
`self.current_fight.show(f'{self.name}: "{q}"')`. No repetition tracking; the
same line can recur.

### When lines are spoken

- Prefight: `BaseFight.handle_prefight_quote` (`fight/_base_fight.py`) calls
  `say_prefight_quote()` on `side_a[0]` and `side_b[0]` only — side leaders,
  not everyone. It sums the two bool returns (`make_pause = f1... + f2...`);
  `say_prefight_quote` returns whether a line was actually spoken purely so
  the pause (`pak()`) is skipped when both fighters are quoteless. Called from
  `AutoFight.__init__`, so every fight runs it; in headless fights `show` is a
  no-op and the quotes vanish.
- Win: `handle_win_quote` is called from `_resolve_winner_name`, i.e. as part
  of `show_win_message` — `winners[0]` alone speaks, and only when the win
  message is actually displayed (human main player, or spectated fights via
  `_spectating.py`). On a draw (`winners == []`) no quote.
- Sparring (`fight/_sparring.py`) overrides both handlers with no-ops.
- Win-message wording: `_resolve_winner_name` prints "X wins." unless the
  winner's name is exactly `'Thug 1'` or `'Robber 1'`, which `GROUP_NAMES`
  (`actors/names.py`) maps to "Thugs win." / "Robbers win." ⚠️ Only those two
  exact crowd-leader names are special-cased; a lone fighter named `Thug`
  prints "Thug wins."

### Non-fight pools

- `WISDOM` — masters' prefight/win pool (above); not used anywhere else.
- `MASTER_CRITICISM` — school encounter (`happenings/encounters/_school.py`):
  a master who declines to praise the player shows a random criticism line.
- `TRAINING_INJURY` — `BasePlayer.check_training_injury`
  (`actors/player/_base_player.py`): on a training-injury roll the player
  "says" a random line, then gets `injure(1)`.

## Names

### Generation

`actors/names.py` is pure data: 91 `SURNAME_PARTS` and 116
`FIRST_NAME_PARTS` (single Chinese-ish syllables, lowercase), plus fixed lists
for special cases.

`BaseGame.get_new_name(prefix='')` (`game/_base_game.py`):

- No prefix: `name = f'{sur} {fir}'.title()` where `sur` is a random surname
  part and `fir` is 1–2 syllables from `random.sample(FIRST_NAME_PARTS,
  rndint(1, 2))` — sampling without replacement, so two-syllable given names
  never repeat a syllable. ≈ 1.2 M distinct combinations.
- With prefix: `f'{prefix} {sur}'.title()` → "Master Bai", "Thief Wang",
  "Gambler Chen". Prefixes used in code: `Master`, `Beggar`, `Drunkard`,
  `Thief`, `Official`, `Gambler`, and robber nicknames (below).
- Collision loop: the candidate is retried while it's in `self.used_names`
  (populated by `register_fighter`; rebuilt from `fighters_dict` by
  `collect_used_names`). After 1000 failed tries it prints
  `'1000 names failed'` and the prefix... then keeps looping forever ⚠️ —
  the outer `while True` has no escape, so an exhausted namespace hangs the
  game (unreachable in practice at ~1.2 M combos).

Names matter beyond display: `register_fighter` raises on a duplicate name,
and JSON saves cross-reference fighters *by name* — uniqueness is a save-format
invariant, which is what the collision loop protects.

### Fixed-name content

- Crowds: `fighter_factory` builds e.g. several `Thug`s and
  `add_numbers_to_names` appends ` 1`, ` 2`, … — this produces the
  `GROUP_NAMES` keys above.
- `ROBBER_NICKNAMES` (23: Atrocious … Wild) are used as *prefixes* for
  robber/criminal NPCs (`encounters/_utils.py`, `story/_bandit_fiance.py`,
  `game/_playing.py`).
- `new_foreigner` picks a country from `FOREIGN_COUNTRIES` (6) and a surname
  from `FOREIGN_NAMES` (5–11 per country) ⚠️ without the `get_new_name`
  collision check — a duplicate would blow up later in `register_fighter`.
- `TURTLE_NAMES` (the four Ninja Turtles) for the turtle encounter;
  `DFLT_TOURN_PART_NAME = 'Unknown'` and `GANG_LEADER = 'Gang Leader'` are
  defined but unused in `kf_lib` ⚠️; `CAPITAL_LETTERS` likewise.

## ASCII art

### Storage

`moves/ascii_mapping.txt` holds 166 hand-drawn blocks, each introduced by a
`# Name[, Name...]` header line (one picture can serve several moves, e.g.
`# Stance, Catch Breath`) → 206 move-name keys total. All blocks are parsed
at import by `set_ascii_art()` (`kung_fu/ascii_art.py`) into two dicts,
`FIGHTER_ART_L` and `FIGHTER_ART_R` (right-facing mirror).

Parsing details (`finalize` / `mirror`):

- `finalize` strips the last character of every line and then replaces all
  `'s'` with spaces — `s` is a *spacing marker convention* in the source file,
  not a drawing character.
- `mirror` builds the right-facing copy by swapping directional characters
  (`\ / < > ( ) [ ] { }`, plus `p→q` and `c→D` with a "todo better mirroring"
  comment) and reversing each line.
- A move name appearing twice in the file prints a warning and then calls
  `input('Press Enter to continue')` ⚠️ — at import time, so a duplicate
  would block the game startup on a prompt (no duplicates currently).

### Matching a move to art — `get_ascii(move_name)`

Fallback chain, first hit wins:

1. Exact move name.
2. If `'Flying'` is one of the words: `'Flying ' + last_word` (e.g. "Flying
   Side Kick" → "Flying Kick").
3. Otherwise try `first_word + last_word`, then `second_word + last_word`, …
   (each earlier word paired with the last).
4. The last word alone.
5. `DEFAULT_MOVE_ART = 'Stance'`.

⚠️ The `'Flying'` branch (2) is terminal: if `'Flying X'` has no art, the
lookup drops straight to `Stance` without trying `X` alone (branches 3–4 are
in the `else`).

The chain works well in practice: of ~13 800 generated moves only 4 end up on
the Stance fallback — `Backfist`, `Do Nothing`, `Mantis Hook`,
`No-Shadow_Kick`.

Besides move names, the mapping contains situational pictures the fight code
asks for directly: `Stance`, `Win`, `Lying`, `Falling`, `Knockback`,
`Dodge`/`Block`/`Hit`, their `Lying …` variants, `Hit Effect` and `Lying Hit
Effect`. Each `Move` caches its pair at construction (`Move.set_ascii` →
`get_ascii(self.name)`).

### Per-fight flow (`fighter/_ascii.py`)

- Every turn, before `exec_move`, `fight_loop` calls `f.refresh_ascii()`:
  the actor takes `self.action.ascii_l/ascii_r`, both fighters' `ascii_buffer`
  reset to 0, and the target is reset to `'Lying'` (if lying) or `'Stance'`.
- During resolution the target's picture is swapped by events: `defend()` sets
  `['Lying ']Dodge/Block/Hit`; knockdown → `'Falling'`; knockback →
  `'Knockback'` and `ascii_buffer += dist` (the horizontal gap).
- ⚠️ `cause_shock` / `cause_slow_down` / `cause_stun`
  (`_strike_mechanics.py`) compute the lying prefix with
  `self.ascii_name.startswith('lying')` — lowercase. Stored names are
  `'Lying …'` (capital L), so the prefix is never applied and a
  shocked/stunned/slowed *lying* fighter shows the standing `'Hit Effect'`
  art; the `Lying Hit Effect` picture is unreachable through this path.
- `show_ascii()` picks `ascii_l` vs `ascii_r` by which side the fighter is on
  (side_a faces right), joins the two pictures with
  `ascii_art.concat(a, b, buffer)` where `buffer = max(self.ascii_buffer,
  target.ascii_buffer)`, shows the result and appends it to
  `fight.cartoon`.
- At fight end, winners get `set_ascii('Win')`, losers `set_ascii('Lying')`;
  `show_win_message` draws one final picture via
  `main_player.show_ascii()`.
- ⚠️ `concat` is only correct with `BUFFER_WIDTH = 1`; the code carries
  `todo if you set buffer width to >=2, there is a bug in concat`.
- ⚠️ `show_ascii` catches `AttributeError` around the side lookup and dumps
  full `vars()` of the fighter and fight before re-raising — a debug leftover.

### The cartoon buffer

`BaseFight.cartoon = ['']` collects one frame per `show_ascii` call (the
leading empty string is dropped in `post_fight_menu`). The post-fight menu
offers a `Slideshow` (frame-by-frame replay) and `Save slideshow` (writes all
frames to a user-named text file). `check_epic` labels the fight ` (epic!)` if
≥ 80 % of frames are unique, ` (boring...)` if ≤ 40 % (only for fights with
≥ 10 frames; constants at the top of `_base_fight.py`) — a fight that mostly
loops the same Stance pictures reads as "boring".
