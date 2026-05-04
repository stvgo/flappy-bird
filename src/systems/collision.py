from __future__ import annotations

from ..entities.bird import Bird
from ..entities.pipe import Pipe


def bird_hit_pipe(bird: Bird, pipe: Pipe) -> bool:
    bird_rect = bird.rect.inflate(-6, -6)
    return bird_rect.colliderect(pipe.rect_top) or bird_rect.colliderect(pipe.rect_bottom)


def bird_hit_ground(bird: Bird, ground_y: int) -> bool:
    return bird.rect.bottom >= ground_y


def bird_hit_ceiling(bird: Bird) -> bool:
    return bird.rect.top <= 0
