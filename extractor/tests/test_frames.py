import unittest
from os import path
from typing import Dict

from numpy import testing as nptest

from extractor.data import load_frame
from extractor.frames import FrameIterator, ImageFiles, VideoFile, YouTubeVideo

from .paths import TESTING


class TestVideoFile(unittest.TestCase):
    @staticmethod
    def validate(file: str, second: float, expected_file: str):
        f = VideoFile(file)
        actual = f.get_frame(second)
        expected = load_frame(expected_file)

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


image_files = {
    0.0: path.join(TESTING, "night_0_0.png"),
    0.5: path.join(TESTING, "night_0_5.png"),
    2.0: path.join(TESTING, "night_2_0.png"),
}


class TestImageFiles(unittest.TestCase):
    @staticmethod
    def validate(files: Dict[float, str], second: float, expected_file: str):
        f = ImageFiles(files)
        actual = f.get_frame(second)
        expected = load_frame(expected_file)

        nptest.assert_equal(actual, expected)

    def test_night_0_0(self):
        self.validate(
            image_files,
            0.0,
            path.join(TESTING, "night_0_0.png"),
        )

    def test_night_0_5(self):
        self.validate(
            image_files,
            0.5,
            path.join(TESTING, "night_0_5.png"),
        )

    def test_night_2_0(self):
        self.validate(
            image_files,
            2.0,
            path.join(TESTING, "night_2_0.png"),
        )


class TestYouTubeVideo(unittest.TestCase):
    @staticmethod
    def validate(url: str, quality: str, second: float, expected_file: str):
        f = YouTubeVideo(url, quality=quality)
        actual = f.get_frame(second)
        expected = load_frame(expected_file)

        nptest.assert_equal(actual, expected)

    def test_sd(self):
        self.validate(
            "https://www.youtube.com/watch?v=x_fsXdtsnOc",
            "sd",
            5.0,
            path.join(TESTING, "youtube_sd.png"),
        )

    def test_hd(self):
        self.validate(
            "https://www.youtube.com/watch?v=x_fsXdtsnOc",
            "hd",
            5.0,
            path.join(TESTING, "youtube_hd.png"),
        )

    def test_fullhd(self):
        self.validate(
            "https://www.youtube.com/watch?v=x_fsXdtsnOc",
            "fullhd",
            5.0,
            path.join(TESTING, "youtube_fullhd.png"),
        )


class TestFrameGenerator(unittest.TestCase):
    def test_video_1_0(self):
        video = VideoFile(path.join(TESTING, "night.mp4"))
        iterator = FrameIterator(video, 1.0)
        frames = []
        for f in iterator:
            frames.append(f)

        nptest.assert_equal(frames[0][1], load_frame(
            path.join(TESTING, "night_0_0.png")))
        nptest.assert_equal(frames[2][1], load_frame(
            path.join(TESTING, "night_2_0.png")))

        self.assertEqual(int(video.length) + 1, len(iterator))

    def test_video_2_0(self):
        video = VideoFile(path.join(TESTING, "night.mp4"))
        iterator = FrameIterator(video, 2.0)
        frames = []
        for f in iterator:
            frames.append(f)

        nptest.assert_equal(frames[0][1], load_frame(
            path.join(TESTING, "night_0_0.png")))
        nptest.assert_equal(frames[1][1], load_frame(
            path.join(TESTING, "night_2_0.png")))

        self.assertEqual(int(video.length/2) + 1, len(iterator))


if __name__ == "__main__":
    unittest.main()
