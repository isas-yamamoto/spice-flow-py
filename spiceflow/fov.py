import numpy as np
import spiceypy as spice
from itertools import combinations
from .flow_rect import FlowRect


class Fov:
    MAX_ROOMS = 256

    def __init__(self, inst_id):
        fov = spice.getfov(inst_id, Fov.MAX_ROOMS)
        self._shape = fov[0]
        self._frame = fov[1]
        self._boresight = fov[2]
        self._nbounds = fov[3]
        self._bounds = fov[4]

        self._bounds_rect = self._calc_bounds_rect()
        self._fovmax = self._calc_fovmax()
        self._fovy = (
            spice.vsep(self.bounds_rect.center_vec, self.bounds_rect.top_vec)
            * 2.0
            * spice.dpr()
        )
        self._aspect = self.bounds_rect.aspect

    @property
    def shape(self):
        return self._shape

    @property
    def frame(self):
        return self._frame

    @property
    def boresight(self):
        return self._boresight

    @property
    def bounds(self):
        return self._bounds

    @property
    def bounds_rect(self):
        return self._bounds_rect

    @property
    def fovmax(self):
        return self._fovmax

    @property
    def fovy(self):
        return self._fovy

    @property
    def aspect(self):
        return self._aspect

    def _calc_bounds_rect(self):
        if self._shape in ["RECTANGLE", "POLYGON"]:
            left = np.min(self._bounds[:, 0])
            top = np.min(self._bounds[:, 1])
            right = np.max(self._bounds[:, 0])
            bottom = np.max(self._bounds[:, 1])
        elif self._shape == "CIRCLE":
            dx = self._bounds[0] - self._boresight[0]
            dy = self._bounds[1] - self._boresight[1]
            r = np.sqrt(dx ** 2 + dy ** 2)
            left = self._boresight[0] - r
            top = self._boresight[1] - r
            right = self._boresight[0] + r
            bottom = self._boresight[1] + r
        elif self._shape == "ELLIPSE":
            cx = self._boresight[0]
            cy = self._boresight[1]
            left = right = cx
            top = bottom = cy
            dx = self._bounds[0] - cx
            dy = self._bounds[1] - cy
            a = np.sqrt(dx ** 2 + dy ** 2)
            t = np.arctan2(dy, dx)
            sint = np.sin(t)
            cost = np.cos(t)
            dx = self._bounds[3] - cx
            dy = self._bounds[4] - cy
            b = np.sqrt(dx ** 2 + dy ** 2)
            for i in range(90):
                rad = np.radians(i)
                tx = a * np.cos(rad)
                ty = b * np.sin(rad)
                x = tx * cost - ty * sint + cx
                y = tx * sint + ty * cost + cy
                right = max(x, right)
                bottom = max(y, bottom)
            left = right - (right - cx) * 2
            top = bottom - (bottom - cy) * 2
        else:
            raise ValueError(
                "Unknown instrument shape {}".format(self._shape)
            )
        return FlowRect(
            left, top, right, bottom, self._bounds[0, 2], f"({self._frame})"
        )

    def _calc_fovmax(self):
        fovmax = -1.0
        if self._shape in ["RECTANGLE", "POLYGON"]:
            fovmax = -1.0
            for i, j in combinations(range(len(self._bounds)), 2):
                dist = spice.vsep(self._bounds[i], self._bounds[j]) * 0.5
                if dist > fovmax:
                    fovmax = dist
        elif self._shape == "CIRCLE":
            fovmax = spice.vsep(self._boresight, self._bounds[0])
        elif self._shape == "ELLIPSE":
            dist1 = spice.vsep(self._boresight, self._bounds[0])
            dist2 = spice.vsep(self._boresight, self._bounds[1])
            fovmax = dist1 if dist1 > dist2 else dist1
        return fovmax
