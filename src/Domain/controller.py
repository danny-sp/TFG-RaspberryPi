from datetime import datetime, time
from geopy.distance import geodesic
from typing import Tuple

from src.Domain.charger_type import ChargerType
from src.Domain.charging_station import ChargingStation
from src.Domain.charger import Charger
from src.Domain.option import Option
from src.Domain.price_rate import PriceRate
from src.Domain.service import Service

from src.Persistance.route_client import get_route_geometry

from src.Utils.constants import ServiceType
from src.Utils.logger import setup_logger

class Controller:
    def __init__(self, gps_client=None):
        self.gps_client = gps_client
        self.charging_stations = {}
        self._logger = setup_logger("Controller")

    def get_stations(self):
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

    def get_position(self) -> Tuple[float, float]:
        default_pos = (39.54505007110555, -4.328554881757664)  # Default position
        data = self.gps_client.get_data() if self.gps_client else None
        if data:
            latitude = data.get('lat', default_pos[0])  # Default latitude if not available
            longitude = data.get('lon', default_pos[1])  # Default longitude if not available
            return (latitude, longitude)

        return default_pos

    def get_connected_gps(self) -> bool:
        return self.gps_client.get_connected() if self.gps_client else False

    def get_route_str(self, destination: str):
        start_coords = self.get_position()

        if destination == "BILBAO":
            end_coords = (43.262873, -2.947564)
        elif destination == "MADRID":
            end_coords = (40.451843, -3.686502)
        else:
            self._logger.warning(f"Unknown destination '{destination}' requested")
            return None

        self._logger.info(f"Fetching route from {start_coords} to {end_coords} for destination '{destination}'")
        response = get_route_geometry(start_coords, end_coords)

        if response is None:
            self._logger.warning(f"No route found for destination '{destination}'")
            return None

        route, distance, duration = response
        if len(route) > 1000:
            self._logger.debug(f"Route has {len(route)} points, reducing for performance.")
            route = route[::5]

        return route, distance, duration

    def get_route_coords(self, destination: Tuple[float, float]):
        start_coords = self.get_position()
        end_coords = destination

        self._logger.info(f"Fetching route from {start_coords} to {end_coords} for custom coordinates")
        route, distance, duration = get_route_geometry(start_coords, end_coords)

        if not route:
            self._logger.warning(f"No route found for custom coordinates {destination}")
        if len(route) > 1000:
            self._logger.debug(f"Route has {len(route)} points, reducing for performance.")
            route = route[::5]

        return route, distance, duration

    def get_distance_coords(self, destination: Tuple[float, float]) -> float:
        start_coords = self.get_position()
        end_coords = destination

        self._logger.info(f"Fetching distance from {start_coords} to {end_coords} for custom coordinates")
        response = get_route_geometry(start_coords, end_coords)

        if response is None:
            self._logger.warning(f"No route found for custom coordinates {destination}")
            distance = geodesic(start_coords, end_coords).kilometers
        else:
            _, distance, _ = response
            distance /= 1000

        return distance
