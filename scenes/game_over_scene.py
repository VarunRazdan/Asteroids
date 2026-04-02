"""Game over screen with score, name entry, and top-10 scoreboard."""
import math

import pygame

from colors import CYAN, NEON_GREEN, RED, WHITE, YELLOW
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from scenes.scene_manager import Scene
from scoreboard import Scoreboard


class GameOverScene(Scene):
    def __init__(self, manager, final_score, background, screen_effects, audio,
                 input_mgr=None):
        super().__init__(manager)
        self.final_score = final_score
        self.background = background
        self.effects = screen_effects
        self.audio = audio
        self.input_mgr = input_mgr
        self.timer = 0

        # Fonts
        self.title_font = pygame.font.SysFont("arial", 72)
        self.score_font = pygame.font.SysFont("arial", 56)
        self.prompt_font = pygame.font.SysFont("arial", 32)
        self.board_font = pygame.font.SysFont("arial", 28)
        self.entry_font = pygame.font.SysFont("arial", 48)

        # Pre-create overlay surface
        self._overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self._overlay.fill((0, 0, 0, 150))

        # Scoreboard
        self._scoreboard = Scoreboard()
        self._is_high_score = self._scoreboard.is_high_score(final_score)
        self._score_saved = False
        self._show_board = not self._is_high_score

        # Name entry (classic arcade: 3 chars, A-Z)
        self._initials = [0, 0, 0]  # index into A-Z (0=A, 25=Z)
        self._cursor = 0
        self._played_jingle = False

    def on_enter(self):
        if self.audio and not self._played_jingle:
            self.audio.play("game_over", priority=3)
            self._played_jingle = True

    def handle_events(self, events):
        # Controller input for name entry navigation
        if self._is_high_score and not self._score_saved and self.input_mgr:
            v = self.input_mgr.get_menu_vertical()
            if v < 0:  # up
                self._initials[self._cursor] = (
                    (self._initials[self._cursor] + 1) % 26
                )
                if self.audio:
                    self.audio.play("menu_blip", priority=2)
            elif v > 0:  # down
                self._initials[self._cursor] = (
                    (self._initials[self._cursor] - 1) % 26
                )
                if self.audio:
                    self.audio.play("menu_blip", priority=2)
            h = self.input_mgr.get_menu_horizontal()
            if h > 0:
                self._cursor = min(2, self._cursor + 1)
            elif h < 0:
                self._cursor = max(0, self._cursor - 1)
            if self.input_mgr.is_confirm():
                self._save_score()
                return
        elif self._show_board and self.input_mgr:
            if self.input_mgr.is_confirm():
                self._go_to_title()
                return

        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if self._is_high_score and not self._score_saved:
                self._handle_name_entry_key(event)
            elif self._show_board:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._go_to_title()

    def _handle_name_entry_key(self, event):
        """Handle keyboard input for name entry."""
        if self.audio:
            self.audio.play("menu_blip", priority=2)

        # Direct A-Z typing
        if pygame.K_a <= event.key <= pygame.K_z:
            self._initials[self._cursor] = event.key - pygame.K_a
            if self._cursor < 2:
                self._cursor += 1
        elif event.key == pygame.K_BACKSPACE:
            self._initials[self._cursor] = 0
            if self._cursor > 0:
                self._cursor -= 1
        elif event.key == pygame.K_UP:
            self._initials[self._cursor] = (
                (self._initials[self._cursor] + 1) % 26
            )
        elif event.key == pygame.K_DOWN:
            self._initials[self._cursor] = (
                (self._initials[self._cursor] - 1) % 26
            )
        elif event.key == pygame.K_RIGHT:
            self._cursor = min(2, self._cursor + 1)
        elif event.key == pygame.K_LEFT:
            self._cursor = max(0, self._cursor - 1)
        elif event.key == pygame.K_RETURN:
            self._save_score()

    def _save_score(self):
        name = "".join(chr(65 + c) for c in self._initials)
        self._scoreboard.add_score(name, self.final_score)
        self._score_saved = True
        self._show_board = True

    def _go_to_title(self):
        if self.audio:
            self.audio.play("menu_blip", priority=2)
        from scenes.title_scene import TitleScene
        self.manager.replace(TitleScene(
            self.manager, self.background,
            None, self.effects, self.audio, self.input_mgr,
        ))

    def update(self, dt):
        self.timer += dt

    def draw(self, screen):
        screen.fill("black")

        if self.background:
            self.background.draw(screen)

        screen.blit(self._overlay, (0, 0))

        # "GAME OVER" title
        title_surf = self.title_font.render("GAME OVER", True, RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_surf, title_rect)

        # Final score
        score_text = f"{self.final_score:,}"
        score_surf = self.score_font.render(score_text, True, YELLOW)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(score_surf, score_rect)

        if self._is_high_score and not self._score_saved:
            self._draw_name_entry(screen)
        elif self._show_board:
            self._draw_scoreboard(screen)
            if self.timer > 1.0:
                alpha = int(127 + 128 * math.sin(self.timer * 3))
                prompt = self.prompt_font.render(
                    "PRESS ENTER TO CONTINUE", True, NEON_GREEN
                )
                prompt.set_alpha(alpha)
                pr = prompt.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
                )
                screen.blit(prompt, pr)

        # CRT scanlines
        if self.effects and "crt" in self.effects:
            self.effects["crt"].draw(screen)

    def _draw_name_entry(self, screen):
        """Draw the 3-character name entry interface."""
        pulse = 1.0 + 0.15 * math.sin(self.timer * 5)
        size = int(36 * pulse)
        font = pygame.font.SysFont("arial", size)
        label = font.render("NEW HIGH SCORE!", True, NEON_GREEN)
        lr = label.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(label, lr)

        inst = self.prompt_font.render(
            "TYPE A-Z  |  ARROWS to navigate  |  ENTER to confirm",
            True, (150, 150, 160),
        )
        ir = inst.get_rect(center=(SCREEN_WIDTH // 2, 240))
        screen.blit(inst, ir)

        # 3-character display
        cx = SCREEN_WIDTH // 2
        cy = 300
        spacing = 60

        for i in range(3):
            char = chr(65 + self._initials[i])
            color = CYAN if i == self._cursor else WHITE
            char_surf = self.entry_font.render(char, True, color)
            x = cx + (i - 1) * spacing
            cr = char_surf.get_rect(center=(x, cy))
            screen.blit(char_surf, cr)

            if i == self._cursor and int(self.timer * 4) % 2 == 0:
                ux = x - 15
                uy = cy + 22
                pygame.draw.line(screen, CYAN, (ux, uy), (ux + 30, uy), 3)

        # Up/down arrows for current slot
        ax = cx + (self._cursor - 1) * spacing
        arrow_col = (100, 100, 120)
        pygame.draw.polygon(screen, arrow_col, [
            (ax, cy - 40), (ax - 8, cy - 30), (ax + 8, cy - 30),
        ])
        pygame.draw.polygon(screen, arrow_col, [
            (ax, cy + 40), (ax - 8, cy + 30), (ax + 8, cy + 30),
        ])

        self._draw_scoreboard(screen, y_start=380)

    def _draw_scoreboard(self, screen, y_start=200):
        """Draw the top-10 scoreboard table."""
        scores = self._scoreboard.get_scores()
        if not scores:
            empty = self.board_font.render(
                "No scores yet", True, (100, 100, 120)
            )
            er = empty.get_rect(center=(SCREEN_WIDTH // 2, y_start + 40))
            screen.blit(empty, er)
            return

        header = self.board_font.render(
            "RANK   NAME    SCORE", True, (120, 120, 140)
        )
        hr = header.get_rect(center=(SCREEN_WIDTH // 2, y_start))
        screen.blit(header, hr)

        sep_y = y_start + 16
        sep_w = 260
        pygame.draw.line(
            screen, (60, 60, 70),
            (SCREEN_WIDTH // 2 - sep_w // 2, sep_y),
            (SCREEN_WIDTH // 2 + sep_w // 2, sep_y),
        )

        saved_name = "".join(chr(65 + c) for c in self._initials)
        for i, entry in enumerate(scores):
            y = y_start + 30 + i * 28
            rank = f"{i + 1:>2}."
            name = entry["name"]
            score = f"{entry['score']:>8,}"
            text = f"{rank}    {name}    {score}"

            is_current = (
                self._score_saved
                and entry["score"] == self.final_score
                and entry["name"] == saved_name
            )
            color = YELLOW if is_current else WHITE
            line_surf = self.board_font.render(text, True, color)
            line_rect = line_surf.get_rect(
                center=(SCREEN_WIDTH // 2, y)
            )
            screen.blit(line_surf, line_rect)
