import numpy as np
from typing import List, Tuple
from data import load_frame
from colorsys import rgb_to_hsv


def _extract_hsv(frame: np.array, mask: np.array) -> List[Tuple[float, float, float]]:
    """
    Extract colors from the given frame, respecting the given mask.

    frame: np.array
        Shape of `(<height>,<width>,3)` with RGB channels.
    mask: np.array
        Shape of `(<height>,<width>,3)` with black/white RGB channels.

    returns: List[Tuple[float, float, float]]
        List of `(hue, saturation, value)` of length #(pixels included in the mask).
    """

    frame = np.where(mask > 127, frame, np.zeros_like(frame))

    height = frame.shape[0]
    width = frame.shape[1]

    frame = frame/255

    hues = np.reshape(frame, (height*width, 3)).tolist()
    hues = list(filter(lambda rgb: not rgb[0] == rgb[1] == rgb[2] == 0, hues))
    hues = list(map(lambda rgb: rgb_to_hsv(*rgb), hues))

    return hues


def _average_hsv(data: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    return tuple(np.mean(np.array(data), 0))


def _deviation_hsv(data: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    return tuple(np.std(np.array(data), 0))


def extract_color(frame: np.array, mask: np.array, brightness_cutoff=0.5) -> Tuple[float, float, float]:
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
