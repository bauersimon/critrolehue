from abc import ABC, abstractmethod
import numpy as np
from data import load_frame, get_frame
from typing import Dict
from yt_dlp import YoutubeDL
from tempfile import TemporaryDirectory
from os import path


class FrameGenerator(ABC):
    @abstractmethod
    def get_frame(self, second: float) -> np.array:
        """Obtain a frame at a certain time point."""
        pass


class VideoFile(FrameGenerator):
    _file: str

    def __init__(self, file: str):
        self._file = file

    def get_frame(self, second: float) -> np.array:
        """Obtain a frame at a certain time point."""
        return get_frame(self._file, second)


class ImageFiles(FrameGenerator):
    _files: Dict[float, str]

    def __init__(self, files: Dict[float, str]):
        self._files = files

    def get_frame(self, second: float) -> np.array:
        """Obtain a frame at a certain time point."""
        file = self._files.get(second, None)
        if not file:
            raise Exception(f"no frame for {second}s")
        return load_frame(file)


_formats = {
    "sd": "396",
    "hd": "398",
    "fullhd": "399",
}


class YouTubeVideo(FrameGenerator):
    _url: str
    _format: str

    def __init__(self, url: str, quality: str = 'hd'):
        self._url = url
        self._format = _formats[quality]

    def get_frame(self, second: float) -> np.array:
        def section(*args, **kwargs): return [{
            "start_time": second - 0.1,
            "end_time": second + 0.1,
        }]

        with TemporaryDirectory() as temp:
            yt = YoutubeDL({
                "format": self._format,
                "download_ranges": section,
                "force_keyframes_at_cuts": True,
                "paths": {
                    "home": temp,
                },
                "outtmpl": "download.mp4",
                "quiet": True,
            })

            yt.download([self._url])

            return get_frame(path.join(temp, "download.mp4"), 0.1)
