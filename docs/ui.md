# Terminal UI and colors

How the game talks to the terminal: output funnels, the color-markup engine,
menus, and alignment. Source files: `kf_lib/ui/` (all star-exported via
`__init__.py`), `kf_lib/actors/human_controlled_fighter.py` (the main output
funnel). Items marked ⚠️ look unintentional or surprising — verify before
building on them.

## Output funnels

There is no single print wrapper; most human-visible text flows through a few
choke points, all of which resolve color markup (see below) before printing:

- `HumanControlledFighter.show(text, align=True)` — the dominant funnel
  (~370 `.show()` / `.write()` / `.msg()` call sites). `align=True` word-wraps
  and justifies each paragraph to 60 columns via `align_text`
  (`kf_lib/ui/_align.py`); `align=False` prints as-is. `write()` = `show()` +
  `log()`; `msg()` = `write()` + `pak()`. `NormalFight.display` delegates to
  the human player's `show`, so all interactive fight output passes through
  here too.
- `SpectateFight.show` (`kf_lib/fighting/fight/_spectating.py`) — `rprint`.
- `SmartAIPVisible.log` (`kf_lib/actors/player/_ai_player.py`) — prints with
  `render()`, appends the *stripped* text to the player log.
- `menu()` / `yn()` and `msg()` / input prompts (`kf_lib/ui/_menu.py`,
  `kf_lib/ui/_interactive.py`).
- A long tail of bare `print()` calls, mostly in dev/testing code, stays
  uncolored.

Player log files (`plog`, saved with the game) never contain markup or ANSI
codes: `BasePlayer.log` and `SmartAIPVisible.log` strip tags before appending.

## Color markup (`kf_lib/ui/_rich_format.py`)

Call sites embed rich-style **tags**, never raw ANSI codes:

```python
from kf_lib.ui import red, style
self.show(f'hit: {red(f"-{dam} HP")} ({tgt.hp})')
self.show(style('CRITICAL!', 'bold red'))
```

- Syntax: `[tag]...[/tag]` or self-closing `[tag]...[/]`; tags may be compound
  (`[bold red]`). Nesting works — closing an inner tag re-opens the outer one.
- Available tags: `red green yellow blue magenta cyan white grey`,
  `bold dim italic`. Convenience wrappers (`red(s)`, `bold(s)`, ...) just wrap
  text in tags, so they are safe to use anywhere a string is built.
- A bracketed chunk is a tag only if **every word in it is a known tag name**,
  so literal text like `[Enter]` or `[1]` passes through untouched.
- `render(text)` — tags → ANSI codes (or stripped when colors are off);
  `rprint(text)` — print with `render`; `strip_tags(text)` — remove tags;
  `visible_len(text)` — on-screen length (tags not counted).

### When colors are on

`init_colors()` (called once from `kfw.py`) enables colors only when stdout is
a TTY, `NO_COLOR` is unset, `KFW_COLOR` is not `never`, and `TERM` is not
`dumb`; `--no-color` forces them off. On Windows (`os.name == 'nt'`) VT
processing is enabled with `os.system('')` (Windows 10+). When colors are off,
`render()` just strips tags, so piped output, tests and logs are always clean.
`set_colors_enabled(bool)` toggles at runtime (e.g. for a future debug-menu
option).

### Semantic palette

| What | Style |
|---|---|
| damage numbers (`-N HP`), bleeding | red |
| criticals, KO, unblockable, fury | bold red |
| epic strikes | bold magenta |
| dodges, blocks, disarms, environment use, improvised weapons | cyan |
| status effects (stun, shock, off-balance, slow), misses/fails, counters, preemptives, draws | yellow |
| money amounts | yellow |
| exp gains | green |
| victory message, level-ups, resisting KO | bold green / green |
| fighter names (fight-info header) | bold |
| menu titles | bold (applied globally in `menu()`) |
| menu option keys | cyan (applied globally in `menu()`) |
| style-selection menu options | white style names, grey short descriptions |
| quotes / flavor text | dim |
| HP bar | green → yellow → red by fill %; SP bar yellow; QP bar magenta |

## Alignment and width math

All width-sensitive code measures **visible** length (`visible_len`), so tags
never skew layout: `align_text` (60-col justification), `pretty_table` (column
padding), and the two-column HP/SP/QP header in
`HumanControlledFighter.see_fight_info`.

⚠️ ASCII art frames (`kf_lib/kung_fu/ascii_art.py`, `fighter/_ascii.py`,
`concat()`) must stay **uncolored**: frames are fixed-width and joined
horizontally, and even the current monochrome `concat` is fragile — embedding
tags inside art would corrupt the picture. Whole-message colors around art
(like the win message) are fine.
