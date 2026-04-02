"""Unified input manager: keyboard + Xbox/gamepad controller."""
import pygame

from constants import DEADZONE


def _apply_deadzone(value, threshold=DEADZONE):
    """Zero out values below the dead zone, remap the rest to full range."""
    if abs(value) < threshold:
        return 0.0
    sign = 1 if value > 0 else -1
    return sign * (abs(value) - threshold) / (1.0 - threshold)


class InputManager:
    """Reads keyboard and one optional gamepad, exposes unified queries.

    Call ``handle_event(event)`` for every pygame event each frame,
    then call ``update()`` once per frame before reading any input.
    """

    def __init__(self):
        pygame.joystick.init()
        self._joystick = None
        self._init_first_joystick()

        # One-shot edge detection: stores *previous frame* state
        self._prev_bomb = False
        self._prev_pause = False
        self._prev_confirm = False
        self._prev_music_toggle = False
        self._prev_sfx_toggle = False
        self._prev_menu_v = 0
        self._prev_menu_h = 0

        # Current frame raw state (set in update)
        self._keys = None
        self._joy_buttons = {}
        self._joy_axes = {}
        self._joy_hat = (0, 0)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _init_first_joystick(self):
        if pygame.joystick.get_count() > 0:
            self._joystick = pygame.joystick.Joystick(0)
            self._joystick.init()

    def handle_event(self, event):
        """Process controller connect/disconnect events."""
        if event.type == pygame.JOYDEVICEADDED:
            if self._joystick is None:
                self._joystick = pygame.joystick.Joystick(event.device_index)
                self._joystick.init()
        elif event.type == pygame.JOYDEVICEREMOVED:
            if self._joystick is not None:
                try:
                    if event.instance_id == self._joystick.get_instance_id():
                        self._joystick = None
                except pygame.error:
                    self._joystick = None

    def update(self):
        """Snapshot keyboard and joystick state. Call once per frame."""
        self._keys = pygame.key.get_pressed()

        if self._joystick is not None:
            try:
                for i in range(self._joystick.get_numbuttons()):
                    self._joy_buttons[i] = self._joystick.get_button(i)
                for i in range(self._joystick.get_numaxes()):
                    self._joy_axes[i] = self._joystick.get_axis(i)
                if self._joystick.get_numhats() > 0:
                    self._joy_hat = self._joystick.get_hat(0)
                else:
                    self._joy_hat = (0, 0)
            except pygame.error:
                self._joystick = None
                self._joy_buttons = {}
                self._joy_axes = {}
                self._joy_hat = (0, 0)
        else:
            self._joy_buttons = {}
            self._joy_axes = {}
            self._joy_hat = (0, 0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _btn(self, index):
        return self._joy_buttons.get(index, False)

    def _axis(self, index):
        return _apply_deadzone(self._joy_axes.get(index, 0.0))

    # ------------------------------------------------------------------
    # Gameplay input (continuous — True every frame while held)
    # ------------------------------------------------------------------

    def is_thrust(self):
        """W key, left stick up, or right trigger."""
        if self._keys and self._keys[pygame.K_w]:
            return True
        if self._axis(1) < -0.3:  # stick up (Y axis inverted)
            return True
        if self._joy_axes.get(5, -1.0) > 0.0:  # right trigger
            return True
        return False

    def is_reverse(self):
        """S key or left stick down."""
        if self._keys and self._keys[pygame.K_s]:
            return True
        return self._axis(1) > 0.3

    def get_rotation(self):
        """Return -1 to +1. A/D keys or left stick X axis."""
        val = 0.0
        if self._keys:
            if self._keys[pygame.K_a]:
                val -= 1.0
            if self._keys[pygame.K_d]:
                val += 1.0
        stick_x = self._axis(0)
        if abs(stick_x) > abs(val):
            val = stick_x
        return max(-1.0, min(1.0, val))

    def is_shoot(self):
        """Space, A button (0), or RB (5)."""
        if self._keys and self._keys[pygame.K_SPACE]:
            return True
        return self._btn(0) or self._btn(5)

    # ------------------------------------------------------------------
    # One-shot input (True only on the frame the button is first pressed)
    # ------------------------------------------------------------------

    def is_bomb(self):
        """B key or X button (2). One-shot."""
        raw = (
            (self._keys and self._keys[pygame.K_b])
            or self._btn(2)
            or self._btn(1)
        )
        result = raw and not self._prev_bomb
        self._prev_bomb = raw
        return result

    def is_pause(self):
        """ESC key or Start button (7). One-shot."""
        raw = (
            (self._keys and self._keys[pygame.K_ESCAPE])
            or self._btn(7)
        )
        result = raw and not self._prev_pause
        self._prev_pause = raw
        return result

    def is_confirm(self):
        """Enter, Space, or A button (0). One-shot."""
        raw = (
            (self._keys and (self._keys[pygame.K_RETURN]
                             or self._keys[pygame.K_SPACE]))
            or self._btn(0)
        )
        result = raw and not self._prev_confirm
        self._prev_confirm = raw
        return result

    def is_music_toggle(self):
        """M key or Y button (3). One-shot."""
        raw = (
            (self._keys and self._keys[pygame.K_m])
            or self._btn(3)
        )
        result = raw and not self._prev_music_toggle
        self._prev_music_toggle = raw
        return result

    def is_sfx_toggle(self):
        """N key. One-shot."""
        raw = bool(self._keys and self._keys[pygame.K_n])
        result = raw and not self._prev_sfx_toggle
        self._prev_sfx_toggle = raw
        return result

    # ------------------------------------------------------------------
    # Menu navigation (returns -1, 0, or +1 — with edge detection)
    # ------------------------------------------------------------------

    def get_menu_vertical(self):
        """UP/DOWN arrows, D-pad, or left stick Y. One-shot per direction."""
        raw = 0
        if self._keys:
            if self._keys[pygame.K_UP]:
                raw = -1
            elif self._keys[pygame.K_DOWN]:
                raw = 1
        hat_y = self._joy_hat[1]
        if hat_y != 0:
            raw = -hat_y  # hat Y: 1=up, -1=down; we want -1=up, 1=down
        stick_y = self._axis(1)
        if abs(stick_y) > 0.5:
            raw = 1 if stick_y > 0 else -1
        result = raw if raw != self._prev_menu_v else 0
        self._prev_menu_v = raw
        return result

    def get_menu_horizontal(self):
        """LEFT/RIGHT arrows, D-pad, or left stick X. One-shot per direction."""
        raw = 0
        if self._keys:
            if self._keys[pygame.K_LEFT]:
                raw = -1
            elif self._keys[pygame.K_RIGHT]:
                raw = 1
        hat_x = self._joy_hat[0]
        if hat_x != 0:
            raw = hat_x
        stick_x = self._axis(0)
        if abs(stick_x) > 0.5:
            raw = 1 if stick_x > 0 else -1
        result = raw if raw != self._prev_menu_h else 0
        self._prev_menu_h = raw
        return result

    @property
    def has_joystick(self):
        return self._joystick is not None
