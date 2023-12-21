import unittest
from os import path

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


if __name__ == "__main__":
    unittest.main()
