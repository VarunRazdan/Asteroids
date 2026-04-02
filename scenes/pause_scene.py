"""Pause overlay scene — pushed on top of PlayingScene."""
import math

import pygame

from colors import CYAN, WHITE
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from scenes.scene_manager import Scene


class PauseScene(Scene):
    def __init__(self, manager, input_mgr=None):
        super().__init__(manager)
        self.input_mgr = input_mgr
        self.timer = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_small = pygame.font.Font(None, 28)

    def handle_events(self, events):
        if self.input_mgr:
            if self.input_mgr.is_pause() or self.input_mgr.is_confirm():
                self.manager.pop()
                return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.manager.pop()

    def update(self, dt):
        self.timer += dt

    def draw(self, screen):
        # Semi-transparent overlay (PlayingScene is drawn below us)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        text_surf = self.font_large.render("PAUSED", True, WHITE)
        text_rect = text_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        )
        screen.blit(text_surf, text_rect)

        alpha = int(127 + 128 * math.sin(self.timer * 3))
        prompt = self.font_small.render("PRESS ESC / START TO RESUME", True, CYAN)
        prompt.set_alpha(alpha)
        pr = prompt.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        )
        screen.blit(prompt, pr)
