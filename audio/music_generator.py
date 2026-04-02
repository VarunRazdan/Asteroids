"""Procedural chiptune music loop for the Asteroids game.

Generates a 4-bar loop at 140 BPM using square-wave melody and sawtooth bass.
"""

import numpy as np
import pygame

from audio.sound_generator import (
    SAMPLE_RATE,
    apply_envelope,
    sawtooth_wave,
    square_wave,
    to_stereo,
)


def generate_music_loop() -> pygame.mixer.Sound:
    """Return a ~6.86 s seamless chiptune loop as a ``pygame.mixer.Sound``.

    Structure
    ---------
    * 140 BPM  -> one beat = 60/140 ~= 0.4286 s
    * 4 bars of 4 beats = 16 beats total
    * Melody: E minor pentatonic (E4, G4, A4, B4, D5) ascending then descending
    * Bass: root movement on A2, E2, F2, G2 (one note per bar, whole notes)
    """
    bpm = 140
    beat_dur = 60.0 / bpm  # ~0.4286 s
    bar_dur = beat_dur * 4  # ~1.7143 s
    total_dur = bar_dur * 4  # ~6.8571 s
    total_samples = int(SAMPLE_RATE * total_dur)

    # -- Melody (square wave, E minor pentatonic) --
    # Notes as (midi-style freq, start_beat, duration_in_beats)
    # E minor pentatonic: E4=329.63 G4=392.00 A4=440.00 B4=493.88 D5=587.33
    melody_notes = [
        # Bar 1 — ascending
        (329.63, 0, 1),    # E4
        (392.00, 1, 1),    # G4
        (440.00, 2, 1),    # A4
        (493.88, 3, 1),    # B4
        # Bar 2 — peak and descend
        (587.33, 4, 1),    # D5
        (493.88, 5, 1),    # B4
        (440.00, 6, 1),    # A4
        (392.00, 7, 1),    # G4
        # Bar 3 — ascending variation
        (329.63, 8, 1),    # E4
        (440.00, 9, 0.5),  # A4 (eighth)
        (493.88, 9.5, 0.5),# B4 (eighth)
        (587.33, 10, 1.5), # D5 (dotted quarter)
        (493.88, 11.5, 0.5),# B4 (eighth)
        # Bar 4 — descending resolution
        (440.00, 12, 1),   # A4
        (392.00, 13, 1),   # G4
        (329.63, 14, 2),   # E4 (half note, resolves)
    ]

    melody = np.zeros(total_samples, dtype=np.float64)
    for freq, start_beat, dur_beats in melody_notes:
        note_dur = dur_beats * beat_dur
        start_sample = int(start_beat * beat_dur * SAMPLE_RATE)
        note = square_wave(freq, note_dur, amplitude=0.35)
        note = apply_envelope(note, attack=0.01, decay=0.04, sustain_level=0.6, release=0.03)
        end_sample = start_sample + len(note)
        if end_sample > total_samples:
            note = note[: total_samples - start_sample]
            end_sample = total_samples
        melody[start_sample:end_sample] += note.astype(np.float64)

    # -- Bass (sawtooth wave, one note per bar) --
    bass_notes = [
        (110.00, 0),   # A2 — bar 1
        (82.41, 1),    # E2 — bar 2
        (87.31, 2),    # F2 — bar 3
        (98.00, 3),    # G2 — bar 4
    ]

    bass = np.zeros(total_samples, dtype=np.float64)
    for freq, bar_idx in bass_notes:
        note_dur = bar_dur
        start_sample = int(bar_idx * bar_dur * SAMPLE_RATE)
        note = sawtooth_wave(freq, note_dur, amplitude=0.30)
        note = apply_envelope(note, attack=0.02, decay=0.1, sustain_level=0.5, release=0.05)
        end_sample = start_sample + len(note)
        if end_sample > total_samples:
            note = note[: total_samples - start_sample]
            end_sample = total_samples
        bass[start_sample:end_sample] += note.astype(np.float64)

    # -- Mix melody + bass --
    combined = melody + bass
    peak = np.max(np.abs(combined))
    if peak > 0:
        combined = combined / peak * 32767
    mono = combined.astype(np.int16)

    stereo = to_stereo(mono)
    return pygame.sndarray.make_sound(stereo)
