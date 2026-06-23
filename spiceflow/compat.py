"""Runtime compatibility shims (NumPy 2.x, pyrender on Colab/notebooks)."""

from __future__ import annotations

import os
import sys
import types

_compat_applied = False


def patch_numpy_for_pyrender() -> None:
    """pyrender 0.1.45 still references np.infty, removed in NumPy 2.0."""
    import numpy as np

    if not hasattr(np, "infty"):
        np.infty = np.inf


def patch_pyrender_viewer_stub() -> None:
    """Avoid importing pyrender.viewer (needs a display) on headless hosts."""
    if "pyrender.viewer" in sys.modules:
        return

    viewer_stub = types.ModuleType("pyrender.viewer")

    class Viewer:  # noqa: D101 - headless stub for pyrender
        pass

    viewer_stub.Viewer = Viewer
    sys.modules["pyrender.viewer"] = viewer_stub


def apply_pyrender_compat() -> None:
    global _compat_applied
    if _compat_applied:
        return
    patch_numpy_for_pyrender()
    _compat_applied = True


def enable_colab_render() -> None:
    """Prepare pyrender on Google Colab (keeps Colab's NumPy 2.x)."""
    apply_pyrender_compat()
    if "COLAB_RELEASE_TAG" in os.environ:
        os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
