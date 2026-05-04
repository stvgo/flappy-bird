import pygame

from . import config


class AssetManager:
    """Centralizes sprite loading with an in-memory cache.

    Convert images to pygame's optimal pixel format on load via convert_alpha,
    so blitting is fast and we don't pay the conversion cost per frame.
    """

    def __init__(self) -> None:
        self._cache: dict[str, pygame.Surface] = {}

    def image(self, name: str) -> pygame.Surface:
        if name not in self._cache:
            path = config.ASSETS_DIR / f"{name}.png"
            self._cache[name] = pygame.image.load(str(path)).convert_alpha()
        return self._cache[name]

    def digit(self, n: int) -> pygame.Surface:
        return self.image(str(n))
