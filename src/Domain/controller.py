from datetime import datetime, time

from src.Domain.charger_type import ChargerType
from src.Domain.charging_station import ChargingStation
from src.Domain.charger import Charger
from src.Domain.option import Option
from src.Domain.price_rate import PriceRate
from src.Domain.service import Service


from src.Utils.constants import ServiceType

class Controller:
    @staticmethod
    def get_stations(cls):
        charger_type1 = ChargerType(id=1, name="Type 2", kw_speed=22, description="Standard Type 2 charger")
        charger_type2 = ChargerType(id=2, name="CCS", kw_speed=50, description="Fast CCS charger")

        chargers_s1 = [
            Charger(id=1, type=charger_type1, busy=False, active=True),
            Charger(id=2, type=charger_type2, busy=False, active=True)
        ]
        chargers_s2 = [
            Charger(id=3, type=charger_type1, busy=False, active=True),
            Charger(id=4, type=charger_type2, busy=False, active=True)
        ]

        services_s1 = [
            Service(id=1, name="Motel", type=ServiceType.MOTEL, open_time=time(0, 0), close_time=time(23, 59)),
            Service(id=2, name="Bar Paco", type=ServiceType.CAFE, open_time=time(8, 0), close_time=time(20, 0))
        ]
        services_s2 = [
            Service(id=3, name="Farmacia", type=ServiceType.PHARMACY, open_time=time(0, 0), close_time=time(23, 59)),
            Service(id=4, name="Banco Santander", type=ServiceType.MECHANIC, open_time=time(7, 0), close_time=time(22, 0))
        ]

        pr_s1 = [
            PriceRate(id=1, charger_type=charger_type1, start_date=datetime(2024, 1, 1), end_date=datetime(2027, 12, 31), price_per_kwh=0.30),
            PriceRate(id=2, charger_type=charger_type2, start_date=datetime(2024, 1, 1), end_date=datetime(2027, 12, 31), price_per_kwh=0.50)
        ]
        pr_s2 = [
            PriceRate(id=3, charger_type=charger_type1, start_date=datetime(2024, 1, 1), end_date=datetime(2027, 12, 31), price_per_kwh=0.25),
            PriceRate(id=4, charger_type=charger_type2, start_date=datetime(2024, 1, 1), end_date=datetime(2027, 12, 31), price_per_kwh=0.45)
        ]

        station1 = ChargingStation(id=1, name="Luz del Tajo", latitude=39.857591, longitude=-4.020744, open_time=time(0, 0), close_time=time(23, 59), services=services_s1, chargers=chargers_s1, price_rates=pr_s1)
        station2 = ChargingStation(id=2, name="Islazul", latitude=40.364541, longitude=-3.736241, open_time=time(0, 0), close_time=time(23, 59), services=services_s2, chargers=chargers_s2, price_rates=pr_s2)

        o1 = Option(request_id=1, charging_station=station1, price_rate=pr_s1[0], charger_type=charger_type1, start_time=datetime(2024, 6, 1, 10, 0), end_time=datetime(2024, 6, 1, 12, 0))
        o2 = Option(request_id=2, charging_station=station1, price_rate=pr_s1[1], charger_type=charger_type2, start_time=datetime(2024, 6, 1, 14, 0), end_time=datetime(2024, 6, 1, 15, 30))
        o3 = Option(request_id=3, charging_station=station2, price_rate=pr_s2[0], charger_type=charger_type1, start_time=datetime(2024, 6, 1, 9, 0), end_time=datetime(2024, 6, 1, 11, 0))
        o4 = Option(request_id=4, charging_station=station2, price_rate=pr_s2[1], charger_type=charger_type2, start_time=datetime(2024, 6, 1, 13, 0), end_time=datetime(2024, 6, 1, 14, 30))

        return (o1, o2, o3, o4)

