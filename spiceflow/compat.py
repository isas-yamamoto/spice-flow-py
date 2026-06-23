"""Runtime compatibility shims (NumPy 2.x, pyrender on Colab/notebooks)."""

from __future__ import annotations

import os
import subprocess
import sys
import types
import warnings

_compat_applied = False
_colab_platform: str | None = None


def is_colab() -> bool:
    return "COLAB_RELEASE_TAG" in os.environ


def opengl_already_imported() -> bool:
    return "OpenGL" in sys.modules or "pyrender" in sys.modules


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


def install_colab_gl_packages() -> None:
    """Install EGL/GL system libraries on Google Colab."""
    if not is_colab():
        return
    subprocess.run(["apt-get", "update", "-qq"], check=False)
    subprocess.run(
        [
            "apt-get",
            "install",
            "-y",
            "-qq",
            "libegl1",
            "libgles2",
            "libgl1",
            "libosmesa6",
        ],
        check=False,
    )


def _configure_pyopengl_platform(platform: str) -> None:
    os.environ["PYOPENGL_PLATFORM"] = platform


def _smoke_test_offscreen_renderer() -> None:
    patch_pyrender_viewer_stub()
    import pyrender

    renderer = pyrender.OffscreenRenderer(64, 64)
    try:
        scene = pyrender.Scene()
        renderer.render(scene)
    finally:
        renderer.delete()


def enable_colab_render(*, install_system_packages: bool = True) -> str:
    """
    Prepare pyrender on Google Colab.

    Call this before the first ``render()`` / ``OffscreenRenderer`` use.
    Returns the OpenGL platform that succeeded (``'egl'`` or ``'osmesa'``).

    On Colab, also install with a recent PyOpenGL (pyrender pins 3.1.0)::

        !pip install pyrender==0.1.45 --no-deps
        !pip install "PyOpenGL>=3.1.5" freetype-py pyglet imageio
    """
    global _colab_platform
    if _colab_platform is not None:
        return _colab_platform

    apply_pyrender_compat()

    if opengl_already_imported():
        warnings.warn(
            "OpenGL/pyrender was already imported before enable_colab_render(). "
            "Use Runtime → Restart session, reinstall packages, then call "
            "enable_colab_render() before rendering.",
            RuntimeWarning,
            stacklevel=2,
        )

    if install_system_packages and is_colab():
        install_colab_gl_packages()

    patch_pyrender_viewer_stub()

    errors: list[str] = []
    platforms = ("egl", "osmesa")
    if not is_colab():
        platforms = ("osmesa", "egl")

    for platform in platforms:
        try:
            _configure_pyopengl_platform(platform)
            _smoke_test_offscreen_renderer()
            _colab_platform = platform
            if is_colab():
                print(f"spice-flow: using PYOPENGL_PLATFORM={platform}")
            return platform
        except Exception as exc:
            errors.append(f"{platform}: {exc!r}")

    raise RuntimeError(
        "pyrender OffscreenRenderer failed. Try restarting the runtime, then:\n"
        "  !pip install pyrender==0.1.45 --no-deps\n"
        '  !pip install "PyOpenGL>=3.1.5" freetype-py pyglet imageio\n'
        "  from spiceflow import enable_colab_render\n"
        "  enable_colab_render()\n"
        "Details:\n  " + "\n  ".join(errors)
    )


# Backwards-compatible alias used by lazy exports.
