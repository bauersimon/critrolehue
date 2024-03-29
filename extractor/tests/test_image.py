import unittest
from os import path

from extractor import image, io

from .constants import TESTING


class TestSimilarImage(unittest.TestCase):
    def test_similar(self):
        img_0 = io.load_frame(path.join(TESTING, "day_0_0.png"))
        img_1 = io.load_frame(path.join(TESTING, "day_0_0.png"))
        actual = image.similar_image(img_0, img_1)

        self.assertGreater(actual, 0.99)

    def test_different(self):
        img_0 = io.load_frame(path.join(TESTING, "night_0_0.png"))
        img_1 = io.load_frame(path.join(TESTING, "night_2_0.png"))
        actual = image.similar_image(img_0, img_1)

        self.assertLess(actual, 0.99)

    def test_similar_mask(self):
        img = io.load_frame(path.join(TESTING, "day_0_0.png"))
        ref = io.load_frame(path.join(TESTING, "frame_hd.png"))
        mask = io.load_frame(path.join(TESTING, "frame_mask_hd.png"))
        actual = image.similar_image(img, ref, mask)

        self.assertGreater(actual, 0.95)

    def test_different_mask(self):
        # Use the frame itself as image because it's all-white.
        img = io.load_frame(path.join(TESTING, "frame_mask_hd.png"))
        ref = io.load_frame(path.join(TESTING, "frame_hd.png"))
        mask = io.load_frame(path.join(TESTING, "frame_mask_hd.png"))
        actual = image.similar_image(img, ref, mask)

        self.assertLess(actual, 0.95)


if __name__ == "__main__":
    unittest.main()
