from abc import ABC, abstractmethod
from os import path
from tempfile import TemporaryDirectory
from typing import Dict, Union

import numpy.typing as npt
from yt_dlp import YoutubeDL

from . import io


class FrameGenerator(ABC):
    @abstractmethod
    def get_frame(self, second: float) -> npt.NDArray:
        """Obtain a frame at a certain time point."""
        pass

    @property
    @abstractmethod
    def length(self) -> float:
        pass


class VideoFile(FrameGenerator):
    def __init__(self, file: str):
        self._file = file
        self._length = io.video_length(file)

    def get_frame(self, second: float) -> npt.NDArray:
        """Obtain a frame at a certain time point."""
        return io.get_frame(self._file, second)

    @property
    def length(self) -> float:
        return self._length


class ImageFiles(FrameGenerator):
    def __init__(self, files: Dict[float, str]):
        self._files = files

    def get_frame(self, second: float) -> npt.NDArray:
        """Obtain a frame at a certain time point."""
        file = self._files.get(second, None)
        if not file:
            raise Exception(f"no frame for {second}s")
        return io.load_frame(file)

    @property
    def length(self) -> float:
        return max(self._files.keys())


_formats = {
    "sd": "396",
    "hd": "398",
    "fullhd": "399",
}


class YouTubeVideo(FrameGenerator):
    def __init__(self, url: str, quality: str = "hd"):
        self._url = url
        self._format = _formats[quality]

        with YoutubeDL({"quiet": True}) as yt:
            info = yt.extract_info(url, download=False)
            if info is None:
                raise Exception("url {url} not found")
            self._length = float(info["duration"])

    def get_frame(self, second: float) -> Union[npt.NDArray, None]:
        if second > self._length - 0.1:
            return None

        def section(*args, **kwargs):
            return [
                {
                    "start_time": second - 0.1,
                    "end_time": second + 0.1,
                }
            ]

        with TemporaryDirectory() as temp:
            yt = YoutubeDL(
                {
                    "format": self._format,
                    "download_ranges": section,
                    "force_keyframes_at_cuts": True,
                    "paths": {
                        "home": temp,
                    },
                    "outtmpl": "download.mp4",
                    "quiet": True,
                }
            )

            yt.download([self._url])

            return io.get_frame(path.join(temp, "download.mp4"), 0.1)

    @property
    def length(self) -> float:
        return self._length
