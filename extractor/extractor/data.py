import cv2
import numpy as np
from matplotlib import pyplot as plt


def get_frame(file: str, second: float) -> np.array:
    """
    Extract a frame at the given second from the given video file.

    Returns an `ndarray` of the shape: `(<height>,<width>,3)`.
    """
    # pylint: disable=no-member

    video = cv2.VideoCapture(file)
    ms = 1000*float(second)
    video.set(cv2.CAP_PROP_POS_MSEC, ms)
    success, frame = video.read()
    if not success:
        raise Exception(f"could not extract frame at {second}s in {file}")

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return np.array(frame)


def video_length(file: str) -> float:
    # pylint: disable=no-member
    video = cv2.VideoCapture(file)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    return frame_count / fps


def show_frame(frame: np.array):
    # pylint: disable=no-member

    plt.imshow(frame)
    plt.show()


def save_frame(file: str, frame: np.array):
    # pylint: disable=no-member

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(file, frame)


def load_frame(file: str) -> np.array:
    # pylint: disable=no-member

    frame = cv2.imread(file)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return np.array(frame)
