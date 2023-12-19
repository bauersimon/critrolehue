class ColorUpdate:
    def __init__(self, colors: list[tuple[float, float, float]], temps: list[float]):
        self._colors = colors
        self._temps = temps

    def set_timestamp(self, timestamp: float):
        self._timestamp = timestamp

    def __str__(self) -> str:
        return f"{self._timestamp:.2f}s: {self._colors} {self._temps}"
