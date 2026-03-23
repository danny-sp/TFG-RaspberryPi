"""
This module defines the Option class, which represents a charging option for an electric vehicle.
"""

from __future__ import annotations

from datetime import datetime

from src.Domain.charging_station import ChargingStation
from src.Utils.constants import ServiceType


class Option:
    """
    Represents a charging option for an electric vehicle.

    Attributes:
        request_id (int): The ID of the charging request associated with this option.
        charging_station (ChargingStation): The charging station associated with this option.
        price (float): The price of this charging option.
        start_time (datetime): The start time of the charging session.
        end_time (datetime): The end time of the charging session.
        duration_hours (float): The duration of the charging session in hours.
        services_nearby (list[ServiceType]): A list of services available near the charging station.
    """

    def __init__(
        self,
        request_id: int,
        charging_station: ChargingStation,
        price: float,
        start_time: datetime,
        end_time: datetime,
        services_nearby: list[ServiceType],
    ):
        self._request_id = request_id
        self._charging_station = charging_station
        self._price = price
        self._start_time = start_time
        self._end_time = end_time
        self._duration_hours = (end_time - start_time).total_seconds() / 3600
        # self._price = self._duration_hours * self._price_rate.price_per_kwh
        self._price = 40.7
        self._services_nearby = services_nearby

    @staticmethod
    def from_dict(data: dict) -> Option:
        """
        Creates an Option instance from a dictionary.

        Args:
            data (dict): A dictionary containing the option data.

        Returns:
            Option: An instance of the Option class.
        """

        charging_station_data = data["charging_station"]
        services_nearby_data = data["services_nearby"]

        charging_station = ChargingStation(
            id=charging_station_data["id"],
            name=charging_station_data["name"],
            location=charging_station_data["location"],
            operator=charging_station_data["operator"],
        )

        return Option(
            request_id=data["request_id"],
            charging_station=charging_station,
            price=data["price"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            services_nearby=[
                ServiceType[service.upper()] for service in services_nearby_data
            ],
        )

    ##############
    # PROPERTIES #
    ##############
    @property
    def request_id(self) -> int:
        """
        The ID of the charging request associated with this option.
        """
        return self._request_id

    @property
    def charging_station(self) -> ChargingStation:
        """
        Charging station associated with this option.
        """
        return self._charging_station

    @property
    def price(self) -> float:
        """
        The price of this charging option.
        """
        return self._price

    @property
    def start_time(self) -> datetime:
        """
        The start time of the charging session.
        """
        return self._start_time

    @property
    def end_time(self) -> datetime:
        """
        The end time of the charging session.
        """
        return self._end_time

    @property
    def duration_hours(self) -> float:
        """
        The duration of the charging session in hours.
        """
        return self._duration_hours

    @property
    def services_nearby(self) -> list[ServiceType]:
        """
        A list of services available near the charging station.
        """
        return self._services_nearby
