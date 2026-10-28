"""Scores for the KFW soundtrack drafts (see playlist.md).

Each tune is a function returning a `Tune`. Melodies are mostly pentatonic;
accompaniment is generated from chord names with `chord_line`. Durations are
in 16ths: a 4/4 bar is 16 steps, a 3/4 bar 12.
"""
import re
from typing import List, NamedTuple

from chipsynth import Inst, Voice, midi, note_name, transpose


class Tune(NamedTuple):
    bpm: int
    voices: dict
    sections: dict
    intro: List[str]
    loop: List[str]
    bar_steps: int = 16
    swing: float = 0.0


_CHORD_RE = re.compile(r'^([A-G][#b]?)(m|5|sus4|sus2|aug|dim)?$')
_THIRD = {'': 4, 'm': 3, '5': 7, 'sus4': 5, 'sus2': 2, 'aug': 4, 'dim': 3}
_FIFTH = {'aug': 8, 'dim': 6}


def _interval(key, third, fifth):
    named = {'R': 0, '3': third, '5': fifth, '8': 12, '10': third + 12,
             '-5': fifth - 12, '-8': -12, '6': 9, '2': 2, '4': 5, 'b7': 10,
             '9': 14, 'b2': 1}
    return named[key]


def chord_line(chords, pattern, octave, bar_steps=16):
    """Accompaniment from per-bar chord names.

    `chords`: one entry per bar; 'C D' splits the bar evenly. `pattern`: one
    bar of tokens like 'R:2 5:2 8:4 r:2 x:2' — R/3/5/8/10/... are chord
    intervals, `x` the whole triad as an arpeggio, `r` a rest.
    """
    toks = [(k, int(n)) for k, n in (t.split(':') for t in pattern.split())]
    if sum(n for _, n in toks) != bar_steps:
        raise ValueError(f'pattern is not one bar: {pattern}')
    out = []
    for bar in chords:
        parts = bar.split()
        pos = 0
        for key, n in toks:
            m = _CHORD_RE.match(parts[pos * len(parts) // bar_steps])
            q = m.group(2) or ''
            root, third, fifth = (midi(m.group(1) + str(octave)), _THIRD[q],
                                  _FIFTH.get(q, 7))
            if key == 'r':
                out.append(f'r:{n}')
            elif key == 'x':
                notes = ''.join(note_name(root + i) for i in (0, third, fifth))
                out.append(f'[{notes}]:{n}')
            else:
                out.append(
                    f'{note_name(root + _interval(key, third, fifth))}:{n}')
            pos += n
        out.append('|')
    return ' '.join(out)


def bars(*patterns):
    return ' | '.join(patterns)


def drums(bar, n, first=None, last=None):
    """`n` bars of one drum pattern, optionally with a different first/last."""
    out = [bar] * n
    if first:
        out[0] = first
    if last:
        out[-1] = last
    return ''.join(out)


# Instrument presets
BASS = Inst('tri', a=0.002, d=0.0, s=1.0, r=0.02)
SOFT_BASS = Inst('tri', a=0.005, d=0.0, s=1.0, r=0.04)
LEAD = Inst('pulse', 0.25, a=0.005, d=0.12, s=0.7, r=0.1, vib=0.2,
            vib_delay=0.2)
FLUTE = Inst('pulse', 0.5, a=0.03, d=0.2, s=0.7, r=0.15, vib=0.2,
             vib_rate=5.0, vib_delay=0.25, slide=0.09)
ERHU = Inst('pulse', 0.25, a=0.05, d=0.2, s=0.8, r=0.15, vib=0.35,
            vib_rate=5.5, vib_delay=0.12, slide=0.12)
PLUCK = Inst('pulse', 0.125, a=0.002, d=0.18, s=0.0, r=0.05)
HARM = Inst('pulse', 0.5, a=0.01, d=0.2, s=0.6, r=0.1, vib=0.2,
            vib_delay=0.25)
STAB = Inst('pulse', 0.5, a=0.002, d=0.06, s=0.2, r=0.03)
ARPS = Inst('pulse', 0.125, a=0.002, d=0.12, s=0.3, r=0.05)


def pipa(bpm):
    """Tremolo lute: retriggers every 32nd note."""
    return Inst('pulse', 0.125, a=0.002, d=0.0, s=0.8, r=0.08, vib=0.1,
                trem=60 / bpm / 8)


# --- 1. Title: The Path of the Fist -----------------------------------------

TITLE_THEME = bars(  # also quoted by the finale
    'D5:6 E5:2 G5:4 A5:4', 'B5:6 A5:2 G5:4 E5:4', 'D5:4 E5:2 D5:2 B4:4 A4:4',
    'G4:12 A4:2 B4:2', 'D5:6 E5:2 G5:4 A5:4', 'B5:4 D6:4 B5:2 A5:2 G5:4',
    'A5:4 G5:2 E5:2 D5:4 E5:4', 'G5:12 r:4')


def path_of_the_fist():
    voices = {
        'lead': Voice(Inst('pulse', 0.25, a=0.01, d=0.15, s=0.75, r=0.12,
                           vib=0.25, vib_delay=0.2), 0.55, echo=(3, 0.35)),
        'harm': Voice(Inst('pulse', 0.5, a=0.01, d=0.2, s=0.6, r=0.1,
                           vib=0.2, vib_delay=0.25), 0.28),
        'arps': Voice(Inst('pulse', 0.125, a=0.002, d=0.12, s=0.3, r=0.05),
                      0.3),
        'bass': Voice(Inst('tri', a=0.002, d=0.0, s=1.0, r=0.02), 0.9),
        'drums': Voice(None, 0.85),
    }
    a_chords = ['G', 'Em', 'D', 'G', 'G', 'Em', 'C D', 'G']
    a_lead = TITLE_THEME
    a_drums = ('c.h.s.hkk.h.s.h.' + 'k.h.s.hkk.h.s.h.' * 6
               + 'k.h.s.h.t.tTT.ss')
    a_bass = chord_line(a_chords, 'R:3 R:1 5:2 8:2 R:3 R:1 5:2 8:2', 2)
    a_arps = chord_line(a_chords, 'x:2 r:2 x:2 r:1 x:1 r:2 x:2 x:2 r:2', 4)
    b_chords = ['Em', 'G', 'Em', 'Em', 'G', 'Am', 'C', 'D']
    sections = {
        'intro': {
            'bars': 2,
            'lead': 'r:16 | r:10 G4:2 A4:2 B4:2',
            'bass': 'G2:16 | G2:8 D2:4 D3:4',
            'drums': 'g............... t.t.ttT.T.TTs.ss',
        },
        'A': {'bars': 8, 'lead': a_lead, 'bass': a_bass, 'arps': a_arps,
              'drums': a_drums},
        'B': {
            'bars': 8,
            'lead': bars(
                'E5:4 r:2 E5:2 G5:4 E5:4', 'D5:4 B4:4 D5:8',
                'E5:4 r:2 E5:2 G5:4 A5:4', 'B5:12 A5:2 B5:2',
                'D6:6 B5:2 A5:4 G5:4', 'A5:6 G5:2 E5:8', 'D5:4 E5:4 G5:4 A5:4',
                'B5:16'),
            'bass': chord_line(b_chords, 'R:4 R:2 5:2 R:4 8:4', 2),
            'arps': chord_line(b_chords, 'x:6 x:2 x:8', 4),
            'drums': ('g...s..wk.w.s..w' + 'k...s..wk.w.s..w' * 6
                      + 's.s.s.ssT.T.TTTT'),
        },
        'A2': {'bars': 8, 'lead': a_lead, 'harm': transpose(a_lead, -5),
               'bass': a_bass, 'arps': a_arps, 'drums': a_drums},
    }
    return Tune(120, voices, sections, ['intro'], ['A', 'B', 'A2'])


# --- 3. Town day: Morning Market ---------------------------------------------


def morning_market():
    voices = {
        'lead': Voice(Inst('pulse', 0.5, a=0.03, d=0.2, s=0.7, r=0.15,
                           vib=0.2, vib_rate=5.0, vib_delay=0.25, slide=0.09),
                      0.5, echo=(3, 0.3)),
        'pluck': Voice(Inst('pulse', 0.125, a=0.002, d=0.18, s=0.0, r=0.05),
                       0.3),
        'bass': Voice(Inst('tri', a=0.005, d=0.0, s=1.0, r=0.04), 0.8),
        'drums': Voice(None, 1.1),
    }
    pluck = 'R:2 5:2 8:2 10:2 8:2 5:2 3:2 5:2'
    bass = 'R:4 r:2 5:2 8:4 5:4'
    blocks = 'w..W..w.w.W.....'
    a_chords = ['D', 'Bm', 'G', 'A', 'D', 'Bm', 'G A', 'D']
    b_chords = ['Bm', 'G', 'D', 'A', 'Bm', 'G', 'A', 'D']
    sections = {
        'intro': {
            'bars': 2,
            'pluck': chord_line(['D'], pluck, 4)
            + ' D5:1 E5:1 F#5:1 A5:1 B5:1 D6:1 E6:1 F#6:1 A6:8',
            'bass': 'D2:16 | A1:8 A2:8',
            'drums': 'w...............' + 'w...w...w.W.W.W.',
        },
        'A': {
            'bars': 8,
            'lead': bars(
                'E5>F#5:4 A5:2 B5:2 A5:4 F#5:2 E5:2', 'C#5>D5:6 E5:2 F#5:8',
                'E5:4 F#5:2 A5:2 B5:4 A5:2 F#5:2', 'E5:12 r:4',
                'F#5:4 A5:2 B5:2 D6:4 B5:2 A5:2', 'B5:4 A5:2 F#5:2 E5:4 D5:4',
                'E5:4 F#5:2 E5:2 D5:2 B4:2 A4:4', 'D5:12 r:4'),
            'pluck': chord_line(a_chords, pluck, 4),
            'bass': chord_line(a_chords, bass, 2),
            'drums': blocks * 7 + 'w.w.W.W.w.W.WW..',
        },
        'B': {
            'bars': 8,
            'lead': bars(
                'B5:6 A5:2 F#5:4 A5:4', 'B5:4 D6:4 D6>E6:8',
                'D6:4 B5:2 A5:2 F#5:4 A5:4', 'E5:12 r:4',
                'F#5:4 E5:2 D5:2 B4:4 D5:4', 'E5:4 F#5:4 A5:4 B5:4',
                'A5:6 F#5:2 E5:4 F#5:2 E5:2', 'D5:16'),
            'pluck': chord_line(b_chords, pluck, 4),
            'bass': chord_line(b_chords, bass, 2),
            'drums': ('w..W..w.w.W...h.' * 7 + 'w.w.W.W.w.W.w.W.'),
        },
    }
    return Tune(100, voices, sections, ['intro'], ['A', 'B'])


# --- 8. Street fight: Fists Like Rain ----------------------------------------


def fists_like_rain():
    step = 60 / 152 / 4
    voices = {
        'lead': Voice(Inst('pulse', 0.25, a=0.003, d=0.08, s=0.6, r=0.05,
                           vib=0.15, vib_delay=0.25), 0.62, echo=(3, 0.3)),
        'harm': Voice(Inst('pulse', 0.5, a=0.003, d=0.1, s=0.5, r=0.05), 0.25),
        'pipa': Voice(Inst('pulse', 0.125, a=0.002, d=0.0, s=0.8, r=0.08,
                           vib=0.1, trem=step / 2), 0.5, echo=(2, 0.25)),
        'stabs': Voice(Inst('pulse', 0.5, a=0.002, d=0.06, s=0.2, r=0.03),
                       0.3),
        'bass': Voice(Inst('tri', a=0.002, d=0.0, s=1.0, r=0.02), 0.95),
        'drums': Voice(None, 0.85),
    }
    a_chords = ['Em', 'Em', 'C', 'D', 'Em', 'Em', 'C', 'B']
    a_lead = bars(
        'E5:2 E5:1 G5:1 A5:2 G5:2 E5:2 D5:2 E5:4',
        'r:2 B4:2 D5:2 E5:2 G5:4 A5:2 B5:2', 'B5:2 A5:2 G5:2 E5:2 G5:4 A5:4',
        'A5:6 B5:2 D6:8', 'E6:2 D6:2 B5:2 A5:2 B5:4 E5:4',
        'G5:2 A5:2 B5:2 D6:2 B5:2 A5:2 G5:4', 'E5:3 G5:3 A5:2 G5:2 E5:2 C5:4',
        'D#5:4 F#5:4 B5:8')
    a_bass = chord_line(a_chords, 'R:2 R:2 8:2 R:2 R:2 5:2 8:2 5:2', 2)
    a_stabs = chord_line(a_chords, 'r:2 x:2 r:2 x:2 r:2 x:2 r:2 x:2', 4)
    a_drums = ('c.h.s.hkk.hks.h.' + 'k.h.s.hkk.hks.h.' * 6
               + 'k.h.s.h.t.t.T.Ts')
    b_chords = ['Am', 'Em', 'Am', 'B', 'C', 'D', 'B', 'B']
    sections = {
        'intro': {
            'bars': 2,
            'bass': 'E2:2 r:1 E2:1 r:2 E2:2 r:2 E2:2 E2:2 D2:2 | '
                    'E2:2 E2:2 E3:2 E2:2 G2:2 A2:2 B2:2 D3:2',
            'drums': 'c..k..k.k..k.s..' + 'k.k.k.k.s.s.ssss',
        },
        'A': {'bars': 8, 'lead': a_lead, 'bass': a_bass, 'stabs': a_stabs,
              'drums': a_drums},
        'A2': {'bars': 8, 'lead': a_lead, 'harm': transpose(a_lead, -5),
               'bass': a_bass, 'stabs': a_stabs, 'drums': a_drums},
        'B': {
            'bars': 8,
            'pipa': bars(
                'A5:8 C6:4 B5:4', 'G5:8 E5:8', 'A5:8 C6:4 D6:4', 'B5:16',
                'C6:8 E6:4 D6:4', 'D6:8 B5:4 A5:4', 'B5:8 F#5:4 A5:4',
                'B5:16'),
            'bass': chord_line(b_chords, 'R:4 r:2 R:2 5:4 8:4', 2),
            'stabs': chord_line(b_chords, 'x:8 x:8', 4),
            'drums': ('g.h.h.h.s.h.h.hk' + 'k.h.h.h.s.h.h.hk' * 6
                      + 's.s.s.s.ssssssss'),
        },
    }
    return Tune(152, voices, sections, ['intro'], ['A', 'A2', 'B'])


# --- 2. New game: Choosing a Style -------------------------------------------


def choosing_a_style():
    voices = {
        'lead': Voice(Inst('pulse', 0.25, a=0.003, d=0.25, s=0.35, r=0.1,
                           vib=0.15, vib_delay=0.2), 0.55, echo=(3, 0.3)),
        'bells': Voice(PLUCK, 0.28),
        'bass': Voice(BASS, 0.85),
        'drums': Voice(None, 0.8),
    }
    a_chords = ['C', 'Am', 'F', 'G', 'C', 'Am', 'F G', 'C']
    b_chords = ['F', 'G', 'Em', 'Am', 'F', 'G', 'Am', 'G']
    bells = 'r:2 x:1 r:3 x:1 r:1 x:1 r:3 x:2 r:2'
    bass = 'R:4 5:2 R:2 8:4 5:4'
    beat = 'k...w.h.k.k.w.h.'
    sections = {
        'intro': {'bars': 2, 'bells': chord_line(['C', 'G'], bells, 5),
                  'bass': 'C2:16 | G2:16',
                  'drums': drums('....w.h.....w.h.', 2)},
        'A': {
            'bars': 8,
            'lead': bars(
                'E5:2 G5:2 A5:2 G5:2 E5:4 D5:4', 'C5:2 D5:2 E5:2 G5:2 A5:8',
                'A5:2 C6:2 A5:2 G5:2 E5:4 C5:4', 'D5:6 E5:2 D5:8',
                'E5:2 G5:2 A5:2 G5:2 E5:4 G5:4', 'A5:2 C6:2 D6:2 C6:2 A5:8',
                'G5:2 A5:2 G5:2 E5:2 D5:4 E5:2 D5:2', 'C5:12 r:4'),
            'bells': chord_line(a_chords, bells, 5),
            'bass': chord_line(a_chords, bass, 2),
            'drums': drums(beat, 8, last='k...w.h.k.w.w.ww'),
        },
        'B': {
            'bars': 8,
            'lead': bars(
                'A5:4 A5:2 G5:2 A5:4 C6:4', 'D6:4 C6:2 A5:2 G5:8',
                'E5:4 G5:2 E5:2 D5:4 E5:4', 'A4:2 C5:2 E5:2 A5:2 G5:4 E5:4',
                'F5:4 A5:2 C6:2 A5:4 G5:4', 'G5:4 A5:2 G5:2 D5:8',
                'E5:2 D5:2 C5:2 D5:2 E5:4 A5:4', 'G5:8 D5:4 G4:4'),
            'bells': chord_line(b_chords, bells, 5),
            'bass': chord_line(b_chords, bass, 2),
            'drums': drums(beat, 8, last='k.k.w.w.t.t.T.T.'),
        },
    }
    return Tune(110, voices, sections, ['intro'], ['A', 'B'])


# --- 4. Town day: Teahouse Afternoon (3/4) -----------------------------------


def teahouse_afternoon():
    voices = {
        'lead': Voice(ERHU, 0.5, echo=(3, 0.25)),
        'flute': Voice(FLUTE, 0.25),
        'pluck': Voice(PLUCK, 0.3),
        'bass': Voice(SOFT_BASS, 0.8),
        'drums': Voice(None, 1.6),
    }
    a_chords = ['F', 'Dm', 'Bb', 'C', 'F', 'Dm', 'C', 'F']
    b_chords = ['Bb', 'C', 'Am', 'Dm', 'Bb', 'C', 'Dm', 'C']
    pluck = 'R:2 5:2 8:2 10:2 8:2 5:2'
    bass = 'R:4 r:4 5:4'
    beat = 'W...w...w...'
    a_lead = bars(
        'C5>D5:6 C5:2 A4:4', 'D5:4 F5:4 A5:4', 'G5:6 F5:2 D5:4', 'C5:12',
        'A5:6 G5:2 F5:4', 'D5:4 F5:2 G5:2 A5:4', 'G5:4 F5:2 D5:2 C5:2 D5:2',
        'F5:12')
    a = {'pluck': chord_line(a_chords, pluck, 4, 12),
         'bass': chord_line(a_chords, bass, 2, 12),
         'drums': drums(beat, 8, last='W...w.w.w.w.')}
    sections = {
        'intro': {'bars': 2, 'pluck': chord_line(['F', 'C'], pluck, 4, 12),
                  'bass': 'F2:12 | C2:12', 'drums': drums(beat, 2)},
        'A': dict(a, bars=8, lead=a_lead),
        'B': {
            'bars': 8,
            'lead': bars(
                'D6:6 C6:2 A5:4', 'G5:4 A5:2 G5:2 C5:4', 'A5>C6:6 A5:2 G5:4',
                'F5:4 D5:4 A4:4', 'F5:6 G5:2 D5:4', 'C5:4 D5:2 F5:2 G5:4',
                'A5:6 G5:2 F5:2 D5:2', 'C5:12'),
            'pluck': chord_line(b_chords, pluck, 4, 12),
            'bass': chord_line(b_chords, bass, 2, 12),
            'drums': drums(beat, 8, last='W...w.w.w.w.'),
        },
        'A2': dict(a, bars=8, lead=a_lead, flute=transpose(a_lead, -12)),
    }
    return Tune(96, voices, sections, ['intro'], ['A', 'B', 'A2'],
                bar_steps=12)


# --- 5. Town day: Lanterns at Dusk -------------------------------------------


def lanterns_at_dusk():
    voices = {
        'lead': Voice(FLUTE, 0.5, echo=(4, 0.3)),
        'pad': Voice(HARM, 0.18),
        'pluck': Voice(PLUCK, 0.3),
        'bass': Voice(SOFT_BASS, 0.8),
        'drums': Voice(None, 1.6),
    }
    a_chords = ['Am', 'F', 'C', 'G', 'Am', 'F', 'G', 'Am']
    b_chords = ['F', 'G', 'Em', 'Am', 'F', 'G', 'Esus4', 'E']
    pluck = 'R:2 5:2 8:2 5:2 10:2 5:2 8:2 5:2'
    bass = 'R:8 5:8'
    beat = 'W.......w...h...'
    sections = {
        'intro': {'bars': 2, 'pluck': chord_line(['Am', 'Am'], pluck, 4),
                  'bass': 'A2:16 | A2:16', 'drums': drums('W' + '.' * 15, 2)},
        'A': {
            'bars': 8,
            'lead': bars(
                'E5:6 D5:2 C5:4 A4:4', 'C5:4 D5:4 E5:8', 'G5:6 E5:2 D5:4 C5:4',
                'D5:12 r:4', 'E5:6 G5:2 A5:4 G5:4', 'E5:4 D5:2 C5:2 A4:8',
                'C5:4 D5:4 G4:4 D5>E5:4', 'A4:12 r:4'),
            'pluck': chord_line(a_chords, pluck, 4),
            'bass': chord_line(a_chords, bass, 2),
            'drums': drums(beat, 8),
        },
        'B': {
            'bars': 8,
            'lead': bars(
                'A5:6 G5:2 E5:4 G5:4', 'G5:6 E5:2 D5:8',
                'E5:4 G5:2 E5:2 D5:4 B4:4', 'C5:4 E5:4 A5:8',
                'C6:6 A5:2 G5:4 E5:4', 'D5:4 E5:2 G5:2 A5:4 G5:4',
                'E5:8 D5:4 B4:4', 'E5:12 r:4'),
            'pad': chord_line(b_chords, '3:8 5:8', 4),
            'pluck': chord_line(b_chords, pluck, 4),
            'bass': chord_line(b_chords, bass, 2),
            'drums': drums(beat, 8),
        },
    }
    return Tune(84, voices, sections, ['intro'], ['A', 'B'])


# --- 6. School practice: Bamboo Courtyard ------------------------------------


def bamboo_courtyard():
    voices = {
        'lead': Voice(Inst('pulse', 0.25, a=0.003, d=0.08, s=0.4, r=0.04,
                           vib=0.1, vib_delay=0.15), 0.6, echo=(2, 0.25)),
        'harm': Voice(HARM, 0.25),
        'pipa': Voice(pipa(128), 0.45, echo=(2, 0.2)),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.9),
    }
    a_chords = ['Dm', 'Dm', 'C', 'C', 'Bb', 'C', 'Dm', 'Dm']
    b_chords = ['Gm', 'Am', 'Bb', 'C', 'Gm', 'Am', 'Bb', 'A']
    a_lead = bars(
        'D5:2 D5:2 F5:2 G5:2 A5:4 r:4', 'A4:2 A4:2 C5:2 D5:2 F5:4 r:4',
        'C5:2 C5:2 E5:2 G5:2 A5:4 G5:4', 'G4:2 G4:2 A4:2 C5:2 E5:4 r:4',
        'D6:2 C6:2 A5:2 G5:2 F5:4 D5:4', 'C6:2 A5:2 G5:2 F5:2 E5:4 C5:4',
        'D5:2 F5:2 A5:2 D6:2 C6:2 A5:2 G5:2 F5:2', 'D5:4 r:2 D5:2 D5:4 r:4')
    a = {'bass': chord_line(a_chords, 'R:2 R:2 r:2 R:2 8:2 R:2 5:2 8:2', 2),
         'drums': drums('k.w.s.w.k.wwsw.w', 8, first='c.w.s.w.k.wwsw.w',
                        last='k.w.s.w.t.t.T.T.')}
    sections = {
        'intro': {'bars': 2, 'bass': chord_line(
            ['Dm', 'Dm'], 'R:2 R:2 r:2 R:2 8:2 R:2 5:2 8:2', 2),
            'drums': 'k.w.s.w.k.w.s.w.' + 'k.w.s.w.t.t.T.T.'},
        'A': dict(a, bars=8, lead=a_lead),
        'B': {
            'bars': 8,
            'pipa': bars(
                'G5:8 Bb5:4 A5:4', 'A5:8 C6:4 E6:4', 'D6:8 C6:4 Bb5:4',
                'C6:8 G5:8', 'Bb5:6 A5:2 G5:4 D5:4', 'C5:6 D5:2 E5:8',
                'F5:4 G5:4 A5:4 Bb5:4', 'A5:8 C#6:4 E6:4'),
            'bass': chord_line(b_chords, 'R:4 R:2 5:2 R:4 8:4', 2),
            'drums': drums('k...s...k.k.s...', 8, first='g...s...k.k.s...',
                           last='s.s.s.s.ssssT.T.'),
        },
        'A2': dict(a, bars=8, lead=a_lead, harm=transpose(a_lead, -5)),
    }
    return Tune(128, voices, sections, ['intro'], ['A', 'B', 'A2'])


# --- 7. Master's teachings: Words of the Master ------------------------------


def words_of_the_master():
    guqin = Inst('pulse', 0.25, a=0.003, d=1.6, s=0.0, r=0.3, vib=0.12,
                 vib_rate=4.5, vib_delay=0.3, slide=0.15)
    voices = {
        'guqin': Voice(guqin, 0.6, echo=(4, 0.3)),
        'harmonics': Voice(Inst('pulse', 0.125, a=0.002, d=0.5, s=0.0, r=0.2),
                           0.3, echo=(3, 0.35)),
        'bass': Voice(SOFT_BASS, 0.6),
        'drums': Voice(None, 0.8),
    }
    sections = {
        'A': {
            'bars': 8,
            'guqin': bars(
                'E4:4 r:2 G4:2 A4>B4:8', 'D5:4 B4:4 A4:4 G4:4',
                'E4:8 r:4 D4>E4:4', 'B3:16', 'G4:4 A4:2 B4:2 D5:8',
                'E5:4 D5:2 B4:2 A4>B4:8', 'A4:4 G4:4 E4:4 D4:4', 'E4:16'),
            'bass': 'E2:16 | E2:16 | E2:16 | B1:16 | G2:16 | E2:16 | '
                    'A2:8 D2:8 | E2:16',
            'drums': 'g' + '.' * 15 + '.' * 16 * 6 + '........W.......',
        },
        'B': {
            'bars': 8,
            'harmonics': bars(
                'B5:4 r:4 E6:4 r:4', 'D6:4 r:4 B5:8', 'A5:4 r:4 G5:4 r:4',
                'E5:16', 'G5:4 r:4 A5:4 r:4', 'B5:4 r:4 D6:8',
                'E6:4 r:4 D6:4 B5:4', 'E6:16'),
            'guqin': bars('E3:8 B3:8', 'G3:8 D4:8', 'A3:8 E4:8', 'B3:16',
                          'C4:8 G4:8', 'D4:8 A4:8', 'C4:8 B3:8', 'E3:16'),
            'bass': 'E2:16 | G2:16 | A2:16 | B1:16 | C2:16 | D2:16 | '
                    'C2:8 B1:8 | E2:16',
            'drums': drums('W' + '.' * 31, 4),
        },
    }
    return Tune(72, voices, sections, [], ['A', 'B'])


# --- 9. Street fight: Alley Cats (swung) -------------------------------------


def alley_cats():
    voices = {
        'lead': Voice(Inst('pulse', 0.25, a=0.003, d=0.1, s=0.45, r=0.05,
                           vib=0.15, vib_delay=0.2, slide=0.05), 0.6,
                      echo=(3, 0.25)),
        'harm': Voice(HARM, 0.25),
        'stabs': Voice(STAB, 0.3),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.85),
    }
    a_chords = ['Am', 'D', 'Am', 'E', 'Am', 'D', 'E', 'Am']
    b_chords = ['Dm', 'Am', 'Dm', 'Am', 'F', 'E', 'F', 'E']
    a_lead = bars(
        'A4:2 C5:2 r:2 D5:2 Eb5:1 E5:3 C5:2 A4:2', 'r:4 G5:2 E5:2 D5:4 C5:4',
        'A4:2 C5:2 r:2 D5:2 Eb5:1 E5:3 G5:2 A5:2', 'G#5:4 E5:2 D5:2 B4:8',
        'A5:2 A5:2 G5:2 E5:2 G5:2 E5:2 D5:2 C5:2',
        'D5:2 F#5:2 A5:2 C6:2 A5:4 F#5:4', 'E5:2 G#5:2 B5:2 D6:2 r:2 B5:2 G#5:4',
        'A5:4 E5:2 C5:2 A4:4 r:4')
    a = {'bass': chord_line(a_chords, 'R:4 3:4 5:4 6:4', 2),
         'stabs': chord_line(a_chords, 'r:4 x:2 r:6 x:2 r:2', 4),
         'drums': drums('k.h.s.hhk.h.s.hh', 8, first='c.h.s.hhk.h.s.hh',
                        last='k.h.s.hhk.t.t.T.')}
    sections = {
        'intro': {'bars': 1, 'bass': 'A2:4 C3:4 D3:4 Eb3:4',
                  'drums': 'k...k...k.k.s.s.'},
        'A': dict(a, bars=8, lead=a_lead),
        'B': {
            'bars': 8,
            'lead': bars(
                'F5:2 r:2 F5:2 r:2 E5:2 F5:2 A5:4',
                'E5:2 r:2 E5:2 r:2 C5:2 E5:2 A4:4',
                'D5:2 F5:2 A5:2 D6:2 C6:2 A5:2 F5:4', 'E5:12 r:4',
                'A5:2 r:2 C6:2 r:2 A5:2 F5:2 C5:4',
                'B4:2 r:2 D5:2 r:2 E5:2 G#5:2 B5:4', 'C6:4 A5:4 F5:4 Eb5:4',
                'E5:2 r:2 E5:2 r:2 E5:2 E5:2 E5:4'),
            'bass': chord_line(b_chords, 'R:2 r:2 R:2 r:2 5:2 R:2 8:4', 2),
            'stabs': chord_line(b_chords, 'x:2 r:6 x:2 r:6', 4),
            'drums': drums('k.....s.k.....s.', 8, last='k.....s.s.s.ssss'),
        },
        'A2': dict(a, bars=8, lead=a_lead, harm=transpose(a_lead, -12)),
    }
    return Tune(140, voices, sections, ['intro'], ['A', 'B', 'A2'], swing=0.3)


