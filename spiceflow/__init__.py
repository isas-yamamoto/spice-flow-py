"""
https://github.com/isas-yamamoto/spice-flow-py
----------------------------------------------

SPICE Flow is a Python-based field-of-view visuallizer using SPICE technologies
for planetary explorers.
"""

from .version import __version__

_LAZY_EXPORTS = {
    "simulate": ".simulate",
    "render": ".render",
    "remote_furnsh": ".furnsh",
    "enable_headless_pyrender": ".headless",
}

__all__ = ["__version__", *_LAZY_EXPORTS]


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr = _LAZY_EXPORTS[name], name
    if module_name.startswith("."):
        import importlib

        module = importlib.import_module(module_name, __name__)
        value = getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(name)
