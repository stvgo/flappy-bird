#!/usr/bin/env python3
"""Interpreter / CLI para el proyecto Flappy Bird.

Unifica las operaciones más comunes del proyecto en un solo entry point:
run, test, build web, deploy, bootstrap AWS, y limpieza.

Uso:
    python interpreter.py run          # Ejecuta el juego desktop
    python interpreter.py test         # Corre pytest
    python interpreter.py build        # Build WASM con pygbag
    python interpreter.py serve        # Sirve build/web/ localmente
    python interpreter.py deploy       # Build + sync S3 + invalida CloudFront
    python interpreter.py bootstrap    # Crea recursos AWS (one-time)
    python interpreter.py clean        # Elimina build/, __pycache__, etc.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# -----------------------------------------------------------------------------
# Constantes
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_WEB = PROJECT_ROOT / "build" / "web"
DEPLOY_DIR = PROJECT_ROOT / "deploy"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def run_cmd(cmd: list[str] | str, *, cwd: Path | None = None, env: dict[str, str] | None = None) -> int:
    """Ejecuta un comando y retorna su exit code."""
    print(f"==> {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, env=env)
    return result.returncode


def require_venv() -> None:
    """Avisa si no parece estar activado un venv (solo warning)."""
    import sys
    if sys.prefix == sys.base_prefix:
        print("⚠️  No detecté un virtualenv activo. Si fallan imports, activá .venv/")


# -----------------------------------------------------------------------------
# Comandos
# -----------------------------------------------------------------------------
def cmd_run(args: argparse.Namespace) -> int:
    """Ejecuta el juego en modo desktop (main.py)."""
    require_venv()
    return run_cmd([sys.executable, "main.py"])


def cmd_test(args: argparse.Namespace) -> int:
    """Ejecuta pytest sobre tests/."""
    require_venv()
    test_path = args.path if args.path else "tests/"
    return run_cmd([sys.executable, "-m", "pytest", test_path, "-v"])


def cmd_build(args: argparse.Namespace) -> int:
    """Compila el bundle WASM usando deploy/build.sh."""
    build_script = DEPLOY_DIR / "build.sh"
    if not build_script.exists():
        print("❌ deploy/build.sh no encontrado.", file=sys.stderr)
        return 1
    return run_cmd(["bash", str(build_script)])


def cmd_serve(args: argparse.Namespace) -> int:
    """Sirve build/web/ en un servidor HTTP local."""
    if not BUILD_WEB.exists():
        print(f"❌ {BUILD_WEB} no existe. Corré primero: python interpreter.py build", file=sys.stderr)
        return 1

    port = args.port
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(BUILD_WEB), **k)

    with HTTPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"🌐 Sirviendo {BUILD_WEB} en {url}")
        if args.open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Servidor detenido.")
    return 0


def cmd_deploy(args: argparse.Namespace) -> int:
    """Ejecuta deploy-s3.sh (build + sync S3 + invalidación CloudFront)."""
    deploy_script = DEPLOY_DIR / "deploy-s3.sh"
    if not deploy_script.exists():
        print("❌ deploy/deploy-s3.sh no encontrado.", file=sys.stderr)
        return 1
    return run_cmd(["bash", str(deploy_script)])


def cmd_bootstrap(args: argparse.Namespace) -> int:
    """Ejecuta bootstrap-aws.sh (crea bucket, OAC y CloudFront)."""
    bootstrap_script = DEPLOY_DIR / "bootstrap-aws.sh"
    if not bootstrap_script.exists():
        print("❌ deploy/bootstrap-aws.sh no encontrado.", file=sys.stderr)
        return 1
    return run_cmd(["bash", str(bootstrap_script)])


def cmd_clean(args: argparse.Namespace) -> int:
    """Elimina artefactos generados."""
    patterns = ["build", "__pycache__", "*.pyc", ".pytest_cache", "*.egg-info"]
    removed = 0
    for pat in patterns:
        for path in PROJECT_ROOT.rglob(pat):
            # Evitar borrar .venv si alguien lo llamó __pycache__ (improbable)
            if ".venv" in path.parts:
                continue
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                print(f"🗑️  Eliminado dir : {path.relative_to(PROJECT_ROOT)}")
                removed += 1
            elif path.is_file():
                path.unlink()
                print(f"🗑️  Eliminado file: {path.relative_to(PROJECT_ROOT)}")
                removed += 1
    if removed == 0:
        print("Nada que limpiar.")
    else:
        print(f"Limpieza completa ({removed} items).")
    return 0


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="interpreter.py",
        description="CLI / Interprete del proyecto Flappy Bird. Ejecutá 'python interpreter.py <comando> --help' para más info.",
    )
    sub = parser.add_subparsers(dest="command", required=True, help="Comando a ejecutar")

    # run
    sub.add_parser("run", help="Ejecuta el juego en modo desktop (main.py)")

    # test
    p_test = sub.add_parser("test", help="Ejecuta pytest")
    p_test.add_argument("path", nargs="?", default="tests/", help="Ruta de tests (default: tests/)")

    # build
    sub.add_parser("build", help="Compila el bundle WASM con pygbag (deploy/build.sh)")

    # serve
    p_serve = sub.add_parser("serve", help="Sirve build/web/ en un servidor HTTP local")
    p_serve.add_argument("--port", type=int, default=8000, help="Puerto (default: 8000)")
    p_serve.add_argument("--open", action="store_true", help="Abre el navegador automáticamente")

    # deploy
    sub.add_parser("deploy", help="Build + sync a S3 + invalida CloudFront (deploy/deploy-s3.sh)")

    # bootstrap
    sub.add_parser("bootstrap", help="Crea recursos AWS de una sola vez (deploy/bootstrap-aws.sh)")

    # clean
    sub.add_parser("clean", help="Elimina build/, __pycache__, *.pyc, etc.")

    return parser


COMMANDS = {
    "run": cmd_run,
    "test": cmd_test,
    "build": cmd_build,
    "serve": cmd_serve,
    "deploy": cmd_deploy,
    "bootstrap": cmd_bootstrap,
    "clean": cmd_clean,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
