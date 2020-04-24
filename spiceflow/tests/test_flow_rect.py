import unittest
import numpy as np
from numpy.testing import assert_array_equal

from flow_rect import FlowRect


class TestCase(unittest.TestCase):
    def test_shape(self):
        rect = FlowRect(left=1, top=2, right=3, bottom=4, z=5)
        self.assertEqual(rect.shape, (5,))

    def test_index_access_read(self):
        rect = FlowRect(left=1, top=2, right=3, bottom=4, z=5)
        self.assertEqual(rect[0], 1)
        self.assertEqual(rect[1], 2)
        self.assertEqual(rect[2], 3)
        self.assertEqual(rect[3], 4)
        self.assertEqual(rect[4], 5)

    def test_index_access_write(self):
        rect = FlowRect()
        for i in range(5):
            rect[i] = i + 10
        self.assertEqual(rect[0], 10)
        self.assertEqual(rect[1], 11)
        self.assertEqual(rect[2], 12)
        self.assertEqual(rect[3], 13)
        self.assertEqual(rect[4], 14)

    def test_attribute_access_read(self):
        rect = FlowRect(left=1, top=2, right=3, bottom=4, z=5)
        self.assertEqual(rect.left, 1)
        self.assertEqual(rect.top, 2)
        self.assertEqual(rect.right, 3)
        self.assertEqual(rect.bottom, 4)
        self.assertEqual(rect.z, 5)

    def test_attribute_access_write(self):
        rect = FlowRect(left=1, top=2, right=3, bottom=4, z=5)
        self.assertEqual(rect.left, 1)
        self.assertEqual(rect.top, 2)
        self.assertEqual(rect.right, 3)
        self.assertEqual(rect.bottom, 4)
        self.assertEqual(rect.z, 5)

    def test_width(self):
        rect = FlowRect(left=1, top=2, right=3, bottom=4, z=5)
        self.assertEqual(rect.width, 2)

    def test_height(self):
        rect = FlowRect(left=1, top=2, right=3, bottom=4, z=5)
        self.assertEqual(rect.height, -2)

    def test_center(self):
        rect = FlowRect(left=1, top=2, right=3, bottom=4, z=5)
        assert_array_equal(rect.center, np.array([2, 3, 5]))


if __name__ == "__main__":
    unittest.main()
