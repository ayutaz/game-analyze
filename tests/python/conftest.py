"""Shared test configuration for Python tests.

This module is imported automatically by pytest (if pytest is installed) and is
also safe to import explicitly from unittest test modules via:

    from tests.python import conftest  # noqa: F401

Its purpose is to make repository-internal modules importable regardless of how
the test runner is invoked. In particular it:

1. Adds the repository root to ``sys.path`` so ``import scripts.build_aggregate``
   style imports work even though ``scripts/`` has no ``__init__.py`` (the
   ``scripts`` directory is registered as a namespace package on the path).
2. Adds the ``scripts/`` directory itself to ``sys.path`` so individual modules
   can also be imported flatly, e.g. ``import build_aggregate``.
3. Exposes ``REPO_ROOT``, ``SCRIPTS_DIR``, and ``DATA_DIR`` constants that
   individual tests may use to locate fixtures / data files.
4. Provides a small ``load_script_module(name)`` helper backed by
   ``importlib.util`` for tests that prefer explicit, isolated loading rather
   than relying on ``sys.path`` injection.

Tests should *not* mutate global state (e.g. ``os.chdir``); use absolute paths
derived from these constants instead.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
# tests/python/conftest.py  ->  parents[2] == repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]
SCRIPTS_DIR: Path = REPO_ROOT / "scripts"
DATA_DIR: Path = REPO_ROOT / "data"
GAMES_DIR: Path = DATA_DIR / "games"
ANALYSES_DIR: Path = DATA_DIR / "analyses"
SITE_DIR: Path = REPO_ROOT / "site"

# ---------------------------------------------------------------------------
# sys.path setup
# ---------------------------------------------------------------------------
# Make `from scripts import build_aggregate` work (namespace package style,
# because scripts/ has no __init__.py).
_repo_root_str = str(REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

# Make `import build_aggregate` work too, for tests that prefer flat imports.
_scripts_dir_str = str(SCRIPTS_DIR)
if _scripts_dir_str not in sys.path:
    sys.path.insert(0, _scripts_dir_str)


# ---------------------------------------------------------------------------
# Explicit loader (for tests that don't want to rely on sys.path)
# ---------------------------------------------------------------------------
def load_script_module(name: str) -> ModuleType:
    """Load a module from ``scripts/<name>.py`` via importlib.util.

    Returns a freshly-loaded module object. Useful when a test wants a clean
    instance of the module without sys.path side-effects.
    """
    path = SCRIPTS_DIR / f"{name}.py"
    if not path.exists():
        raise FileNotFoundError(f"No such script module: {path}")
    spec = importlib.util.spec_from_file_location(f"scripts_{name}", path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"Could not build import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


__all__ = [
    "REPO_ROOT",
    "SCRIPTS_DIR",
    "DATA_DIR",
    "GAMES_DIR",
    "ANALYSES_DIR",
    "SITE_DIR",
    "load_script_module",
]
