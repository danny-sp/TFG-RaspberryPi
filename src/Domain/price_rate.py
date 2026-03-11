from datetime import datetime

from src.Domain.charger_type import ChargerType

class PriceRate:
    def __init__(self, id: int, charger_type: ChargerType = None, start_date: datetime = datetime.now(), end_date: datetime = None, price_per_kwh: float = 0):
        self._id = id
        self._charger_type = charger_type
        self._start_date = start_date
        self._end_date = end_date
        self._price_per_kwh = price_per_kwh

    ##############
    # PROPERTIES #
    ##############
    @property
    def id(self) -> int:
        return self._id

    @property
    def charger_type(self) -> ChargerType:
        return self._charger_type

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @property
    def end_date(self) -> datetime:
        return self._end_date

    @property
    def price_per_kwh(self) -> float:
        return self._price_per_kwh
