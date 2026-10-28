"""Tiny NES-flavoured chiptune synth for KFW's music and sound effects.

Voices: pulse (12.5/25/50% duty), a 4-bit stepped triangle, and sample-and-hold
noise (long or short "metallic" period), plus a drum kit of one-shots.
Scores are written in a tracker-ish text notation on a 16th-note grid (see
`parse_line`). numpy + scipy only; writes 16-bit mono WAV.
"""
from dataclasses import dataclass
import re
from typing import Dict, List, Optional, Tuple
import wave

import numpy as np
from scipy.signal import lfilter

SR = 44100
FRAME = 1 / 60  # NES frame: the arpeggio rate
STEPS_PER_BAR = 16

_rng = np.random.default_rng(2013)
NOISE_LONG = _rng.choice([-1.0, 1.0], 32767)
NOISE_SHORT = _rng.choice([-1.0, 1.0], 93)  # short period: metallic, tonal

_NOTE_RE = re.compile(r'([A-G])([#b]?)(-?\d)')
_SEMI = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi(name):
    m = _NOTE_RE.fullmatch(name)
    if not m:
        raise ValueError(f'bad note {name!r}')
    n, acc, octv = m.groups()
    return 12 * (int(octv) + 1) + _SEMI[n] + {'#': 1, 'b': -1, '': 0}[acc]


def note_name(m):
    return f'{_NAMES[m % 12]}{m // 12 - 1}'


def hz(m):
    return 440.0 * 2 ** ((np.asarray(m, dtype=float) - 69) / 12)


# --- oscillators and envelopes ---------------------------------------------


def _polyblep(t, dt):
    out = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    out[m] = x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    out[m] = x * x + x + x + 1
    return out


def osc(kind, freq, duty=0.5):
    """Per-sample frequency array (Hz) -> waveform in [-1, 1]."""
    dt = np.minimum(np.asarray(freq, dtype=float) / SR, 0.5)
    phase = np.cumsum(dt)
    t = phase % 1.0
    if kind == 'pulse':
        y = np.where(t < duty, 1.0, -1.0)
        y += _polyblep(t, dt)
        y -= _polyblep((t + 1 - duty) % 1.0, dt)
        return y
    if kind == 'tri':
        y = 2 * np.abs(2 * t - 1) - 1
        return np.round((y + 1) * 7.5) / 7.5 - 1  # 16 steps, like the NES
    if kind in ('noise', 'metal'):
        table = NOISE_LONG if kind == 'noise' else NOISE_SHORT
        return table[np.floor(phase).astype(int) % len(table)]
    raise ValueError(kind)


def quantize(env):
    """NES volume has 16 levels."""
    return np.round(np.clip(env, 0, 1) * 15) / 15


def adsr(n, gate_s, a, d, s, r):
    t = np.arange(n) / SR
    env = np.where(
        t < a,
        t / max(a, 1e-9),
        np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-9), s),
    )
    if d > 0 and s == 0:
        env = np.where(t >= a + d, 0.0, env)
    g = int(gate_s * SR)
    if g < n:
        level = env[g] if g < n else 0
        rel = np.clip(1 - (t[g:] - gate_s) / max(r, 1e-9), 0, 1)
        env[g:] = np.minimum(env[g:], level * rel)
    return env


def fade_edges(y, ms_in=1.0, ms_out=4.0):
    n_in = min(len(y), int(SR * ms_in / 1000))
    n_out = min(len(y), int(SR * ms_out / 1000))
    if n_in:
        y[:n_in] *= np.linspace(0, 1, n_in)
    if n_out:
        y[-n_out:] *= np.linspace(1, 0, n_out)
    return y


def tone(kind, f0, f1=None, dur=0.2, tau=None, duty=0.5, a=0.002, vib=0.0,
         vib_rate=6.0, env=None, quant=True):
    """One-shot with an exponential pitch glide f0 -> f1 over `dur`.

    `tau` is the exponential decay time; `env` (array or callable of t)
    replaces the default envelope. For noise, f0/f1 are the sample-and-hold
    rates. `vib` is vibrato depth in semitones.
    """
    n = int(dur * SR)
    t = np.arange(n) / SR
    f1 = f0 if f1 is None else f1
    f = f0 * (f1 / f0) ** (t / dur)
    if vib:
        f = f * 2 ** (vib / 12 * np.sin(2 * np.pi * vib_rate * t))
    y = osc(kind, f, duty)
    if env is None:
        e = np.minimum(1, t / a) * (np.exp(-t / tau) if tau else 1)
    else:
        e = env(t) if callable(env) else env
    if quant:
        e = quantize(e)
    return fade_edges(y * e)


def mix(*parts):
    """mix((signal, start_s, gain), ...) -> one array."""
    n = max(int(at * SR) + len(x) for x, at, _ in parts)
    out = np.zeros(n)
    for x, at, g in parts:
        i = int(at * SR)
        out[i:i + len(x)] += x * g
    return out


# --- drum kit ---------------------------------------------------------------


