"""Unit tests for the audio subsystem (sound_generator + audio_manager)."""

import numpy as np
import pytest

from audio.audio_manager import AudioManager
from audio.sound_generator import (
    SAMPLE_RATE,
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
# Sound generator — waveform primitives
# ---------------------------------------------------------------------------

class TestSoundGenerator:
    @pytest.mark.parametrize("generator,freq,dur", [
        (sine_wave, 440, 0.1),
        (square_wave, 440, 0.1),
        (sawtooth_wave, 440, 0.1),
    ])
    def test_sound_generator_produces_arrays(self, generator, freq, dur):
        """Each waveform function should return a non-empty int16 numpy array."""
        wave = generator(freq, dur)
        assert isinstance(wave, np.ndarray)
        assert wave.dtype == np.int16
        assert len(wave) > 0
        expected_len = int(SAMPLE_RATE * dur)
        assert len(wave) == expected_len

    def test_noise_produces_array(self):
        wave = noise(0.1)
        assert isinstance(wave, np.ndarray)
        assert wave.dtype == np.int16
        assert len(wave) == int(SAMPLE_RATE * 0.1)

    def test_pitch_sweep_produces_array(self):
        wave = pitch_sweep(440, 220, 0.1)
        assert isinstance(wave, np.ndarray)
        assert wave.dtype == np.int16
        assert len(wave) > 0

    def test_apply_envelope_preserves_length(self):
        wave = sine_wave(440, 0.1)
        result = apply_envelope(wave, attack=0.01, decay=0.02,
                                sustain_level=0.5, release=0.01)
        assert len(result) == len(wave)
        assert result.dtype == np.int16

    def test_mix_waves_combines(self):
        w1 = sine_wave(440, 0.1)
        w2 = square_wave(440, 0.1)
        mixed = mix_waves(w1, w2)
        assert len(mixed) == max(len(w1), len(w2))
        assert mixed.dtype == np.int16

    def test_mix_waves_empty(self):
        mixed = mix_waves()
        assert len(mixed) == 0

    def test_to_stereo(self):
        mono = sine_wave(440, 0.1)
        stereo = to_stereo(mono)
        assert stereo.shape == (len(mono), 2)
        assert stereo.dtype == np.int16
        # Both channels should be identical
        np.testing.assert_array_equal(stereo[:, 0], stereo[:, 1])

    def test_amplitude_scaling(self):
        """Half amplitude should produce values roughly half of full."""
        full = sine_wave(440, 0.1, amplitude=1.0)
        half = sine_wave(440, 0.1, amplitude=0.5)
        # Peak of half should be roughly half of full
        assert np.max(np.abs(half)) < np.max(np.abs(full))


# ---------------------------------------------------------------------------
# AudioManager
# ---------------------------------------------------------------------------

class TestAudioManager:
    def test_audio_manager_preload(self):
        """preload_all should populate the internal _sounds dict."""
        am = AudioManager()
        am.preload_all()
        assert len(am._sounds) > 0
        # Check a few well-known sound names
        assert "laser_single" in am._sounds
        assert "explosion_small" in am._sounds
        assert "menu_blip" in am._sounds

    def test_audio_manager_play_unknown_sound(self):
        """Playing an unknown sound name should not raise."""
        am = AudioManager()
        am.play("nonexistent_sound")  # should silently return

    def test_volume_clamping(self):
        """Volume setters should clamp values to [0.0, 1.0]."""
        am = AudioManager()

        am.master_volume = 1.5
        assert am.master_volume == 1.0

        am.master_volume = -0.5
        assert am.master_volume == 0.0

        am.sfx_volume = 2.0
        assert am.sfx_volume == 1.0

        am.sfx_volume = -1.0
        assert am.sfx_volume == 0.0

        am.music_volume = 3.0
        assert am.music_volume == 1.0

        am.music_volume = -2.0
        assert am.music_volume == 0.0

    def test_default_volumes(self):
        am = AudioManager()
        assert am.master_volume == 1.0
        assert am.sfx_volume == 0.7
        assert am.music_volume == 0.4
