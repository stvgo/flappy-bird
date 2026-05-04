#!/usr/bin/env bash
set -euo pipefail

# Compila el juego a WASM con pygbag. Output queda en build/web/.
# Requiere: pip install pygbag (incluido en requirements-dev.txt)
#
# Pygbag escanea recursivamente el directorio del main script. Para evitar
# que incluya .venv/, .git/, build/, tests/, etc., copiamos solo lo necesario
# a un staging dir y construimos desde ahí.

cd "$(dirname "$0")/.."
ROOT=$(pwd)

if ! python -c "import pygbag" 2>/dev/null; then
    echo "pygbag no encontrado. Instalá con: pip install -r requirements-dev.txt" >&2
    exit 1
fi

STAGE_PARENT=$(mktemp -d)
STAGE="$STAGE_PARENT/flappy-bird"
mkdir "$STAGE"
trap 'rm -rf "$STAGE_PARENT"' EXIT

echo "==> Staging en $STAGE"
cp -R main.py src assets "$STAGE/"

echo "==> Building WASM bundle (pygbag)"
cd "$STAGE"
python -m pygbag --build --ume_block 0 main.py

cd "$ROOT"
rm -rf build
mkdir -p build
cp -R "$STAGE/build/web" build/web

echo "==> Inyectando CSS fullscreen en index.html"
python deploy/patch_index.py build/web/index.html

echo "==> Listo. Output en build/web/"
ls -lh build/web/ | head -10
