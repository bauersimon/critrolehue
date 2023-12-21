import logging
from abc import ABC
from multiprocessing import Pool

import numpy.typing as npt
import tqdm

from . import color, constants, data, image, model

logger = logging.getLogger(__name__)


class AbstractExtractor(ABC):
    def is_valid(self, frame: npt.NDArray) -> bool:
        """Checks if the frame is valid for the scheme."""
        raise NotImplementedError

    def extract(self, frame: npt.NDArray) -> model.ColorUpdate:
        """Extracts the color from the frame."""
        raise NotImplementedError

    def similar(self, update1: model.ColorUpdate, update2: model.ColorUpdate) -> bool:
        """Checks if the two updates are similar."""
        raise NotImplementedError


class Extractor(AbstractExtractor):
    def __init__(self, c: color.AbstractColor, hue_areas: list[npt.NDArray], temp_areas: list[npt.NDArray], valid_mask: npt.NDArray, valid_content: npt.NDArray, valid_threshold: float = 0.8):
        """Defines how to search for the color and temperature of the image."""
        self._color = c
        self._hue_areas = hue_areas
        self._temp_areas = temp_areas
        self._valid_mask = valid_mask
        self._valid_content = valid_content
        self._valid_threshold = valid_threshold

    def is_valid(self, frame: npt.NDArray) -> bool:
        """Checks if the frame is valid for the scheme."""
        return image.similar_image(frame, self._valid_content, self._valid_mask) > self._valid_threshold

    def extract(self, frame: npt.NDArray) -> model.ColorUpdate:
        """Extracts the color from the frame."""
        if not self.is_valid(frame):
            raise Exception("Frame is not valid for this scheme.")

        hues = []
        temps = []
        for area in self._hue_areas:
            hue = self._color.hue(frame, area)
            hues.append(hue)
        for area in self._temp_areas:
            temp = self._color.temp(frame, area)
            temps.append(temp)
        return model.ColorUpdate(hues, temps)

    def similar(self, update1: model.ColorUpdate, update2: model.ColorUpdate) -> bool:
        """Checks if the two updates are similar."""
        return self._color.similar(update1, update2)


class Search:
    def __init__(self, s: AbstractExtractor, d: data.FrameGenerator, step: int = 120, refinement_accuracy: float = 3.0, workers: int = 1, quiet: bool = constants.QUIET):
        """Extracts the color and temperature of the data in a binary-search fashion."""
        self._scheme = s
        self._data = d
        self._step = step
        self._refinement_accuracy = refinement_accuracy
        self._workers = workers
        self._quiet = quiet

    def _search_step(self, step: float) -> model.ColorUpdate:
        try:
            frame = self._data.get_frame(step)
        except Exception as e:
            logger.warning(f"frame {step:.2f}s frame error: {e}")
            return model.ColorUpdate.invalid(timestamp=step)

        if not self._scheme.is_valid(frame):
            logger.debug(f"frame {step:.2f}s not valid")
            return model.ColorUpdate.invalid(timestamp=step)

        try:
            update = self._scheme.extract(frame)
        except Exception as e:
            logger.warning(f"frame {step:.2f}s extraction error: {e}")
            return model.ColorUpdate.invalid(timestamp=step)

        update.set_timestamp(step)
        return update

    def _search_raw(self) -> list[model.ColorUpdate]:
        steps = int(self._data.length / self._step)

        with Pool(self._workers) as p:
            return list(
                tqdm.tqdm(p.imap(
                    self._search_step,
                    range(0, int(self._data.length)+1, self._step)
                ), total=steps, disable=self._quiet))

    def _search_compact(self, raw: list[model.ColorUpdate]) -> list[model.ColorUpdate]:
        updates: list[model.ColorUpdate] = []

        for update in raw:
            if update._invalid:
                continue
            if len(updates) > 0 and self._scheme.similar(update, updates[-1]):
                logger.debug(
                    f"frame {update._timestamp:.2f}s similar to previous")
                continue
            updates.append(update)
        return updates

    def search(self) -> list[model.ColorUpdate]:
        """Searches for the color and temperature of the data in a binary-search fashion."""
        updates = self._search_raw()
        updates = self._search_compact(updates)

        return updates