# --- 10. Street fight: Thugs at the Bridge -----------------------------------


def thugs_at_the_bridge():
    voices = {
        'lead': Voice(Inst('pulse', 0.5, a=0.01, d=0.15, s=0.7, r=0.08,
                           vib=0.2, vib_delay=0.25), 0.55, echo=(2, 0.2)),
        'harm': Voice(Inst('pulse', 0.25, a=0.01, d=0.15, s=0.6, r=0.08), 0.3),
        'stabs': Voice(Inst('pulse', 0.25, a=0.002, d=0.1, s=0.3, r=0.04),
                       0.3),
        'bass': Voice(BASS, 1.0),
        'drums': Voice(None, 0.95),
    }
    a_chords = ['C5', 'C5', 'Ab5', 'Bb5', 'C5', 'C5', 'Ab5', 'G5']
    b_chords = ['Fm', 'Fm', 'C5', 'C5', 'Ab5', 'Bb5', 'G5', 'G5']
    bass = 'R:4 r:2 R:2 R:4 8:2 R:2'
    a_lead = bars(
        'C4:4 r:2 C4:2 Eb4:4 F4:4', 'G4:6 F4:2 Eb4:4 C4:4',
        'Eb4:4 r:2 Eb4:2 F4:4 C4:4', 'Bb4:8 G4:4 F4:4',
        'C5:4 r:2 C5:2 Bb4:4 G4:4', 'F4:4 G4:2 F4:2 Eb4:4 C4:4',
        'Eb4:4 F4:4 G4:4 Bb4:4', 'G4:4 B4:4 D5:8')
    a = {'bass': chord_line(a_chords, bass, 2),
         'stabs': chord_line(a_chords, 'x:3 x:3 x:2 r:8', 3),
         'drums': drums('k..k....s..k....', 8, first='c..k....s..k....',
                        last='k..k....s.s.ssss')}
    sections = {
        'intro': {'bars': 2, 'bass': 'C2:8 C2:8 | C2:8 G1:8',
                  'drums': 'k.......k.......' + 'k.......k...ssss'},
        'A': dict(a, bars=8, lead=a_lead),
        'B': {
            'bars': 8,
            'lead': bars(
                'F5:4 Ab5:4 G5:2 F5:2 Eb5:4', 'C5:8 F5:8',
                'G5:4 Bb5:4 G5:2 F5:2 Eb5:4', 'C5:16', 'Eb5:4 F5:4 G5:4 Ab5:4',
                'Bb5:8 Ab5:4 G5:4', 'G5:4 F5:2 Eb5:2 D5:8',
                'B4:4 D5:4 F5:4 G5:4'),
            'bass': chord_line(b_chords, bass, 2),
            'stabs': chord_line(b_chords, 'x:3 x:3 x:2 r:8', 3),
            'drums': drums('k.k.s..kk.k.s...', 8, last='TTttTTttssssssss'),
        },
        'A2': dict(a, bars=8, lead=transpose(a_lead, 12), harm=a_lead),
    }
    return Tune(116, voices, sections, ['intro'], ['A', 'B', 'A2'])


