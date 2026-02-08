from enum import StrEnum

class ServiceType(StrEnum):
    CAFE = '\uf0f4'
    RESTAURANT = '\uf2e7'
    MOTEL = '\uf236'
    MECHANIC = '\uf0ad'
    SUPERMARKET = '\uf07a'
    ATM = '\uf3e7'
    PHARMACY = '\uf484'

class BookingStatus(StrEnum):
    SCHEDULED = 'scheduled'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'