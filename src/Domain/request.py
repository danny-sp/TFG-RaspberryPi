from datetime import datetime
from typing import Tuple
import uuid

class Request:
    def __init__(self, plate: str, current_percent: float, position: Tuple[float, float], destination: Tuple[float, float]):
        self._uuid = str(uuid.uuid4())
        self._plate = plate
        self._timestamp = datetime.now()
        self._current_percent = current_percent
        self._position = position
        self._destination = destination

    ##############
    # PROPERTIES #
    ##############
    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def plate(self) -> str:
        return self._plate

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def current_percent(self) -> float:
        return self._current_percent

    @property
    def position(self) -> Tuple[float, float]:
        return self._position

    @property
    def destination(self) -> Tuple[float, float]:
        return self._destination

    def to_dict(self):
        return {
            "uuid": self._uuid,
            "plate": self._plate,
            "timestamp": self._timestamp.isoformat(),
            "current_percent": self._current_percent,
            "latitude": self._position[0],
            "longitude": self._position[1],
            "destination_lat": self._destination[0],
            "destination_lon": self._destination[1]
        }
