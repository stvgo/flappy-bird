from __future__ import annotations

import pygame

from ..assets import AssetManager
from .entity import Entity


class Scroller(Entity):
    """Horizontally scrolling tiled image (background or ground).

    Two copies are blitted side by side; when the leading edge slides off the
    left, the offset wraps so the seam is invisible.
    """

    def __init__(self, assets: AssetManager, image_name: str, y: int, speed: float) -> None:
        self._image = assets.image(image_name)
        self._y = y
        self._speed = speed
        self._offset = 0.0
        self._width = self._image.get_width()
        self.scrolling = True

    def update(self, dt: float) -> None:
        if not self.scrolling:
            return
        self._offset = (self._offset + self._speed * dt) % self._width

    def draw(self, surface: pygame.Surface) -> None:
        x = -int(self._offset)
        screen_w = surface.get_width()
        while x < screen_w:
            surface.blit(self._image, (x, self._y))
            x += self._width

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(0, self._y, self._image.get_width(), self._image.get_height())
