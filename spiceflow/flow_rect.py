import numpy as np


class FlowRect:
    """
    Rectangle with z-depth

    The rectangle is defined on the XY-plane in a right-handed coordinate
    system. The four points of the rectangle are defined as position vectors:
        Upper Left:  (left , top,    z)
        Upper Right: (right, top,    z)
        Lower Left:  (left , bottom, z)
        Lower Right: (right, bottom, z)

    The default coordinate on 3D is in the followings:

    X------------------> +X
    |   +-----------+  top
    |   |           |
    |   |           |
    |   |           |
    |   +-----------+  bottom
    | left        right
    V
    +Y

    The +X direction is from 'left' to 'right', and the +Y direction is from
    'bottom' to 'top'. If 'frame' is 'OpenGL', the coordinate is flopped:

    +Y
    ^
    |   +-----------+  top
    |   |           |
    |   |           |
    |   |           |
    |   +-----------+  bottom
    | left        right
    o------------------> +X

    """

    def __init__(self, left=0, top=0, right=0, bottom=0, z=0, frame=None):
        assert left < right, "right must be greater thatn left"
        if frame == "OpenGL":
            assert top > bottom, "bottom must be greater than top"
        else:
            assert top < bottom, "bottom must be greater than top"
        self._rect = np.array([left, top, right, bottom, z])
        self._frame = frame

    def __getitem__(self, n):
        return self._rect[n]

    def __setitem__(self, n, value):
        self._rect[n] = value

    @property
    def left(self):
        return self._rect[0]

    @left.setter
    def left(self, value):
        self._rect[0] = value

    @property
    def top(self):
        return self._rect[1]

    @top.setter
    def top(self, value):
        self._rect[1] = value

    @property
    def right(self):
        return self._rect[2]

    @right.setter
    def right(self, value):
        self._rect[2] = value

    @property
    def bottom(self):
        return self._rect[3]

    @bottom.setter
    def bottom(self, value):
        self._rect[3] = value

    @property
    def z(self):
        return self._rect[4]

    @z.setter
    def z(self, value):
        self._rect[4] = value

    @property
    def frame(self):
        return self._frame

    @property
    def width(self):
        return np.abs(self.right - self.left)

    @property
    def height(self):
        return np.abs(self.bottom - self.top)

    @property
    def aspect(self):
        return self.height / self.width

    @property
    def shape(self):
        return self._rect.shape

    @property
    def left_vec(self):
        return np.array([self.left, 0, self.z])

    @property
    def top_vec(self):
        return np.array([0, self.top, self.z])

    @property
    def right_vec(self):
        return np.array([self.right, 0, self.z])

    @property
    def bottom_vec(self):
        return np.array([0, self.bottom, self.z])

    @property
    def center_vec(self):
        return np.array(
            [
                (self.left + self.right) / 2.0,
                (self.top + self.bottom) / 2.0,
                self.z,
            ]
        )

    def to_opengl(self):
        return FlowRect(
            left=self.left,
            top=self.bottom,
            right=self.right,
            bottom=self.top,
            z=-self.z,
            frame="OpenGL",
        )

    def __str__(self):
        fmt = "FlowRect(left={0},top={1},right={2},bottom={3},z={4})"
        s = fmt.format(self.left, self.top, self.right, self.bottom, self.z)
        if self._frame is not None:
            s += f" on '{self._frame}'"
        return s
