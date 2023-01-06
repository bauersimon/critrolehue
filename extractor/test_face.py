import unittest
from data import load_frame
from face import _extract_faces, _head_mask, remove_heads_from_mask
from numpy import testing as nptest
from os import path
from paths import TESTING


class TestHeadMask(unittest.TestCase):

    def test_compute_heads(self):
        f = load_frame(path.join(TESTING, "night_0_5.png"))
        faces = _extract_faces(f)
        actual = _head_mask(faces, f.shape[0], f.shape[1], 0.8)
        expected = load_frame(path.join(TESTING, "night_0_5_faces.png"))

        nptest.assert_equal(actual, expected)

    def test_remove_heads(self):
        f = load_frame(path.join(TESTING, "night_0_5.png"))
        m = load_frame(path.join(TESTING, "mask_windows.png"))
        actual = remove_heads_from_mask(f, m, 1.5)
        expected = load_frame(path.join(TESTING, "night_0_5_mask.png"))

        nptest.assert_equal(actual, expected)

if __name__ == "__main__":
    unittest.main()