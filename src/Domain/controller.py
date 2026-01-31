from src.Domain.chargingStation import chargingStation
from src.Domain.chargingStation import chargingStation

class Controller:
    def __init__(self, gps_client=None):
        self.gps_client = gps_client
        self.charging_stations = {}
        self.demo_stations()

    def demo_stations(self):
        station1 = chargingStation(id="Luz del Tajo", latitude=39.857591, longitude=-4.020744, power_kw=22)
        station2 = chargingStation(id="Islazul", latitude=40.364541, longitude=-3.736241, power_kw=50)
        self.charging_stations[station1.id] = station1
        self.charging_stations[station2.id] = station2

    def get_stations(self) -> list[chargingStation]:
        return list(self.charging_stations.values())

    def get_position(self) -> (float, float):
        default_pos = (39.54505007110555, -4.328554881757664)  # Default position
        data = self.gps_client.get_data() if self.gps_client else None
        if data:
            latitude = data.get('lat', default_pos[0])  # Default latitude if not available
            longitude = data.get('lon', default_pos[1])  # Default longitude if not available
            return (latitude, longitude)

        return default_pos

    def get_connected_gps(self) -> bool:
        return self.gps_client.get_connected() if self.gps_client else False
