import unittest
from os import path

from numpy import testing as nptest

from extractor import face, io

from .constants import TESTING


class TestHeadMask(unittest.TestCase):

    def test_compute_heads(self):
        f = io.load_frame(path.join(TESTING, "night_0_5.png"))
        faces = face._extract_faces(f)
        actual = face._head_mask(faces, f.shape[0], f.shape[1], 0.8)
        expected = io.load_frame(path.join(TESTING, "night_0_5_faces.png"))

        nptest.assert_equal(actual, expected)

    def test_remove_heads(self):
        f = io.load_frame(path.join(TESTING, "night_0_5.png"))
        m = io.load_frame(path.join(TESTING, "mask_windows.png"))
        actual = face.remove_heads_from_mask(f, m, 1.5)
        expected = io.load_frame(path.join(TESTING, "night_0_5_mask.png"))

        nptest.assert_equal(actual, expected)


if __name__ == "__main__":
    unittest.main()
