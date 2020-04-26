import itertools
import numpy as np
import spiceypy as spice
from .transform import viewport_frustum
from .util import vec_padist


def search_stars(obsinfo, mag_limit=7.0):
    query = (
        "SELECT"
        " CATALOG_NUMBER,RA,DEC,VISUAL_MAGNITUDE,PARLAX,SPECTRAL_TYPE"
        " FROM HIPPARCOS"
    )
    nmrows, _error, _errmsg = spice.ekfind(query)
    stars = []
    for row in range(nmrows):
        ra = spice.ekgd(1, row, 0)[0] * spice.rpd()
        dec = spice.ekgd(2, row, 0)[0] * spice.rpd()
        mag = spice.ekgd(3, row, 0)[0]
        vec = spice.radrec(1.0, ra, dec)
        tvec = spice.mxv(obsinfo.ref2obsmtx, vec)
        _tpa, tdist = vec_padist(obsinfo.center, tvec)
        if tdist < obsinfo.fov.fovmax and mag < mag_limit:
            parallax = spice.ekgd(4, row, 0)[0]
            spectral = spice.ekgc(5, row, 0)[0]
            distance = 1.0 / np.tan(parallax * spice.rpd())
            distance = spice.convrt(distance, "AU", "km")
            pos = tvec * distance
            vp = viewport_frustum(
                obsinfo.fov.bounds_rect, obsinfo.width, obsinfo.height, pos
            )
            star = {
                "hip_id": spice.ekgi(0, row, 0)[0],
                "position": tvec,
                "ra": ra,
                "dec": dec,
                "spectral_type": spectral,
                "visual_magnitude": mag,
                "distance": distance,
                "image_pos": vp[0:2],
                "color": get_star_color(spectral),
            }
            stars.append(star)
    return stars


def get_star_color(spectral):
    """ Obtain RGB values from the spectral type of a star """

    rgb = {
        "O": (128, 128, 255),
        "W": (128, 128, 255),  # Wolf-Rayet
        "B": (160, 160, 255),
        "A": (192, 192, 255),
        "F": (224, 224, 255),
        "G": (255, 192, 192),
        "K": (255, 160, 160),
        "k": (255, 160, 160),
        "R": (255, 160, 160),
        "M": (255, 128, 128),
        "N": (255, 128, 128),
        "S": (255, 128, 128),
        "s": (255, 128, 128),
        "C": (255, 128, 128),  # carbon star
    }

    color = rgb["G"]  # default

    type = spectral[0]
    if type == "(" or type == "D":
        type = spectral[1]

    if type in rgb:
        color = rgb[type]

    return color


_star_map = [
    [
        [0x00, 0x00, 0x99, 0x99, 0x00, 0x00],
        [0x00, 0xCC, 0xFF, 0xFF, 0xCC, 0x00],
        [0x99, 0xFF, 0xFF, 0xFF, 0xFF, 0x99],
        [0x99, 0xFF, 0xFF, 0xFF, 0xFF, 0x99],
        [0x00, 0xCC, 0xFF, 0xFF, 0xCC, 0x00],
        [0x00, 0x00, 0x99, 0x99, 0x00, 0x00],
    ],
    [
        [0x00, 0x99, 0xFF, 0x99, 0x00],
        [0x99, 0xFF, 0xFF, 0xFF, 0x99],
        [0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
        [0x99, 0xFF, 0xFF, 0xFF, 0x99],
        [0x00, 0x99, 0xFF, 0x99, 0x00],
    ],
    [
        [0x00, 0xCC, 0xCC, 0x00],
        [0xCC, 0xFF, 0xFF, 0xCC],
        [0xCC, 0xFF, 0xFF, 0xCC],
        [0x00, 0xCC, 0xCC, 0x00],
    ],
    [[0x99, 0xFF, 0x99], [0xFF, 0xFF, 0xFF], [0x99, 0xFF, 0x99]],
    [[0x00, 0xCC, 0x00], [0xCC, 0xFF, 0xCC], [0x00, 0xCC, 0x00]],
    [[0x00, 0x99, 0x00], [0x99, 0xFF, 0x99], [0x00, 0x99, 0x00]],
    [[0xFF]],
    [[0x99]],
]


def star_texture(pos_x, pos_y, mag, color, width, height):
    mag_idx = np.clip(int(np.floor(mag + 0.5)), 0, 7)
    img = np.zeros(shape=(height, width, 4), dtype=np.uint8)
    star = _star_map[mag_idx]
    d = len(star)
    cx = -d / 2
    cy = -d / 2
    for x, y in itertools.product(range(d), range(d)):
        px = int(pos_x + cx + x)
        py = int(pos_y + cy + y)
        if px >= 0 and px < width and py >= 0 and py < height:
            img[py, px, 0:3] = np.array(color) * star[x][y] / 255.0
    return img
