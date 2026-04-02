"""Procedurally generated sound effects for the Asteroids game.

Every function returns a ``pygame.mixer.Sound`` ready to play.
"""

import numpy as np
import pygame

from audio.sound_generator import (
    apply_envelope,
    mix_waves,
    noise,
    pitch_sweep,
    sawtooth_wave,
    sine_wave,
    square_wave,
    to_stereo,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_sound(wave: np.ndarray) -> pygame.mixer.Sound:
    """Convert a mono int16 numpy array to a ``pygame.mixer.Sound``.

    Handles the mono -> stereo conversion so callers only need to think in
    mono waveforms.
    """
    stereo = to_stereo(wave)
    # pygame.sndarray.make_sound expects a (num_samples, num_channels) int16 array
    # that matches the mixer format (frequency=44100, size=-16, channels=2).
    return pygame.sndarray.make_sound(stereo)


# ---------------------------------------------------------------------------
# 1. Laser — single shot
# ---------------------------------------------------------------------------

def laser_single() -> pygame.mixer.Sound:
    """Sharp zap — square wave + pitch sweep 880->220 Hz, 0.15 s."""
    dur = 0.15
    sweep = pitch_sweep(880, 220, dur, amplitude=0.8)
    sq = square_wave(660, dur, amplitude=0.4)
    # trim sq to match sweep length
    sq = sq[: len(sweep)]
    wave = mix_waves(sweep, sq)
    wave = apply_envelope(wave, attack=0.005, decay=0.05, sustain_level=0.3, release=0.04)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 2. Laser — spread shot
# ---------------------------------------------------------------------------

def laser_spread() -> pygame.mixer.Sound:
    """Chord zap — 3 sine sweeps at slightly different pitches, 0.12 s."""
    dur = 0.12
    s1 = pitch_sweep(660, 165, dur, amplitude=0.6)
    s2 = pitch_sweep(830, 207, dur, amplitude=0.5)
    s3 = pitch_sweep(990, 247, dur, amplitude=0.5)
    wave = mix_waves(s1, s2, s3)
    wave = apply_envelope(wave, attack=0.005, decay=0.04, sustain_level=0.2, release=0.03)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 3. Laser — rapid fire
# ---------------------------------------------------------------------------

def laser_rapid() -> pygame.mixer.Sound:
    """Staccato pew — square + sweep 1200->600 Hz, 0.06 s."""
    dur = 0.06
    sweep = pitch_sweep(1200, 600, dur, amplitude=0.7)
    sq = square_wave(900, dur, amplitude=0.4)
    sq = sq[: len(sweep)]
    wave = mix_waves(sweep, sq)
    wave = apply_envelope(wave, attack=0.002, decay=0.02, sustain_level=0.2, release=0.01)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 4. Explosion — small
# ---------------------------------------------------------------------------

def explosion_small() -> pygame.mixer.Sound:
    """Noise + sine at 150 Hz, 0.2 s."""
    dur = 0.2
    n = noise(dur, amplitude=0.7)
    s = sine_wave(150, dur, amplitude=0.5)
    s = s[: len(n)]
    wave = mix_waves(n, s)
    wave = apply_envelope(wave, attack=0.005, decay=0.06, sustain_level=0.2, release=0.08)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 5. Explosion — medium
# ---------------------------------------------------------------------------

def explosion_medium() -> pygame.mixer.Sound:
    """Noise + two low sines, 0.4 s."""
    dur = 0.4
    n = noise(dur, amplitude=0.8)
    s1 = sine_wave(40, dur, amplitude=0.6)
    s2 = sine_wave(80, dur, amplitude=0.5)
    wave = mix_waves(n, s1, s2)
    wave = apply_envelope(wave, attack=0.01, decay=0.12, sustain_level=0.25, release=0.15)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 6. Explosion — large
# ---------------------------------------------------------------------------

def explosion_large() -> pygame.mixer.Sound:
    """Noise + sweep + sub bass, 0.7 s."""
    dur = 0.7
    n = noise(dur, amplitude=0.9)
    sweep = pitch_sweep(100, 25, dur, amplitude=0.6)
    sub = sine_wave(30, dur, amplitude=0.5)
    wave = mix_waves(n, sweep, sub)
    wave = apply_envelope(wave, attack=0.01, decay=0.2, sustain_level=0.3, release=0.25)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 7. Power-up collect
# ---------------------------------------------------------------------------

def powerup_collect() -> pygame.mixer.Sound:
    """Square-wave arpeggio C5-E5-G5, 0.3 s."""
    note_dur = 0.1
    c5 = square_wave(523.25, note_dur, amplitude=0.5)
    e5 = square_wave(659.25, note_dur, amplitude=0.5)
    g5 = square_wave(783.99, note_dur, amplitude=0.5)
    c5 = apply_envelope(c5, attack=0.005, decay=0.03, sustain_level=0.4, release=0.02)
    e5 = apply_envelope(e5, attack=0.005, decay=0.03, sustain_level=0.4, release=0.02)
    g5 = apply_envelope(g5, attack=0.005, decay=0.03, sustain_level=0.4, release=0.02)
    wave = np.concatenate([c5, e5, g5])
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 8. Shield activate
# ---------------------------------------------------------------------------

def shield_activate() -> pygame.mixer.Sound:
    """Sine sweep 300->1200 Hz, 0.4 s."""
    dur = 0.4
    wave = pitch_sweep(300, 1200, dur, amplitude=0.6)
    wave = apply_envelope(wave, attack=0.02, decay=0.1, sustain_level=0.5, release=0.1)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 9. Shield hit
# ---------------------------------------------------------------------------

def shield_hit() -> pygame.mixer.Sound:
    """Square + noise at 500 Hz, 0.15 s."""
    dur = 0.15
    sq = square_wave(500, dur, amplitude=0.6)
    n = noise(dur, amplitude=0.4)
    wave = mix_waves(sq, n)
    wave = apply_envelope(wave, attack=0.003, decay=0.04, sustain_level=0.2, release=0.04)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 10. Bomb detonate
# ---------------------------------------------------------------------------

def bomb_detonate() -> pygame.mixer.Sound:
    """Noise + sweep + sub bass 200->20 Hz, 1.0 s."""
    dur = 1.0
    n = noise(dur, amplitude=0.9)
    sweep = pitch_sweep(200, 20, dur, amplitude=0.7)
    sub = sine_wave(25, dur, amplitude=0.6)
    wave = mix_waves(n, sweep, sub)
    wave = apply_envelope(wave, attack=0.02, decay=0.3, sustain_level=0.35, release=0.3)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 11. Player death
# ---------------------------------------------------------------------------

def player_death() -> pygame.mixer.Sound:
    """Square sweep + noise, 800->100 Hz, 0.8 s."""
    dur = 0.8
    sweep = pitch_sweep(800, 100, dur, amplitude=0.7)
    # use square wave character by clipping the sweep
    sq_sweep = np.sign(sweep.astype(np.float64)).astype(np.int16) * (abs(sweep) // 2).astype(
        np.int16
    )
    n = noise(dur, amplitude=0.5)
    wave = mix_waves(sq_sweep, n)
    wave = apply_envelope(wave, attack=0.01, decay=0.2, sustain_level=0.3, release=0.25)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 12. Thrust loop
# ---------------------------------------------------------------------------

def thrust_loop() -> pygame.mixer.Sound:
    """Sawtooth + noise at 60 Hz, 0.5 s — designed to be looped."""
    dur = 0.5
    saw = sawtooth_wave(60, dur, amplitude=0.4)
    n = noise(dur, amplitude=0.3)
    wave = mix_waves(saw, n)
    # gentle envelope so it loops seamlessly
    wave = apply_envelope(wave, attack=0.02, decay=0.05, sustain_level=0.7, release=0.02)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 13. Life lost
# ---------------------------------------------------------------------------

def life_lost() -> pygame.mixer.Sound:
    """Two descending square notes E4->C4, 0.4 s total."""
    half = 0.2
    e4 = square_wave(329.63, half, amplitude=0.5)
    c4 = square_wave(261.63, half, amplitude=0.5)
    e4 = apply_envelope(e4, attack=0.005, decay=0.05, sustain_level=0.4, release=0.04)
    c4 = apply_envelope(c4, attack=0.005, decay=0.05, sustain_level=0.4, release=0.04)
    wave = np.concatenate([e4, c4])
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 14. Menu blip
# ---------------------------------------------------------------------------

def menu_blip() -> pygame.mixer.Sound:
    """Short square C6, 0.05 s."""
    dur = 0.05
    wave = square_wave(1046.50, dur, amplitude=0.4)
    wave = apply_envelope(wave, attack=0.002, decay=0.015, sustain_level=0.3, release=0.01)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 15. Game-over jingle
# ---------------------------------------------------------------------------

def game_over_jingle() -> pygame.mixer.Sound:
    """Descending square arpeggio E4-C4-A3-F3, 1.2 s."""
    note_dur = 0.3
    e4 = square_wave(329.63, note_dur, amplitude=0.5)
    c4 = square_wave(261.63, note_dur, amplitude=0.5)
    a3 = square_wave(220.00, note_dur, amplitude=0.5)
    f3 = square_wave(174.61, note_dur, amplitude=0.5)
    for arr in (e4, c4, a3, f3):
        arr[:] = apply_envelope(arr, attack=0.01, decay=0.08, sustain_level=0.4, release=0.08)
    wave = np.concatenate([e4, c4, a3, f3])
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 16. Alien shoot
# ---------------------------------------------------------------------------

def alien_shoot() -> pygame.mixer.Sound:
    """High-pitched descending buzz — square wave 1500->800 Hz, 0.1 s."""
    dur = 0.1
    sweep = pitch_sweep(1500, 800, dur, amplitude=0.7)
    sq = square_wave(1150, dur, amplitude=0.5)
    sq = sq[: len(sweep)]
    wave = mix_waves(sweep, sq)
    wave = apply_envelope(wave, attack=0.002, decay=0.03, sustain_level=0.3, release=0.02)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 17. Alien destroyed
# ---------------------------------------------------------------------------

def alien_destroyed() -> pygame.mixer.Sound:
    """Crunchy electronic explosion — noise + square sweep 600->200 Hz, 0.4 s."""
    dur = 0.4
    n = noise(dur, amplitude=0.8)
    sweep = pitch_sweep(600, 200, dur, amplitude=0.7)
    # clip the sweep to give it square-wave crunch
    sq_sweep = np.sign(sweep.astype(np.float64)).astype(np.int16) * (abs(sweep) // 2).astype(
        np.int16
    )
    wave = mix_waves(n, sq_sweep)
    wave = apply_envelope(wave, attack=0.005, decay=0.1, sustain_level=0.2, release=0.15)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 18. Black-hole ambient
# ---------------------------------------------------------------------------

def blackhole_ambient() -> pygame.mixer.Sound:
    """Low ominous drone — sine 40 Hz + sub-bass sine 20 Hz, 1.0 s, loopable."""
    dur = 1.0
    s1 = sine_wave(40, dur, amplitude=0.6)
    s2 = sine_wave(20, dur, amplitude=0.5)
    wave = mix_waves(s1, s2)
    # sustain envelope for seamless looping
    wave = apply_envelope(wave, attack=0.05, decay=0.05, sustain_level=0.8, release=0.05)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 19. Black-hole suck
# ---------------------------------------------------------------------------

def blackhole_suck() -> pygame.mixer.Sound:
    """Descending spiral whoosh — pitch sweep 400->60 Hz + noise, 1.5 s."""
    dur = 1.5
    sweep = pitch_sweep(400, 60, dur, amplitude=0.7)
    n = noise(dur, amplitude=0.5)
    wave = mix_waves(sweep, n)
    wave = apply_envelope(wave, attack=0.02, decay=0.3, sustain_level=0.3, release=0.4)
    return make_sound(wave)


# ---------------------------------------------------------------------------
# 20. Black-hole kill
# ---------------------------------------------------------------------------

def blackhole_kill() -> pygame.mixer.Sound:
    """Deep implosion pop — short noise burst then sharp cutoff, 0.3 s."""
    dur = 0.3
    n = noise(dur, amplitude=0.9)
    sub = sine_wave(35, dur, amplitude=0.7)
    wave = mix_waves(n, sub)
    wave = apply_envelope(wave, attack=0.05, decay=0.08, sustain_level=0.1, release=0.05)
    return make_sound(wave)
