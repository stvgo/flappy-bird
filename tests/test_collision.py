from src import config
from src.entities.bird import Bird
from src.entities.pipe import Pipe
from src.systems import collision


def _bird_at(assets, x: float, y: float) -> Bird:
    bird = Bird(assets)
    bird.x = float(x)
    bird.y = float(y)
    return bird


def test_bird_inside_gap_does_not_hit_pipe(assets):
    bird = _bird_at(assets, 100, 256)
    pipe = Pipe(assets, x=100, gap_top=200)
    assert collision.bird_hit_pipe(bird, pipe) is False


def test_bird_overlapping_top_pipe_collides(assets):
    bird = _bird_at(assets, 100, 100)
    pipe = Pipe(assets, x=100, gap_top=200)
    assert collision.bird_hit_pipe(bird, pipe) is True


def test_bird_overlapping_bottom_pipe_collides(assets):
    bird = _bird_at(assets, 100, 400)
    pipe = Pipe(assets, x=100, gap_top=100)
    assert collision.bird_hit_pipe(bird, pipe) is True


def test_bird_far_from_pipe_does_not_collide(assets):
    bird = _bird_at(assets, 10, 256)
    pipe = Pipe(assets, x=250, gap_top=100)
    assert collision.bird_hit_pipe(bird, pipe) is False


def test_bird_hit_ground_when_below_line(assets):
    bird = _bird_at(assets, 96, config.GROUND_Y + 5)
    assert collision.bird_hit_ground(bird, config.GROUND_Y) is True


def test_bird_hit_ground_false_when_above_line(assets):
    bird = _bird_at(assets, 96, 100)
    assert collision.bird_hit_ground(bird, config.GROUND_Y) is False


def test_bird_hit_ceiling_when_at_top(assets):
    bird = _bird_at(assets, 96, 5)
    assert collision.bird_hit_ceiling(bird) is True


def test_bird_hit_ceiling_false_when_visible(assets):
    bird = _bird_at(assets, 96, 100)
    assert collision.bird_hit_ceiling(bird) is False
