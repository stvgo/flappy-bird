from __future__ import annotations

import asyncio
import math
import sys

import pygame

from . import config
from .assets import AssetManager
from .entities.bird import Bird
from .entities.scroller import Scroller
from .systems import collision
from .systems.pipe_spawner import PipeSpawner
from .systems.score import Score


READY = "ready"
PLAYING = "playing"
DEAD = "dead"


class Game:
    """Owns the main loop and orchestrates entities and systems.

    State machine: READY (waiting for first input, kiro bobs in place) →
    PLAYING (full physics) → DEAD (world frozen) → back to READY on restart.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(config.GAME_TITLE)
        self.screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
        self.clock = pygame.time.Clock()

        self.assets = AssetManager()
        self.background = Scroller(
            self.assets, "background-day", y=0, speed=config.BG_SCROLL_SPEED
        )
        # Tint the sky in-place to a Kiro twilight purple. Scroller already
        # holds a reference to the cached surface, so this affects rendering.
        self.assets.image("background-day").fill(
            config.KIRO_BG_TINT, special_flags=pygame.BLEND_RGB_MULT
        )
        self.ground = Scroller(
            self.assets, "base", y=config.GROUND_Y, speed=config.GROUND_SCROLL_SPEED
        )
        self.bird = Bird(self.assets)
        self.spawner = PipeSpawner(self.assets)
        self.score = Score(self.assets)

        self.font_title = pygame.font.SysFont("arial", 30, bold=True)
        self.font_sub = pygame.font.SysFont("arial", 12, bold=True)
        self.font_prompt = pygame.font.SysFont("arial", 14, bold=True)

        self.state = READY
        self.t = 0.0
        self.running = True

    def reset(self) -> None:
        self.bird.reset()
        self.spawner.reset()
        self.score.reset()
        self.ground.scrolling = True
        self.state = READY
        self.t = 0.0

    async def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
            await asyncio.sleep(0)
        pygame.quit()
        sys.exit(0)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.state == READY:
                        self.state = PLAYING
                        self.bird.jump()
                    elif self.state == PLAYING:
                        self.bird.jump()
                    elif self.state == DEAD:
                        self.reset()

    def _update(self, dt: float) -> None:
        self.t += dt
        self.background.update(dt)
        if self.state == READY:
            self.bird.y = config.BIRD_START_Y + math.sin(
                self.t * config.START_BOB_FREQ
            ) * config.START_BOB_AMP
            self.ground.update(dt)
        elif self.state == PLAYING:
            self.bird.update(dt)
            self.ground.update(dt)
            self.spawner.update(dt)
            self.score.check_passes(self.bird, self.spawner.pipes)
            self._check_collisions()

    def _check_collisions(self) -> None:
        if collision.bird_hit_ground(self.bird, config.GROUND_Y):
            self._die(snap_to_ground=True)
            return
        if collision.bird_hit_ceiling(self.bird):
            self._die()
            return
        for pipe in self.spawner.pipes:
            if collision.bird_hit_pipe(self.bird, pipe):
                self._die()
                return

    def _die(self, snap_to_ground: bool = False) -> None:
        self.state = DEAD
        self.bird.alive = False
        self.ground.scrolling = False
        if snap_to_ground:
            self.bird.y = config.GROUND_Y - self.bird.rect.height // 2
            self.bird.vy = 0.0

    def _draw(self) -> None:
        self.background.draw(self.screen)
        self.spawner.draw(self.screen)
        self.ground.draw(self.screen)
        self.bird.draw(self.screen)
        if self.state == PLAYING:
            self.score.draw(self.screen)
        if self.state == READY:
            self._draw_start_overlay()
        elif self.state == DEAD:
            self._draw_game_over_overlay()

    def _draw_start_overlay(self) -> None:
        veil = pygame.Surface((config.SCREEN_W, config.SCREEN_H), pygame.SRCALPHA)
        veil.fill((*config.KIRO_BG, 90))
        self.screen.blit(veil, (0, 0))

        title = self.font_title.render("FLAPPY KIRO", True, config.KIRO_PURPLE)
        title_rect = title.get_rect(center=(config.SCREEN_W // 2, 110))
        self.screen.blit(title, title_rect)

        sub = self.font_sub.render("the friendly ghost", True, config.KIRO_TEXT_DIM)
        sub_rect = sub.get_rect(center=(config.SCREEN_W // 2, 140))
        self.screen.blit(sub, sub_rect)

        alpha = int(150 + 90 * math.sin(self.t * config.PROMPT_PULSE_FREQ))
        prompt = self.font_prompt.render(
            "PRESS SPACE TO START", True, config.KIRO_TEXT
        )
        prompt.set_alpha(max(60, min(255, alpha)))
        prompt_y = 360 + math.sin(self.t * 2.5) * 4
        prompt_rect = prompt.get_rect(center=(config.SCREEN_W // 2, prompt_y))
        self.screen.blit(prompt, prompt_rect)

    def _draw_game_over_overlay(self) -> None:
        veil = pygame.Surface((config.SCREEN_W, config.SCREEN_H), pygame.SRCALPHA)
        veil.fill((*config.KIRO_BG, 140))
        self.screen.blit(veil, (0, 0))

        title = self.font_title.render("GAME OVER", True, config.KIRO_PINK)
        title_rect = title.get_rect(center=(config.SCREEN_W // 2, 200))
        self.screen.blit(title, title_rect)

        self.score.draw(self.screen)

        alpha = int(150 + 90 * math.sin(self.t * config.PROMPT_PULSE_FREQ))
        prompt = self.font_prompt.render(
            "PRESS SPACE TO RESTART", True, config.KIRO_TEXT
        )
        prompt.set_alpha(max(60, min(255, alpha)))
        prompt_rect = prompt.get_rect(center=(config.SCREEN_W // 2, 300))
        self.screen.blit(prompt, prompt_rect)
