"""Render the soundtrack and sound effects.

Run from this directory: ../../.venv/bin/python render.py [--game] [--previews]

--previews (the default with no flag) writes WAV listening previews to out/:
each tune plays intro + its loop twice, fading out at the end.
--game writes the files the game plays, as OGG Vorbis, to the committed
../../audio/ folder: per tune an intro file and a seamless loop file (see
`game_files`), and every effect and jingle as a one-shot.
"""
import argparse
from pathlib import Path

import numpy as np
import soundfile

from chipsynth import SR, finish, render_song, write_wav
from sfx import SFX
from tunes import TUNES

OUT = Path('out')
GAME_OUT = Path('../../audio')
# libsndfile's Vorbis setting: 0 = best, 1 = smallest. 0.8 is about 64-70
# kbit/s on this mono material (square waves smear much below that).
VORBIS_LEVEL = 0.8
SILENT = 1e-5  # raw render level counted as silence when measuring tails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', action='store_true',
                    help='write the OGG files the game plays to audio/')
    ap.add_argument('--previews', action='store_true',
                    help='write WAV listening previews to out/ (default)')
    args = ap.parse_args()
    if args.game:
        write_game_files()
    if args.previews or not args.game:
        write_previews()


def write_previews():
    (OUT / 'music').mkdir(parents=True, exist_ok=True)
    (OUT / 'sfx').mkdir(parents=True, exist_ok=True)
    for name, (tune, loudness) in TUNES.items():
        t = tune()
        x = render_song(t.bpm, t.voices, t.sections, t.intro + t.loop * 2,
                        fade_s=6, bar_steps=t.bar_steps, swing=t.swing)
        peak = write_wav(OUT / 'music' / f'{name}.wav', x, loudness)
        print(f'{name}: {len(x) / SR:.1f} s, peak {peak:.2f}')
    for fn, loudness in SFX.items():
        peak = write_wav(OUT / 'sfx' / f'{fn.__name__}.wav', fn(), loudness,
                         window_s=0.05)
        print(f'{fn.__name__}: peak {peak:.2f}')
    write_index()


def _render(t, order, tail_s=0.0):
    return render_song(t.bpm, t.voices, t.sections, order,
                       bar_steps=t.bar_steps, swing=t.swing, tail_s=tail_s)


def _seconds(t, order):
    steps = sum(t.sections[s]['bars'] * t.bar_steps for s in order)
    return steps * 60 / t.bpm / 4


def _tail_s(t, order):
    """How long sound rings on after `order` ends (releases, echoes, gongs)."""
    x = _render(t, order, tail_s=4.0)
    end = int(_seconds(t, order) * SR)
    loud = np.nonzero(np.abs(x[end:]) > SILENT)[0]
    return (loud[-1] + 1) / SR if len(loud) else 0.0


def game_files(t):
    """(intro, loop) sample arrays for one tune, before mastering.

    The game plays the intro file once, then repeats the loop file. Notes
    ring on past the loop's end (releases, echoes, gongs), so in the steady
    state each loop pass starts with the previous pass's tail. To get that
    without overlapping playback, the intro file runs `x` seconds into the
    first loop pass (x = the longest tail, so the intro's own tail is over by
    then), and the loop file is one full loop period cut from the steady
    state, starting x seconds into a pass. Repeating it is seamless: its end
    flows into its start exactly as one pass flows into the next. Tunes
    without an intro still get an intro file: the first x seconds, without
    the tail of a pass that never played.
    """
    x = max(_tail_s(t, t.intro) if t.intro else 0.0, _tail_s(t, t.loop)) + 0.05
    intro_s, loop_s = _seconds(t, t.intro), _seconds(t, t.loop)
    full = _render(t, t.intro + t.loop * 3)
    a = int(round((intro_s + x) * SR))
    b = int(round((intro_s + loop_s + x) * SR))
    n = int(round(loop_s * SR))
    return full, slice(0, a), slice(b, b + n)


def write_game_files():
    (GAME_OUT / 'music').mkdir(parents=True, exist_ok=True)
    (GAME_OUT / 'sfx').mkdir(parents=True, exist_ok=True)
    total = 0
    for name, (tune, loudness) in TUNES.items():
        full, intro, loop = game_files(tune())
        # Loudness is measured on the loop, and the same gain goes to both
        # files, so the hand-over from intro to loop keeps its level.
        y, peak = finish(full, loudness, ref=loop)
        for part, sl in (('intro', intro), ('loop', loop)):
            total += _write_ogg(GAME_OUT / 'music' / f'{name}_{part}.ogg', y[sl])
        print(f'{name}: intro {(intro.stop - intro.start) / SR:.1f} s, '
              f'loop {(loop.stop - loop.start) / SR:.1f} s, peak {peak:.2f}')
    for fn, loudness in SFX.items():
        y, peak = finish(fn(), loudness, window_s=0.05)
        total += _write_ogg(GAME_OUT / 'sfx' / f'{fn.__name__}.ogg', y)
    print(f'total {total / 1e6:.1f} MB')


def _write_ogg(path, x):
    soundfile.write(str(path), np.clip(x, -1, 1), SR, format='OGG',
                    subtype='VORBIS', compression_level=VORBIS_LEVEL)
    return path.stat().st_size


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
