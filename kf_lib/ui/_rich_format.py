"""Terminal colors via rich-style markup tags.

Call sites wrap text in tags (``[red]...[/red]`` or with the helpers below),
never in raw ANSI codes. Tags are resolved to ANSI escapes by ``render()`` at the
print choke points (``show()``, ``menu()``, ...) and stripped everywhere else
(``log()``, width math), so log files stay clean and disabling colors is just
"strip the tags".

Supported tags: red green yellow blue magenta cyan white grey, bold dim italic;
compound tags like ``[bold red]``; closing is ``[/tag]`` or just ``[/]``.

``render()`` also auto-colors systematic patterns in any text it processes:
quoted speech (dim), levels ``lv.5`` (cyan), percentages (yellow), ``HP:`` /
``SP:`` / ``QP:`` stat tokens (green/yellow/magenta), ``Round N`` / ``Day N``
headers (bold), healing ``+N HP`` (green), money (``100 coins``, ``100-coin`` →
yellow) and exp amounts (``100 exp`` → green) — so call sites do not have to
mark those up by hand.
"""

import os
import re
import sys

__all__ = [
    'init_colors',
    'set_colors_enabled',
    'colors_enabled',
    'render',
    'rprint',
    'strip_tags',
    'visible_len',
    'style',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white',
    'grey',
    'bold',
    'dim',
    'italic',
]

_ANSI_CODES = {
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'grey': 90,
    'bold': 1,
    'dim': 2,
    'italic': 3,
}

_TAG_RE = re.compile(r'\[(/?)([^\[\]]*)\]')

# systematic coloring applied at render time, so every message gets it without
# call sites having to wrap anything; order matters — quoted speech is wrapped
# first so that amounts inside quotes still get their own colors
_AUTO_COLOR_RES = (
    (re.compile(r'"[^"]*"'), 'dim'),  # quoted speech
    (re.compile(r'\blv\.?\s?\d+'), 'cyan'),  # levels: lv.5, lv 10
    (re.compile(r'\d+(?:\.\d+)?%'), 'yellow'),  # percentages: 40%
    (re.compile(r'\bHP(?=:)'), 'green'),  # stat tokens (colon guards against -N HP damage text)
    (re.compile(r'\bSP(?=:)'), 'yellow'),
    (re.compile(r'\bQP(?=:)'), 'magenta'),
    (re.compile(r'\b(?:Round|Day) \d+'), 'bold'),  # headers: Round 3, Day 12
    (re.compile(r'(?<![\w+])\+\d+ HP\b'), 'green'),  # healing: +5 HP
    # money/exp amounts
    (re.compile(r'(?<![\w+-])[+-]?\d[\d,]*(?: coins?|-coins?)\b'), 'yellow'),
    (re.compile(r'(?<![\w+-])[+-]?\d[\d,]* exp\b'), 'green'),
)

_colors_enabled = False


def colors_enabled():
    return _colors_enabled


def set_colors_enabled(value):
    global _colors_enabled
    _colors_enabled = bool(value)


def init_colors(no_color_flag=False):
    """Decide whether to emit ANSI colors; call once at program start."""
    if no_color_flag or os.environ.get('NO_COLOR') or os.environ.get('KFW_COLOR') == 'never':
        set_colors_enabled(False)
        return
    if not sys.stdout.isatty() or os.environ.get('TERM') == 'dumb':
        set_colors_enabled(False)
        return
    if os.name == 'nt':
        # enable VT processing on Windows 10+
        os.system('')
    set_colors_enabled(True)


def style(text, tag):
    """Wrap text in a markup tag, e.g. style('ouch', 'bold red')."""
    return f'[{tag}]{text}[/{tag}]'


def _make_wrapper(tag):
    def wrapper(text):
        return style(text, tag)

    wrapper.__name__ = tag
    return wrapper


red = _make_wrapper('red')
green = _make_wrapper('green')
yellow = _make_wrapper('yellow')
blue = _make_wrapper('blue')
magenta = _make_wrapper('magenta')
cyan = _make_wrapper('cyan')
white = _make_wrapper('white')
grey = _make_wrapper('grey')
bold = _make_wrapper('bold')
dim = _make_wrapper('dim')
italic = _make_wrapper('italic')


def _is_tag(body):
    """A bracketed chunk is a markup tag only if every word in it is a known tag
    (so literal text like '[Enter]' is left alone)."""
    words = body.split()
    return bool(words) and all(w in _ANSI_CODES for w in words)


def _resolve(tags):
    return '\x1b[' + ';'.join(str(_ANSI_CODES[t]) for t in tags.split()) + 'm'


def _auto_color(text):
    """Wrap systematic patterns (quoted speech, levels, percentages, stat
    tokens, round/day headers, healing, money/exp amounts) in color tags;
    existing tags are unaffected (digits never appear in them)."""
    for pattern, tag in _AUTO_COLOR_RES:
        text = pattern.sub(f'[{tag}]\\g<0>[/{tag}]', text)
    return text


def render(text):
    """Replace markup tags with ANSI codes (or strip them if colors are off)."""
    text = _auto_color(text)
    if '[' not in text:
        return text
    if not _colors_enabled:
        return strip_tags(text)
    out = []
    pos = 0
    stack = []
    for m in _TAG_RE.finditer(text):
        closing, tag = m.groups()
        if closing:
            is_tag = not tag or _is_tag(tag)
        else:
            is_tag = _is_tag(tag)
        if not is_tag:
            continue  # literal brackets, not markup
        out.append(text[pos: m.start()])
        if closing:
            if stack:
                stack.pop()
                out.append('\x1b[0m')
                if stack:
                    out.append(_resolve(stack[-1]))
        else:
            stack.append(tag)
            out.append(_resolve(tag))
        pos = m.end()
    out.append(text[pos:])
    return ''.join(out)


def rprint(text='', **kwargs):
    """print() with markup tags resolved to colors."""
    print(render(text), **kwargs)


def strip_tags(text):
    """Remove all markup tags, keeping the text."""
    if '[' not in text:
        return text

    def repl(m):
        closing, tag = m.groups()
        if closing:
            return '' if not tag or _is_tag(tag) else m.group(0)
        return '' if _is_tag(tag) else m.group(0)

    return _TAG_RE.sub(repl, text)


def visible_len(text):
    """Length of the text as it appears on screen (tags not counted)."""
    return len(strip_tags(text))
