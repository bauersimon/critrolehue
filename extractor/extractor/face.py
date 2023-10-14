from os import path
from typing import Sequence

import cv2
import cv2.typing as cvt
import numpy as np
import numpy.typing as npt

from .image import subtract_mask
from .paths import ROOT


def _extract_faces(frame: npt.NDArray) -> Sequence[cvt.Rect]:
    """Extract a list of `(x,y,w,h)`."""
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    classifier = cv2.CascadeClassifier(path.join(ROOT, 'face_model.xml'))
    faces = classifier.detectMultiScale(
        image=frame,
        scaleFactor=1.1,
        minNeighbors=5,
    )

    return faces


def _head_mask(
        faces: Sequence[cvt.Rect],
        height: int,
        width: int,
        radius_factor: float
) -> npt.NDArray:
    """Create a mask of the found faces."""
    mask = np.zeros((height, width, 3))
    for (x, y, w, h) in faces:
        center = (int(x + 0.5*w), int(y + 0.4*h))
        radius = np.max([w, h])
        mask = cv2.circle(
            mask,
            center,
            int(radius * radius_factor),
            (255, 255, 255),
            -1,
        )

    return mask


def remove_heads_from_mask(
        frame: npt.NDArray,
        mask: npt.NDArray,
        head_radius=0.8
) -> npt.NDArray:
    faces = _extract_faces(frame)
    height = frame.shape[0]
    width = frame.shape[1]
    head_mask = _head_mask(faces, height, width, head_radius)

    return subtract_mask(mask, head_mask)
