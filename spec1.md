# Plan: Flappy Bird (Hackathon)

## Entregable previo (paso 0)

Antes de codificar, copiar este plan completo a `/Users/john.valeriano/Desktop/flappy-bird/spec1.md` para preservarlo como spec inicial versionado dentro del proyecto.

## Context

Proyecto nuevo desde cero (`/Users/john.valeriano/Desktop/flappy-bird/` está vacío) para un hackathon. Objetivo: clon de Flappy Bird jugable, con buena arquitectura y patrones de diseño aplicables, sin sobre-ingeniería. Stack confirmado: **Python + Pygame** con sprites pixel art clásicos. Alcance: core gameplay (bird, tubos, colisiones, score). Sin menús, sonidos ni persistencia.

## Stack seleccionado

| Componente | Elección | Razón |
|---|---|---|
| Lenguaje | Python 3.11+ | Iteración rápida en hackathon |
| Game lib | `pygame` 2.5+ | Estándar, simple, suficiente para 2D |
| Build/deps | `requirements.txt` + `venv` | Mínimo, sin overhead |
| Test (opcional) | `pytest` | Para lógica pura (física, colisiones) |

Una sola dependencia runtime: `pygame`. Cero compilación, demo cross-platform desde `python main.py`.

## Estructura del proyecto

```
flappy-bird/
├── main.py                       # Entry point: instancia Game y corre run()
├── requirements.txt              # pygame
├── README.md                     # Cómo correr y controles
├── assets/
│   └── images/
│       ├── bird.png              # Sprite con frames de aleteo
│       ├── pipe.png              # Tubo (mismo sprite invertido para techo)
│       ├── background.png        # Fondo scrollable
│       └── ground.png            # Piso scrollable
└── src/
    ├── __init__.py
    ├── config.py                 # Constantes de diseño (físicas, dims, FPS)
    ├── game.py                   # Clase Game: game loop, orquestación
    ├── assets.py                 # AssetManager: carga centralizada de sprites
    ├── entities/
    │   ├── __init__.py
    │   ├── entity.py             # Clase base Entity (update/draw/rect)
    │   ├── bird.py               # Bird: gravedad, jump, animación
    │   ├── pipe.py               # Pipe (par superior + inferior con gap)
    │   └── scroller.py           # Fondo y piso con desplazamiento infinito
    └── systems/
        ├── __init__.py
        ├── pipe_spawner.py       # Factory: spawnea Pipes a intervalos
        ├── collision.py          # Detección bird vs pipes/ground
        └── score.py              # Tracker de score + render
```

## Diseño / Patrones aplicados

1. **Game Loop centralizado** (`Game` en `src/game.py`)
   - Loop fijo: `handle_events()` → `update(dt)` → `draw()` → `tick(FPS)`
   - Maneja flag `alive` para reinicio con SPACE tras morir (sin state machine completa, alcance pedido)

2. **Entity base class** (template method) en `src/entities/entity.py`
   - Interfaz: `update(dt)`, `draw(surface)`, propiedad `rect`
   - `Bird`, `Pipe`, `Scroller` heredan de `Entity` — facilita iterar/dibujar uniformemente

3. **AssetManager** (`src/assets.py`)
   - Singleton-light: una instancia compartida via `Game`
   - Método `image(name)` con caché interno → evita recargar sprites
   - Aísla I/O del resto del juego (fácil de stub en tests)

4. **Factory / Spawner** (`src/systems/pipe_spawner.py`)
   - Encapsula creación de pares de tubos (random gap-Y) y mantiene cooldown
   - El `Game` solo le pide "actualízate y devuélveme nuevos pipes"

5. **Separation of concerns** — sistemas puros sin dependencias de pygame.draw:
   - `collision.py`: funciones puras `bird_hit_pipe(bird, pipe)`, `bird_hit_ground(bird, ground_y)` → testeable con pytest sin abrir ventana
   - `score.py`: lleva contador + dibuja con fuente; recibe eventos "pipe_passed"

6. **Config inmutable** (`src/config.py`)
   - Constantes (`SCREEN_W`, `GRAVITY`, `JUMP_VELOCITY`, `PIPE_SPEED`, `PIPE_GAP`, `SPAWN_INTERVAL_MS`, `FPS`)
   - Una sola fuente de verdad para tuning rápido durante hackathon

## Flujo del game loop

```
Game.run()
 ├─ events → si SPACE y alive → bird.jump(); si dead → reset()
 ├─ update(dt)
 │    ├─ bird.update(dt)              # gravedad + posición
 │    ├─ scroller.update(dt)          # fondo y piso
 │    ├─ pipe_spawner.update(dt)      # spawn nuevos pipes, mueve existentes
 │    ├─ collision check               # si choca → alive=False
 │    └─ score.check_passes(bird, pipes)
 └─ draw()
      ├─ scroller.draw(bg)
      ├─ pipes.draw()
      ├─ bird.draw()
      ├─ scroller.draw(ground)
      └─ score.draw()
```

## Archivos críticos a implementar (orden sugerido)

1. `requirements.txt`, `main.py` — esqueleto
2. `src/config.py` — constantes
3. `src/assets.py` — carga de sprites (con assets descargados a `assets/images/`)
4. `src/entities/entity.py` — base
5. `src/entities/bird.py` — gravedad + jump + animación de aleteo
6. `src/entities/pipe.py` — par sup/inf con gap
7. `src/entities/scroller.py` — fondo y piso scrollables
8. `src/systems/pipe_spawner.py` — factory + lista activa
9. `src/systems/collision.py` — funciones puras
10. `src/systems/score.py` — contador y render
11. `src/game.py` — game loop integrado

## Assets

Descargar sprites desde el repo GitHub `samuelcust/flappy-bird-assets` directamente a `assets/images/` durante la implementación (yo lo haré con `curl`/`git clone`, no se le pide al usuario). Sprites concretos a usar:

- `yellowbird-upflap.png`, `yellowbird-midflap.png`, `yellowbird-downflap.png` — animación del bird
- `pipe-green.png` — tubos (se rota 180° en código para el tubo superior)
- `background-day.png` — fondo
- `base.png` — piso
- `0.png`–`9.png` — dígitos para score

Comando previsto: `git clone https://github.com/samuelcust/flappy-bird-assets.git /tmp/fbassets` + copiar `sprites/*.png` a `assets/images/`. Luego eliminar el clone temporal. Documentar fuente y licencia en README.

## Verificación end-to-end

1. **Setup**: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. **Run**: `python main.py` → abre ventana, bird cae con gravedad
3. **Controles**: SPACE salta; tras morir, SPACE reinicia
4. **Smoke test gameplay**:
   - Bird responde al SPACE (impulso hacia arriba)
   - Tubos aparecen periódicamente y se mueven a la izquierda
   - Bird choca con tubo → muere y queda quieto hasta reinicio
   - Bird toca piso → muere
   - Score sube al pasar cada par de tubos
5. **Tests opcionales**: `pytest tests/test_collision.py` para validar funciones puras de colisión sin abrir ventana

## Fuera de alcance (explícitamente)

- Menú principal / pantalla de Game Over diseñada
- Sonidos / música
- High score persistente
- Múltiples dificultades / power-ups