# --- 11. Group fights: Outnumbered -------------------------------------------


def outnumbered():
    voices = {
        'lead': Voice(Inst('pulse', 0.25, a=0.002, d=0.08, s=0.6, r=0.04,
                           vib=0.15, vib_delay=0.2), 0.55, echo=(3, 0.3)),
        'harm': Voice(HARM, 0.25),
        'pipa': Voice(pipa(168), 0.45, echo=(2, 0.25)),
        'stabs': Voice(STAB, 0.25),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.85),
    }
    a_chords = ['F#m', 'F#m', 'D', 'E', 'F#m', 'F#m', 'D', 'C#']
    b_chords = ['G#m', 'G#m', 'E', 'F#', 'G#m', 'G#m', 'E', 'D#']
    c_chords = ['Bm', 'C#m', 'D', 'E', 'Bm', 'C#m', 'D', 'C#']
    bass16 = ' '.join(['R:1 R:1 8:1 R:1'] * 4)
    stabs = 'r:2 x:2 r:2 x:2 r:2 x:2 r:2 x:2'
    beat = drums('k.hks.hkk.hks.hk', 8, first='c.hks.hkk.hks.hk',
                 last='k.s.s.s.ssssssss')
    a_lead = bars(
        'F#5:2 A5:2 B5:2 C#6:2 B5:2 A5:2 F#5:4',
        'E5:2 F#5:2 A5:2 F#5:2 E5:2 C#5:2 B4:4', 'A5:2 B5:2 A5:2 F#5:2 A5:4 D6:4',
        'B5:4 G#5:4 E5:4 B5:4', 'F#6:2 E6:2 C#6:2 B5:2 C#6:2 B5:2 A5:2 F#5:2',
        'A5:2 B5:2 C#6:2 E6:2 F#6:8', 'D6:2 C#6:2 A5:2 F#5:2 D5:4 F#5:4',
        'F5:4 G#5:4 C#6:8')
    b_lead = transpose(a_lead, 2)
    sections = {
        'intro': {'bars': 1, 'bass': chord_line(['F#m'], bass16, 2),
                  'drums': 'k.k.k.k.s.s.ssss'},
        'A': {'bars': 8, 'lead': a_lead, 'bass': chord_line(a_chords, bass16, 2),
              'stabs': chord_line(a_chords, stabs, 4), 'drums': beat},
        'B': {'bars': 8, 'lead': b_lead, 'harm': transpose(b_lead, -5),
              'bass': chord_line(b_chords, bass16, 2),
              'stabs': chord_line(b_chords, stabs, 4), 'drums': beat},
        'C': {
            'bars': 8,
            'pipa': bars('B5:8 D6:8', 'C#6:8 E6:8', 'F#6:8 E6:4 D6:4', 'E6:16',
                         'D6:8 C#6:4 B5:4', 'C#6:8 B5:4 A5:4',
                         'B5:8 A5:4 F#5:4', 'F5:8 G#5:8'),
            'bass': chord_line(c_chords, 'R:4 r:2 R:2 5:4 8:4', 2),
            'stabs': chord_line(c_chords, 'x:8 x:8', 4),
            'drums': drums('k.h.h.h.s.h.h.hk', 8, first='g.h.h.h.s.h.h.hk',
                           last='s.s.s.s.ssssssss'),
        },
    }
    return Tune(168, voices, sections, ['intro'], ['A', 'B', 'C'])


