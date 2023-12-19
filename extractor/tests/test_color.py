import unittest
from os import path

from extractor import color, io, model

from .paths import TESTING


class TestExtractColor(unittest.TestCase):
    def validate(
        self, frame_path: str, mask_path: str, expected: tuple[float, float, float]
    ):
        frame = io.load_frame(frame_path)
        mask = io.load_frame(mask_path)
        actual = color.extract_color(frame, mask)

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


class TestHueToTemperature(unittest.TestCase):
    def test_warm(self):
        self.assertAlmostEqual(
            color.hue_to_temperature(0.0, 1, 1),  # Red.
            1667.0,  # Warm.
            delta=100,
        )

    def test_neutral(self):
        self.assertAlmostEqual(
            color.hue_to_temperature(0.0, 0.0, 1),  # White.
            6300,  # Warm.
            delta=100,
        )

    def test_cold(self):
        self.assertAlmostEqual(
            color.hue_to_temperature(0.66, 1, 1),  # Blue.
            25000,  # Warm.
            delta=100,
        )


class TestSimilar(unittest.TestCase):
    def setUp(self):
        self.c = color.Color()
        pass

    def test_similar(self):
        colors1 = [(0.1, 0.2, 0.3), (0.4, 0.5, 0.6)]
        temps1 = [3000.0, 4000.0]
        colors2 = [(0.11, 0.21, 0.31), (0.41, 0.51, 0.61)]
        temps2 = [3100.0, 4100.0]

        update1 = model.ColorUpdate(colors1, temps1)
        update2 = model.ColorUpdate(colors2, temps2)

        self.assertTrue(self.c.similar(update1, update2))

    def test_different_color(self):
        colors1 = [(0.1, 0.2, 0.3), (0.4, 0.5, 0.6)]
        temps1 = [3000.0, 4000.0]
        colors2 = [(0.3, 0.21, 0.31), (0.41, 0.51, 0.61)]
        temps2 = [3100.0, 4100.0]

        update1 = model.ColorUpdate(colors1, temps1)
        update2 = model.ColorUpdate(colors2, temps2)

        self.assertFalse(self.c.similar(update1, update2))

    def test_different_temp(self):
        colors1 = [(0.1, 0.2, 0.3), (0.4, 0.5, 0.6)]
        temps1 = [3000.0, 4000.0]
        colors2 = [(0.11, 0.21, 0.31), (0.41, 0.51, 0.61)]
        temps2 = [4200.0, 4100.0]

        update1 = model.ColorUpdate(colors1, temps1)
        update2 = model.ColorUpdate(colors2, temps2)

        self.assertFalse(self.c.similar(update1, update2))


if __name__ == "__main__":
    unittest.main()
