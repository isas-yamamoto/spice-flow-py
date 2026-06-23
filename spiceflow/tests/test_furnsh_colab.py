from spiceflow.furnsh import _warn_colab_drive_path


def test_warn_colab_drive_path_on_colab(monkeypatch):
    monkeypatch.setenv("COLAB_RELEASE_TAG", "test")
    import warnings

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _warn_colab_drive_path("/content/drive/My Drive/flow/kernels/SELENE")
    assert any("Google Drive" in str(item.message) for item in caught)


def test_no_warn_for_content_path(monkeypatch):
    monkeypatch.setenv("COLAB_RELEASE_TAG", "test")
    import warnings

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _warn_colab_drive_path("/content/flow/kernels/SELENE")
    assert not caught
