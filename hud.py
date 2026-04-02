"""Heads-up display: score, lives, combo, power-up timers, bombs, weapon type."""
import math

import pygame

from colors import (
    HUD_COMBO_COLOR,
    HUD_LIVES_COLOR,
    HUD_SCORE_COLOR,
    NEON_GREEN,
    PURPLE,
    SHIELD_COLOR,
)
from constants import (
    HUD_FONT_SIZE,
    HUD_FONT_SIZE_LARGE,
    HUD_MARGIN,
    SCORE_POPUP_LIFETIME,
    SCORE_POPUP_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIELD_DURATION,
    SPEED_BOOST_DURATION,
    WEAPON_POWERUP_DURATION,
)


class ScorePopup:
    """Floating score text that rises and fades."""

    def __init__(self, x, y, text, color=HUD_SCORE_COLOR):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.age = 0
        self.alive = True

    def update(self, dt):
        self.y -= SCORE_POPUP_SPEED * dt
        self.age += dt
        if self.age >= SCORE_POPUP_LIFETIME:
            self.alive = False

    def draw(self, screen, font):
        if not self.alive:
            return
        alpha = max(0, 255 * (1 - self.age / SCORE_POPUP_LIFETIME))
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(int(alpha))
        screen.blit(text_surf, (self.x - text_surf.get_width() // 2, int(self.y)))


class HUD:
    """Draws all HUD elements."""

    # Audio icon positions (top-right corner)
    ICON_SIZE = 24
    MUSIC_ICON_POS = (SCREEN_WIDTH - HUD_MARGIN - 100, HUD_MARGIN)
    SFX_ICON_POS = (SCREEN_WIDTH - HUD_MARGIN - 100, HUD_MARGIN + 28)

    def __init__(self):
        self.font = pygame.font.Font(None, HUD_FONT_SIZE)
        self.font_large = pygame.font.Font(None, HUD_FONT_SIZE_LARGE)
        self.icon_font = pygame.font.Font(None, 20)
        self.score_popups = []
        self._score_scale = 1.0
        self._prev_score = 0

    def add_score_popup(self, x, y, points, multiplier=1):
        text = f"+{points}"
        if multiplier > 1:
            text = f"+{points} x{multiplier}"
        color = HUD_COMBO_COLOR if multiplier > 1 else HUD_SCORE_COLOR
        self.score_popups.append(ScorePopup(x, y, text, color))

    def update(self, dt, score):
        # Score pop animation
        if score != self._prev_score:
            self._score_scale = 1.3
            self._prev_score = score
        if self._score_scale > 1.0:
            self._score_scale = max(1.0, self._score_scale - dt * 3)

        # Update popups
        for popup in self.score_popups:
            popup.update(dt)
        self.score_popups = [p for p in self.score_popups if p.alive]

    def draw(self, screen, player, lives, audio=None):
        self._draw_score(screen, player.score)
        self._draw_lives(screen, lives)
        self._draw_combo(screen, player)
        self._draw_weapon(screen, player)
        self._draw_bombs(screen, player)
        self._draw_powerup_timers(screen, player)
        self._draw_popups(screen)
        if audio:
            self._draw_audio_icons(screen, audio)

    def _draw_score(self, screen, score):
        text = f"{score:,}"
        size = int(HUD_FONT_SIZE_LARGE * self._score_scale)
        font = pygame.font.Font(None, size)
        surf = font.render(text, True, HUD_SCORE_COLOR)
        screen.blit(surf, (HUD_MARGIN, HUD_MARGIN))

    def _draw_lives(self, screen, lives):
        y = HUD_MARGIN + HUD_FONT_SIZE_LARGE + 5
        for i in range(lives):
            x = HUD_MARGIN + i * 25
            # Draw mini ship triangle
            points = [
                (x, y),
                (x - 6, y + 12),
                (x + 6, y + 12),
            ]
            pygame.draw.polygon(screen, HUD_LIVES_COLOR, points, 1)

    def _draw_combo(self, screen, player):
        if player.combo_multiplier <= 1:
            return
        text = f"x{player.combo_multiplier}"
        pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)
        size = int(HUD_FONT_SIZE * pulse)
        font = pygame.font.Font(None, size)
        surf = font.render(text, True, HUD_COMBO_COLOR)
        x = HUD_MARGIN + 200
        screen.blit(surf, (x, HUD_MARGIN + 10))

    def _draw_weapon(self, screen, player):
        text = player.active_weapon.name
        color = player.active_weapon.shot_color
        surf = self.font.render(text, True, color)
        screen.blit(surf, (HUD_MARGIN, SCREEN_HEIGHT - HUD_MARGIN - HUD_FONT_SIZE))

    def _draw_bombs(self, screen, player):
        if player.bombs <= 0:
            return
        y = SCREEN_HEIGHT - HUD_MARGIN - 15
        x_start = SCREEN_WIDTH - HUD_MARGIN - player.bombs * 25
        for i in range(player.bombs):
            x = x_start + i * 25
            pygame.draw.circle(screen, PURPLE, (x + 8, y), 8, 2)
            pygame.draw.line(screen, PURPLE, (x + 8, y - 8), (x + 8, y - 12), 2)

    def _draw_powerup_timers(self, screen, player):
        """Draw active power-up timer bars on the right side."""
        bars = []
        if player.shield_active:
            bars.append(("SHIELD", player.shield_timer / SHIELD_DURATION, SHIELD_COLOR))
        if player.speed_boost_active:
            bars.append(("SPEED", player.speed_boost_timer / SPEED_BOOST_DURATION, NEON_GREEN))
        if player.weapon_timer > 0:
            bars.append((player.active_weapon.name,
                         player.weapon_timer / WEAPON_POWERUP_DURATION,
                         player.active_weapon.shot_color))

        x = SCREEN_WIDTH - HUD_MARGIN - 120
        for i, (label, frac, color) in enumerate(bars):
            y = HUD_MARGIN + 60 + i * 30  # below audio toggle labels
            # Label
            label_surf = self.font.render(label, True, color)
            screen.blit(label_surf, (x, y))
            # Bar background
            bar_x = x
            bar_y = y + 18
            bar_w = 120
            bar_h = 6
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            # Bar fill
            fill_w = int(bar_w * max(0, frac))
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_w, bar_h))

    def _draw_popups(self, screen):
        for popup in self.score_popups:
            popup.draw(screen, self.font)

    def _draw_audio_icons(self, screen, audio):
        """Draw music and SFX toggle labels in the top-right corner."""
        mx, my = self.MUSIC_ICON_POS
        sx, sy = self.SFX_ICON_POS

        # Music: [M] MUSIC ON / OFF
        music_on = audio.music_playing
        m_col = (80, 220, 255) if music_on else (180, 60, 60)
        m_status = "ON" if music_on else "OFF"
        m_text = f"[M] MUSIC {m_status}"
        m_surf = self.icon_font.render(m_text, True, m_col)
        screen.blit(m_surf, (mx, my))

        # SFX: [N] SFX ON / OFF
        sfx_on = audio.sfx_enabled
        s_col = (80, 220, 255) if sfx_on else (180, 60, 60)
        s_status = "ON" if sfx_on else "OFF"
        s_text = f"[N] SFX {s_status}"
        s_surf = self.icon_font.render(s_text, True, s_col)
        screen.blit(s_surf, (sx, sy))

    def handle_click(self, pos, audio):
        """Check if a mouse click hit an audio label. Returns True if handled."""
        if audio is None:
            return False
        mx, my = self.MUSIC_ICON_POS
        if mx <= pos[0] <= mx + 120 and my <= pos[1] <= my + 20:
            audio.toggle_music()
            return True
        sx, sy = self.SFX_ICON_POS
        if sx <= pos[0] <= sx + 100 and sy <= pos[1] <= sy + 20:
            audio.toggle_sfx()
            return True
        return False
