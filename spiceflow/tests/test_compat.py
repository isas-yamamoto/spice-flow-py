import numpy as np

from spiceflow.compat import apply_pyrender_compat, patch_numpy_for_pyrender


def test_patch_numpy_for_pyrender_provides_infty():
    patch_numpy_for_pyrender()
    assert hasattr(np, "infty")
    assert np.infty == np.inf


def test_apply_pyrender_compat_is_idempotent():
    apply_pyrender_compat()
    apply_pyrender_compat()
