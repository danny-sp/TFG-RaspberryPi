"""
This module defines the Option class, which represents a charging option for an electric vehicle.
Following Pydantic's BaseModel.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.Domain.charging_station import ChargingStation
from src.Utils.constants import ServiceType


class Option(BaseModel):
    """
    Represents a charging option for an electric vehicle.

    Attributes:
        request_id (str): The ID of the charging request associated with this option.
        charging_station (ChargingStation): The charging station associated with this option.
        price (float): The price of this charging option.
        kw_speed (float): The charging speed in kW for this option.
        start_time (datetime): The start time of the charging session.
        end_time (datetime): The end time of the charging session.
        charging_hours (float): The duration of the charging session in hours.
        route_hours (float): The route duration to the charging station in hours.
        delay_hours (float): Total delay from the original route.
        services_nearby (list[ServiceType]): A list of services available near the charging station.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)

    request_id: str = Field(
        ..., description="The ID of the charging request associated with this option"
    )
    charging_station: ChargingStation = Field(
        ..., description="The charging station associated with this option"
    )
    price: float = Field(..., description="The price of this charging option")
    kw_speed: float = Field(..., description="The charging speed in kW for this option")
    start_time: datetime = Field(
        ..., description="The start time of the charging session"
    )
    end_time: datetime = Field(..., description="The end time of the charging session")
    charging_hours: float = Field(
        ..., description="The duration of the charging session in hours"
    )
    route_hours: float = Field(
        ..., description="The route duration to the charging station in hours"
    )
    delay_hours: float = Field(..., description="Total delay from the original route")
    services_nearby: list[ServiceType] = Field(
        ..., description="A list of services available near the charging station"
    )

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the Option object to a dictionary representation.
        """
        return {
            "request_id": self.request_id,
            "charging_station": {
                "id": self.charging_station.id,
                "name": self.charging_station.name,
                "location": self.charging_station.location,
                "operator": self.charging_station.operator,
            },
            "price": self.price,
            "kw_speed": self.kw_speed,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "charging_hours": self.charging_hours,
            "route_hours": self.route_hours,
            "delay_hours": self.delay_hours,
            "services_nearby": [service.name for service in self.services_nearby],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Option:
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

        return cls(
            request_id=data["request_id"],
            charging_station=charging_station,
            price=data["price"],
            kw_speed=data["kw_speed"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            charging_hours=data["charging_hours"],
            route_hours=data["route_hours"],
            delay_hours=data["delay_hours"],
            services_nearby=[
                ServiceType[service.upper()] for service in services_nearby_data
            ],
        )
