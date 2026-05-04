from src import config
from src.entities.bird import Bird


def test_initial_state(assets):
    bird = Bird(assets)
    assert bird.x == config.BIRD_START_X
    assert bird.y == config.BIRD_START_Y
    assert bird.vy == 0.0
    assert bird.alive is True


def test_gravity_increases_vy(assets):
    bird = Bird(assets)
    bird.update(0.1)
    assert bird.vy == config.GRAVITY * 0.1


def test_jump_sets_vy_to_jump_velocity(assets):
    bird = Bird(assets)
    bird.vy = 200.0
    bird.jump()
    assert bird.vy == config.JUMP_VELOCITY


def test_vy_clamped_to_max_fall_speed(assets):
    bird = Bird(assets)
    for _ in range(120):
        bird.update(1 / 60)
    assert bird.vy == config.MAX_FALL_SPEED


def test_reset_restores_initial_state(assets):
    bird = Bird(assets)
    bird.x = 999.0
    bird.y = 999.0
    bird.vy = 500.0
    bird.alive = False
    bird.reset()
    assert bird.x == config.BIRD_START_X
    assert bird.y == config.BIRD_START_Y
    assert bird.vy == 0.0
    assert bird.alive is True


def test_animation_advances_after_interval(assets):
    bird = Bird(assets)
    initial = bird._frame_idx
    bird.update(config.BIRD_FLAP_INTERVAL + 0.001)
    assert bird._frame_idx == (initial + 1) % len(bird.FRAMES)


def test_animation_does_not_advance_when_dead(assets):
    bird = Bird(assets)
    bird.alive = False
    initial = bird._frame_idx
    for _ in range(20):
        bird.update(config.BIRD_FLAP_INTERVAL)
    assert bird._frame_idx == initial


def test_tilt_moves_up_after_jump(assets):
    bird = Bird(assets)
    bird.jump()
    bird.update(1 / 60)
    assert bird._tilt < 0
