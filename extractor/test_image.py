import unittest
from paths import TESTING, FRAMES
from os import path
from image import similar_image
from data import load_frame


class TestSimilarImage(unittest.TestCase):
    def test_similar(self):
        img_0 = load_frame(path.join(TESTING, "day_0_0.png"))
        img_1 = load_frame(path.join(TESTING, "day_0_0.png"))
        actual = similar_image(img_0, img_1)

        self.assertGreater(actual, 0.99)

    def test_different(self):
        img_0 = load_frame(path.join(TESTING, "night_0_0.png"))
        img_1 = load_frame(path.join(TESTING, "night_2_0.png"))
        actual = similar_image(img_0, img_1)

        self.assertLess(actual, 0.99)

    def test_similar_mask(self):
        img = load_frame(path.join(TESTING, "day_0_0.png"))
        ref = load_frame(path.join(FRAMES, "frame_raw_hd.png"))
        mask = load_frame(path.join(FRAMES, "frame_hd.png"))
        actual = similar_image(img, ref, mask)

        self.assertGreater(actual, 0.95)

    def test_different_mask(self):
        # Use the frame itself as image because it's all-white.
        img = load_frame(path.join(FRAMES, "frame_hd.png"))
        ref = load_frame(path.join(FRAMES, "frame_raw_hd.png"))
        mask = load_frame(path.join(FRAMES, "frame_hd.png"))
        actual = similar_image(img, ref, mask)

        self.assertLess(actual, 0.95)


if __name__ == "__main__":
    unittest.main()
