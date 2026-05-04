from __future__ import annotations

import pygame

from .. import config
from ..assets import AssetManager
from ..entities.bird import Bird
from ..entities.pipe import Pipe


class Score:
    """Tracks the player's score and renders it as centered digit sprites."""

    def __init__(self, assets: AssetManager) -> None:
        self._assets = assets
        self.value = 0

    def reset(self) -> None:
        self.value = 0

    def check_passes(self, bird: Bird, pipes: list[Pipe]) -> None:
        for pipe in pipes:
            if not pipe.scored and pipe.x < bird.x:
                pipe.scored = True
                self.value += 1

    def draw(self, surface: pygame.Surface) -> None:
        digits = [self._assets.digit(int(d)) for d in str(self.value)]
        total_w = sum(d.get_width() for d in digits)
        x = (config.SCREEN_W - total_w) // 2
        y = 40
        for digit in digits:
            surface.blit(digit, (x, y))
            x += digit.get_width()
