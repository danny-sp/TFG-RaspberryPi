"""
Represents a charging station for electric vehicles.
"""

from src.Domain.charger import Charger


class ChargingStation:
    """
    Represents a charging station for electric vehicles.

    Attributes:
        id (int): The unique identifier of the charging station.
        name (str): The name of the charging station.
        location (tuple[float, float]): The geographical location of the charging station.
        operator (str): The operator of the charging station.
        chargers (list[Charger]): A list of chargers available at the charging station.
    """

    def __init__(
        self,
        id: int,
        name: str,
        location: tuple[float, float],
        operator: str,
        chargers: list[Charger] = [],
    ):
        self._id = id
        self._name = name
        self._location = location
        self._operator = operator
        self._chargers = chargers

    ##############
    # PROPERTIES #
    ##############
    @property
    def id(self) -> int:
        """
        The unique identifier of the charging station.
        """
        return self._id

    @property
    def name(self) -> str:
        """
        The name of the charging station.
        """
        return self._name

    @property
    def location(self) -> tuple[float, float]:
        """
        The geographical location of the charging station as a tuple of (latitude, longitude).
        """
        return self._location

    @property
    def latitude(self) -> float:
        """
        The latitude of the charging station's location.
        """
        return self._location[0]

    @property
    def longitude(self) -> float:
        """
        The longitude of the charging station's location.
        """
        return self._location[1]

    @property
    def operator(self) -> str:
        """
        The operator of the charging station.
        """
        return self._operator

    @property
    def chargers(self) -> list[Charger]:
        """
        A list of chargers available at the charging station.
        """
        return self._chargers
