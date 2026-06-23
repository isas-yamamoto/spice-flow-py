# spice-flow-py

Field-of-view visualizer for planetary missions, built on [SPICE](https://naif.jpl.nasa.gov/naif/) (NASA/JPL/NAIF) via [SpiceyPy](https://github.com/AndrewAnnex/SpiceyPy).

Related project: [spice-flow-web](https://github.com/isas-yamamoto/spice-flow-web) — web UI and mission configuration on top of this library.

## Features

- Instrument field-of-view geometry from SPICE kernels
- Solar-system body and Hipparcos star search inside the FOV
- GPU / offscreen rendering to a NumPy RGBA image (`pyrender`)
- Remote meta-kernel fetch helper (`remote_furnsh`)

## Requirements

- Python 3.10+
- SPICE kernels (meta kernel + SPK, FK, IK, etc.)
- For headless servers: OSMesa and `libosmesa6` (see below)

## Install

```bash
pip install "git+https://github.com/isas-yamamoto/spice-flow-py.git@v0.1.0"
```

Development install:

```bash
git clone https://github.com/isas-yamamoto/spice-flow-py.git
cd spice-flow-py
pip install -e ".[dev]"
```

NumPy must stay below 2.0 for compatibility with `pyrender==0.1.45`.

## Quick start

```python
import spiceypy as spice
from spiceflow import simulate, render
from spiceflow.headless import enable_headless_pyrender

enable_headless_pyrender()  # required on servers without a display

spice.furnsh("/path/to/meta_kernel.tm")

obsinfo = simulate(
    inst="MY_INSTRUMENT",
    et=spice.utc2et("2020-01-01T00:00:00"),
    abcorr="LT+S",
    obsrvr="SPACECRAFT",
    width=512,
    height=512,
    mag_limit=7.0,
)

# Attach simple sphere textures before rendering (see spice-flow-web for catalog helpers)
for body in obsinfo.solar_objects:
    body["model"] = {
        "type": "texture-body",
        "file": f"/path/to/textures/{body['name'].lower()}.png",
    }

image = render(obsinfo)
print(image.shape)  # (height, width, 4)
```

## Headless rendering

On Linux servers or in Docker, set OSMesa before importing `pyrender`:

```python
from spiceflow.headless import enable_headless_pyrender

enable_headless_pyrender()
```

System packages (Debian/Ubuntu example):

```bash
apt-get install -y libgl1 libosmesa6 libosmesa6-dev
export PYOPENGL_PLATFORM=osmesa
```

[spice-flow-web](https://github.com/isas-yamamoto/spice-flow-web) uses the same pattern in its application bootstrap.

## API overview

| Symbol | Description |
|--------|-------------|
| `simulate(...)` | Build an `ObsInfo` (geometry, stars, solar objects) |
| `render(obsinfo, ...)` | Render RGBA image with pyrender |
| `remote_furnsh(url, path)` | Download kernels referenced by a remote meta kernel |
| `enable_headless_pyrender()` | OSMesa + pyrender stubs for headless use |

## Tests

```bash
pip install -e ".[dev]"
pytest -m "not integration"
```

Integration tests (network + SPICE download):

```bash
pytest -m integration
```

## License

MIT — see [LICENSE](LICENSE).
