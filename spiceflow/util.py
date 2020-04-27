import numpy as np
import spiceypy as spice


def vec_padist(vec1, vec2):
    """
    Calculate position angle

    Parameters
    ----------
    vec1 : numpy.ndarray
        position vector of target 1
    vec2 : numpy.ndarray
        position vector of target 2

    Returns
    -------
    pa : float
        position angle in radians
    dist : float
        great-circle distance in radians
    """
    _, ra1, dec1 = spice.recrad(vec1)
    _, ra2, dec2 = spice.recrad(vec2)
    d_ra = ra2 - ra1
    d_dec = dec2 - dec1

    pa = np.arctan2(
        np.cos(dec2) * np.sin(d_ra),
        (
            np.cos(dec1) * np.sin(dec2)
            - np.sin(dec1) * np.cos(dec2) * np.cos(d_ra)
        ),
    )
    if pa < 0.0:
        pa += spice.twopi()

    sda = np.sin(d_ra / 2)
    sdd = np.sin(d_dec / 2)
    dist = np.sqrt(sdd ** 2 + np.cos(dec1) * np.cos(dec2) * sda ** 2)
    dist = np.arcsin(dist) * 2
    return pa, dist


def get_object_type(object_id):
    """
    Obtain object type

    Parameters
    ----------
    object_id : int
        object identifier

    Returns
    -------
    object_type : str
        type of object
    """
    # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html
    if object_id < -100000:
        # artificial satellite (earth orbitting spacecraft)
        return "ASAT"
    elif object_id < 0:
        # spacecraft or instrument
        return "SPACECRAFT"
    elif object_id < 10:
        # Required size for System barycenter
        return "BARYCENTER"
    elif object_id == 10:
        # sun
        return "SUN"
    elif object_id < 100:
        # invalid (11...99)
        return "INVALID"
    elif (object_id % 100) == 99:
        # planet (199, 299, ...)
        return "PLANET"
    elif (object_id % 100) == 0:
        # invalid (100, 200, ...)
        return "INVALID"
    elif object_id < 100000:
        # satellite (PXX, PNXXX, 1<=P<=9, N=0,5)
        return "SATELLITE"
    else:
        # comets, asteroids or other objects
        return "SMALL_BODY"
