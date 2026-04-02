"""Title screen scene with ASCII art, author credit, and version."""
import math

import pygame

from colors import CYAN, NEON_GREEN, WHITE, YELLOW
from constants import GAME_VERSION, SCREEN_HEIGHT, SCREEN_WIDTH
from scenes.scene_manager import Scene
from scoreboard import Scoreboard

TITLE_ART = [
    " █████  ███████ ████████ ███████ ██████   ██████  ██ ██████  ███████",
    "██   ██ ██         ██    ██      ██   ██ ██    ██ ██ ██   ██ ██     ",
    "███████ ███████    ██    █████   ██████  ██    ██ ██ ██   ██ ███████",
    "██   ██      ██    ██    ██      ██   ██ ██    ██ ██ ██   ██      ██",
    "██   ██ ███████    ██    ███████ ██   ██  ██████  ██ ██████  ███████",
]


class TitleScene(Scene):
    def __init__(self, manager, background, vfx_manager, screen_effects, audio,
                 input_mgr=None):
        super().__init__(manager)
        self.background = background
        self.vfx = vfx_manager
        self.effects = screen_effects
        self.audio = audio
        self.input_mgr = input_mgr
        self.timer = 0

        mono = "couriernew,courier,monospace"
        self.art_font = pygame.font.SysFont(mono, 22)
        self.subtitle_font = pygame.font.SysFont("arial", 40)
        self.author_font = pygame.font.SysFont("arial", 34)
        self.link_font = pygame.font.SysFont("arial", 28)
        self.controls_font = pygame.font.SysFont("arial", 26)
        self.highscore_font = pygame.font.SysFont("arial", 36)
        self.version_font = pygame.font.SysFont("arial", 24)
        self._high_score = Scoreboard().high_score()

    def on_enter(self):
        self._high_score = Scoreboard().high_score()
        if self.audio:
            try:
                from audio.music_generator import generate_music_loop
                music = generate_music_loop()
                self.audio.start_music(music)
            except Exception:
                pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_game()
                    return
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button
                    self._start_game()
                    return

    def _start_game(self):
        if self.audio:
            self.audio.play("menu_blip", priority=2)
        from scenes.playing_scene import PlayingScene
        self.manager.replace(PlayingScene(
            self.manager, self.background, self.vfx,
            self.effects, self.audio, self.input_mgr,
        ))

    def update(self, dt):
        self.timer += dt

    def draw(self, screen):
        screen.fill("black")

        if self.background:
            self.background.draw(screen)

        # Block-letter title with glow
        art_y_start = 80
        line_height = 26

        # Glow pass (cyan, pulsing)
        glow_alpha = 70 + int(40 * math.sin(self.timer * 2))
        for i, line in enumerate(TITLE_ART):
            surf = self.art_font.render(line, True, CYAN)
            surf.set_alpha(glow_alpha)
            rect = surf.get_rect(
                center=(SCREEN_WIDTH // 2, art_y_start + i * line_height)
            )
            screen.blit(surf, rect)

        # Sharp pass (bright white on top)
        for i, line in enumerate(TITLE_ART):
            surf = self.art_font.render(line, True, WHITE)
            rect = surf.get_rect(
                center=(SCREEN_WIDTH // 2, art_y_start + i * line_height)
            )
            screen.blit(surf, rect)

        # Author credit
        art_bottom = art_y_start + len(TITLE_ART) * line_height + 30
        author_surf = self.author_font.render(
            "Created by Varun Razdan", True, WHITE
        )
        ar = author_surf.get_rect(center=(SCREEN_WIDTH // 2, art_bottom))
        screen.blit(author_surf, ar)

        # GitHub link
        link_surf = self.link_font.render(
            "Github.com/VarunRazdan/Asteroids", True, CYAN
        )
        lr = link_surf.get_rect(center=(SCREEN_WIDTH // 2, art_bottom + 30))
        screen.blit(link_surf, lr)

        # High score
        if self._high_score > 0:
            hs_text = f"HIGH SCORE: {self._high_score:,}"
            hs_surf = self.highscore_font.render(hs_text, True, YELLOW)
            hs_rect = hs_surf.get_rect(
                center=(SCREEN_WIDTH // 2, art_bottom + 65)
            )
            screen.blit(hs_surf, hs_rect)

        # Blinking "PRESS ENTER / A TO START"
        alpha = int(127 + 128 * math.sin(self.timer * 3))
        prompt_text = "PRESS ENTER TO START"
        prompt_surf = self.subtitle_font.render(prompt_text, True, NEON_GREEN)
        prompt_surf.set_alpha(alpha)
        prompt_y = SCREEN_HEIGHT // 2 + 100
        pr = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, prompt_y))
        screen.blit(prompt_surf, pr)

        # Controls
        controls = [
            "KEYBOARD: W/A/S/D Move  |  SPACE Shoot  |  B Bomb  |  ESC Pause",
            "GAMEPAD:  Left Stick Move  |  A Shoot  |  X Bomb  |  START Pause",
            "M - Toggle Music  |  N - Toggle SFX  |  F - Fullscreen",
        ]
        y = prompt_y + 50
        for line in controls:
            surf = self.controls_font.render(line, True, (210, 215, 230))
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
            screen.blit(surf, rect)
            y += 26

        # Version (bottom-right)
        ver_surf = self.version_font.render(
            f"v{GAME_VERSION}", True, (180, 180, 195)
        )
        screen.blit(ver_surf, (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 30))

        # CRT overlay
        if self.effects and "crt" in self.effects:
            self.effects["crt"].draw(screen)
