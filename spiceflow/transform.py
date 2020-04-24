import numpy as np


def viewport_frustum(rect, width, height, v):
    """
    Get corresponding point on viewport

    rect : FlowRect
        FOV rectangle
    width : int
        scale width
    height : int
        scale height
    v : numpy.ndarray
        a point on window

    Returns
    -------
    point : numpy.ndarray
        correspondhing point on viewport
    """
    return np.array(
        [
            (rect.z / v[2] * v[0] - rect.left) * width / rect.width,
            (rect.z / v[2] * v[1] - rect.top) * height / rect.height,
            v[2],
        ]
    )


def viewport_ortho(rect, width, height, v):
    """
    Get corresponding point on viewport

    rect : FlowRect
        view port screen rectangle
    width : int
        scale width
    height : int
        scale height
    v : numpy.ndarray
        a point on window

    Returns
    -------
    point : numpy.ndarray
        correspondhing point on viewport
    """
    return np.array(
        [
            (v[0] - rect.left) * width / rect.width,
            (v[1] - rect.top) * height / rect.height,
            v[2],
        ]
    )
