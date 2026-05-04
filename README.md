# Flappy Bird

Clon de Flappy Bird construido para hackathon en Python + Pygame, con foco en arquitectura limpia y patrones de diseño.

## Requisitos

- Python 3.11+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Correr

### Directo

```bash
python main.py
```

### Mediante el intérprete / CLI del proyecto

El archivo `interpreter.py` unifica todas las operaciones comunes:

```bash
python interpreter.py run          # Ejecuta el juego desktop
python interpreter.py test         # Corre pytest
python interpreter.py build        # Build WASM con pygbag
python interpreter.py serve        # Sirve build/web/ localmente
python interpreter.py deploy       # Build + sync S3 + invalida CloudFront
python interpreter.py bootstrap    # Crea recursos AWS (one-time)
python interpreter.py clean        # Limpia build/, __pycache__, etc.
```

## Controles

- `SPACE` — saltar / reiniciar tras morir
- `ESC` o cerrar ventana — salir

## Arquitectura

Ver [spec1.md](./spec1.md) para diseño detallado.

```
src/
├── config.py            # Constantes
├── game.py              # Game loop
├── assets.py            # AssetManager
├── entities/            # Bird, Pipe, Scroller, Entity (base)
└── systems/             # PipeSpawner, collision, Score
```

Patrones aplicados: Entity base class (template method), AssetManager (singleton-light con caché), PipeSpawner (factory), separación de lógica pura de colisiones para testabilidad, config inmutable centralizada.

## Assets

Sprites cortesía de [samuelcust/flappy-bird-assets](https://github.com/samuelcust/flappy-bird-assets). Ver licencia en ese repositorio.
