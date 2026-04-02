"""Main gameplay scene — sprite groups, collisions, scoring, everything."""
import random

import pygame

from alien import AlienCraft, AlienShot, AlienSpawner
from asteroid import Asteroid
from asteroidfield import AsteroidField
from blackhole import BlackHole, BlackHoleSpawner
from collision import sat_triangle_circle
from constants import (
    ALIEN_POWERUP_CHANCE,
    ALIEN_SCORE,
    ASTEROID_MIN_RADIUS,
    COMBO_MAX_MULTIPLIER,
    COMBO_TIMEOUT,
    DEATH_DELAY,
    PLAYER_LIVES,
    POWERUP_SPAWN_CHANCE,
    SCORE_LARGE_ASTEROID,
    SCORE_MEDIUM_ASTEROID,
    SCORE_SMALL_ASTEROID,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from hud import HUD
from player import Player
from powerup import (
    ALL_TYPES,
    BOMB,
    LIFE,
    POWERUP_COLORS,
    SHIELD,
    SPEED,
    WEAPON_RAPID,
    WEAPON_SPREAD,
    PowerUp,
)
from scenes.scene_manager import Scene
from shot import Shot
from weapons import RapidFire, SpreadShot


class PlayingScene(Scene):
    def __init__(self, manager, background, vfx_manager, screen_effects, audio,
                 input_mgr=None):
        super().__init__(manager)
        self.background = background
        self.vfx = vfx_manager
        self.effects = screen_effects
        self.audio = audio
        self.input_mgr = input_mgr

        # Sprite groups
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_shots = pygame.sprite.Group()
        self.blackholes = pygame.sprite.Group()

        # Set containers before creating any sprites
        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable,)
        Shot.containers = (self.shots, self.updatable, self.drawable)
        PowerUp.containers = (self.powerups, self.updatable, self.drawable)
        AlienCraft.containers = (self.aliens, self.updatable, self.drawable)
        AlienShot.containers = (
            self.alien_shots, self.updatable, self.drawable,
        )
        AlienSpawner.containers = (self.updatable,)
        BlackHole.containers = (
            self.blackholes, self.updatable, self.drawable,
        )
        BlackHoleSpawner.containers = (self.updatable,)

        # Create game objects
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player.input_mgr = self.input_mgr
        self.asteroid_field = AsteroidField()
        self.alien_spawner = AlienSpawner(self.aliens, self.player)
        self.blackhole_spawner = BlackHoleSpawner(
            self.blackholes, self.player,
        )

        self.lives = PLAYER_LIVES
        self.hud = HUD()
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Death delay — let explosion play before transitioning to game over
        self._game_over_pending = False
        self._game_over_timer = 0
        self._spiral_death_pending = False

    def handle_events(self, events):
        if self.input_mgr:
            if self.input_mgr.is_pause():
                from scenes.pause_scene import PauseScene
                self.manager.push(PauseScene(self.manager, self.input_mgr))
                return
            if self.input_mgr.is_bomb():
                self._use_bomb()
                return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.pause_scene import PauseScene
                    self.manager.push(PauseScene(self.manager, self.input_mgr))
                elif event.key == pygame.K_b:
                    self._use_bomb()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.hud.handle_click(event.pos, self.audio)

    def update(self, dt):
        # Apply slow-mo scaling
        real_dt = dt
        if self.effects:
            game_dt = dt * self.effects["slowmo"].get_scale()
        else:
            game_dt = dt

        # Death delay — still update VFX/effects but skip gameplay
        if self._game_over_pending:
            self._game_over_timer -= real_dt
            if self.vfx:
                self.vfx.update(game_dt)
            if self.effects:
                self.effects["shake"].update(real_dt)
                self.effects["flash"].update(real_dt)
                self.effects["slowmo"].update(real_dt)
            # Asteroids keep moving during death delay
            self.updatable.update(game_dt)
            if self._game_over_timer <= 0:
                from scenes.game_over_scene import GameOverScene
                self.manager.replace(GameOverScene(
                    self.manager, self.player.score,
                    self.background, self.effects, self.audio,
                    self.input_mgr,
                ))
            return

        # Update all sprites
        self.updatable.update(game_dt)

        # Update effects
        if self.vfx:
            self.vfx.update(game_dt)
        if self.effects:
            self.effects["shake"].update(real_dt)
            self.effects["flash"].update(real_dt)
            self.effects["slowmo"].update(real_dt)

        self.hud.update(real_dt, self.player.score)

        # Player thrust particles
        if self.player.is_thrusting and self.vfx:
            self.vfx.on_player_thrust(self.player.position, self.player.rotation)

        # Shoot sound + muzzle flash
        if self.player.just_shot:
            weapon_name = self.player.active_weapon.name.lower()
            if self.audio:
                sound_map = {
                    "single": "laser_single",
                    "spread": "laser_spread",
                    "rapid": "laser_rapid",
                }
                snd = sound_map.get(weapon_name, "laser_single")
                self.audio.play(snd)
            if self.vfx:
                self.vfx.on_player_shoot(
                    self.player.position, self.player.rotation,
                    weapon_name,
                )

        # Collision: player vs asteroids (SAT triangle collision)
        if not self.player.invulnerable:
            for asteroid in list(self.asteroids):
                tri_points = self.player.get_triangle_points()
                if sat_triangle_circle(tri_points, asteroid.position, asteroid.radius):
                    self._player_hit()
                    return  # stop processing after death

        # Collision: shots vs asteroids
        for asteroid in list(self.asteroids):
            for shot in list(self.shots):
                if asteroid.collides_with(shot):
                    self._asteroid_destroyed(asteroid)
                    shot.kill()
                    break

        # Collision: player vs power-ups
        for powerup in list(self.powerups):
            if self.player.collides_with(powerup):
                self._collect_powerup(powerup)

        # Collision: player vs aliens (SAT)
        if not self.player.invulnerable and not self.player.being_sucked:
            for alien in list(self.aliens):
                tri = self.player.get_triangle_points()
                if sat_triangle_circle(tri, alien.position, alien.radius):
                    self._player_hit()
                    return

        # Collision: player vs alien shots
        if not self.player.invulnerable and not self.player.being_sucked:
            for ashot in list(self.alien_shots):
                if self.player.collides_with(ashot):
                    ashot.kill()
                    self._player_hit()
                    return

        # Collision: player shots vs aliens
        for alien in list(self.aliens):
            for shot in list(self.shots):
                if alien.collides_with(shot):
                    shot.kill()
                    if alien.take_damage():
                        self._alien_destroyed(alien)
                    break

        # Black hole gravity & kill zone
        for bh in list(self.blackholes):
            if self.vfx:
                self.vfx.on_blackhole_pull(bh.position)
            # Pull all nearby entities
            for entity in list(self.asteroids):
                bh.apply_gravity(entity, game_dt)
            for entity in list(self.shots):
                bh.apply_gravity(entity, game_dt)
            for entity in list(self.powerups):
                bh.apply_gravity(entity, game_dt)
            # Player: check kill zone
            if (not self.player.invulnerable
                    and not self.player.being_sucked):
                killed = bh.apply_gravity(self.player, game_dt)
                if killed:
                    self._blackhole_death(bh)
                    return
            # Check if player spiral finished
            if (self.player.being_sucked
                    and not self.player.alive()):
                pass  # handled by spiral timer

        # Check if spiral death animation finished
        if (self._spiral_death_pending
                and not self.player.being_sucked):
            self._spiral_death_pending = False
            self._player_hit()
            return

    def draw(self, screen):
        self.game_surface.fill("black")

        # Background
        if self.background:
            self.background.draw(self.game_surface)

        # Particles (behind game objects)
        if self.vfx:
            self.vfx.draw(self.game_surface)

        # Game objects
        for obj in self.drawable:
            obj.draw(self.game_surface)

        # Blit game surface with shake offset
        if self.effects:
            ox, oy = self.effects["shake"].get_offset()
        else:
            ox, oy = 0, 0
        screen.blit(self.game_surface, (ox, oy))

        # HUD (no shake)
        self.hud.draw(screen, self.player, self.lives, self.audio)

        # Screen flash
        if self.effects:
            self.effects["flash"].draw(screen)
            self.effects["crt"].draw(screen)

    def _player_hit(self):
        """Handle player being hit by an asteroid."""
        if self.player.shield_active:
            self.player.shield_active = False
            self.player.shield_timer = 0
            if self.audio:
                self.audio.play("shield_hit")
            if self.effects:
                self.effects["shake"].add_trauma(0.3)
            return

        self.lives -= 1
        if self.audio:
            self.audio.play("player_death", priority=3)
            self.audio.play("life_lost", priority=3)
        if self.vfx:
            self.vfx.on_player_death(self.player.position)
        if self.effects:
            self.effects["shake"].add_trauma(0.8)
            self.effects["flash"].trigger()

        if self.lives <= 0:
            # Start death delay — let explosion play before game over
            self._game_over_pending = True
            self._game_over_timer = DEATH_DELAY
            self.player.kill()  # remove from drawable/updatable
            return

        # Respawn
        self.player.reset_position()
        self.player.make_invulnerable()

    def _asteroid_destroyed(self, asteroid):
        """Handle asteroid destruction: score, split, particles, power-up drop."""
        # Score based on size
        if asteroid.radius <= ASTEROID_MIN_RADIUS:
            base_points = SCORE_SMALL_ASTEROID
        elif asteroid.radius <= ASTEROID_MIN_RADIUS * 2:
            base_points = SCORE_MEDIUM_ASTEROID
        else:
            base_points = SCORE_LARGE_ASTEROID

        # Combo system
        self.player.combo_timer = COMBO_TIMEOUT
        points = base_points * self.player.combo_multiplier
        self.player.score += points
        if self.player.combo_multiplier < COMBO_MAX_MULTIPLIER:
            self.player.combo_multiplier += 1

        # HUD popup
        self.hud.add_score_popup(
            asteroid.position.x, asteroid.position.y,
            base_points, self.player.combo_multiplier
        )

        # Audio
        if self.audio:
            if asteroid.radius <= ASTEROID_MIN_RADIUS:
                self.audio.play("explosion_small")
            elif asteroid.radius <= ASTEROID_MIN_RADIUS * 2:
                self.audio.play("explosion_medium")
            else:
                self.audio.play("explosion_large")

        # VFX
        if self.vfx:
            self.vfx.on_asteroid_destroyed(asteroid.position, asteroid.velocity, asteroid.radius)

        # Screen shake proportional to size
        if self.effects:
            trauma = min(0.6, asteroid.radius / 60)
            self.effects["shake"].add_trauma(trauma)

        # Split the asteroid
        asteroid.split()

        # Power-up drop (medium/large only)
        if asteroid.radius > ASTEROID_MIN_RADIUS and random.random() < POWERUP_SPAWN_CHANCE:
            ptype = random.choice(ALL_TYPES)
            PowerUp(asteroid.position.x, asteroid.position.y, ptype)

    def _collect_powerup(self, powerup):
        """Apply power-up effect to player."""
        if self.audio:
            self.audio.play("powerup_collect")
        if self.vfx:
            color = POWERUP_COLORS.get(powerup.powerup_type, (255, 255, 255))
            self.vfx.on_powerup_collected(powerup.position, color)

        ptype = powerup.powerup_type
        if ptype == SHIELD:
            self.player.activate_shield()
            if self.audio:
                self.audio.play("shield_activate")
        elif ptype == SPEED:
            self.player.activate_speed_boost()
        elif ptype == WEAPON_SPREAD:
            self.player.set_weapon(SpreadShot)
        elif ptype == WEAPON_RAPID:
            self.player.set_weapon(RapidFire)
        elif ptype == BOMB:
            self.player.add_bomb()
        elif ptype == LIFE:
            self.lives = min(self.lives + 1, 5)

        powerup.kill()

    def _alien_destroyed(self, alien):
        """Handle alien craft destruction."""
        self.player.score += ALIEN_SCORE
        self.hud.add_score_popup(
            alien.position.x, alien.position.y, ALIEN_SCORE,
        )
        if self.audio:
            self.audio.play("alien_destroyed")
        if self.vfx:
            self.vfx.on_alien_destroyed(alien.position)
        alien.kill()
        # High chance power-up drop
        if random.random() < ALIEN_POWERUP_CHANCE:
            PowerUp(alien.position.x, alien.position.y, random.choice(ALL_TYPES))

    def _blackhole_death(self, blackhole):
        """Start the spiral death animation for the player."""
        if self.player.shield_active:
            self.player.shield_active = False
            self.player.shield_timer = 0
            if self.audio:
                self.audio.play("shield_hit")
            return
        if self.audio:
            self.audio.play("blackhole_suck", priority=3)
        self.player.start_spiral_death(blackhole.position)
        self._spiral_death_pending = True

    def _use_bomb(self):
        """Detonate a bomb, destroying all on-screen asteroids."""
        if self.player.bombs <= 0:
            return
        self.player.bombs -= 1

        if self.audio:
            self.audio.play("bomb_detonate", priority=3)
        if self.vfx:
            self.vfx.on_bomb_detonated(self.player.position)
        if self.effects:
            self.effects["shake"].add_trauma(1.0)
            self.effects["flash"].trigger(255)
            self.effects["slowmo"].trigger()

        # Destroy all asteroids and aliens
        for asteroid in list(self.asteroids):
            self.player.score += SCORE_SMALL_ASTEROID
            if self.vfx:
                self.vfx.on_asteroid_destroyed(
                    asteroid.position, asteroid.velocity, asteroid.radius
                )
            asteroid.kill()
        for alien in list(self.aliens):
            self.player.score += ALIEN_SCORE
            if self.vfx:
                self.vfx.on_alien_destroyed(alien.position)
            alien.kill()
        for ashot in list(self.alien_shots):
            ashot.kill()
