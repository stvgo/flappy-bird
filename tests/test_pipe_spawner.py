from src import config
from src.systems.pipe_spawner import PipeSpawner


def test_no_pipes_initially(assets):
    spawner = PipeSpawner(assets)
    assert spawner.pipes == []


def test_does_not_spawn_before_interval(assets):
    spawner = PipeSpawner(assets)
    spawner.update(config.PIPE_SPAWN_INTERVAL - 0.1)
    assert len(spawner.pipes) == 0


def test_spawns_pipe_after_interval(assets):
    spawner = PipeSpawner(assets)
    spawner.update(config.PIPE_SPAWN_INTERVAL + 0.01)
    assert len(spawner.pipes) == 1


def test_removes_off_screen_pipes(assets):
    spawner = PipeSpawner(assets)
    spawner.update(config.PIPE_SPAWN_INTERVAL + 0.01)
    assert len(spawner.pipes) == 1
    spawner.pipes[0].x = -200
    spawner.update(0.001)
    assert len(spawner.pipes) == 0


def test_reset_clears_pipes_and_timer(assets):
    spawner = PipeSpawner(assets)
    spawner.update(config.PIPE_SPAWN_INTERVAL + 0.01)
    assert len(spawner.pipes) > 0
    spawner.reset()
    assert spawner.pipes == []
    assert spawner._timer == 0.0


def test_spawning_false_blocks_new_pipes(assets):
    spawner = PipeSpawner(assets)
    spawner.spawning = False
    spawner.update(config.PIPE_SPAWN_INTERVAL * 3)
    assert spawner.pipes == []
