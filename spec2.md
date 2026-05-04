# Plan: Deploy Flappy Bird en AWS (single-player, web) — spec2

## Context

`spec1.md` describe el clon single-player en Python + Pygame ya implementado en `src/`. Ahora queremos exponerlo en una URL pública servida desde AWS, **manteniendo single-player y sin backend online**: cualquiera abre el link y juega en su navegador. Estrategia: compilar Pygame a WebAssembly con [`pygbag`](https://github.com/pygame-web/pygbag) y servir el bundle estático desde **S3 + CloudFront**.

Sin servidor, sin sesiones, sin multiplayer: solo archivos estáticos.

## Stack seleccionado

| Componente | Elección | Razón |
|---|---|---|
| Build | `pygbag` (Python → WASM via Pyodide) | Único toolchain estable que corre Pygame en navegador |
| Game loop | `asyncio` + `await asyncio.sleep(0)` por frame | Requisito de pygbag para no bloquear el browser |
| Hosting | S3 (bucket privado) + CloudFront (OAC) | Costo casi cero, CDN global, HTTPS automático |
| TLS | CloudFront default cert (`*.cloudfront.net`) | Sin dominio custom = sin ACM |
| IaC | Bash + AWS CLI (`deploy/*.sh`) | Mínimo viable, sin Terraform/CDK |

## Cambios sobre spec1

Pygbag necesita que el main loop sea `async`. Cambios mínimos a `src/`:

- `src/game.py:50` — `run()` es ahora `async def run()` y termina cada frame con `await asyncio.sleep(0)` (cede control al runtime de WASM).
- `main.py` — envuelve en `asyncio.run(main())`.

El gameplay y la arquitectura de spec1 quedan intactos (entities, systems, assets, config).

## Estructura del proyecto (incremento sobre spec1)

```
flappy-bird/
├── main.py                     # asyncio.run(Game().run())
├── src/                        # (sin cambios excepto game.py async)
├── assets/                     # (sin cambios)
├── spec1.md                    # (sin cambios)
├── spec2.md                    # este plan
├── requirements.txt            # solo pygame (runtime)
├── requirements-dev.txt        # pygame + pytest + pygbag
├── build/                      # generado por pygbag (gitignore)
│   └── web/
│       ├── index.html
│       ├── main.apk            # bundle del juego + assets
│       └── ...
└── deploy/
    ├── build.sh                # `python -m pygbag --build --ume_block 0 main.py`
    ├── deploy-s3.sh            # sync build/web → s3 + invalidación CloudFront
    └── bootstrap-aws.sh        # one-time: crea bucket, OAC, distribución
```

## Diseño / decisiones clave

1. **Pygbag build**: produce un sitio estático autocontenido en `build/web/`. No requiere servidor: `index.html` + `main.apk` (zip con bytecode + assets) + runtime WASM cargado desde CDN de pygbag.

2. **Bucket S3 privado + Origin Access Control (OAC)**: el bucket no es público; solo CloudFront puede leerlo. Esto evita listings inesperados y costos por abuso.

3. **CloudFront default cert**: usar `https://<dist>.cloudfront.net` evita ACM/Route53. Si después se quiere dominio custom: ACM en `us-east-1` + alias en CloudFront.

4. **Sin compresión custom**: pygbag ya genera archivos optimizados. CloudFront comprime gzip/brotli on-the-fly por default.

5. **Cache busting**: cada deploy invalida `/*` en CloudFront. Suficiente; no hay tráfico que justifique versionado de assets.

6. **Headers HTTP requeridos por pygbag/Pyodide**: WebAssembly con SharedArrayBuffer requiere `Cross-Origin-Opener-Policy: same-origin` y `Cross-Origin-Embedder-Policy: require-corp`. Se setean via CloudFront Response Headers Policy. Sin esto, `pygame.image` puede fallar al cargar PNGs en algunos navegadores.

7. **Fullscreen letterbox**: el juego renderiza internamente a 288×512 (portrait pixel art). Post-build se inyecta CSS en `index.html` que escala el canvas a `height: 100vh` con `aspect-ratio: 288/512` y `image-rendering: pixelated`. En desktop wide aparecen franjas negras a los costados (pixel art portrait). En mobile portrait llena casi toda la pantalla. La resolución de juego no cambia. Implementado en `deploy/patch_index.py`.

## Flujo de despliegue (paso a paso)

### One-time setup (`deploy/bootstrap-aws.sh`)

1. `aws s3 mb s3://flappy-bird-<acct>-<region>` — bucket privado
2. `aws s3api put-public-access-block` — bloqueo de acceso público
3. Crear OAC: `aws cloudfront create-origin-access-control`
4. Crear distribución CloudFront apuntando al bucket con OAC, default root object `index.html`, cert default
5. Aplicar bucket policy permitiendo `cloudfront.amazonaws.com` con condición de la distribución
6. (Opcional) Response Headers Policy con COOP/COEP

### Deploy (`deploy/deploy-s3.sh`)

```bash
bash deploy/build.sh                          # genera build/web
aws s3 sync build/web s3://<bucket>/ --delete
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

Tiempo: build ~30s, sync <10s, invalidación 1-2min.

## Reuso de spec1 (verificado)

- `src/config.py`, `src/assets.py`, `src/entities/*`, `src/systems/*`, `tests/` — sin cambios.
- `src/game.py` — solo se vuelve `async` el método `run()` (1 línea de import + 1 línea de sleep).
- `assets/images/*.png` — pygbag los empaqueta automáticamente al detectar `assets/` desde `main.py`.

## Archivos críticos a implementar

1. `src/game.py` — `async def run()` + `await asyncio.sleep(0)` (✅ hecho).
2. `main.py` — `asyncio.run(...)` (✅ hecho).
3. `requirements-dev.txt` — añadir `pygbag` (✅ hecho).
4. `deploy/build.sh` — wrapper de `python -m pygbag --build`.
5. `deploy/bootstrap-aws.sh` — one-time AWS resources.
6. `deploy/deploy-s3.sh` — sync + invalidación.
7. `.gitignore` — agregar `build/`.

## Verificación end-to-end

1. **Local desktop** (regresión): `python main.py` → ventana, gameplay sin cambios.
2. **Local pygbag**: `python -m pygbag main.py` → abre `http://localhost:8000` → juego corre en navegador, SPACE responde, score sube.
3. **Build estático**: `bash deploy/build.sh` → revisar que `build/web/index.html` y `build/web/main.apk` existen.
4. **AWS deploy**: `bash deploy/bootstrap-aws.sh` (una vez) → `bash deploy/deploy-s3.sh` → abrir URL CloudFront → mismo smoke test que (2).
5. **Rendimiento**: en navegador, FPS estable cerca de 60 (DevTools Performance). Asset load < 5s en conexión normal.

## Fuera de alcance (explícito)

- Multijugador / sesiones / leaderboard online (descartado explícitamente).
- Dominio custom + ACM + Route53.
- Persistencia de high scores en cloud (LocalStorage del browser sería trivial pero no se pide).
- CI/CD automático (queda como `bash deploy/deploy-s3.sh` manual).
- Soporte mobile (pygbag funciona pero el SPACE no aplica; se podría agregar handler de touch).

## Limitaciones conocidas

- Pygbag entrega ~5-8 MB iniciales (runtime Pyodide). Aceptable con CDN.
- Primer load lento (~3-5s) por bootstrap del runtime; subsequent loads cacheados.
- Sin SSR ni SEO; es una single-page WASM app.