# --- 12. Free-for-all: Every Fist for Itself ---------------------------------


def every_fist_for_itself():
    voices = {
        'lead': Voice(LEAD, 0.55, echo=(3, 0.3)),
        'harm': Voice(HARM, 0.25),
        'stabs': Voice(STAB, 0.28),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.85),
    }
    a_chords = ['Bm', 'Bm', 'C', 'C', 'Bm', 'Bm', 'A', 'G']
    b_chords = ['Em', 'F#m', 'G', 'A', 'Em', 'F#', 'G', 'F#']
    bass = 'R:3 R:3 8:3 R:3 5:2 8:2'  # 3+3+3+3+2+2: the lurching accents
    stabs = 'x:3 x:3 x:3 x:3 r:4'
    a_lead = bars(
        'B4:3 D5:3 F#5:3 B5:3 A5:2 F#5:2', 'G5:3 F#5:3 E5:3 D5:3 C5:4',
        'C5:3 E5:3 G5:3 C6:3 B5:2 G5:2', 'B5:6 A5:6 G5:4',
        'F#5:3 B5:3 D6:3 C6:3 B5:2 A5:2', 'B5:3 F#5:3 D5:3 B4:3 C5:4',
        'C#5:3 E5:3 A5:3 C#6:3 B5:2 A5:2', 'G5:6 F#5:6 r:4')
    a = {'bass': chord_line(a_chords, bass, 2),
         'stabs': chord_line(a_chords, stabs, 4),
         'drums': drums('k.hs.hk.hs.hk.s.', 8, first='c.hs.hk.hs.hk.s.',
                        last='k..s..k..s..ssss')}
    sections = {
        'intro': {'bars': 1, 'bass': 'B1:3 B1:3 B1:3 B1:3 B2:4',
                  'drums': 'k..k..k..k..ssss'},
        'A': dict(a, bars=8, lead=a_lead),
        'B': {
            'bars': 8,
            'lead': bars(
                'E6:4 r:2 E6:2 D6:4 B5:4', 'C#6:4 r:2 C#6:2 A5:4 F#5:4',
                'G5:3 B5:3 D6:3 G6:3 F#6:4', 'E6:3 C#6:3 A5:6 E5:4',
                'E5:2 G5:2 B5:2 E6:2 D6:2 B5:2 G5:4',
                'F#5:2 A#5:2 C#6:2 F#6:2 E6:2 C#6:2 A#5:4',
                'B5:4 G5:4 D5:4 B4:4', 'A#4:4 C#5:4 F#5:8'),
            'bass': chord_line(b_chords, bass, 2),
            'stabs': chord_line(b_chords, stabs, 4),
            'drums': drums('k..s..k..s..k.s.', 8, last='T..T..t..t..ssss'),
        },
        'A2': dict(a, bars=8, lead=a_lead, harm=transpose(a_lead, -5)),
    }
    return Tune(160, voices, sections, ['intro'], ['A', 'B', 'A2'])


