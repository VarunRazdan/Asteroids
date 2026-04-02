"""Stack-based scene manager for game state transitions."""


class Scene:
    """Base class for all game scenes."""

    def __init__(self, manager):
        self.manager = manager

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

    def on_enter(self):
        """Called when this scene becomes the active scene."""
        pass

    def on_exit(self):
        """Called when this scene is removed or covered."""
        pass


class SceneManager:
    """Manages a stack of scenes. The top scene receives events/updates/draws."""

    def __init__(self):
        self._stack = []

    @property
    def current_scene(self):
        return self._stack[-1] if self._stack else None

    def push(self, scene):
        """Push a scene on top (e.g., pause overlay)."""
        if self._stack:
            self._stack[-1].on_exit()
        self._stack.append(scene)
        scene.on_enter()

    def pop(self):
        """Remove the top scene and return to the one below."""
        if self._stack:
            self._stack[-1].on_exit()
            self._stack.pop()
            if self._stack:
                self._stack[-1].on_enter()

    def replace(self, scene):
        """Replace the top scene (e.g., menu → playing)."""
        if self._stack:
            self._stack[-1].on_exit()
            self._stack.pop()
        self._stack.append(scene)
        scene.on_enter()

    def handle_events(self, events):
        if self._stack:
            self._stack[-1].handle_events(events)

    def update(self, dt):
        if self._stack:
            self._stack[-1].update(dt)

    def draw(self, screen):
        # Draw all scenes in stack order (bottom to top) for overlays
        for scene in self._stack:
            scene.draw(screen)
