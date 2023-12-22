import logging
from abc import ABC, abstractmethod
from multiprocessing import Pool

import numpy.typing as npt
import tqdm

from . import color, constants, data, image, model

logger = logging.getLogger(__name__)


class AbstractExtractor(ABC):
    @abstractmethod
    def is_valid(self, frame: npt.NDArray) -> bool:
        """Checks if the frame is valid for the scheme."""
        raise NotImplementedError

    @abstractmethod
    def extract(self, frame: npt.NDArray) -> model.ColorUpdate:
        """Extracts the color from the frame."""
        raise NotImplementedError

    @abstractmethod
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
    def __init__(self, s: AbstractExtractor, d: data.FrameGenerator, step: int = 120, refinement_accuracy: float = 10.0, workers: int = 1, quiet: bool = constants.QUIET):
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
            updates = list(
                tqdm.tqdm(p.imap(
                    self._search_step,
                    range(0, int(self._data.length)+1, self._step)
                ), total=steps, disable=self._quiet))

            p.close()
            p.join()

            return updates

    def _search_compact(self, raw: list[model.ColorUpdate]) -> list[model.ColorUpdate]:
        to_refine: list[tuple[model.ColorUpdate, model.ColorUpdate]] = []
        for i in range(1, len(raw)):
            first = raw[i-1]
            second = raw[i]
            if second._invalid:
                continue
            elif self._scheme.similar(first, second):
                continue
            to_refine.append((first, second))

        with Pool(self._workers) as p:
            refined = list(
                tqdm.tqdm(p.imap(
                    self._refine,
                    to_refine
                ), total=len(to_refine), disable=self._quiet))

            p.close()
            p.join()

        updates: list[model.ColorUpdate] = []
        # Include the first update since it is not part of the refinement.
        if not raw[0]._invalid:
            updates.append(raw[0])

        for i in range(len(to_refine)):
            first, second = to_refine[i]
            second.set_timestamp(refined[i])
            updates.append(second)

        return updates

    def _refine(self, updates: tuple[model.ColorUpdate, model.ColorUpdate]) -> float:
        """Computes a more accurate timestamp for the second update."""
        first, second = updates
        if first._timestamp >= second._timestamp:
            raise Exception("First update must be before second update.")
        elif second._invalid:
            raise Exception("Second update must be valid.")

        update = self._refine_recursion(first, second)
        logger.debug(f"refined {second._timestamp:.2f}s to {update:.2f}s")
        return update

    def _refine_recursion(self, first: model.ColorUpdate, second: model.ColorUpdate) -> float:
        """Recursively computes a more accurate timestamp for the second update."""
        if abs(first._timestamp - second._timestamp) < self._refinement_accuracy:
            return second._timestamp

        mid = (first._timestamp + second._timestamp) / 2
        mid_update = self._search_step(mid)

        if mid_update._invalid or self._scheme.similar(first, mid_update):
            return self._refine_recursion(mid_update, second)
        elif self._scheme.similar(mid_update, second):
            return self._refine_recursion(first, mid_update)

        logger.warning(
            f"could not refine from {first.timestring} to {second.timestring}, color transition might be longer than refinement_accuracy={self._refinement_accuracy:.1f}s")
        return second._timestamp

    def search(self) -> list[model.ColorUpdate]:
        """Searches for the color and temperature of the data in a binary-search fashion."""
        logger.info(f"color extraction pass (every {self._step/60:.1f}min)")
        updates = self._search_raw()
        logger.debug(f"obtained {len(updates)} color updates")
        logger.info(
            f"color refinement pass (down to {self._refinement_accuracy:.1f}s)")
        updates = self._search_compact(updates)
        logger.debug(f"refined {len(updates)} color updates")

        return updates
