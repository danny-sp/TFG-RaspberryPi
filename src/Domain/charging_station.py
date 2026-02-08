from __future__ import annotations
from datetime import time

from src.Domain.charger import Charger
from src.Domain.price_rate import PriceRate

class ChargingStation:
    def __init__(self, id: int, name: str, latitude: float, longitude: float, open_time: time, close_time: time, services: list[Service], chargers: list[Charger], price_rates: list[PriceRate]):
        self._id = id
        self._name = name
        self._latitude = latitude
        self._longitude = longitude
        self._open_time = open_time
        self._close_time = close_time
        self._services = services
        self._chargers = chargers
        self._price_rates = price_rates

    def add_service(self, service: Service):
        self._services.append(service)

    def add_charger(self, charger: Charger):
        self._chargers.append(charger)

    def add_price_rate(self, price_rate: PriceRate):
        self._price_rates.append(price_rate)

    ##############
    # PROPERTIES #
    ##############
    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def latitude(self) -> float:
        return self._latitude

    @property
    def longitude(self) -> float:
        return self._longitude

    @property
    def location(self) -> tuple[float, float]:
        return (self._latitude, self._longitude)

    @property
    def open_time(self) -> time:
        return self._open_time

    @property
    def close_time(self) -> time:
        return self._close_time

    @property
    def services(self) -> list[Service]:
        return self._services

    @property
    def chargers(self) -> list[Charger]:
        return self._chargers
