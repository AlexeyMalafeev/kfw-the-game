"""In-fight sound effects and short jingles (see playlist.md)."""
import numpy as np
from scipy.signal import butter, lfilter

from chipsynth import (DRUMS, SR, Inst, Voice, fade_edges, hz, midi, mix,
                       osc, render_song, tone, transpose)


def _swell(dur, peak=0.4):
    """Envelope rising to its peak at `peak` of the way, then falling."""
    def env(t):
        x = t / dur
        return np.where(x < peak, x / peak, (1 - x) / (1 - peak)) ** 1.5
    return env


def whiff():
    return tone('noise', 2500, 11000, dur=0.2, env=_swell(0.2, 0.55))


def dodge():
    """A light double "fwip-fwip": the body sways out of the way."""
    def fwip(g):
        return tone('noise', 5000, 15000, dur=0.08, env=_swell(0.08, 0.6)), g
    zip_ = tone('pulse', 700, 1500, dur=0.07, tau=0.04, duty=0.125)
    (a, ga), (b, gb) = fwip(1.0), fwip(0.6)
    return mix((a, 0, ga), (zip_, 0.01, 0.15), (b, 0.11, gb))


def hit():
    return mix(
        (tone('noise', 7000, 1200, dur=0.1, tau=0.03), 0, 0.8),
        (tone('tri', 190, 55, dur=0.14, tau=0.05), 0, 1.0),
    )


def hit_weapon():
    slash = tone('noise', 14000, 4000, dur=0.09, env=_swell(0.09, 0.3))
    return mix((slash, 0, 0.7), (hit(), 0.06, 0.8),
               (tone('metal', 9000, 7000, dur=0.12, tau=0.04), 0.06, 0.25))


def _cha(dur, bright=1.0):
    """One "CHA" of the old movie punch: a bright crack with a noisy tail.

    `bright` < 1 darkens it (lower noise rates), for the echoes.
    """
    return mix(
        (tone('noise', 11000 * bright, 2500 * bright, dur=dur, tau=dur / 3), 0,
         1.0),
        (tone('tri', 210 * bright, 55, dur=min(dur, 0.18), tau=0.06), 0, 0.9),
    )


def critical():
    """CHA-cha-cha: the hit and its echoes, each quieter and darker."""
    return mix((_cha(0.17), 0, 1.0), (_cha(0.14, 0.75), 0.16, 0.45),
               (_cha(0.12, 0.55), 0.31, 0.2))


def epic():
    """CHAAA-CHAAA-CHAAA-chaa-cha, over a heavy thump."""
    thump = tone('tri', 160, 35, dur=0.4, tau=0.15)
    parts = [(thump, 0, 1.0),
             (tone('pulse', 300, 50, dur=0.3, tau=0.1, duty=0.25), 0, 0.4)]
    for i, (dur, g, bright) in enumerate([(0.32, 1.0, 1.0), (0.32, 0.85, 0.92),
                                          (0.32, 0.7, 0.85), (0.22, 0.4, 0.7),
                                          (0.15, 0.22, 0.55)]):
        parts.append((_cha(dur, bright), i * 0.23, g))
    return mix(*parts)


def block():
    return mix(
        (tone('pulse', 620, 420, dur=0.06, tau=0.02, duty=0.25), 0, 0.6),
        (tone('noise', 5000, 2500, dur=0.05, tau=0.015), 0, 0.5),
        (tone('tri', 150, 70, dur=0.08, tau=0.03), 0, 0.6),
    )


def block_full():
    return mix(
        (block(), 0, 0.9),
        (tone('pulse', 1100, dur=0.35, tau=0.09, duty=0.125), 0.01, 0.3),
        (tone('pulse', 1480, dur=0.3, tau=0.07, duty=0.125), 0.01, 0.22),
    )


