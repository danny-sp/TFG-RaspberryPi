"""
Constants and enumerations for the application.
"""

from enum import Enum, StrEnum


class ServiceType(StrEnum):
    """
    Enumeration of different types of services that can be near a charging station, along with their corresponding FontAwesome icons.
    """

    CAFE = "\uf0f4"
    RESTAURANT = "\uf2e7"
    MOTEL = "\uf236"
    MECHANIC = "\uf0ad"
    SUPERMARKET = "\uf07a"
    ATM = "\uf09d"
    PHARMACY = "\uf484"


class Destinations(Enum):
    """
    Enumeration of different destinations that can be selected in the application.
    """

    MADRID = (40.451843, -3.686502)
    BILBAO = (43.262873, -2.947564)


class BookingStatus(StrEnum):
    """
    Enumeration of different booking statuses for a charging station reservation.
    """

    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