# --- 13. Tournament: Tournament Day ------------------------------------------


def tournament_day():
    voices = {
        'horn': Voice(Inst('pulse', 0.5, a=0.02, d=0.2, s=0.75, r=0.15,
                           vib=0.2, vib_delay=0.3), 0.5, echo=(4, 0.3)),
        'lead': Voice(LEAD, 0.55, echo=(3, 0.3)),
        'harm': Voice(HARM, 0.25),
        'arps': Voice(ARPS, 0.3),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.9),
    }
    a_chords = ['D', 'D', 'G', 'A', 'D', 'Bm', 'G A', 'D']
    b_chords = ['Bm', 'A', 'G', 'A', 'Bm', 'A', 'G', 'A']
    a_lead = bars(
        'A5:4 A5:2 B5:2 A5:4 F#5:4', 'D5:4 E5:2 F#5:2 A5:8',
        'B5:4 B5:2 D6:2 B5:4 A5:4', 'E5:4 F#5:2 E5:2 A4:8',
        'A5:4 A5:2 B5:2 D6:4 B5:4', 'D6:4 B5:2 A5:2 F#5:8',
        'G5:4 B5:4 A5:4 E5:4', 'D5:12 r:4')
    a = {'bass': chord_line(a_chords, 'R:4 5:4 R:4 5:4', 2),
         'arps': chord_line(a_chords, 'x:2 r:2 x:2 r:2 x:2 r:2 x:2 r:2', 4),
         'drums': drums('k...s.s.k...s.ss', 8, first='c...s.s.k...s.ss',
                        last='k...s.s.t.t.T.T.')}
    sections = {
        'intro': {  # ceremonial: taiko and a horn call before the bouts
            'bars': 4,
            'horn': bars('D5:4 r:4 A4:4 D5:4', 'A5:12 r:4',
                         'B5:4 A5:4 F#5:4 E5:4', 'D5:8 A4:8'),
            'bass': 'D2:16 | D2:16 | G2:16 | A2:16',
            'drums': ('g...T...T...T.T.' + 'T...T...T...T.T.'
                      + 'T...T...t.t.T.T.' + 'T.T.T.T.ttttssss'),
        },
        'A': dict(a, bars=8, lead=a_lead),
        'B': {
            'bars': 8,
            'lead': bars(
                'F#5:2 F#5:2 A5:2 B5:2 D6:4 B5:4', 'C#6:2 C#6:2 B5:2 A5:2 E5:8',
                'D5:2 E5:2 F#5:2 A5:2 B5:4 D6:4', 'E6:4 C#6:4 A5:8',
                'F#6:2 E6:2 D6:2 B5:2 D6:4 B5:4', 'C#6:2 B5:2 A5:2 F#5:2 E5:8',
                'D5:2 G5:2 B5:2 D6:2 B5:4 G5:4', 'A5:4 C#6:4 E6:4 A5:4'),
            'bass': chord_line(b_chords, 'R:2 R:2 8:2 R:2 R:2 5:2 8:2 5:2', 2),
            'arps': chord_line(b_chords, 'r:2 x:2 r:2 x:2 r:2 x:2 r:2 x:2', 4),
            'drums': drums('k.hks.hkk.hks.hk', 8, last='k.s.s.s.ssssssss'),
        },
        'A2': dict(a, bars=8, lead=a_lead, harm=transpose(a_lead, -5)),
    }
    return Tune(136, voices, sections, ['intro'], ['A', 'B', 'A2'])


