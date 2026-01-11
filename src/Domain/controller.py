from src.Domain.chargingStation import chargingStation

class ChargeController:
    def __init__(self):
        self.charging_stations = {}
        self.demo_stations()

    def demo_stations(self):
        station1 = chargingStation(id="Luz del Tajo", latitude=39.857591, longitude=-4.020744, power_kw=22)
        station2 = chargingStation(id="Islazul", latitude=40.364541, longitude=-3.736241, power_kw=50)
        self.charging_stations[station1.id] = station1
        self.charging_stations[station2.id] = station2

    def get_stations(self):
        return list(self.charging_stations.values())

