"""Integration tests for scene management transitions."""

from unittest.mock import MagicMock

import pygame

from scenes.scene_manager import Scene, SceneManager
from scenes.title_scene import TitleScene


class TestTitleToPlaying:
    def test_title_to_playing(self):
        """Pressing ENTER on the title screen should transition to PlayingScene."""
        sm = SceneManager()
        title = TitleScene(sm, background=None, vfx_manager=None,
                           screen_effects=None, audio=None)
        sm.push(title)
        assert sm.current_scene is title

        # Simulate a KEYDOWN RETURN event
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        sm.handle_events([event])

        # After handling RETURN, the scene should have been replaced
        current = sm.current_scene
        assert current is not title
        # Verify it is a PlayingScene (by class name to avoid circular imports)
        assert type(current).__name__ == "PlayingScene"


class TestPlayingPauseResume:
    def test_playing_pause_resume(self):
        """ESC should push PauseScene; ESC again should pop back to PlayingScene."""
        sm = SceneManager()
        title = TitleScene(sm, background=None, vfx_manager=None,
                           screen_effects=None, audio=None)
        sm.push(title)

        # Transition to playing
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        sm.handle_events([enter_event])
        playing = sm.current_scene
        assert type(playing).__name__ == "PlayingScene"

        # Pause
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        sm.handle_events([esc_event])
        assert type(sm.current_scene).__name__ == "PauseScene"

        # Resume
        sm.handle_events([esc_event])
        assert sm.current_scene is playing


class TestSceneManagerStack:
    def test_push_pop(self):
        sm = SceneManager()
        s1 = Scene(sm)
        s2 = Scene(sm)
        sm.push(s1)
        sm.push(s2)
        assert sm.current_scene is s2
        sm.pop()
        assert sm.current_scene is s1

    def test_replace(self):
        sm = SceneManager()
        s1 = Scene(sm)
        s2 = Scene(sm)
        sm.push(s1)
        sm.replace(s2)
        assert sm.current_scene is s2
        # Stack should have only one scene
        sm.pop()
        assert sm.current_scene is None

    def test_on_enter_on_exit_called(self):
        sm = SceneManager()
        s1 = Scene(sm)
        s1.on_enter = MagicMock()
        s1.on_exit = MagicMock()

        sm.push(s1)
        s1.on_enter.assert_called_once()

        sm.pop()
        s1.on_exit.assert_called_once()
