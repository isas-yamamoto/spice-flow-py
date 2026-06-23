import numpy as np
import pytest


@pytest.mark.gl
def test_render_solar_object_without_model_returns_none(gl_available):
    if not gl_available:
        pytest.skip("OpenGL / OSMesa not available")

    from spiceflow.render import render_solar_object

    assert render_solar_object({"name": "SUN", "radius": [1.0]}, False) is None


@pytest.mark.gl
def test_render_solar_object_unknown_model_type_returns_none(gl_available):
    if not gl_available:
        pytest.skip("OpenGL / OSMesa not available")

    from spiceflow.render import render_solar_object

    solar_object = {
        "model": {"type": "unsupported"},
        "rotation": np.eye(3),
        "position": np.zeros(3),
        "radius": [1.0],
    }
    assert render_solar_object(solar_object, False) is None
