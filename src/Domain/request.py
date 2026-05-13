"""
Represents a charging request from an electric vehicle.
Following Pydantic's BaseModel.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Request(BaseModel):
    """
    Represents a charging request from an electric vehicle.

    Attributes:
        uuid (str): Unique identifier for the request, typically a UUID string.
        plate (str): The license plate of the vehicle making the request.
        timestamp (datetime): The exact time when the request was generated.
        current_percent (float): The current battery percentage of the vehicle (0 to 100).
        position (tuple[float, float]): The current GPS coordinates of the vehicle (latitude, longitude).
        destination (tuple[float, float]): The GPS coordinates of the desired destination (latitude, longitude).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    uuid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the request",
    )
    plate: str = Field(..., min_length=1, description="Vehicle license plate")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Exact time the request was generated"
    )
    current_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Current battery percentage (0 to 100)"
    )
    position: tuple[float, float] = Field(
        ..., description="Current GPS coordinates (lat, lon)"
    )
    destination: tuple[float, float] = Field(
        ..., description="Destination GPS coordinates (lat, lon)"
    )

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the Request into a flattened dictionary format.
        """
        return {
            "uuid": self.uuid,
            "plate": self.plate,
            "timestamp": self.timestamp.isoformat(),
            "current_percent": self.current_percent,
            "latitude": self.position[0],
            "longitude": self.position[1],
            "destination_lat": self.destination[0],
            "destination_lon": self.destination[1],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Request:
        """
        Factory method to instantiate a Request from a flattened dictionary.
        """
        return cls(
            uuid=data.get("uuid", str(uuid.uuid4())),
            plate=data["plate"],
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if "timestamp" in data
                else datetime.now()
            ),
            current_percent=data["current_percent"],
            position=(data["latitude"], data["longitude"]),
            destination=(data["destination_lat"], data["destination_lon"]),
        )
