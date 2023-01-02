import unittest
from data import get_frame, load_frame
from numpy import testing as nptest
from os import path
from paths import TESTING


class TestGetFrame(unittest.TestCase):
    @staticmethod
    def validate(file: str, second: float, expected: str):
        actual = get_frame(file, second)
        expected = load_frame(expected)
        nptest.assert_equal(actual, expected)

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