def _kick():
    body = tone('tri', 160, 42, dur=0.22, tau=0.09)
    click = tone('noise', 9000, 3000, dur=0.012, tau=0.004)
    return mix((body, 0, 1.0), (click, 0, 0.5))


def _snare():
    rattle = tone('noise', 9000, 6000, dur=0.18, tau=0.05)
    body = tone('tri', 240, 160, dur=0.06, tau=0.03)
    return mix((rattle, 0, 0.7), (body, 0, 0.6))


def _gong():
    t_dur = 3.0
    parts = [(tone('noise', 7000, 2000, dur=0.4, tau=0.12), 0, 0.5)]
    for ratio, g in [(1, 0.5), (1.48, 0.35), (2.03, 0.25), (2.71, 0.2),
                     (3.16, 0.15), (4.13, 0.1)]:
        parts.append((tone('pulse', 98 * ratio, 96 * ratio, dur=t_dur,
                           tau=0.9, duty=0.5, a=0.01, vib=0.08,
                           vib_rate=3.0 + ratio), 0, g))
    return mix(*parts)


DRUMS = {
    'k': _kick(),
    's': _snare(),
    'h': tone('noise', 18000, dur=0.04, tau=0.012),
    'o': tone('noise', 18000, dur=0.25, tau=0.08),
    'c': tone('metal', 16000, 12000, dur=1.0, tau=0.3),  # crash
    't': tone('tri', 330, 160, dur=0.16, tau=0.07),  # high tom
    'T': tone('tri', 200, 90, dur=0.2, tau=0.09),  # low tom
    'w': mix((tone('pulse', 1250, 1150, dur=0.05, tau=0.015, duty=0.5), 0,
              0.7), (tone('noise', 12000, dur=0.006, tau=0.002), 0, 0.3)),
    'W': mix((tone('pulse', 820, 760, dur=0.06, tau=0.02, duty=0.5), 0,
              0.7), (tone('noise', 12000, dur=0.006, tau=0.002), 0, 0.3)),
    'g': _gong(),
}
DRUM_GAIN = {'k': 1.0, 's': 0.8, 'h': 0.3, 'o': 0.3, 'c': 0.35, 't': 0.8,
             'T': 0.9, 'w': 0.6, 'W': 0.6, 'g': 0.7}


# --- score notation ---------------------------------------------------------


@dataclass
class Inst:
    wave: str = 'pulse'
    duty: float = 0.5
    a: float = 0.005
    d: float = 0.1
    s: float = 0.7
    r: float = 0.05
    vib: float = 0.0  # vibrato depth, semitones
    vib_rate: float = 5.5
    vib_delay: float = 0.15
    trem: float = 0.0  # retrigger period in s (pipa-style tremolo), 0 = off
    slide: float = 0.07  # glide time for 'A>B' notes, s


@dataclass
class Voice:
    inst: Optional[Inst]  # None = drum kit
    gain: float = 1.0
    echo: Optional[Tuple[int, float]] = None  # (delay in steps, gain)


Event = Tuple[int, int, Tuple[int, ...], Optional[int]]

_TOKEN_RE = re.compile(r'^([^:]+)(?::(\d+))?$')


def parse_line(text, default_len=4, bar_steps=STEPS_PER_BAR):
    """Parse a melodic line into events (start_step, steps, pitches, slide_to).

    Tokens, whitespace-separated, each optionally followed by ':steps'
    (16ths): `E5` a note, `r` a rest, `[E4G4B4]` a chord played as a fast
    arpeggio, `D5>E5` a note that slides into another. `|` marks a bar line
    and is checked to fall on a bar boundary.
    """
    events: List[Event] = []
    pos = 0
    for tok in text.split():
        if tok == '|':
            if pos % bar_steps:
                raise ValueError(f'bar line at step {pos} in: {text[:60]}...')
            continue
        m = _TOKEN_RE.match(tok)
        if not m:
            raise ValueError(f'bad token {tok!r}')
        body, ln = m.group(1), int(m.group(2) or default_len)
        if body == 'r':
            pass
        elif body.startswith('['):
            notes = tuple(midi(''.join(g)) for g in _NOTE_RE.findall(body))
            events.append((pos, ln, notes, None))
        elif '>' in body:
            a, b = body.split('>')
            events.append((pos, ln, (midi(a),), midi(b)))
        else:
            events.append((pos, ln, (midi(body),), None))
        pos += ln
    return events, pos


def drum_steps(text):
    return [c for c in text if c not in ' |\n']


def transpose(text, semis):
    return _NOTE_RE.sub(lambda m: note_name(midi(m.group(0)) + semis), text)


