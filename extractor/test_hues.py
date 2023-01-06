import unittest
from hues import extract_color
from data import load_frame
from paths import TESTING
from os import path


class TestExtractColor(unittest.TestCase):
    def validate(self, frame: str, mask: str, expected: tuple((float, float, float))):
        frame = load_frame(frame)
        mask = load_frame(mask)
        actual = extract_color(frame, mask)

        self.assertAlmostEqual(actual[0], expected[0], delta=0.01)
        self.assertAlmostEqual(actual[1], expected[1], delta=0.01)
        self.assertAlmostEqual(actual[2], expected[2], delta=0.01)

    def test_lamps(self):
        self.validate(
            path.join(TESTING, "day_0_0.png"),
            path.join(TESTING, "mask_lamps.png"),
            (0.11, 0.33, 0.89),  # Orange of the lamps.
        )

    def test_windows(self):
        self.validate(
            path.join(TESTING, "day_0_0.png"),
            path.join(TESTING, "mask_windows.png"),
            (0.59, 0.63, 0.82),  # Blue of the windows.
        )

if __name__ == "__main__":
    unittest.main()