def qi_shield():
    parts = [(tone('noise', 3000, 9000, dur=0.4, env=_swell(0.4, 0.2)), 0,
              0.15)]
    notes = ['B5', 'E6', 'G#6', 'B6'] * 3
    for i, n in enumerate(notes):
        parts.append((tone('pulse', float(hz(midi(n))), dur=0.07, tau=0.05,
                           duty=0.125), i * 0.035, 0.4 * (1 - i / 14)))
    return mix(*parts)


def counter():
    swish = tone('noise', 4000, 12000, dur=0.08, env=_swell(0.08, 0.7))
    return mix((swish, 0, 0.6), (hit(), 0.07, 1.0))


def knockdown():
    return mix(
        (tone('noise', 2500, 300, dur=0.25, tau=0.07), 0, 0.7),
        (tone('tri', 130, 38, dur=0.35, tau=0.13), 0, 1.0),
        (tone('noise', 1200, 400, dur=0.12, tau=0.04), 0.13, 0.4),
    )


def stun(f_hi=1600, f_lo=1250, n=6):
    parts = []
    for i in range(n):
        f = f_hi if i % 2 == 0 else f_lo
        parts.append((tone('pulse', f, f * 1.25, dur=0.1, tau=0.06, duty=0.25,
                           vib=1.0, vib_rate=25), i * 0.11, 0.4))
    return mix(*parts)


def shock():
    """A stronger stun: a crackling zap, then lower, longer birdies."""
    zap = tone('pulse', 220, 160, dur=0.5, tau=0.25, duty=0.125, vib=4,
               vib_rate=35)
    crackle = tone('metal', 9000, 3000, dur=0.45, tau=0.15)
    return mix((_cha(0.12), 0, 0.7), (zap, 0.02, 0.5), (crackle, 0.02, 0.3),
               (stun(1150, 900, 8), 0.4, 1.0))


def knockback():
    """A short downward sweep: the fighter flies back."""
    sweep = tone('noise', 9000, 1200, dur=0.3, env=_swell(0.3, 0.2))
    return mix((sweep, 0, 0.8),
               (tone('tri', 320, 80, dur=0.3, tau=0.12), 0, 0.6))


def _formants(x, bands):
    """Pass `x` through parallel band-pass filters: (center Hz, gain)."""
    out = np.zeros_like(x)
    for fc, g in bands:
        b, a = butter(2, [fc * 0.8 / (SR / 2), fc * 1.25 / (SR / 2)],
                      btype='band')
        out += lfilter(b, a, x) * g
    return out


def fury():
    """Kung-fu yell, "wa-TAAAH!": a pulse voice through vowel formants."""
    def voice(dur, f0, f1, f_end, bands, vib=0.0):
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = f0 * (f1 / f0) ** np.minimum(t / 0.12, 1)
        tail = t > dur - 0.15
        f[tail] *= (f_end / f1) ** ((t[tail] - (dur - 0.15)) / 0.15)
        f *= 2 ** (vib / 12 * np.sin(2 * np.pi * 6.5 * t))
        env = np.minimum(1, t / 0.02) * np.clip((dur - t) / 0.12, 0, 1)
        return fade_edges(_formants(osc('pulse', f, 0.2), bands) * env)
    wa = voice(0.16, 330, 420, 400, [(350, 1.0), (800, 0.6)])
    taah = voice(0.75, 480, 600, 430, [(800, 1.0), (1200, 0.7), (2500, 0.3)],
                 vib=0.35)
    breath = tone('noise', 6000, 3000, dur=0.08, env=_swell(0.08, 0.5))
    t_click = tone('noise', 9000, dur=0.03, tau=0.008)
    return mix((breath, 0, 0.25), (wa, 0.04, 1.0), (t_click, 0.22, 0.4),
               (taah, 0.23, 1.0))


def ko():
    fall = tone('pulse', 880, 70, dur=0.75, duty=0.5, vib=0.6, vib_rate=16,
                env=lambda t: np.minimum(1, t / 0.005) * (1 - t / 0.75) ** 0.5)
    return mix((fall, 0, 0.45), (knockdown(), 0.68, 1.0),
               (DRUMS['g'][:int(1.8 * SR)], 0.7, 0.35))


