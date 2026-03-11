from enum import StrEnum
from enum import Enum

class ServiceType(StrEnum):
    CAFE = '\uf0f4'
    RESTAURANT = '\uf2e7'
    MOTEL = '\uf236'
    MECHANIC = '\uf0ad'
    SUPERMARKET = '\uf07a'
    ATM = '\uf3e7'
    PHARMACY = '\uf484'

class Destinations(Enum):
    MADRID = (40.451843, -3.686502)
    BILBAO = (43.262873, -2.947564)

class BookingStatus(StrEnum):
    SCHEDULED = 'scheduled'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'