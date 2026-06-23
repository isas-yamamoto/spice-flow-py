"""Headless pyrender setup for servers and Docker (OSMesa)."""

from __future__ import annotations

import os
import sys
import types


def _patch_osmesa() -> None:
    os.environ.setdefault("PYOPENGL_PLATFORM", "osmesa")
    try:
        import OpenGL.osmesa as osmesa
    except ImportError:
        return

    if hasattr(osmesa, "OSMesaCreateContextAttribs"):
        return

    def osmesa_create_context_attribs(attrs, share):  # noqa: ANN001
        fmt = osmesa.OSMESA_RGBA
        if attrs:
            for index in range(0, len(attrs) - 1, 2):
                if attrs[index] == osmesa.OSMESA_FORMAT:
                    fmt = attrs[index + 1]
                    break
        return osmesa.OSMesaCreateContextExt(fmt, 24, share)

    osmesa.OSMesaCreateContextAttribs = osmesa_create_context_attribs


def _patch_numpy_for_pyrender() -> None:
    # pyrender still references np.infty, removed in NumPy 2.0.
    import numpy as np

    if not hasattr(np, "infty"):
        np.infty = np.inf


def enable_headless_pyrender() -> None:
    """Configure OSMesa and stubs so pyrender works without a display."""
    _patch_numpy_for_pyrender()
    _patch_osmesa()
    if "pyrender.viewer" in sys.modules:
        return

    viewer_stub = types.ModuleType("pyrender.viewer")

    class Viewer:  # noqa: D101 - headless stub for pyrender
        pass

    viewer_stub.Viewer = Viewer
    sys.modules["pyrender.viewer"] = viewer_stub