def resist_ko():
    rise = tone('pulse', 220, 880, dur=0.28, tau=0.6, duty=0.25)
    hold = tone('pulse', 880, dur=0.3, tau=0.12, duty=0.25, vib=0.4,
                vib_rate=12)
    return mix((rise, 0, 0.45), (hold, 0.28, 0.45),
               (tone('pulse', 1320, dur=0.3, tau=0.12, duty=0.125), 0.28,
                0.2))


def guard():
    return mix(
        (tone('noise', 6000, 2500, dur=0.07, tau=0.02), 0, 0.35),
        (tone('pulse', float(hz(midi('A4'))), dur=0.06, tau=0.04, duty=0.25),
         0, 0.4),
        (tone('pulse', float(hz(midi('E5'))), dur=0.2, tau=0.07, duty=0.25),
         0.05, 0.4),
    )


def step():
    return tone('noise', 1800, 900, dur=0.05, tau=0.012)


def rush():
    dash = tone('noise', 1500, 7000, dur=0.18, env=_swell(0.18, 0.75))
    return mix((step(), 0, 0.8), (dash, 0.02, 0.6), (step(), 0.17, 0.9))


def retreat():
    dash = tone('noise', 7000, 1500, dur=0.18, env=_swell(0.18, 0.25))
    return mix((step(), 0, 0.8), (dash, 0, 0.6), (step(), 0.19, 0.6))


def focus():
    rise = tone('pulse', 300, 900, dur=0.7, duty=0.5, vib=0.3, vib_rate=9,
                env=_swell(0.7, 0.8))
    shimmer = tone('noise', 2000, 12000, dur=0.7, env=_swell(0.7, 0.85))
    return mix((rise, 0, 0.35), (shimmer, 0, 0.12),
               (tone('pulse', 1800, dur=0.25, tau=0.08, duty=0.125), 0.62, 0.2))


def catch_breath():
    inhale = tone('noise', 1500, 4500, dur=0.45, env=_swell(0.45, 0.8))
    exhale = tone('noise', 4000, 1000, dur=0.5, env=_swell(0.5, 0.15))
    return mix((inhale, 0, 0.4), (exhale, 0.5, 0.35))


def bleeding():
    def drip():
        return tone('pulse', 900, 2200, dur=0.05, tau=0.02, duty=0.5)
    return mix((drip(), 0, 0.5), (drip(), 0.16, 0.35))


def disarm():
    def clang(f, g):
        return mix((tone('pulse', f, f * 0.97, dur=0.3, tau=0.08, duty=0.125),
                    0, g), (tone('metal', 12000, dur=0.04, tau=0.015), 0, g))
    return mix((hit(), 0, 0.7), (clang(1500, 0.45), 0.05, 1),
               (clang(1150, 0.35), 0.28, 1), (clang(1300, 0.2), 0.4, 1),
               (clang(1200, 0.12), 0.48, 1))


def item_use():
    parts = []
    for i, (f0, f1) in enumerate([(380, 520), (450, 620), (560, 800)]):
        parts.append((tone('pulse', f0, f1, dur=0.07, tau=0.04, duty=0.5),
                      i * 0.09, 0.45))
    for i, n in enumerate(['C6', 'E6', 'G6', 'C7']):
        parts.append((tone('pulse', float(hz(midi(n))), dur=0.08, tau=0.05,
                           duty=0.125), 0.32 + i * 0.04, 0.25))
    return mix(*parts)


def fight_start():
    return mix((DRUMS['g'], 0, 0.8), (DRUMS['T'], 0, 1.0),
               (DRUMS['k'], 0.0, 1.0), (DRUMS['T'], 0.28, 0.9),
               (DRUMS['k'], 0.28, 0.9))


