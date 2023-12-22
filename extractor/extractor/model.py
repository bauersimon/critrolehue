
class ColorUpdate:
    def __init__(self, colors: list[tuple[float, float, float]], temps: list[float], timestamp: float = -1.0):
        self._colors = colors
        self._temps = temps
        self._timestamp = timestamp
        self._invalid = False

    def set_timestamp(self, timestamp: float):
        self._timestamp = timestamp

    def __str__(self) -> str:
        if self._invalid:
            return f"{self._timestamp:.2f}s: invalid"
        return f"{self._timestamp:.2f}s: {self._colors} {self._temps}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ColorUpdate):
            return False
        elif self._invalid != __value._invalid:
            return False
        return self._colors == __value._colors and self._temps == __value._temps and self._timestamp == __value._timestamp

    @staticmethod
    def invalid(timestamp: float = -1.0):
        update = ColorUpdate([], [], timestamp)
        update._invalid = True
        return update
