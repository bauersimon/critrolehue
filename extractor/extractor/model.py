import datetime
import json


class ColorUpdate:
    def __init__(self, colors: list[tuple[float, float, float]], temps: list[float], timestamp: float = -1.0):
        self._colors = colors
        self._temps = temps
        self._timestamp = timestamp
        self._invalid = False

    def set_timestamp(self, timestamp: float):
        self._timestamp = timestamp

    @property
    def timestring(self) -> str:
        return str(datetime.timedelta(seconds=self._timestamp))

    def __str__(self) -> str:
        if self._invalid:
            return f"{self.timestring}: invalid"
        return f"{self.timestring}: {self._colors} {self._temps}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ColorUpdate):
            return False
        elif self._invalid != __value._invalid:
            return False
        return self._colors == __value._colors and self._temps == __value._temps and self._timestamp == __value._timestamp

    def to_dict(self) -> dict:
        if self._invalid:
            raise ValueError("Cannot convert invalid update to dict.")

        return {
            "time": self._timestamp,
            "hue": self._colors,
            "temp": self._temps
        }

    @staticmethod
    def invalid(timestamp: float = -1.0):
        update = ColorUpdate([], [], timestamp)
        update._invalid = True
        return update

    @staticmethod
    def from_dict(d: dict):
        hues = d["hue"]
        for i in range(len(hues)):
            hue = hues[i]
            if len(hue) != 3:
                raise ValueError("Invalid hue color.")
            for c in hue:
                if not isinstance(c, float):
                    raise ValueError("Invalid hue type.")
                elif c < 0.0 or c > 1.0:
                    raise ValueError("Invalid hue color.")
            hues[i] = tuple(hue)
        temps = d["temp"]
        for temp in temps:
            if not isinstance(temp, float) and not isinstance(temp, int):
                raise ValueError("Invalid temperature type.")
            elif temp < 0.0:
                raise ValueError("Invalid temperature.")
        timestamp = d["time"]
        if not isinstance(timestamp, float) and not isinstance(timestamp, int):
            raise ValueError("Invalid timestamp type.")
        elif timestamp < 0.0:
            raise ValueError("Invalid timestamp.")
        return ColorUpdate(hues, temps, timestamp)


def to_json(updates: list[ColorUpdate], url: str, compact: bool = False) -> str:
    data = {
        "url": url,
        "updates": list(map(lambda u: u.to_dict(), updates))
    }

    return json.dumps(data, indent=None if compact else 4, separators=(",", ":") if compact else None)


def from_json(json_string: str) -> tuple[str, list[ColorUpdate]]:
    data = json.loads(json_string)
    url = data["url"]
    if not isinstance(url, str):
        raise ValueError("Invalid url type.")
    updates = list(map(lambda u: ColorUpdate.from_dict(u), data["updates"]))
    return url, updates