def render_voice(events, inst, at, n_total):
    """`at(step)` maps a grid step to seconds (it carries tempo and swing)."""
    out = np.zeros(n_total + SR * 4)
    note_starts = [e[0] for e in events]
    for i, (st, ln, pitches, slide_to) in enumerate(events):
        start = int(round(at(st) * SR))
        gate = at(st + ln) - at(st)
        n = int((gate + inst.r) * SR)
        if i + 1 < len(events):
            n = min(n, int(round(at(note_starts[i + 1]) * SR)) - start)
        t = np.arange(n) / SR
        if len(pitches) > 1:
            idx = (t // FRAME).astype(int) % len(pitches)
            p = np.array(pitches, dtype=float)[idx]
        else:
            p = np.full(n, float(pitches[0]))
        if slide_to is not None:
            p += (slide_to - p) * np.clip(t / inst.slide, 0, 1)
        if inst.vib:
            ramp = np.clip((t - inst.vib_delay) / 0.15, 0, 1)
            p += inst.vib * ramp * np.sin(2 * np.pi * inst.vib_rate * t)
        y = osc(inst.wave, hz(p), inst.duty)
        env = adsr(n, gate, inst.a, inst.d, inst.s, inst.r)
        if inst.trem:
            tt = t % inst.trem
            env = env * (0.45 + 0.55 * np.exp(-tt / (inst.trem * 0.45)))
        out[start:start + n] += fade_edges(y * quantize(env), 0.5, 3)
    return out


def render_drums(steps, at, n_total):
    out = np.zeros(n_total + SR * 4)
    for i, c in enumerate(steps):
        if c == '.':
            continue
        x = DRUMS[c] * DRUM_GAIN[c]
        start = int(round(at(i) * SR))
        out[start:start + len(x)] += x
    return out


def render_song(bpm, voices: Dict[str, Voice], sections, order,
                fade_s=0.0, tail_s=1.5, bar_steps=STEPS_PER_BAR, swing=0.0):
    """Render sections (name -> {'bars': n, voice: text}) in `order`.

    A voice missing from a section rests for it. Every voice's line must
    fill the section exactly (checked). `bar_steps` is 12 for 3/4 time;
    `swing` delays every off-beat 8th by that share of an 8th
    (1/3 = triplet swing).
    """
    step_s = 60 / bpm / 4

    def at(step):
        return step * step_s + (swing * 2 * step_s if step % 4 == 2 else 0)

    lines = {v: [] for v in voices}
    pos = 0
    for name in order:
        sec = sections[name]
        sec_steps = sec['bars'] * bar_steps
        for v, voice in voices.items():
            text = sec.get(v)
            if text is None:
                continue
            if voice.inst is None:
                steps = drum_steps(text)
                n = len(steps)
                lines[v].extend((pos + i, c) for i, c in enumerate(steps))
            else:
                evs, n = parse_line(text, bar_steps=bar_steps)
                lines[v].extend((pos + s, ln, p, sl) for s, ln, p, sl in evs)
            if n != sec_steps:
                raise ValueError(f'section {name}, voice {v}: {n} steps, '
                                 f'expected {sec_steps}')
        pos += sec_steps
    n_total = int(pos * step_s * SR)
    out = np.zeros(n_total + SR * 4)
    for v, voice in voices.items():
        if voice.inst is None:
            steps = ['.'] * pos
            for i, c in lines[v]:
                steps[i] = c
            y = render_drums(steps, at, n_total)
        else:
            y = render_voice(lines[v], voice.inst, at, n_total)
        if voice.echo:
            d = int(voice.echo[0] * step_s * SR)
            y[d:] += y[:-d].copy() * voice.echo[1]
        out += y * voice.gain
    out = out[:n_total + int(tail_s * SR)]
    if fade_s:
        nf = int(fade_s * SR)
        end = n_total
        out[end - nf:end] *= np.linspace(1, 0, nf) ** 1.5
        out[end:] = 0
        out = out[:end]
    return out


# --- output -----------------------------------------------------------------


def master(x):
    # DC blocker (~20 Hz) and a gentle one-pole low-pass (~13 kHz), like the
    # console's output stage softening the square edges.
    x = lfilter([1, -1], [1, -0.997], x)
    k = np.exp(-2 * np.pi * 13000 / SR)
    return lfilter([1 - k], [1, -k], x)


def loudness_db(x, window_s=None):
    """RMS in dBFS: of the whole signal, or of its loudest window."""
    if window_s is None or len(x) <= int(window_s * SR):
        p = np.mean(x ** 2)
    else:
        w = int(window_s * SR)
        p = np.max(np.convolve(x ** 2, np.ones(w) / w, 'valid'))
    return 10 * np.log10(p)


def finish(x, loudness=-16.0, window_s=None, max_peak=0.97, ref=None):
    """Master, set loudness (see `loudness_db`) and cap the peak.

    `ref` (a slice of the mastered signal) is what the loudness is measured
    on; by default the whole signal. Returns (signal, final peak), so callers
    can spot capped files.
    """
    x = master(np.asarray(x, dtype=float))
    m = x if ref is None else x[ref]
    x = x * 10 ** ((loudness - loudness_db(m, window_s)) / 20)
    peak = np.max(np.abs(x if ref is None else x[ref]))
    if peak > max_peak:
        x *= max_peak / peak
    return x, min(peak, max_peak)


def write_wav(path, x, loudness=-16.0, window_s=None, max_peak=0.97):
    """`finish`, then write a 16-bit mono WAV. Returns the final peak."""
    x, peak = finish(x, loudness, window_s, max_peak)
    write_pcm(path, x)
    return peak


def write_pcm(path, x):
    data = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