# --- 14. Tournament final: The Final Platform --------------------------------


def final_platform():
    voices = {
        'lead': Voice(LEAD, 0.55, echo=(3, 0.3)),
        'harm': Voice(HARM, 0.3),
        'pipa': Voice(pipa(144), 0.45, echo=(2, 0.25)),
        'stabs': Voice(STAB, 0.28),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.9),
    }
    a_chords = ['Em', 'C', 'D', 'B', 'Em', 'C', 'Am', 'B']
    b_chords = ['F#m', 'D', 'E', 'C#', 'F#m', 'D', 'Bm', 'C#']
    c_chords = ['C', 'D', 'Bm', 'Em', 'C', 'D', 'B', 'B']
    bass = 'R:2 R:2 8:2 R:2 R:2 5:2 8:2 5:2'
    stabs = 'r:2 x:2 r:2 x:2 r:2 x:2 r:2 x:2'
    beat = drums('k.hks.hkk.hks.hk', 8, first='c.hks.hkk.hks.hk',
                 last='k.s.s.s.t.t.T.T.')
    a_lead = bars(
        'E5:6 G5:2 B5:4 E6:4', 'D6:4 C6:2 B5:2 G5:8', 'A5:6 B5:2 D6:4 F#6:4',
        'D#6:8 B5:8', 'E6:2 D6:2 B5:2 G5:2 B5:4 E6:4', 'G6:4 E6:2 D6:2 C6:8',
        'A5:4 C6:4 E6:4 D6:4', 'B5:4 D#6:4 F#6:8')
    b_lead = transpose(a_lead, 2)  # the stakes rise a step
    sections = {
        'intro': {'bars': 2, 'lead': 'r:16 | B4:4 D#5:4 F#5:4 B5:4',
                  'bass': 'E2:16 | B1:16',
                  'drums': 'g...............' + 'T.T.T.T.ttttssss'},
        'A': {'bars': 8, 'lead': a_lead, 'harm': transpose(a_lead, -5),
              'bass': chord_line(a_chords, bass, 2),
              'stabs': chord_line(a_chords, stabs, 4), 'drums': beat},
        'B': {'bars': 8, 'lead': b_lead, 'harm': transpose(b_lead, -5),
              'bass': chord_line(b_chords, bass, 2),
              'stabs': chord_line(b_chords, stabs, 4), 'drums': beat},
        'C': {
            'bars': 8,
            'pipa': bars('C6:8 G5:8', 'D6:8 A5:8', 'B5:8 D6:4 F#6:4', 'E6:16',
                         'G6:8 E6:4 C6:4', 'A6:8 F#6:4 D6:4', 'D#6:16',
                         'F#6:8 D#6:8'),
            'bass': chord_line(c_chords, 'R:4 r:2 R:2 5:4 8:4', 2),
            'stabs': chord_line(c_chords, 'x:8 x:8', 4),
            'drums': drums('k.h.h.h.s.h.h.hk', 8, first='g.h.h.h.s.h.h.hk',
                           last='s.s.s.s.ssssssss'),
        },
    }
    return Tune(144, voices, sections, ['intro'], ['A', 'B', 'C'])


# --- 15. Story boss: Shadow of the Boss --------------------------------------


def shadow_of_the_boss():
    voices = {
        'lead': Voice(Inst('pulse', 0.5, a=0.01, d=0.2, s=0.8, r=0.1, vib=0.25,
                           vib_delay=0.3), 0.55, echo=(3, 0.3)),
        'harm': Voice(HARM, 0.25),
        'pipa': Voice(pipa(132), 0.45, echo=(2, 0.25)),
        'stabs': Voice(STAB, 0.28),
        'bass': Voice(BASS, 0.95),
        'drums': Voice(None, 0.9),
    }
    a_chords = ['C#m', 'C#m', 'D', 'D', 'C#m', 'C#m', 'A', 'G#']
    b_chords = ['F#m', 'F#m', 'D', 'D', 'A', 'A', 'G#', 'G#']
    ost = ' '.join(['R:1 R:1 8:1 R:1 b2:1 R:1 8:1 R:1'] * 2)  # relentless
    beat = drums('k.hkk.hks.hkk.hs', 8, first='c.hkk.hks.hkk.hs',
                 last='k.hkk.hks.s.ssss')
    a_lead = bars(
        'C#5:8 E5:4 D5:4', 'C#5:12 G#4:4', 'D5:8 F#5:4 E5:4', 'D5:12 A4:4',
        'C#5:4 E5:4 G#5:4 B5:4', 'A5:8 G#5:4 E5:4', 'A5:4 E5:4 C#5:4 A4:4',
        'G#4:4 C5:4 D#5:4 G#5:4')
    a = {'bass': chord_line(a_chords, ost, 2),
         'stabs': chord_line(a_chords, 'x:2 r:6 x:2 r:6', 4), 'drums': beat}
    sections = {
        'intro': {'bars': 2, 'bass': chord_line(['C#m', 'C#m'], ost, 2),
                  'drums': 'g...............' + 'k.k.k.k.s.s.ssss'},
        'A': dict(a, bars=8, lead=a_lead),
        'B': {
            'bars': 8,
            'pipa': bars('F#5:8 A5:8', 'C#6:8 B5:4 A5:4', 'D6:8 C#6:8', 'A5:16',
                         'E6:8 C#6:8', 'A5:8 E5:8', 'C6:8 D#6:8', 'G#6:8 D#6:8'),
            'bass': chord_line(b_chords, ost, 2),
            'stabs': chord_line(b_chords, 'x:8 x:8', 4),
            'drums': drums('k.hkk.hks.hkk.hs', 8, first='g.hkk.hks.hkk.hs',
                           last='s.s.s.s.ssssssss'),
        },
        'A2': dict(a, bars=8, lead=transpose(a_lead, 12), harm=a_lead),
    }
    return Tune(132, voices, sections, ['intro'], ['A', 'B', 'A2'])


# --- 16. Stories: Strange Dreams ---------------------------------------------


def strange_dreams():
    voices = {
        'bell': Voice(Inst('pulse', 0.125, a=0.002, d=0.6, s=0.2, r=0.3,
                           vib=0.15, vib_rate=4.0, vib_delay=0.2), 0.5,
                      echo=(3, 0.45)),
        'pad': Voice(Inst('pulse', 0.25, a=0.15, d=0.5, s=0.5, r=0.4), 0.16),
        'pluck': Voice(PLUCK, 0.25, echo=(2, 0.3)),
        'bass': Voice(SOFT_BASS, 0.7),
        'drums': Voice(None, 0.6),
    }
    a_chords = ['C', 'Caug', 'F', 'Fm', 'C', 'Caug', 'Ab', 'G']
    b_chords = ['Am', 'Em', 'F', 'C', 'Dm', 'Bb', 'Ab', 'G']
    pluck = 'R:2 3:2 5:2 8:2 10:2 8:2 5:2 3:2'
    sections = {
        'A': {
            'bars': 8,
            'bell': bars(
                'E5:4 G5:4 C6:4 B5:4', 'G#5:8 E5:8', 'A5:4 C6:4 F6:4 E6:4',
                'Ab5:12 r:4', 'G5:4 E5:4 D5:4 C5:4', 'E5:4 G#5:4 C6:8',
                'C6:4 Eb6:4 Ab5:8', 'B5:8 D6:4 G5:4'),
            'pad': chord_line(a_chords, 'x:16', 4),
            'pluck': chord_line(a_chords, pluck, 4),
            'bass': chord_line(a_chords, 'R:8 5:8', 2),
            'drums': 'g' + '.' * 127,
        },
        'B': {
            'bars': 8,
            'bell': bars('A5:8 C6:8', 'B5:8 G5:8', 'A5:4 F5:4 C6:8', 'G5:16',
                         'F5:4 A5:4 D6:8', 'D6:8 F6:4 Bb5:4', 'C6:8 Eb6:8',
                         'D6:8 B5:8'),
            'pad': chord_line(b_chords, 'x:16', 4),
            'pluck': chord_line(b_chords, pluck, 4),
            'bass': chord_line(b_chords, 'R:8 5:8', 2),
            'drums': drums('o' + '.' * 15, 8),
        },
    }
    return Tune(90, voices, sections, [], ['A', 'B'])


