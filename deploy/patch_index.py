"""Inject fullscreen letterbox CSS into pygbag's generated index.html.

Keeps the canvas at native 288x512 backing resolution; CSS scales it to
100vh preserving the 288:512 aspect ratio, with black bars on the sides
on wide viewports. Pixel art stays crisp via `image-rendering: pixelated`.
"""

from __future__ import annotations

import sys
from pathlib import Path

CSS_BLOCK = """
<style id="fullscreen-letterbox">
    html, body {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        background: #000 !important;
    }
    canvas.emscripten#canvas {
        position: fixed !important;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        height: 100vh !important;
        width: auto !important;
        aspect-ratio: 864 / 512;
        max-width: 100vw;
        max-height: 100vh;
        image-rendering: pixelated;
        image-rendering: -moz-crisp-edges;
        image-rendering: crisp-edges;
    }
    #transfer { position: fixed; top: 12px; left: 12px; z-index: 10; color: #ddd; }
    #infobox { position: fixed; bottom: 12px; left: 12px; z-index: 10; color: #ddd; }
</style>
"""


def patch(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    if 'id="fullscreen-letterbox"' in html:
        return
    if "</head>" not in html:
        raise SystemExit("no </head> in index.html — pygbag template changed?")
    html = html.replace("</head>", CSS_BLOCK + "</head>", 1)
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_index.py <index.html>")
    patch(Path(sys.argv[1]))
