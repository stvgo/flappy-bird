from src.entities.bird import Bird
from src.entities.pipe import Pipe
from src.systems.score import Score


def test_starts_at_zero(assets):
    score = Score(assets)
    assert score.value == 0


def test_increments_when_bird_passes_pipe(assets):
    score = Score(assets)
    bird = Bird(assets)
    bird.x = 200.0
    pipe = Pipe(assets, x=100, gap_top=200)
    score.check_passes(bird, [pipe])
    assert score.value == 1
    assert pipe.scored is True


def test_does_not_double_count_same_pipe(assets):
    score = Score(assets)
    bird = Bird(assets)
    bird.x = 200.0
    pipe = Pipe(assets, x=100, gap_top=200)
    score.check_passes(bird, [pipe])
    score.check_passes(bird, [pipe])
    score.check_passes(bird, [pipe])
    assert score.value == 1


def test_does_not_increment_before_pipe_passed(assets):
    score = Score(assets)
    bird = Bird(assets)
    bird.x = 50.0
    pipe = Pipe(assets, x=200, gap_top=200)
    score.check_passes(bird, [pipe])
    assert score.value == 0
    assert pipe.scored is False


def test_reset_returns_to_zero(assets):
    score = Score(assets)
    score.value = 42
    score.reset()
    assert score.value == 0
