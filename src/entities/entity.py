from __future__ import annotations

import pygame


class Entity:
    """Base class for anything that lives in the world.

    Subclasses override update(dt) and draw(surface). The rect property is the
    canonical AABB used by collision and rendering helpers.
    """

    def update(self, dt: float) -> None:
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

    @property
    def rect(self) -> pygame.Rect:
        raise NotImplementedError
