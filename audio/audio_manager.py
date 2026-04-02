"""Central audio manager — handles mixer init, channel routing, and volume."""

from enum import IntEnum

import pygame

from audio.sound_effects import (
    alien_destroyed,
    alien_shoot,
    blackhole_ambient,
    blackhole_kill,
    blackhole_suck,
    bomb_detonate,
    explosion_large,
    explosion_medium,
    explosion_small,
    game_over_jingle,
    laser_rapid,
    laser_single,
    laser_spread,
    life_lost,
    menu_blip,
    player_death,
    powerup_collect,
    shield_activate,
    shield_hit,
    thrust_loop,
)


class SoundPriority(IntEnum):
    """Higher value = harder to preempt."""
    AMBIENT = 0
    EFFECTS = 1
    UI = 2
    CRITICAL = 3


class AudioManager:
    """Manages all game audio: SFX, music, channel routing, and volume.

    Channel layout
    --------------
    0-5 : General SFX (chosen by priority)
    6   : Thrust (dedicated, looping)
    7   : UI sounds (dedicated)
    """

    # Channel indices
    _SFX_CHANNELS = list(range(0, 6))
    _THRUST_CHANNEL = 6
    _UI_CHANNEL = 7
    _TOTAL_CHANNELS = 8

    def __init__(self) -> None:
        # Initialise the mixer only if it is not already running.
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(self._TOTAL_CHANNELS)

        # Sound cache (populated by preload_all)
        self._sounds: dict[str, pygame.mixer.Sound] = {}

        # Per-channel priority tracking
        self._channel_priority: dict[int, SoundPriority] = {
            ch: SoundPriority.AMBIENT for ch in self._SFX_CHANNELS
        }

        # Volume defaults
        self._master_volume: float = 1.0
        self._sfx_volume: float = 0.7
        self._music_volume: float = 0.4
        self._ui_volume: float = 0.8

        # Mute state
        self._sfx_muted: bool = False
        self._saved_sfx_volume: float = self._sfx_volume

        # Thrust state
        self._thrust_playing: bool = False

        # Music state
        self._music_channel: pygame.mixer.Channel | None = None
        self._music_sound: pygame.mixer.Sound | None = None
        self._music_paused: bool = False

    # ------------------------------------------------------------------
    # Preloading
    # ------------------------------------------------------------------

    def preload_all(self) -> None:
        """Generate and cache every sound effect (call once at startup)."""
        generators = {
            "laser_single": laser_single,
            "laser_spread": laser_spread,
            "laser_rapid": laser_rapid,
            "explosion_small": explosion_small,
            "explosion_medium": explosion_medium,
            "explosion_large": explosion_large,
            "powerup_collect": powerup_collect,
            "shield_activate": shield_activate,
            "shield_hit": shield_hit,
            "bomb_detonate": bomb_detonate,
            "player_death": player_death,
            "thrust_loop": thrust_loop,
            "life_lost": life_lost,
            "menu_blip": menu_blip,
            "game_over_jingle": game_over_jingle,
            "alien_shoot": alien_shoot,
            "alien_destroyed": alien_destroyed,
            "blackhole_ambient": blackhole_ambient,
            "blackhole_suck": blackhole_suck,
            "blackhole_kill": blackhole_kill,
        }
        for name, gen_fn in generators.items():
            self._sounds[name] = gen_fn()

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

    def play(
        self,
        sound_name: str,
        priority: SoundPriority = SoundPriority.EFFECTS,
        loops: int = 0,
    ) -> None:
        """Play a cached sound on the best available SFX channel.

        Channel selection order:
        1. Free (not busy) channel
        2. Channel playing a sound with *lower* priority (preempt it)

        If no channel is available the sound is silently dropped.
        """
        sound = self._sounds.get(sound_name)
        if sound is None:
            return

        channel = self._find_channel(priority)
        if channel is None:
            return

        ch_idx = channel.get_id() if hasattr(channel, "get_id") else -1
        self._channel_priority[ch_idx] = priority
        effective_vol = self._master_volume * self._sfx_volume
        channel.set_volume(effective_vol)
        channel.play(sound, loops=loops)

    def _find_channel(self, priority: SoundPriority) -> pygame.mixer.Channel | None:
        """Return the best SFX channel for the given priority, or *None*."""
        # Pass 1: look for a free channel
        for ch_idx in self._SFX_CHANNELS:
            ch = pygame.mixer.Channel(ch_idx)
            if not ch.get_busy():
                return ch

        # Pass 2: preempt the lowest-priority channel if it is below *priority*
        lowest_pri = priority
        lowest_ch: pygame.mixer.Channel | None = None
        for ch_idx in self._SFX_CHANNELS:
            ch_pri = self._channel_priority.get(ch_idx, SoundPriority.AMBIENT)
            if ch_pri < lowest_pri:
                lowest_pri = ch_pri
                lowest_ch = pygame.mixer.Channel(ch_idx)
        return lowest_ch

    # ------------------------------------------------------------------
    # Thrust (dedicated channel 6)
    # ------------------------------------------------------------------

    def start_thrust(self) -> None:
        """Start the looping thrust sound on the dedicated channel."""
        if self._thrust_playing:
            return
        sound = self._sounds.get("thrust_loop")
        if sound is None:
            return
        ch = pygame.mixer.Channel(self._THRUST_CHANNEL)
        effective_vol = self._master_volume * self._sfx_volume * 0.6
        ch.set_volume(effective_vol)
        ch.play(sound, loops=-1)
        self._thrust_playing = True

    def stop_thrust(self) -> None:
        """Fade out and stop thrust sound."""
        if not self._thrust_playing:
            return
        ch = pygame.mixer.Channel(self._THRUST_CHANNEL)
        ch.fadeout(150)  # 150 ms fade
        self._thrust_playing = False

    # ------------------------------------------------------------------
    # UI sounds (dedicated channel 7)
    # ------------------------------------------------------------------

    def play_ui(self, sound_name: str) -> None:
        """Play a UI sound on the dedicated UI channel."""
        sound = self._sounds.get(sound_name)
        if sound is None:
            return
        ch = pygame.mixer.Channel(self._UI_CHANNEL)
        effective_vol = self._master_volume * self._ui_volume
        ch.set_volume(effective_vol)
        ch.play(sound)

    # ------------------------------------------------------------------
    # Music
    # ------------------------------------------------------------------

    def start_music(self, music_sound: pygame.mixer.Sound) -> None:
        """Start looping background music from a Sound object."""
        self.stop_music()
        self._music_sound = music_sound
        # Use a dynamically-allocated channel beyond the reserved 8
        self._music_channel = pygame.mixer.find_channel(True)
        if self._music_channel is not None:
            effective_vol = self._master_volume * self._music_volume
            self._music_channel.set_volume(effective_vol)
            self._music_channel.play(music_sound, loops=-1)

    def stop_music(self) -> None:
        """Stop background music with a short fade."""
        if self._music_channel is not None and self._music_channel.get_busy():
            self._music_channel.fadeout(500)
        self._music_channel = None
        self._music_sound = None

    def toggle_music(self) -> bool:
        """Toggle music on/off. Returns True if music is now playing."""
        if self._music_paused:
            # Resume
            if self._music_channel is not None:
                self._music_channel.unpause()
            elif self._music_sound is not None:
                self.start_music(self._music_sound)
            self._music_paused = False
            return True
        else:
            # Pause
            if self._music_channel is not None:
                self._music_channel.pause()
            self._music_paused = True
            return False

    @property
    def music_playing(self) -> bool:
        """True if music is currently playing (not paused)."""
        return not self._music_paused and self._music_channel is not None

    def toggle_sfx(self) -> bool:
        """Toggle SFX on/off. Returns True if SFX is now on."""
        if self._sfx_muted:
            self._sfx_volume = self._saved_sfx_volume
            self._sfx_muted = False
            return True
        else:
            self._saved_sfx_volume = self._sfx_volume
            self._sfx_volume = 0.0
            self._sfx_muted = True
            # Stop any currently playing thrust
            if self._thrust_playing:
                self.stop_thrust()
            return False

    @property
    def sfx_enabled(self) -> bool:
        return not self._sfx_muted

    # ------------------------------------------------------------------
    # Volume properties
    # ------------------------------------------------------------------

    @property
    def master_volume(self) -> float:
        return self._master_volume

    @master_volume.setter
    def master_volume(self, value: float) -> None:
        self._master_volume = max(0.0, min(1.0, value))
        self._apply_volumes()

    @property
    def sfx_volume(self) -> float:
        return self._sfx_volume

    @sfx_volume.setter
    def sfx_volume(self, value: float) -> None:
        self._sfx_volume = max(0.0, min(1.0, value))
        self._apply_volumes()

    @property
    def music_volume(self) -> float:
        return self._music_volume

    @music_volume.setter
    def music_volume(self, value: float) -> None:
        self._music_volume = max(0.0, min(1.0, value))
        self._apply_volumes()

    def _apply_volumes(self) -> None:
        """Push current volume settings to all active channels."""
        sfx_vol = self._master_volume * self._sfx_volume
        for ch_idx in self._SFX_CHANNELS:
            ch = pygame.mixer.Channel(ch_idx)
            ch.set_volume(sfx_vol)

        # Thrust
        thrust_ch = pygame.mixer.Channel(self._THRUST_CHANNEL)
        thrust_ch.set_volume(self._master_volume * self._sfx_volume * 0.6)

        # UI
        ui_ch = pygame.mixer.Channel(self._UI_CHANNEL)
        ui_ch.set_volume(self._master_volume * self._ui_volume)

        # Music
        if self._music_channel is not None and self._music_channel.get_busy():
            self._music_channel.set_volume(self._master_volume * self._music_volume)
