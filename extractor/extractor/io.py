import logging
import os
from os import path

import cv2
import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)


def get_frame(file: str, second: float) -> npt.NDArray:
    """
    Extract a frame at the given second from the given video file.

    Returns an `ndarray` of the shape: `(<height>,<width>,3)`.
    """

    video = cv2.VideoCapture(file)
    ms = 1000*float(second)
    video.set(cv2.CAP_PROP_POS_MSEC, ms)
    success, frame = video.read()
    if not success:
        raise Exception(f"could not extract frame at {second}s in {file}")

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return np.array(frame)


def video_length(file: str) -> float:
    video = cv2.VideoCapture(file)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    return frame_count / fps


def show_frame(frame: npt.NDArray):
    plt.imshow(frame)
    plt.show()


def save_frame(file: str, frame: npt.NDArray):
    frame = frame.astype(np.float32)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(file, frame)


def load_frame(file: str) -> npt.NDArray:
    frame = cv2.imread(file)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return np.array(frame)


def find_frames(frame_dir: str, quality: str) -> tuple[npt.NDArray, npt.NDArray, list[npt.NDArray], list[npt.NDArray]]:
    """
    `frame_(mask)_(fullhd|hd|sd).png` define valid frames and `(hue|temp)_<name>_(fullhd|hd|sd).png` define hue/temperature areas (in alphabetic order)

    Returns a tuple of the form: `(frame_mask, frame, hues, temps)`.
    """
    frame_raw: str = ""
    frame_mask: str = ""
    hues: list[str] = []
    temps: list[str] = []
    for frame in sorted(os.listdir(frame_dir)):
        if frame == f"frame_mask_{quality}.png":
            logging.debug(f"Registered frame mask: {frame}")
            frame_mask = path.join(frame_dir, frame)
        elif frame == f"frame_{quality}.png":
            logging.debug(f"Registered frame content: {frame}")
            frame_raw = path.join(frame_dir, frame)
        elif frame.startswith("hue_") and frame.endswith(f"_{quality}.png"):
            logging.debug(f"Registered hue area: {frame}")
            hues.append(path.join(frame_dir, frame))
        elif frame.startswith("temp_") and frame.endswith(f"_{quality}.png"):
            logging.debug(f"Registered temperature area: {frame}")
            temps.append(path.join(frame_dir, frame))

    return (
        load_frame(frame_mask),
        load_frame(frame_raw),
        list(map(load_frame, hues)),
        list(map(load_frame, temps)),
    )
