import logging
import unittest

import numpy as np
import numpy.typing as npt

from extractor import data, model, search


class TestExtractor(search.AbstractExtractor):
    def __init__(self, valid_frames: list[int] = [], similar_frames: dict[int, int] = {}, updates: dict[int, model.ColorUpdate] = {}) -> None:
        self._valid_frames = valid_frames
        self._updates = updates
        self._similar_frames = similar_frames

    def is_valid(self, frame: npt.NDArray) -> bool:
        """Checks if the frame is valid for the scheme."""
        return int(frame.item()) in self._valid_frames

    def extract(self, frame: npt.NDArray) -> model.ColorUpdate:
        """Extracts the color from the frame."""
        return self._updates[int(frame.item())]

    def similar(self, update1: model.ColorUpdate, update2: model.ColorUpdate) -> bool:
        """Checks if the two updates are similar."""
        try:
            return self._similar_frames[int(update1._timestamp)] == int(update2._timestamp) or self._similar_frames[int(update2._timestamp)] == int(update1._timestamp)
        except KeyError:
            return False


class BrokenExtractor(search.AbstractExtractor):
    def is_valid(self, frame: npt.NDArray) -> bool:
        """Checks if the frame is valid for the scheme."""
        return True

    def extract(self, frame: npt.NDArray) -> model.ColorUpdate:
        """Extracts the color from the frame."""
        raise Exception("broken")

    def similar(self, update1: model.ColorUpdate, update2: model.ColorUpdate) -> bool:
        """Checks if the two updates are similar."""
        raise Exception("broken")


class TestFrameGenerator(data.FrameGenerator):
    def __init__(self, length: int) -> None:
        self._length = length

    def get_frame(self, second: float) -> npt.NDArray:
        """Obtain a frame at a certain time point."""
        return np.array([int(second)])

    @property
    def length(self) -> float:
        return float(self._length)


class BrokenFrameGenerator(data.FrameGenerator):
    def __init__(self, length: int) -> None:
        self._length = length

    def get_frame(self, second: float) -> npt.NDArray:
        """Obtain a frame at a certain time point."""
        raise Exception("broken")

    @property
    def length(self) -> float:
        return float(self._length)


class TestSearch(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.ERROR)

    def test_search_raw(self):
        generator = TestFrameGenerator(5)
        extractor = TestExtractor(
            updates={
                0: model.ColorUpdate([], [0]),
                1: model.ColorUpdate([], [1]),
                2: model.ColorUpdate([], [2]),
                3: model.ColorUpdate([], [3]),
                4: model.ColorUpdate([], [4]),
                5: model.ColorUpdate([], [5]),
            },
            valid_frames=[0, 2, 3, 5],
        )
        actual = search.Search(extractor, generator,
                               step=1, workers=1, quiet=True)._search_raw()
        expected = [
            model.ColorUpdate([], [0], 0.0),
            model.ColorUpdate.invalid(1.0),
            model.ColorUpdate([], [2], 2.0),
            model.ColorUpdate([], [3], 3.0),
            model.ColorUpdate.invalid(4.0),
            model.ColorUpdate([], [5], 5.0),
        ]

        self.assertEqual(actual, expected)

    def test_search_raw_broken_generator(self):
        generator = BrokenFrameGenerator(3)
        extractor = TestExtractor()
        actual = search.Search(extractor, generator,
                               step=1, workers=1, quiet=True)._search_raw()
        expected = [
            model.ColorUpdate.invalid(0.0),
            model.ColorUpdate.invalid(1.0),
            model.ColorUpdate.invalid(2.0),
            model.ColorUpdate.invalid(3.0),
        ]

        self.assertEqual(actual, expected)

    def test_search_raw_broken_extractor(self):
        generator = TestFrameGenerator(3)
        extractor = BrokenExtractor()
        actual = search.Search(extractor, generator,
                               step=1, workers=1, quiet=True)._search_raw()
        expected = [
            model.ColorUpdate.invalid(0.0),
            model.ColorUpdate.invalid(1.0),
            model.ColorUpdate.invalid(2.0),
            model.ColorUpdate.invalid(3.0),
        ]

        self.assertEqual(actual, expected)

    def test_search_compact(self):
        generator = TestFrameGenerator(15)
        extractor = TestExtractor(
            updates={
                6: model.ColorUpdate.invalid(),
                7: model.ColorUpdate([], [7]),
                14: model.ColorUpdate([], [14]),
                13: model.ColorUpdate([], [13]),
            },
            valid_frames=list(range(0, 16)),
            similar_frames={
                7: 8,
                8: 12,
                14: 16,
                13: 14,
            }
        )
        actual = search.Search(extractor, generator,
                               step=4, workers=1, refinement_accuracy=1.0, quiet=True)._search_compact(
                                   [
                                       model.ColorUpdate([], [0], 0.0),
                                       model.ColorUpdate.invalid(4.0),
                                       model.ColorUpdate([], [8], 8.0),
                                       model.ColorUpdate([], [12], 12.0),
                                       model.ColorUpdate([], [16], 16.0),
                                   ]
        )
        expected = [
            model.ColorUpdate([], [0], 0.0),
            model.ColorUpdate([], [8], 7.0),
            model.ColorUpdate([], [16], 13.0),
        ]

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
