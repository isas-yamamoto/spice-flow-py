from pathlib import Path

from spiceflow.furnsh import _kernel_needs_download, _normalize_kernel_url


def test_normalize_kernel_url_upgrades_darts_http():
    url = "http://darts.isas.jaxa.jp/pub/pds3/example.tm"
    assert _normalize_kernel_url(url).startswith("https://darts.isas.jaxa.jp/")


def test_kernel_needs_download_missing_file(tmp_path: Path):
    path = tmp_path / "kernel.bsp"
    assert _kernel_needs_download(path, 100, force=False) is True


def test_kernel_needs_download_empty_file(tmp_path: Path):
    path = tmp_path / "kernel.bsp"
    path.write_bytes(b"")
    assert _kernel_needs_download(path, None, force=False) is True


def test_kernel_needs_download_size_mismatch(tmp_path: Path):
    path = tmp_path / "kernel.bsp"
    path.write_bytes(b"abc")
    assert _kernel_needs_download(path, 10, force=False) is True


def test_kernel_needs_download_skip_when_complete(tmp_path: Path):
    path = tmp_path / "kernel.bsp"
    path.write_bytes(b"12345")
    assert _kernel_needs_download(path, 5, force=False) is False


def test_kernel_needs_download_force(tmp_path: Path):
    path = tmp_path / "kernel.bsp"
    path.write_bytes(b"12345")
    assert _kernel_needs_download(path, 5, force=True) is True
