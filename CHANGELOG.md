# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-06-23

### Added

- `spiceflow.headless.enable_headless_pyrender()` for OSMesa / server-side rendering
- `spiceflow.render_util.bg_color_rgba()` helper (testable without pyrender)
- Lazy imports in `spiceflow` package `__init__` (avoids loading pyrender on `import spiceflow`)
- `pyproject.toml` with dev dependencies (`pytest`)
- GitHub Actions CI (unit tests without network)
- Unit tests for `render` helpers and `FlowRect` import path

### Fixed

- `render()` no longer mutates the caller's `bg_color` list via `append`
- `render()` skips solar objects that have no renderable `model` (avoids unpack crash)
- `render_solar_object()` returns `None` when `model` is missing or has an unknown type
- Directional light pose handles zero-length `obsinfo.pos`
- `test_flow_rect` updated for current `FlowRect` API (`center_vec`, absolute `height`)

### Changed

- Version bumped from `0.0.1` to `0.1.0`
- `setup.py` reads version from `spiceflow/version.py`
- README expanded with install, usage, and headless notes

[0.1.0]: https://github.com/isas-yamamoto/spice-flow-py/compare/v0.0.1...v0.1.0
