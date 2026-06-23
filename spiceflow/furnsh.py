import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import spiceypy as spice

__all__ = ["download", "remote_furnsh", "validate_kernel_files"]

_REQUEST_HEADERS = {"User-Agent": "spice-flow-py/0.1.2"}
_DEFAULT_CHUNK_SIZE = 1024 * 1024
_DEFAULT_TIMEOUT_S = 600


def _normalize_kernel_url(url: str) -> str:
    if url.startswith("http://darts.isas.jaxa.jp/"):
        return "https://darts.isas.jaxa.jp/" + url[len("http://darts.isas.jaxa.jp/") :]
    return url


def _remote_content_length(url: str) -> int | None:
    request = urllib.request.Request(
        _normalize_kernel_url(url),
        method="HEAD",
        headers=_REQUEST_HEADERS,
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            length = response.headers.get("Content-Length")
            return int(length) if length else None
    except (urllib.error.URLError, ValueError, TimeoutError):
        return None


def _kernel_needs_download(path: Path, expected_size: int | None, *, force: bool) -> bool:
    if force:
        return True
    if not path.is_file():
        return True
    size = path.stat().st_size
    if size == 0:
        return True
    if expected_size is not None and size != expected_size:
        return True
    return False


def _meta_kernel_to_urls(meta_kernel, url, local_kernel_dir, remote_root):
    spice.ldpool(meta_kernel)
    path_values = spice.gcpool("PATH_VALUES", 0, 256)
    path_symbols = spice.gcpool("PATH_SYMBOLS", 0, 256)
    kernels_to_load = spice.gcpool("KERNELS_TO_LOAD", 0, 1024)

    symbols = {}
    for path_value, path_symbol in zip(path_values, path_symbols):
        symbols[f"${path_symbol}"] = path_value

    url_base = urllib.parse.urljoin(_normalize_kernel_url(url), remote_root)
    path_base = Path(local_kernel_dir)
    kernel_urls = []
    for kernel in kernels_to_load:
        resolved = kernel
        for key in symbols:
            if key in resolved:
                resolved = resolved.replace(key, symbols[key])
        remote_url = urllib.parse.urljoin(url_base, resolved)
        local_path = str(path_base / resolved)
        kernel_urls.append((remote_url, local_path))
    return kernel_urls


def validate_kernel_files(kernels) -> None:
    missing: list[str] = []
    for _url, local_path in kernels:
        path = Path(local_path)
        if not path.is_file() or path.stat().st_size == 0:
            missing.append(local_path)
    if missing:
        joined = "\n  ".join(missing)
        raise FileNotFoundError(
            "Kernel files are missing or empty after download:\n  "
            f"{joined}\n"
            "Tip: on Google Colab use a local path such as /content/flow/kernels "
            "(not Google Drive) for large SPICE archives, or pass force=True to retry."
        )


def _download_kernels(kernels, *, verbose=True, force=False):
    for kernel_url, kernel_pathname in kernels:
        path = Path(kernel_pathname)
        expected_size = _remote_content_length(kernel_url)
        if not _kernel_needs_download(path, expected_size, force=force):
            if verbose:
                print(f"skip (exists): {kernel_pathname}")
            continue

        if verbose:
            size_hint = f" ({expected_size} bytes)" if expected_size else ""
            print(f"{kernel_url} ==> {kernel_pathname}{size_hint}")

        if path.exists() and force:
            path.unlink()

        download(kernel_url, kernel_pathname, expected_size=expected_size)


def _make_new_meta_kernel(local_kernel_dir, new_pathname):
    path_values = spice.gcpool("PATH_VALUES", 0, 256)
    path_symbols = spice.gcpool("PATH_SYMBOLS", 0, 256)
    kernels_to_load = spice.gcpool("KERNELS_TO_LOAD", 0, 1024)

    s = "KPL/MK\n"
    s += "\\begindata\n"
    s += "  PATH_VALUES     = (\n"
    path_base = Path(local_kernel_dir)
    for path_value in path_values:
        s += "    '" + str(path_base / path_value) + "'\n"
    s += "  )\n"
    s += "  PATH_SYMBOLS    = (\n"
    for path_symbol in path_symbols:
        s += "    '" + path_symbol + "'\n"
    s += "  )\n"
    s += "  KERNELS_TO_LOAD = (\n"
    for kernel in kernels_to_load:
        s += "    '" + kernel + "'\n"
    s += "  )\n"
    with open(new_pathname, "w", encoding="utf-8") as handle:
        handle.write(s)


def download(
    url,
    filename,
    *,
    expected_size: int | None = None,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
    timeout: int = _DEFAULT_TIMEOUT_S,
):
    """
    Download a file from url with streaming I/O and size verification.

    Parameters
    ----------
    url : str
        Remote URL (http/https).
    filename : str
        Local destination path.
    expected_size : int, optional
        Expected byte size; verified after download when known.
    """
    url = _normalize_kernel_url(url)
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".part")

    request = urllib.request.Request(url, headers=_REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if getattr(response, "status", 200) >= 400:
                raise OSError(f"HTTP {response.status} while downloading {url}")

            header_len = response.headers.get("Content-Length")
            if expected_size is None and header_len:
                expected_size = int(header_len)

            with open(tmp_path, "wb") as handle:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    handle.write(chunk)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    size = tmp_path.stat().st_size
    if size == 0:
        tmp_path.unlink(missing_ok=True)
        raise OSError(f"empty download from {url}")

    if expected_size is not None and size != expected_size:
        tmp_path.unlink(missing_ok=True)
        raise OSError(
            f"incomplete download from {url}: got {size} bytes, expected {expected_size}"
        )

    tmp_path.replace(path)


def remote_furnsh(
    url,
    filename,
    local_kernel_dir=".",
    remote_root="../..",
    verbose=True,
    *,
    force=False,
):
    """
    Download kernels referenced by a remote meta-kernel and load them with furnsh.

    On Google Colab, prefer ``local_kernel_dir="/content/flow/kernels/SELENE"``
    instead of Google Drive paths. Large CK/SPK files (~400 MB) are unreliable
    when written directly to Drive FUSE mounts.
    """
    url = _normalize_kernel_url(url)
    mk = tempfile.NamedTemporaryFile(delete=False)
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers=_REQUEST_HEADERS),
            timeout=60,
        ) as response:
            mk.write(response.read())
        mk.close()

        kernels = _meta_kernel_to_urls(mk.name, url, local_kernel_dir, remote_root)
        _download_kernels(kernels, verbose=verbose, force=force)
        validate_kernel_files(kernels)
        _make_new_meta_kernel(local_kernel_dir, filename)
        spice.furnsh(filename)
        return filename
    finally:
        Path(mk.name).unlink(missing_ok=True)
