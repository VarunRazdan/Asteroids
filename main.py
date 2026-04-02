import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from input_manager import InputManager
from scenes import SceneManager
from scenes.title_scene import TitleScene


def main():
    pygame.init()

    # Internal render resolution (game logic always uses this)
    render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Start windowed at internal resolution; F/F11 to toggle fullscreen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("ASTEROIDS")
    clock = pygame.time.Clock()
    fullscreen = False

    # Input manager (keyboard + gamepad)
    input_mgr = InputManager()

    # Initialize optional systems (graceful fallback if not available)
    background = None
    vfx_manager = None
    screen_effects = None
    audio = None

    try:
        from background import StarfieldBackground
        background = StarfieldBackground()
    except Exception:
        pass

    try:
        from screen_effects import CRTScanlines, ScreenFlash, ScreenShake, SlowMo
        screen_effects = {
            "shake": ScreenShake(),
            "flash": ScreenFlash(),
            "crt": CRTScanlines(),
            "slowmo": SlowMo(),
        }
    except Exception:
        pass

    try:
        from particles import ParticlePool
        from vfx import VFXManager
        pool = ParticlePool()
        vfx_manager = VFXManager(pool, screen_effects)
    except Exception:
        pass

    try:
        from audio.audio_manager import AudioManager
        audio = AudioManager()
        audio.preload_all()
    except Exception:
        pass

    # Scene manager
    scene_manager = SceneManager()
    scene_manager.push(TitleScene(
        scene_manager, background, vfx_manager, screen_effects, audio, input_mgr,
    ))

    # Main loop
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
            input_mgr.handle_event(event)

            # Fullscreen toggle: F or F11
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_f, pygame.K_F11,
            ):
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(
                        (0, 0), pygame.FULLSCREEN
                    )
                else:
                    screen = pygame.display.set_mode(
                        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
                    )

        input_mgr.update()
        dt = clock.tick(60) / 1000

        # Global audio toggles — work in any scene
        if audio and input_mgr.is_music_toggle():
            audio.toggle_music()
        if audio and input_mgr.is_sfx_toggle():
            audio.toggle_sfx()

        # Transform mouse events to game coordinates for scaled rendering
        win_w, win_h = screen.get_size()
        scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
        offset_x = (win_w - int(SCREEN_WIDTH * scale)) // 2
        offset_y = (win_h - int(SCREEN_HEIGHT * scale)) // 2

        game_events = []
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                gx = int((event.pos[0] - offset_x) / scale)
                gy = int((event.pos[1] - offset_y) / scale)
                new_event = pygame.event.Event(
                    event.type, button=event.button, pos=(gx, gy),
                )
                game_events.append(new_event)
            else:
                game_events.append(event)

        # Render to internal surface, then scale to window
        scene_manager.handle_events(game_events)
        scene_manager.update(dt)
        scene_manager.draw(render_surface)

        # Scale render surface to fit the actual window
        if (win_w, win_h) == (SCREEN_WIDTH, SCREEN_HEIGHT):
            screen.blit(render_surface, (0, 0))
        else:
            scaled_w = int(SCREEN_WIDTH * scale)
            scaled_h = int(SCREEN_HEIGHT * scale)
            screen.fill((0, 0, 0))
            scaled = pygame.transform.smoothscale(
                render_surface, (scaled_w, scaled_h)
            )
            screen.blit(scaled, (offset_x, offset_y))

        pygame.display.flip()


if __name__ == "__main__":
    main()
