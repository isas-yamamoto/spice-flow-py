import numpy as np
import spiceypy as spice
from .transform import viewport_frustum
from .util import get_object_type


OBJECT_ID_SUN = 10
OBJECT_ID_MOON = 301
OBJECT_ID_MERCURY = 199
OBJECT_ID_VENUS = 299
OBJECT_ID_EARTH = 399
OBJECT_ID_MARS = 499
OBJECT_ID_JUPITER = 599
OBJECT_ID_SATURN = 699
OBJECT_ID_URANUS = 799
OBJECT_ID_NEPTUNE = 899
OBJECT_ID_PLUTO = 999


def search_solar_objects(obsinfo):
    solar_objects = []
    count = spice.ktotal("spk")
    for which in range(count):
        filename, _filetype, _source, _handle = spice.kdata(which, "spk")
        ids = spice.spkobj(filename)
        for i in range(spice.card(ids)):
            obj = ids[i]
            target = spice.bodc2n(obj)
            if is_target_in_fov(
                obsinfo.inst,
                target,
                obsinfo.et,
                obsinfo.abcorr,
                obsinfo.obsrvr,
            ):
                solar_objects.append(get_solar_object(obsinfo, obj, target))
    return solar_objects


def get_planet_magnitude(object_id, pos_planet, pos_basis):
    """ Planet and Moon magnitudes """

    planet_abs_mag = {
        199: -0.42,  # OBJECT_ID_MERCURY
        299: -4.40,  # OBJECT_ID_VENUS
        399: -2.96,  # OBJECT_ID_EARTH
        499: -1.52,  # OBJECT_ID_MARS
        599: -9.40,  # OBJECT_ID_JUPITER
        699: -8.68,  # OBJECT_ID_SATURN
        799: -7.19,  # OBJECT_ID_URANUS
        899: -6.87,  # OBJECT_ID_NEPTUNE
        999: -1.00,  # OBJECT_ID_PLUTO
    }

    # distance between each objects in AU
    d_planet_basis = spice.vdist(pos_planet, pos_basis)
    d_planet_basis = spice.convrt(d_planet_basis, "km", "AU")
    d_planet_sun = spice.vnorm(pos_planet)
    d_planet_sun = spice.convrt(d_planet_sun, "km", "AU")
    d_sun_basis = spice.vnorm(pos_basis)
    d_sun_basis = spice.convrt(d_sun_basis, "km", "AU")

    if object_id == OBJECT_ID_SUN:
        return -27.3 + 5.0 * np.log10(d_sun_basis)
    elif object_id == OBJECT_ID_MOON:
        return 0.38
    elif object_id in [
        OBJECT_ID_MERCURY,
        OBJECT_ID_VENUS,
        OBJECT_ID_EARTH,
        OBJECT_ID_MARS,
        OBJECT_ID_JUPITER,
        OBJECT_ID_SATURN,
        OBJECT_ID_URANUS,
        OBJECT_ID_NEPTUNE,
        OBJECT_ID_PLUTO,
    ]:
        pass
    else:
        return None

    mag = planet_abs_mag[object_id]
    mag += 5.0 * np.log10(d_planet_basis * d_planet_sun)

    if object_id <= OBJECT_ID_JUPITER:
        pa = 0.0
        tpa = (d_planet_sun ** 2 + d_planet_basis ** 2 - d_sun_basis) / (
            2.0 * d_planet_sun * d_planet_basis
        )
        tpa = np.clip(tpa, -1.0, 1.0)
        pa = np.degrees(np.arccos(tpa))

        if object_id == OBJECT_ID_MERCURY:
            mag += (0.0380 - 0.000273 * pa + 0.000002 * pa * pa) * pa
        elif object_id == OBJECT_ID_VENUS:
            mag += (0.0009 + 0.000239 * pa - 0.00000065 * pa * pa) * pa
        elif object_id == OBJECT_ID_MARS:
            mag += 0.016 * pa
        elif object_id == OBJECT_ID_JUPITER:
            mag += 0.005 * pa
    elif object_id == OBJECT_ID_SATURN:
        mag -= 1.1 * 0.3
    return mag


def get_orientation_matrix(obsinfo, target, object_id):
    iau_frame = f"IAU_{target}"
    frcode = spice.namfrm(iau_frame)
    if frcode == 0:
        frame_name = f"FRAME_{object_id}_NAME"
        _n, iau_frame = spice.gcpool(frame_name, 0, 1)
        frcode = spice.namfrm(iau_frame)
    mtx = spice.pxform(iau_frame, obsinfo.fov.frame, obsinfo.et)
    # rot = get_boresight_rotation_matrix(obsinfo['boresight'])
    # return spice.mxm(rot, mtx)
    return mtx


def is_target_in_fov(inst_name, target, et, abcorr, obsrvr):
    cnfine = spice.cell_double(4)
    spice.wninsd(et, et + 1, cnfine)
    step = 1
    tframe = f"IAU_{target}"
    try:
        results = spice.gftfov(
            inst_name,
            target,
            "ELLIPSOID",
            tframe,
            abcorr,
            obsrvr,
            step,
            cnfine,
        )
    except spice.utils.support_types.SpiceyError:
        return False
    return True if spice.card(results) > 0 else False


def get_solar_object(obsinfo, naif_id, target):
    # magnitude
    target_from_sun_j2000, _ = spice.spkpos(
        target, obsinfo.et, "J2000", "LT+S", "SUN"
    )
    obsrvr_from_sun_j2000, _ = spice.spkpos(
        obsinfo.obsrvr, obsinfo.et, "J2000", "LT+S", "SUN"
    )
    mag = get_planet_magnitude(
        naif_id, target_from_sun_j2000, obsrvr_from_sun_j2000
    )

    # target position on instrument frame
    target_from_obsrvr, lt = spice.spkpos(
        target, obsinfo.et, obsinfo.fov.frame, obsinfo.abcorr, obsinfo.obsrvr
    )

    # radii
    radii = spice.gdpool(f"BODY{naif_id}_RADII", 0, 3)

    # orientation matrix
    mtx = get_orientation_matrix(obsinfo, target, naif_id)

    vp = viewport_frustum(
        obsinfo.fov.bounds_rect,
        obsinfo.width,
        obsinfo.height,
        target_from_obsrvr,
    )

    return {
        "naif_id": naif_id,
        "name": target,
        "type": get_object_type(naif_id),
        "position": target_from_obsrvr,
        "magnitude": mag,
        "distance": lt * spice.clight(),
        "radius": radii,
        "rotation": mtx,
        "image_pos": vp[0:2],
    }
