# Changelog

All notable changes to this project are documented in this file.

## [0.1.3] - 2026-06-23

### Fixed

- Lazy-import `pyrender` so `enable_colab_render()` can run before OpenGL loads
- Colab: install EGL/GL apt packages, try `egl` then `osmesa`, smoke-test `OffscreenRenderer`
- Pin `PyOpenGL>=3.1.5` via `requirements-colab.txt` (Colab `--no-deps` install path)
- Delete `OffscreenRenderer` after use in `render()`

### Added

- `install_colab_gl_packages()` and clearer errors when Colab GL setup fails

## [0.1.2] - 2026-06-23

### Fixed

- `remote_furnsh` / `download`: stream large kernels in chunks instead of loading into memory
- Re-download kernels when file is missing, empty, or size mismatches `Content-Length`
- Upgrade DARTS `http://` URLs to `https://` automatically
- Validate all kernel files exist before `spice.furnsh` with a clearer error message
- Added `force=True` option to `remote_furnsh` to retry failed/partial downloads

### Added

- `validate_kernel_files()` helper
- Colab README guidance: use `/content/...` instead of Google Drive for large kernels

## [0.1.1] - 2026-06-23

### Added

- `spiceflow.compat.apply_pyrender_compat()` — NumPy 2.x shim (`np.infty`) applied before pyrender import
- `enable_colab_render()` for Google Colab (EGL + NumPy compatibility)
- README section for Colab install

### Fixed

- Removed `numpy<2.0` pin so Colab/JAX/OpenCV stacks are not broken by install
- Relaxed `networkx==3.5` to `networkx>=3.5`
- Dropped explicit `PyOpenGL` dependency (let `pyrender` resolve it; avoids fighting Colab's PyOpenGL)

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

[0.1.3]: https://github.com/isas-yamamoto/spice-flow-py/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/isas-yamamoto/spice-flow-py/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/isas-yamamoto/spice-flow-py/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/isas-yamamoto/spice-flow-py/compare/v0.0.1...v0.1.0
