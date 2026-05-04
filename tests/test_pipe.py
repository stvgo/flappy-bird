from src import config
from src.entities.pipe import Pipe


def test_update_moves_pipe_left(assets):
    pipe = Pipe(assets, x=200, gap_top=150)
    pipe.update(1.0)
    assert pipe.x == 200 - config.PIPE_SPEED


def test_rect_top_spans_above_gap(assets):
    pipe = Pipe(assets, x=100, gap_top=200)
    rect = pipe.rect_top
    assert rect.top == 0
    assert rect.bottom == 200
    assert rect.centerx == 100


def test_rect_bottom_starts_at_gap_bottom(assets):
    pipe = Pipe(assets, x=100, gap_top=150)
    expected_gap_bottom = 150 + config.PIPE_GAP
    rect = pipe.rect_bottom
    assert rect.top == expected_gap_bottom
    assert rect.bottom == config.SCREEN_H
    assert rect.centerx == 100


def test_is_off_screen_when_x_far_left(assets):
    pipe = Pipe(assets, x=-100, gap_top=200)
    assert pipe.is_off_screen is True


def test_is_not_off_screen_when_visible(assets):
    pipe = Pipe(assets, x=100, gap_top=200)
    assert pipe.is_off_screen is False


def test_scored_default_false(assets):
    pipe = Pipe(assets, x=100, gap_top=200)
    assert pipe.scored is False
