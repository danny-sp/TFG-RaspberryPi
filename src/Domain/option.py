from datetime import datetime

from src.Domain.charging_station import ChargingStation

from src.Utils.constants import ServiceType

class Option:
    def __init__(self, request_id: int, charging_station: ChargingStation, price: float, start_time: datetime, end_time: datetime, services_nearby: list[ServiceType]):
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
    def from_dict(data: dict):
        charging_station_data = data["charging_station"]
        services_nearby_data = data["services_nearby"]

        charging_station = ChargingStation(
            id=charging_station_data["id"],
            name=charging_station_data["name"],
            location=charging_station_data["location"],
            operator=charging_station_data["operator"]
        )

        return Option(
            request_id=data["request_id"],
            charging_station=charging_station,
            price=data["price"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            services_nearby=[ServiceType[service.upper()] for service in services_nearby_data]
        )

    ##############
    # PROPERTIES #
    ##############
    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def charging_station(self) -> ChargingStation:
        return self._charging_station

    @property
    def price(self) -> float:
        return self._price

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def end_time(self) -> datetime:
        return self._end_time

    @property
    def duration_hours(self) -> float:
        return self._duration_hours

    @property
    def price(self) -> float:
        return self._price

    @property
    def services_nearby(self) -> list[ServiceType]:
        return self._services_nearby
