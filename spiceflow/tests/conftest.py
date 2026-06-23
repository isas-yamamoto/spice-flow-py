import os

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "gl: requires OSMesa / OpenGL")


@pytest.fixture(scope="session")
def gl_available():
    os.environ.setdefault("PYOPENGL_PLATFORM", "osmesa")
    try:
        from spiceflow.headless import enable_headless_pyrender

        enable_headless_pyrender()
        import pyrender  # noqa: F401

        return True
    except ImportError:
        return False