# --- 17. Seedy places: Dice in the Back Room (swung) -------------------------


def dice_in_the_back_room():
    voices = {
        'lead': Voice(Inst('pulse', 0.5, a=0.01, d=0.2, s=0.6, r=0.1, vib=0.3,
                           vib_rate=5.0, vib_delay=0.15, slide=0.1), 0.55,
                      echo=(3, 0.25)),
        'comp': Voice(Inst('pulse', 0.25, a=0.002, d=0.1, s=0.2, r=0.04), 0.3),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.75),
    }
    a_chords = ['Gm', 'Gm', 'Cm', 'Gm', 'D', 'Cm', 'Gm', 'D']
    b_chords = ['Cm', 'Cm', 'Gm', 'Gm', 'Eb', 'D', 'Gm', 'D']
    walk = 'R:4 3:4 5:4 6:4'
    comp = 'r:4 x:2 r:6 x:2 r:2'
    beat = 'k.h.s.h.k.hhs.h.'
    sections = {
        'intro': {'bars': 1, 'bass': 'D3:4 C3:4 Bb2:4 A2:4', 'drums': beat},
        'A': {
            'bars': 8,
            'lead': bars(
                'G4:2 Bb4:2 r:2 C5:2 Db5>D5:4 r:4', 'F5:2 D5:2 r:2 Bb4:2 G4:8',
                'C5:2 Eb5:2 r:2 G5:2 F5>G5:4 Eb5:4', 'D5:6 Bb4:2 G4:8',
                'A4:2 C5:2 r:2 D5:2 F#5:4 A5:4', 'G5:2 F5:2 Eb5:2 C5:2 Db5>D5:8',
                'Bb4:2 G4:2 r:12', 'r:8 D5:2 F#5:2 A5:2 C6:2'),
            'comp': chord_line(a_chords, comp, 4),
            'bass': chord_line(a_chords, walk, 2),
            'drums': drums(beat, 8, last='k.h.s.h.k.t.T.T.'),
        },
        'B': {
            'bars': 8,
            'lead': bars(
                'C6:4 Bb5:2 G5:2 Eb5:8', 'C5:2 Eb5:2 F5:2 Gb5>G5:6 r:4',
                'D5:2 F5:2 G5:2 Bb5:2 D6:4 C6:4', 'Bb5:8 G5:8',
                'G5:4 Bb5:2 G5:2 Eb5:4 Bb4:4', 'A4:4 C5:2 D5:2 F#5:8',
                'G5:2 F5:2 D5:2 C5:2 Bb4:2 G4:6', 'F#4:4 A4:4 C5:4 D5:4'),
            'comp': chord_line(b_chords, comp, 4),
            'bass': chord_line(b_chords, walk, 2),
            'drums': drums(beat, 8, last='k.h.s.h.k.t.T.T.'),
        },
    }
    return Tune(104, voices, sections, ['intro'], ['A', 'B'], swing=1 / 3)


# --- 18. Crime, thieves: Footsteps Behind You --------------------------------


def footsteps_behind_you():
    voices = {
        'lead': Voice(Inst('pulse', 0.25, a=0.005, d=0.3, s=0.5, r=0.15,
                           vib=0.2, vib_delay=0.3), 0.5, echo=(3, 0.35)),
        'trem': Voice(Inst('pulse', 0.125, a=0.3, d=0.0, s=0.6, r=0.3,
                           trem=60 / 100 / 8), 0.15),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 1.3),
    }

    def heart(n, fast=False):  # a heartbeat on the bass
        beat = f'{n}:2 r:1 {n}:1 r:4' if fast else f'{n}:2 r:1 {n}:1 r:12'
        return f'{beat} {beat}' if fast else beat

    def heartbeats(fast):
        notes = ['A1', 'A1', 'A1', 'Bb1', 'A1', 'A1', 'A1', 'E2']
        return bars(*(heart(n, fast) for n in notes))

    sections = {
        'A': {
            'bars': 8,
            'lead': bars(
                'r:8 A4:2 C5:2 Bb4:4', 'A4:12 r:4', 'r:8 E5:2 F5:2 E5:4',
                'Bb4:12 r:4', 'r:8 A4:2 C5:2 E5:4', 'F5:4 E5:4 Bb4:8',
                'r:4 A4:2 Bb4:2 C5:2 Bb4:2 A4:4', 'G#4:16'),
            'trem': 'E6:16 | F6:16 | E6:16 | Eb6:16 | E6:16 | F6:16 | G6:16 | '
                    'F6:8 E6:8',
            'bass': heartbeats(False),
            'drums': drums('w' + '.' * 23 + 'W' + '.' * 7, 4),
        },
        'B': {
            'bars': 8,
            'lead': bars(
                'A5:4 r:4 G5:2 E5:2 D5:4', 'Eb5:12 r:4',
                'A5:4 r:4 C6:2 Bb5:2 A5:4', 'E5:12 r:4',
                'D5:2 E5:2 F5:2 G5:2 A5:2 Bb5:2 C6:2 D6:2', 'Eb6:8 D6:8',
                'C6:4 Bb5:4 A5:4 G#5:4', 'A5:16'),
            'trem': 'C6:16 | Eb6:16 | C6:16 | Bb5:16 | D6:16 | Eb6:16 | '
                    'E6:16 | E6:16',
            'bass': heartbeats(True),
            'drums': drums('h...w...h...W...', 8),
        },
    }
    return Tune(100, voices, sections, [], ['A', 'B'])


# --- 19. Romance: Plum Blossom -----------------------------------------------


def plum_blossom():
    voices = {
        'lead': Voice(ERHU, 0.5, echo=(3, 0.3)),
        'flute': Voice(FLUTE, 0.22),
        'pluck': Voice(PLUCK, 0.3),
        'bass': Voice(SOFT_BASS, 0.7),
        'drums': Voice(None, 1.6),
    }
    a_chords = ['F', 'Dm', 'Bb', 'C', 'F', 'Am', 'Bb', 'C']
    b_chords = ['Bb', 'C', 'Am', 'Dm', 'Bb', 'C', 'F', 'F']
    pluck = 'R:2 5:2 8:2 10:2 8:2 5:2 8:2 5:2'
    beat = 'W.......w.......'
    sections = {
        'intro': {'bars': 1, 'pluck': chord_line(['F'], pluck, 4),
                  'bass': 'F2:16', 'drums': beat},
        'A': {
            'bars': 8,
            'lead': bars(
                'C5>D5:6 C5:2 A4:4 C5:4', 'D5:8 F5:4 G5:4',
                'A5:6 G5:2 F5:4 D5:4', 'C5:16', 'A5:6 C6:2 D6:4 C6:4',
                'A5:8 G5:4 E5:4', 'F5:4 G5:2 F5:2 D5:4 F5:4', 'G5:12 r:4'),
            'pluck': chord_line(a_chords, pluck, 4),
            'bass': chord_line(a_chords, 'R:8 5:8', 2),
            'drums': drums(beat, 8),
        },
        'B': {
            'bars': 8,
            'lead': bars(
                'D6:6 C6:2 A5:4 G5:4', 'G5:6 A5:2 C6:8',
                'C6:4 A5:2 G5:2 E5:8', 'D5:6 F5:2 A5:8',
                'Bb5:6 A5:2 F5:4 D5:4', 'C5:4 D5:4 F5:4 G5:4',
                'A5>C6:8 A5:4 G5:4', 'F5:16'),
            'flute': chord_line(b_chords, '3:8 5:8', 4),
            'pluck': chord_line(b_chords, pluck, 4),
            'bass': chord_line(b_chords, 'R:8 5:8', 2),
            'drums': drums(beat, 8),
        },
    }
    return Tune(76, voices, sections, ['intro'], ['A', 'B'])


