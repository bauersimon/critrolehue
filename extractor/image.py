import numpy as np
import cv2
from sewar.full_ref import uqi as similarity


def apply_mask(frame: np.array, mask: np.array) -> np.array:
    return np.where(mask > 127, frame, np.zeros_like(frame))


def subtract_mask(mask_0: np.array, mask_1: np.array) -> np.array:
    mask = mask_0 - mask_1
    return np.where(mask > 0, mask, np.zeros_like(mask))


def similar_image(img_0: np.array, img_1: np.array, mask: np.array = None, blur: int = 0) -> float:
    # pylint: disable=no-member
    if mask is not None:
        img_0 = apply_mask(img_0, mask)
        img_1 = apply_mask(img_1, mask)

    if blur > 0:
        img_0 = cv2.blur(img_0, (blur, blur))
        img_1 = cv2.blur(img_1, (blur, blur))

    return similarity(img_0, img_1)
