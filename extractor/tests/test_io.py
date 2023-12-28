import tempfile
import unittest
from os import path

import numpy as np
from numpy import testing as nptest

from extractor import io

from .constants import TESTING


class TestGetFrame(unittest.TestCase):
    @staticmethod
    def validate(file: str, second: float, expected: str):
        actual_frame = io.get_frame(file, second)
        expected_frame = io.load_frame(expected)
        nptest.assert_equal(actual_frame, expected_frame)

    def test_night_0_0(self):
        self.validate(
            path.join(TESTING, "night.mp4"),
            0.0,
            path.join(TESTING, "night_0_0.png"),
        )

    def test_night_0_5(self):
        self.validate(
            path.join(TESTING, "night.mp4"),
            0.5,
            path.join(TESTING, "night_0_5.png"),
        )

    def test_night_2_0(self):
        self.validate(
            path.join(TESTING, "night.mp4"),
            2.0,
            path.join(TESTING, "night_2_0.png"),
        )


class TestFindFrames(unittest.TestCase):
    def test_find_frames(self):
        frame_mask = np.ones((720, 1280, 3))
        frame = np.ones((720, 1280, 3))+1
        hue = np.ones((720, 1280, 3))+2
        temp = np.ones((720, 1280, 3))+3

        with tempfile.TemporaryDirectory() as dir:
            io.save_frame(path.join(dir, "frame_mask_hd.png"), frame_mask)
            io.save_frame(path.join(dir, "frame_hd.png"), frame)
            io.save_frame(path.join(dir, "hue_foo_hd.png"), hue)
            io.save_frame(path.join(dir, "temp_foo_hd.png"), temp)

            frame_mask_actual, frame_actual, hues, temps = io.find_frames(
                dir, "hd")

            nptest.assert_equal(frame_mask, frame_mask_actual)
            nptest.assert_equal(frame, frame_actual)
            self.assertEqual(len(hues), 1)
            nptest.assert_equal(hue, hues[0])
            self.assertEqual(len(temps), 1)
            nptest.assert_equal(temp, temps[0])


if __name__ == "__main__":
    unittest.main()
