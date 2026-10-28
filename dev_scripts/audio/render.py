"""Render the soundtrack drafts and sound effects to WAV.

Run from this directory: ../../.venv/bin/python render.py
Tunes play intro + their loop twice, fading out at the end (a listening
preview; seamless loop files come with integration). Output goes to out/.
"""
from pathlib import Path

from chipsynth import render_song, write_wav
from sfx import SFX
from tunes import TUNES

OUT = Path('out')


def main():
    (OUT / 'music').mkdir(parents=True, exist_ok=True)
    (OUT / 'sfx').mkdir(parents=True, exist_ok=True)
    for name, (tune, loudness) in TUNES.items():
        t = tune()
        x = render_song(t.bpm, t.voices, t.sections, t.intro + t.loop * 2,
                        fade_s=6, bar_steps=t.bar_steps, swing=t.swing)
        peak = write_wav(OUT / 'music' / f'{name}.wav', x, loudness)
        print(f'{name}: {len(x) / 44100:.1f} s, peak {peak:.2f}')
    for fn, loudness in SFX.items():
        peak = write_wav(OUT / 'sfx' / f'{fn.__name__}.wav', fn(), loudness,
                         window_s=0.05)
        print(f'{fn.__name__}: peak {peak:.2f}')
    write_index()


def write_index():
    """out/index.html: every render on one page, for listening."""
    rows = []
    for kind in ('music', 'sfx'):
        rows.append(f'<h2>{kind}</h2>')
        for f in sorted((OUT / kind).glob('*.wav')):
            rows.append(f'<div><span>{f.stem}</span>'
                        f'<audio controls preload="none" src="{kind}/{f.name}">'
                        '</audio></div>')
    (OUT / 'index.html').write_text(
        '<!doctype html><meta charset="utf-8"><title>KFW audio drafts</title>'
        '<style>body{font:15px monospace;margin:16px}div{display:flex;'
        'align-items:center;gap:12px;margin:4px 0}span{width:220px}</style>'
        '<h1>KFW audio drafts</h1>' + '\n'.join(rows), encoding='utf-8')


if __name__ == '__main__':
    main()
