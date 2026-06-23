"""Headless pyrender setup for servers and Docker (OSMesa)."""

from __future__ import annotations

import os
import sys

from .compat import apply_pyrender_compat, patch_pyrender_viewer_stub


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


def enable_headless_pyrender() -> None:
    """Configure OSMesa and stubs so pyrender works without a display."""
    apply_pyrender_compat()
    _patch_osmesa()
    patch_pyrender_viewer_stub()
