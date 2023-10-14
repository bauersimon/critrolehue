from typing import Optional

import cv2
import numpy as np
import numpy.typing as npt
from sewar.full_ref import uqi as similarity


def apply_mask(frame: npt.NDArray, mask: npt.NDArray) -> npt.NDArray:
    return np.where(mask > 127, frame, np.zeros_like(frame))


def subtract_mask(mask_0: npt.NDArray, mask_1: npt.NDArray) -> npt.NDArray:
    mask = mask_0 - mask_1
    return np.where(mask > 0, mask, np.zeros_like(mask))


def similar_image(
    img_0: npt.NDArray,
    img_1: npt.NDArray,
    mask: Optional[npt.NDArray] = None,
    blur: int = 0
) -> float:
    if mask is not None:
        img_0 = apply_mask(img_0, mask)
        img_1 = apply_mask(img_1, mask)

    if blur > 0:
        img_0 = cv2.blur(img_0, (blur, blur))
        img_1 = cv2.blur(img_1, (blur, blur))

    return float(similarity(img_0, img_1))
