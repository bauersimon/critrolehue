from colorsys import rgb_to_hsv

import numpy as np
import numpy.typing as npt

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