def gong_clash():
    """Tournament fight start: one big gong struck hard, no drums.

    A bright metallic crash over a deep, long-ringing gong body (lower and
    longer than the kit gong in fight_start), with a mallet thump.
    """
    dur = 3.5
    body = [(tone('pulse', 73 * r, 71 * r, dur=dur, tau=1.3, duty=0.5, a=0.004,
                  vib=0.1, vib_rate=2.5 + r), 0, g)
            for r, g in [(1, 0.55), (1.48, 0.4), (2.03, 0.3), (2.71, 0.25),
                         (3.16, 0.18), (4.13, 0.12), (5.4, 0.08)]]
    crash = tone('metal', 16000, 7000, dur=1.6, tau=0.35)
    hiss = tone('noise', 12000, 3000, dur=0.6, tau=0.15)
    return mix(*body, (crash, 0, 0.45), (hiss, 0, 0.4),
               (DRUMS['T'], 0, 1.0), (DRUMS['g'], 0.01, 0.5))


_LEAD = Inst('pulse', 0.25, a=0.005, d=0.1, s=0.7, r=0.1, vib=0.25,
             vib_delay=0.15)
_TRI = Inst('tri', a=0.002, d=0.0, s=1.0, r=0.05)


def victory():
    lead = 'D5:1 E5:1 G5:1 A5:1 B5:4 A5:2 B5:2 D6:4 | G6:12 r:4'
    voices = {'lead': Voice(_LEAD, 0.5, echo=(2, 0.3)),
              'harm': Voice(Inst('pulse', 0.5, a=0.005, d=0.1, s=0.6, r=0.1),
                            0.25),
              'bass': Voice(_TRI, 0.9), 'drums': Voice(None, 0.6)}
    sec = {'bars': 2, 'lead': lead, 'harm': transpose(lead, -5),
           'bass': 'G2:4 D3:4 G3:4 D3:4 | G2:12 r:4',
           'drums': 'k...k...k.k.s.s.' + 'c...............'}
    return render_song(150, voices, {'v': sec}, ['v'], tail_s=1.5)


def defeat():
    voices = {'lead': Voice(Inst('pulse', 0.5, a=0.01, d=0.2, s=0.6, r=0.3,
                                 vib=0.3, vib_rate=4.5, vib_delay=0.2,
                                 slide=0.15), 0.5),
              'bass': Voice(_TRI, 0.8), 'drums': Voice(None, 0.6)}
    sec = {'bars': 2, 'lead': 'B4:4 A4:4 G4:4 D4:4 | D#4>E4:16',
           'bass': 'E2:8 C2:8 | E2:16',
           'drums': 'T.......T.......' + 'g...............'}
    return render_song(96, voices, {'v': sec}, ['v'], tail_s=2.0)


def level_up():
    voices = {'lead': Voice(Inst('pulse', 0.125, a=0.002, d=0.1, s=0.6,
                                 r=0.1, vib=0.3, vib_delay=0.1), 0.5,
                            echo=(1, 0.35)),
              'bass': Voice(_TRI, 0.7)}
    sec = {'bars': 1, 'lead': 'C5:1 D5:1 E5:1 G5:1 A5:1 C6:1 D6:1 E6:1 G6:8',
           'bass': 'C3:8 G3:8'}
    return render_song(170, voices, {'v': sec}, ['v'], tail_s=0.8)


# Loudness of each effect's loudest 50 ms, dBFS: hits are the reference,
# footwork and breathing sit well under them.
SFX = {
    fight_start: -12, gong_clash: -11, whiff: -20, dodge: -19, hit: -12, hit_weapon: -12,
    critical: -10, epic: -9, block: -14, block_full: -13, qi_shield: -16,
    counter: -12, knockback: -14, knockdown: -12, stun: -18, shock: -14,
    ko: -10, resist_ko: -14, fury: -11, guard: -17, step: -24, rush: -19,
    retreat: -19, focus: -18, catch_breath: -21, bleeding: -18, disarm: -14,
    item_use: -17, victory: -12, defeat: -13, level_up: -14,
}
