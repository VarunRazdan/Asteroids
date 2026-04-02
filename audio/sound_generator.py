"""Numpy waveform primitives used to build every sound effect procedurally."""

import numpy as np

SAMPLE_RATE = 44100
MAX_AMP = 32767


def sine_wave(freq: float, duration: float, amplitude: float = 1.0) -> np.ndarray:
    """Pure sine tone."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) * amplitude
    return (wave * MAX_AMP).astype(np.int16)


def square_wave(freq: float, duration: float, amplitude: float = 1.0) -> np.ndarray:
    """Classic chiptune square wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * freq * t)) * amplitude
    return (wave * MAX_AMP).astype(np.int16)


def sawtooth_wave(freq: float, duration: float, amplitude: float = 1.0) -> np.ndarray:
    """Sawtooth wave — buzzy, good for bass."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = (2 * (t * freq - np.floor(0.5 + t * freq))) * amplitude
    return (wave * MAX_AMP).astype(np.int16)


def noise(duration: float, amplitude: float = 1.0) -> np.ndarray:
    """White noise."""
    num_samples = int(SAMPLE_RATE * duration)
    wave = np.random.uniform(-1.0, 1.0, num_samples) * amplitude
    return (wave * MAX_AMP).astype(np.int16)


def pitch_sweep(
    start_freq: float,
    end_freq: float,
    duration: float,
    amplitude: float = 1.0,
) -> np.ndarray:
    """Sine wave whose frequency sweeps linearly from *start_freq* to *end_freq*."""
    num_samples = int(SAMPLE_RATE * duration)
    freqs = np.linspace(start_freq, end_freq, num_samples)
    # Integrate instantaneous frequency to get phase
    phase = 2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE
    wave = np.sin(phase) * amplitude
    return (wave * MAX_AMP).astype(np.int16)


def apply_envelope(
    wave: np.ndarray,
    attack: float,
    decay: float,
    sustain_level: float = 0.0,
    release: float = 0.0,
) -> np.ndarray:
    """Apply an ADSR amplitude envelope to *wave* (int16 in, int16 out).

    Times are in seconds.  The sustain phase fills whatever duration remains
    after attack + decay + release.
    """
    n = len(wave)
    envelope = np.zeros(n, dtype=np.float64)

    a_samples = min(int(attack * SAMPLE_RATE), n)
    d_samples = min(int(decay * SAMPLE_RATE), n - a_samples)
    r_samples = min(int(release * SAMPLE_RATE), n - a_samples - d_samples)
    s_samples = max(0, n - a_samples - d_samples - r_samples)

    idx = 0
    # Attack: 0 → 1
    if a_samples > 0:
        envelope[idx : idx + a_samples] = np.linspace(0, 1, a_samples)
        idx += a_samples
    # Decay: 1 → sustain_level
    if d_samples > 0:
        envelope[idx : idx + d_samples] = np.linspace(1, sustain_level, d_samples)
        idx += d_samples
    # Sustain
    if s_samples > 0:
        envelope[idx : idx + s_samples] = sustain_level
        idx += s_samples
    # Release: sustain_level → 0
    if r_samples > 0:
        envelope[idx : idx + r_samples] = np.linspace(sustain_level, 0, r_samples)
        idx += r_samples

    result = (wave.astype(np.float64) * envelope).astype(np.int16)
    return result


def mix_waves(*waves: np.ndarray) -> np.ndarray:
    """Mix multiple int16 waveforms, normalising to prevent clipping.

    Shorter arrays are zero-padded to the length of the longest.
    """
    if not waves:
        return np.array([], dtype=np.int16)

    max_len = max(len(w) for w in waves)
    mixed = np.zeros(max_len, dtype=np.float64)
    for w in waves:
        padded = np.zeros(max_len, dtype=np.float64)
        padded[: len(w)] = w.astype(np.float64)
        mixed += padded

    peak = np.max(np.abs(mixed))
    if peak > 0:
        mixed = mixed / peak * MAX_AMP
    return mixed.astype(np.int16)


def to_stereo(mono: np.ndarray) -> np.ndarray:
    """Duplicate a mono int16 array into a stereo (N, 2) int16 array."""
    return np.column_stack((mono, mono)).astype(np.int16)
