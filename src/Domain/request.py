"""
Represents a charging request from an electric vehicle.
"""

import uuid
from datetime import datetime
from typing import Tuple


class Request:
    """
    Represents a charging request from an electric vehicle.

    Attributes:
        uuid (str): The unique identifier of the request.
        plate (str): The license plate of the vehicle making the request.
        timestamp (datetime): The timestamp when the request was created.
        current_percent (float): The current battery percentage of the vehicle.
        position (tuple[float, float]): The current geographical position of the vehicle (latitude, longitude).
        destination (tuple[float, float]): The geographical destination of the vehicle (latitude,
    """

    def __init__(
        self,
        plate: str,
        current_percent: float,
        position: Tuple[float, float],
        destination: Tuple[float, float],
    ):
        self._uuid = str(uuid.uuid4())
        self._plate = plate
        self._timestamp = datetime.now()
        self._current_percent = current_percent
        self._position = position
        self._destination = destination

    def to_dict(self):
        """
        Converts the Request object to a dictionary representation.
        """
        return {
            "uuid": self._uuid,
            "plate": self._plate,
            "timestamp": self._timestamp.isoformat(),
            "current_percent": self._current_percent,
            "latitude": self._position[0],
            "longitude": self._position[1],
            "destination_lat": self._destination[0],
            "destination_lon": self._destination[1],
        }

    ##############
    # PROPERTIES #
    ##############
    @property
    def uuid(self) -> str:
        """
        The unique identifier of the request.
        """
        return self._uuid

    @property
    def plate(self) -> str:
        """
        The license plate of the vehicle making the request.
        """
        return self._plate

    @property
    def timestamp(self) -> datetime:
        """
        The timestamp when the request was created.
        """
        return self._timestamp

    @property
    def current_percent(self) -> float:
        """
        The current battery percentage of the vehicle.
        """
        return self._current_percent

    @property
    def position(self) -> Tuple[float, float]:
        """
        The current geographical position of the vehicle (latitude, longitude).
        """
        return self._position

    @property
    def destination(self) -> Tuple[float, float]:
        """
        The geographical destination of the vehicle (latitude, longitude).
        """
        return self._destination
