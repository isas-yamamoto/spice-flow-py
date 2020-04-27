import urllib.request
import urllib.parse
import tempfile
import spiceypy as spice
from pathlib import Path


__all__ = ["download", "remote_furnsh"]


def _meta_kernel_to_urls(meta_kernel, url, local_kernel_dir, remote_root):
    spice.ldpool(meta_kernel)
    path_values = spice.gcpool("PATH_VALUES", 0, 256)
    path_symbols = spice.gcpool("PATH_SYMBOLS", 0, 256)
    kernels_to_load = spice.gcpool("KERNELS_TO_LOAD", 0, 1024)

    symbols = {}
    for path_value, path_symbol in zip(path_values, path_symbols):
        symbols[f"${path_symbol}"] = path_value

    url_base = urllib.parse.urljoin(url, remote_root)
    path_base = Path(local_kernel_dir)
    kernel_urls = []
    for kernel in kernels_to_load:
        for key in symbols:
            if key in kernel:
                kernel = kernel.replace(key, symbols[key])
        remote_url = urllib.parse.urljoin(url_base, kernel)
        local_path = str(path_base / kernel)
        kernel_urls.append((remote_url, local_path))
    return kernel_urls


def _download_kernels(kernels, verbose=True):
    for kernel_url, kernel_pathname in kernels:
        if verbose is True:
            print("{} ==> {}".format(kernel_url, kernel_pathname))
        p = Path(kernel_pathname)
        if not p.exists():
            if not p.parent.exists():
                p.parent.mkdir(parents=True)
            download(kernel_url, kernel_pathname)


def _make_new_meta_kernel(kernels, local_kernel_dir, new_pathname):
    path_values = spice.gcpool("PATH_VALUES", 0, 256)
    path_symbols = spice.gcpool("PATH_SYMBOLS", 0, 256)
    kernels_to_load = spice.gcpool("KERNELS_TO_LOAD", 0, 1024)

    s = "KPL/MK\n"
    s += "\\begindata\n"
    # PATH_VALUES
    s += "  PATH_VALUES     = (\n"
    path_base = Path(local_kernel_dir)
    for path_value in path_values:
        s += "    '" + str(path_base / path_value) + "'\n"
    s += "  )\n"
    # PATH_SYMBOLS
    s += "  PATH_SYMBOLS    = (\n"
    for path_symbol in path_symbols:
        s += "    '" + path_symbol + "'\n"
    s += "  )\n"
    # KERNELS_TO_LOAD
    s += "  KERNELS_TO_LOAD = (\n"
    for kernel in kernels_to_load:
        s += "    '" + kernel + "'\n"
    s += "  )\n"
    with open(new_pathname, "w") as f:
        f.write(s)


def download(url, filename):
    """
    download a file from url

    Parameters
    ----------
    url : str
        the url of the request
    filename : str
        local filename
    """
    with urllib.request.urlopen(url) as response:
        with open(filename, "wb+") as f:
            f.write(response.read())


def remote_furnsh(
    url, filename, local_kernel_dir=".", remote_root="../..", verbose=True
):
    mk = tempfile.NamedTemporaryFile(delete=False)
    with urllib.request.urlopen(url) as response:
        content = response.read()
        mk.write(content)
    mk.close()
    kernels = _meta_kernel_to_urls(
        mk.name, url, local_kernel_dir, remote_root
    )
    _download_kernels(kernels, verbose)
    _make_new_meta_kernel(kernels, local_kernel_dir, filename)
    Path(mk.name).unlink()
    spice.furnsh(filename)
