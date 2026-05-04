from __future__ import annotations

import pygame

from .. import config
from ..assets import AssetManager
from .entity import Entity


class Bird(Entity):
    FRAMES = ("kiro",)
    SPRITE_SIZE = (40, 40)

    def __init__(self, assets: AssetManager) -> None:
        self._frames = [
            pygame.transform.smoothscale(assets.image(name), self.SPRITE_SIZE)
            for name in self.FRAMES
        ]
        self._frame_idx = 0
        self._frame_timer = 0.0
        self._tilt = 0.0
        self.x = float(config.BIRD_START_X)
        self.y = float(config.BIRD_START_Y)
        self.vy = 0.0
        self.alive = True

    def reset(self) -> None:
        self.x = float(config.BIRD_START_X)
        self.y = float(config.BIRD_START_Y)
        self.vy = 0.0
        self._tilt = 0.0
        self._frame_idx = 0
        self._frame_timer = 0.0
        self.alive = True

    def jump(self) -> None:
        self.vy = config.JUMP_VELOCITY

    def update(self, dt: float) -> None:
        self.vy = min(self.vy + config.GRAVITY * dt, config.MAX_FALL_SPEED)
        self.y += self.vy * dt

        if self.alive:
            self._frame_timer += dt
            if self._frame_timer >= config.BIRD_FLAP_INTERVAL:
                self._frame_timer = 0.0
                self._frame_idx = (self._frame_idx + 1) % len(self._frames)

        target_tilt = config.BIRD_TILT_UP if self.vy < 0 else config.BIRD_TILT_DOWN
        self._tilt += (target_tilt - self._tilt) * min(1.0, config.BIRD_TILT_LERP * dt)

    def draw(self, surface: pygame.Surface) -> None:
        sprite = self._frames[self._frame_idx]
        rotated = pygame.transform.rotate(sprite, -self._tilt)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)

    @property
    def rect(self) -> pygame.Rect:
        sprite = self._frames[self._frame_idx]
        return sprite.get_rect(center=(int(self.x), int(self.y)))
