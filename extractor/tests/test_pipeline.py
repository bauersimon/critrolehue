import unittest
from os import path

from extractor import color, model, pipeline

from .constants import ROOT


class TestPipeline(unittest.TestCase):
    def test_pipeline(self):
        actual = pipeline.extract_from_youtube_video(
            path.join(ROOT, "..", "frames", "c3"),
            "https://www.youtube.com/watch?v=7t2NJJjy8r8",  # Episode 40 of Campaign 3
            "hd",
            step=60*60,  # Every hour to speed things up.
            refinement_accuracy=60*30,  # Only refine down to thirty minutes.
            quiet=True,
        )
        expected = [
            model.ColorUpdate(
                [(0.09, 0.41, 0.82), (0.64, 0.60, 0.60)], [4258.5], 15.0),
            model.ColorUpdate(
                [(0.52, 0.12, 0.90), (0.61, 0.25, 0.10)], [5200.8], 3*60*60),
        ]

        self.assertTrue(len(actual) == len(expected))
        for a, e in zip(actual, expected):
            self.assertTrue(color.Color().similar(a, e))


if __name__ == "__main__":
    unittest.main()