# --- 20. Injured, resting: Healing Herbs -------------------------------------


def healing_herbs():
    voices = {
        'lead': Voice(FLUTE, 0.5, echo=(4, 0.3)),
        'pluck': Voice(PLUCK, 0.3),
        'bass': Voice(SOFT_BASS, 0.7),
    }
    a_chords = ['Dm', 'Bb', 'F', 'C', 'Dm', 'Gm', 'A', 'Dm']
    b_chords = ['Bb', 'C', 'Am', 'Dm', 'Gm', 'C', 'F', 'A']
    pluck = 'R:4 5:4 10:4 5:4'
    sections = {
        'A': {
            'bars': 8,
            'lead': bars(
                'A4:6 C5:2 D5:8', 'F5:6 D5:2 C5:4 A4:4', 'C5:6 A4:2 F4:8',
                'G4:12 r:4', 'A4:6 C5:2 D5:4 F5:4', 'G5:6 F5:2 D5:8',
                'E5:6 C#5:2 A4:8', 'D5:16'),
            'pluck': chord_line(a_chords, pluck, 4),
            'bass': chord_line(a_chords, 'R:16', 2),
        },
        'B': {
            'bars': 8,
            'lead': bars(
                'D5:6 F5:2 G5:4 A5:4', 'G5:6 E5:2 C5:8', 'C5:4 E5:4 A5:8',
                'F5:8 D5:8', 'D5:6 G5:2 Bb5:4 A5:4', 'G5:4 E5:4 C5:8',
                'A4:4 C5:4 F5:8', 'E5:12 r:4'),
            'pluck': chord_line(b_chords, pluck, 4),
            'bass': chord_line(b_chords, 'R:16', 2),
        },
    }
    return Tune(66, voices, sections, [], ['A', 'B'])


# --- 21. Own school: Master of the House -------------------------------------


def master_of_the_house():
    voices = {
        'lead': Voice(LEAD, 0.55, echo=(3, 0.3)),
        'harm': Voice(HARM, 0.25),
        'arps': Voice(ARPS, 0.3),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.85),
    }
    a_chords = ['A', 'A', 'D', 'E', 'A', 'F#m', 'D E', 'A']
    b_chords = ['F#m', 'C#m', 'D', 'A', 'F#m', 'C#m', 'D', 'E']
    bass = 'R:4 5:4 8:4 5:4'
    arps = 'x:2 r:2 x:1 x:1 r:2 x:2 r:2 x:2 r:2'
    a_lead = bars(
        'E5:6 F#5:2 A5:4 E5:4', 'C#5:4 E5:2 C#5:2 A4:8',
        'F#5:6 A5:2 B5:4 A5:4', 'E5:6 F#5:2 E5:4 B4:4',
        'E5:6 F#5:2 A5:4 C#6:4', 'B5:4 A5:2 F#5:2 E5:4 C#5:4',
        'B4:4 C#5:4 E5:4 B4:4', 'A4:12 r:4')
    a = {'bass': chord_line(a_chords, bass, 2),
         'arps': chord_line(a_chords, arps, 4),
         'drums': drums('k...s...k.k.s...', 8, first='c...s...k.k.s...',
                        last='k...s.s.ssssssss')}
    sections = {
        'intro': {'bars': 2, 'bass': 'A2:16 | E2:16',
                  'drums': 'k...k...k...k...' + 's.s.s.s.ssssssss'},
        'A': dict(a, bars=8, lead=a_lead),
        'B': {
            'bars': 8,
            'lead': bars(
                'C#6:6 B5:2 A5:4 F#5:4', 'E5:6 F#5:2 G#5:8',
                'A5:4 F#5:4 D5:4 F#5:4', 'E5:12 r:4',
                'C#6:6 E6:2 C#6:4 B5:4', 'G#5:6 F#5:2 E5:8',
                'F#5:4 A5:4 B5:4 A5:4', 'B5:8 G#5:4 E5:4'),
            'bass': chord_line(b_chords, bass, 2),
            'arps': chord_line(b_chords, arps, 4),
            'drums': drums('k...s.s.k.k.s.s.', 8, last='k...s...k...ssss'),
        },
        'A2': dict(a, bars=8, lead=a_lead, harm=transpose(a_lead, -5)),
    }
    return Tune(108, voices, sections, ['intro'], ['A', 'B', 'A2'])


# --- 22. Victory, end of game: A Legend Is Born ------------------------------


def a_legend_is_born():
    voices = {
        'lead': Voice(Inst('pulse', 0.25, a=0.01, d=0.15, s=0.75, r=0.12,
                           vib=0.25, vib_delay=0.2), 0.55, echo=(3, 0.35)),
        'harm': Voice(HARM, 0.3),
        'arps': Voice(ARPS, 0.3),
        'bass': Voice(BASS, 0.9),
        'drums': Voice(None, 0.85),
    }
    a_chords = ['G', 'Em', 'D', 'G', 'G', 'Em', 'C D', 'G']
    b_chords = ['C', 'D', 'Bm', 'Em', 'C', 'D', 'G', 'G']
    b_lead = bars(
        'E5:4 G5:4 C6:4 E6:4', 'D6:6 C6:2 A5:8', 'B5:4 D6:4 F#6:4 D6:4',
        'E6:6 D6:2 B5:8', 'C6:4 E6:4 G6:4 E6:4', 'F#6:4 E6:4 D6:4 A5:4',
        'G6:12 D6:4', 'G6:16')
    sections = {
        'intro': {'bars': 2, 'lead': 'G4:4 D5:4 G5:8 | B5:4 A5:4 D6:8',
                  'bass': 'G2:16 | D2:16',
                  'drums': 'g...............' + 'T.T.T.T.ttttssss'},
        'A': {  # the title theme, now in full glory
            'bars': 8, 'lead': TITLE_THEME,
            'harm': transpose(TITLE_THEME, -5),
            'bass': chord_line(a_chords, 'R:4 5:4 8:4 5:4', 2),
            'arps': chord_line(a_chords, 'x:8 x:8', 4),
            'drums': drums('k.......s.......', 8, first='c.......s.......',
                           last='k...s...T.T.TTss'),
        },
        'B': {
            'bars': 8, 'lead': b_lead, 'harm': transpose(b_lead, -5),
            'bass': chord_line(b_chords, 'R:2 R:2 8:2 R:2 R:2 5:2 8:2 5:2', 2),
            'arps': chord_line(b_chords, 'x:2 r:2 x:2 r:1 x:1 r:2 x:2 x:2 r:2',
                               4),
            'drums': drums('k.h.s.hkk.h.s.h.', 8, first='g.h.s.hkk.h.s.h.',
                           last='s.s.s.ssT.T.TTTT'),
        },
    }
    return Tune(112, voices, sections, ['intro'], ['A', 'B'])


# name -> (score, overall loudness in dBFS RMS): calm tunes sit lower.
TUNES = {
    '01_path_of_the_fist': (path_of_the_fist, -15.0),
    '02_choosing_a_style': (choosing_a_style, -16.0),
    '03_morning_market': (morning_market, -17.0),
    '04_teahouse_afternoon': (teahouse_afternoon, -17.0),
    '05_lanterns_at_dusk': (lanterns_at_dusk, -17.5),
    '06_bamboo_courtyard': (bamboo_courtyard, -15.5),
    '07_words_of_the_master': (words_of_the_master, -19.0),
    '08_fists_like_rain': (fists_like_rain, -14.5),
    '09_alley_cats': (alley_cats, -14.5),
    '10_thugs_at_the_bridge': (thugs_at_the_bridge, -14.5),
    '11_outnumbered': (outnumbered, -14.5),
    '12_every_fist_for_itself': (every_fist_for_itself, -14.5),
    '13_tournament_day': (tournament_day, -14.5),
    '14_the_final_platform': (final_platform, -14.0),
    '15_shadow_of_the_boss': (shadow_of_the_boss, -14.0),
    '16_strange_dreams': (strange_dreams, -18.0),
    '17_dice_in_the_back_room': (dice_in_the_back_room, -16.0),
    '18_footsteps_behind_you': (footsteps_behind_you, -18.0),
    '19_plum_blossom': (plum_blossom, -17.5),
    '20_healing_herbs': (healing_herbs, -18.5),
    '21_master_of_the_house': (master_of_the_house, -15.5),
    '22_a_legend_is_born': (a_legend_is_born, -14.5),
}
