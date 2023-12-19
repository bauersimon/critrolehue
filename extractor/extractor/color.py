import warnings
from abc import ABC
from colorsys import hsv_to_rgb, rgb_to_hsv

import numpy as np
import numpy.typing as npt
from colour import RGB_to_XYZ, XYZ_to_xy, xy_to_CCT

from . import image


def _extract_hsv(
    frame: npt.NDArray,
    mask: npt.NDArray,
) -> list[tuple[float, float, float]]:
    """
    Extract colors from the given frame, respecting the given mask.

    frame: npt.NDArray
        Shape of `(<height>,<width>,3)` with RGB channels.
    mask: npt.NDArray
        Shape of `(<height>,<width>,3)` with black/white RGB channels.

    returns: list[tuple[float, float, float]]
        list of `(hue, saturation, value)` of length #(pixels included in the mask).
    """

    frame = image.apply_mask(frame, mask)

    height = frame.shape[0]
    width = frame.shape[1]

    frame = frame/255

    hues: list[tuple[float, float, float]] = np.reshape(
        frame, (height*width, 3)).tolist()
    hues = list(filter(lambda rgb: not rgb[0] == rgb[1] == rgb[2] == 0, hues))
    hues = list(map(lambda rgb: rgb_to_hsv(*rgb), hues))

    return hues


def _average_hsv(
        data: list[tuple[float, float, float]]
) -> tuple[float, float, float]:
    hsv: list[float] = np.mean(np.array(data), 0).tolist()
    if len(hsv) == 3:
        t: tuple[float, float, float] = (hsv[0], hsv[1], hsv[2])
        return t
    return (0.0, 0.0, 0.0)


def _deviation_hsv(
        data: list[tuple[float, float, float]]
) -> tuple[float, float, float]:
    hsv: list[float] = np.std(np.array(data), 0).tolist()
    if len(hsv) == 3:
        t: tuple[float, float, float] = (hsv[0], hsv[1], hsv[2])
        return t
    return (0.0, 0.0, 0.0)


class AbstractColor(ABC):
    def hue(self, frame: npt.NDArray, mask: npt.NDArray) -> tuple[float, float, float]:
        raise NotImplementedError

    def temp(self, frame: npt.NDArray, mask: npt.NDArray) -> float:
        raise NotImplementedError


class Color(AbstractColor):
    def __init__(self, brightness_cutoff=0.5):
        self._brightness_cutoff = brightness_cutoff

    def hue(self, frame: npt.NDArray, mask: npt.NDArray) -> tuple[float, float, float]:
        return extract_color(frame, mask, self._brightness_cutoff)

    def temp(self, frame: npt.NDArray, mask: npt.NDArray) -> float:
        hue = self.hue(frame, mask)
        return hue_to_temperature(*hue)


def extract_color(
        frame: npt.NDArray,
        mask: npt.NDArray,
        brightness_cutoff=0.5
) -> tuple[float, float, float]:
    """Extract HSV colors from the given frame, respecting the given mask."""

    colors = _extract_hsv(frame, mask)

    # Remove pixels with a low "value" (brightness).
    _, _, v_m = _average_hsv(colors)
    colors = list(filter(lambda c: c[2] > brightness_cutoff*v_m, colors))
    if len(colors) == 0:
        return (0.0, 0.0, 0.0)

    # Remove pixels that are more then the standard-deviation away from the mean.
    h_m, s_m, _ = _average_hsv(colors)
    h_d, s_d, _ = _deviation_hsv(colors)
    colors = list(
        filter(lambda c: c[1] < s_m + s_d and c[1] > s_m - s_d, colors))
    colors = list(
        filter(lambda c: c[0] < h_m + h_d and c[0] > h_m - h_d, colors))
    if len(colors) == 0:
        return (0.0, 0.0, 0.0)

    return _average_hsv(colors)


def hue_to_temperature(h: float, s: float, v: float) -> float:
    rgb = hsv_to_rgb(h, s, v)
    xyz = RGB_to_XYZ(np.array(rgb), "sRGB")
    xy = XYZ_to_xy(xyz)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        temp = xy_to_CCT(xy, "kang2002").item()

    temp = max(1667.0, temp)  # Clip at 1667.
    temp = min(25000.0, temp)  # Clip at 25000.

    return temp
