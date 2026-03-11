from datetime import datetime

from src.Domain.charging_station import ChargingStation
from src.Domain.price_rate import PriceRate
from src.Domain.charger_type import ChargerType

class Option:
    def __init__(self, request_id: int, charging_station: ChargingStation, price_rate: PriceRate, charger_type: ChargerType, start_time: datetime, end_time: datetime):
        self._request_id = request_id
        self._charging_station = charging_station
        self._price_rate = price_rate
        self._charger_type = charger_type
        self._start_time = start_time
        self._end_time = end_time
        self._duration_hours = (end_time - start_time).total_seconds() / 3600
        # self._price = self._duration_hours * self._price_rate.price_per_kwh
        self._price = 40.7

    @staticmethod
    def from_dict(data: dict):
        charging_station_data = data["charging_station"]
        price_rate_data = data["price_rate"]
        charger_type_data = data["charger_type"]

        charging_station = ChargingStation(
            id=charging_station_data["id"],
            name=charging_station_data["name"],
            location=charging_station_data["location"],
            operator=charging_station_data["operator"]
        )

        price_rate = PriceRate(
            id=price_rate_data["id"],
            price_per_kwh=price_rate_data["price_per_kwh"]
        )

        charger_type = ChargerType(
            id=charger_type_data["id"],
            name=charger_type_data["name"],
            kw_speed=90,
            description="charger_type_data["
        )

        return Option(
            request_id=data["request_id"],
            charging_station=charging_station,
            price_rate=price_rate,
            charger_type=charger_type,
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"])
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
    def price_rate(self) -> PriceRate:
        return self._price_rate

    @property
    def charger_type(self) -> ChargerType:
        return self._charger_type

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
