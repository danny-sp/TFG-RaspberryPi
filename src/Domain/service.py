"""
Defines the Service class, which represents a service available near a charging station.
"""

from __future__ import annotations

from datetime import time

from src.Utils.constants import ServiceType


class Service:
    """
    Represents a service available near a charging station.

    Attributes:
        id (int): The unique identifier of the service.
        name (str): The name of the service.
        type (ServiceType): The type of the service.
        open_time (time): The time when the service opens.
        close_time (time): The time when the service closes.
    """

    def __init__(
        self, id: int, name: str, type: ServiceType, open_time: time, close_time: time
    ):
        self._id = id
        self._name = name
        self._type = type
        self._open_time = open_time
        self._close_time = close_time

    ##############
    # PROPERTIES #
    ##############
    @property
    def id(self) -> int:
        """
        The unique identifier of the service.
        """
        return self._id

    @property
    def name(self) -> str:
        """
        The name of the service.
        """
        return self._name

    @property
    def type(self) -> ServiceType:
        """
        The type of the service.
        """
        return self._type

    @property
    def open_time(self) -> time:
        """
        The time when the service opens.
        """
        return self._open_time

    @property
    def close_time(self) -> time:
        """
        The time when the service closes.
        """
        return self._close_time
