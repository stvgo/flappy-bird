from __future__ import annotations

import random

from .. import config
from ..assets import AssetManager
from ..entities.pipe import Pipe


class PipeSpawner:
    """Owns the active pipe list and produces new ones at a fixed cadence."""

    def __init__(self, assets: AssetManager) -> None:
        self._assets = assets
        self.pipes: list[Pipe] = []
        self._timer = 0.0
        self.spawning = True

    def reset(self) -> None:
        self.pipes.clear()
        self._timer = 0.0
        self.spawning = True

    def update(self, dt: float) -> None:
        for pipe in self.pipes:
            pipe.update(dt)
        self.pipes = [p for p in self.pipes if not p.is_off_screen]

        if not self.spawning:
            return
        self._timer += dt
        if self._timer >= config.PIPE_SPAWN_INTERVAL:
            self._timer = 0.0
            self.pipes.append(self._make_pipe())

    def _make_pipe(self) -> Pipe:
        gap_top = random.randint(config.PIPE_MIN_TOP, config.PIPE_MAX_TOP)
        return Pipe(self._assets, x=config.SCREEN_W + 40, gap_top=gap_top)

    def draw(self, surface) -> None:
        for pipe in self.pipes:
            pipe.draw(surface)
