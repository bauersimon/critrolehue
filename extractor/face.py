import cv2
import numpy as np
from typing import List, Tuple
from paths import ROOT
from os import path
from data import load_frame, show_frame, save_frame
from image import subtract_mask


def _extract_faces(frame: np.array) -> List[Tuple[int, int, int, int]]:
    """Extract a list of `(x,y,w,h)`."""
    # pylint: disable=no-member

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    classifier = cv2.CascadeClassifier(path.join(ROOT, 'face_model.xml'))
    faces = classifier.detectMultiScale(
        image=frame,
        scaleFactor=1.1,
        minNeighbors=5,
    )

    return faces


def _head_mask(faces: List[Tuple[int, int, int, int]], height: int, width: int, radius_factor: float) -> np.array:
    # pylint: disable=no-member
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


def remove_heads_from_mask(frame: np.array, mask: np.array, head_radius=0.8) -> np.array:
    faces = _extract_faces(frame)
    height = frame.shape[0]
    width = frame.shape[1]
    head_mask = _head_mask(faces, height, width, head_radius)

    return subtract_mask(mask, head_mask)

    return mask
