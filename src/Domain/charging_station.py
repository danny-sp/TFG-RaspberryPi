"""
Represents a charging station for electric vehicles.
Following Pydantic's BaseModel.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.Domain.charger import Charger


class ChargingStation(BaseModel):
    """
    Represents a charging station for electric vehicles.

    Attributes:
        id (int): The unique identifier of the charging station.
        name (str): The name of the charging station.
        location (tuple[float, float]): The geographical location of the charging station.
        operator (str): The operator of the charging station.
        chargers (list[Charger]): A list of chargers available at the charging station.
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True, frozen=True)

    id: int = Field(..., description="The unique identifier of the charging station.")
    name: str = Field(
        ..., min_length=1, description="The name of the charging station."
    )
    location: tuple[float, float] = Field(
        ..., description="The geographical location of the charging station."
    )
    operator: str = Field(..., description="The operator of the charging station.")
    chargers: list[Charger] = Field(
        default_factory=list,
        description="A list of chargers available at the charging station.",
    )

    @property
    def latitude(self) -> float:
        """
        The latitude of the charging station's location.
        """
        return self.location[0]

    @property
    def longitude(self) -> float:
        """
        The longitude of the charging station's location.
        """
        return self.location[1]
