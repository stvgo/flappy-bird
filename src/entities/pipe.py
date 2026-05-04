from __future__ import annotations

import pygame

from .. import config
from ..assets import AssetManager
from .entity import Entity


class Pipe(Entity):
    """A pair of pipes (top + bottom) separated by a vertical gap.

    The same sprite is reused: the top pipe is the bottom sprite flipped
    vertically. gap_top is the y of the gap's upper edge.
    """

    def __init__(self, assets: AssetManager, x: float, gap_top: int) -> None:
        self._sprite_bottom = assets.image("pipe-green")
        self._sprite_top = pygame.transform.flip(self._sprite_bottom, False, True)
        self.x = float(x)
        self.gap_top = gap_top
        self.gap_bottom = gap_top + config.PIPE_GAP
        self.scored = False

    def update(self, dt: float) -> None:
        self.x -= config.PIPE_SPEED * dt

    def draw(self, surface: pygame.Surface) -> None:
        top_rect = self._sprite_top.get_rect(midbottom=(int(self.x), self.gap_top))
        bottom_rect = self._sprite_bottom.get_rect(midtop=(int(self.x), self.gap_bottom))
        surface.blit(self._sprite_top, top_rect)
        surface.blit(self._sprite_bottom, bottom_rect)

    @property
    def rect(self) -> pygame.Rect:
        w = self._sprite_bottom.get_width()
        return pygame.Rect(int(self.x) - w // 2, 0, w, config.SCREEN_H)

    @property
    def rect_top(self) -> pygame.Rect:
        w = self._sprite_top.get_width()
        return pygame.Rect(int(self.x) - w // 2, 0, w, self.gap_top)

    @property
    def rect_bottom(self) -> pygame.Rect:
        w = self._sprite_bottom.get_width()
        return pygame.Rect(
            int(self.x) - w // 2,
            self.gap_bottom,
            w,
            config.SCREEN_H - self.gap_bottom,
        )

    @property
    def is_off_screen(self) -> bool:
        return self.x + self._sprite_bottom.get_width() // 2 < 0
